"""Synchronisierte Konturplanung, nachgelagerte Abbrandkorrektur und G-Code."""
import math
import heapq

from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient

from profiles import CamError, Contour, clean, clean_point
from nc_program import verify_program


HEAT_LEAD_MM = 10.0


def number(data, key, low, high, default=None):
    try:
        value = float(data.get(key, default))
    except (ValueError, TypeError):
        raise CamError(f'{key}: gültige Zahl erforderlich.')
    if not math.isfinite(value) or not low <= value <= high:
        raise CamError(f'{key}: Wert zwischen {low:g} und {high:g} erforderlich.')
    return value


def point_at(line, distance, closed):
    if closed:
        distance %= line.length
    p = line.interpolate(distance)
    return [p.x, p.y]


def section(points, start, end, closed):
    line = LineString(points)
    a, b = start * line.length, end * line.length
    if closed and b <= a + 1e-9:
        b += line.length
    if b <= a + 1e-9:
        raise CamError('Offene Kontur: Endpunkt muss hinter dem Startpunkt liegen; Richtung ggf. umkehren.')
    lengths = [0.]
    for p, q in zip(points, points[1:]):
        lengths.append(lengths[-1] + math.dist(p, q))
    distances = sorted({a, b} | {d + shift for d in lengths for shift in (0, line.length)
                                if a < d+shift < b})
    result = [point_at(line, d, closed) for d in distances]
    if closed and abs((b-a)-line.length) < 1e-7:
        result[-1] = result[0][:]
    return Contour(result, getattr(points, 'corners', None))


def corner_sections(points):
    """SVG-Ecken verwenden, sonst an nichtkollinearen Richtungswechseln trennen."""
    indices = [0]
    corners = getattr(points, 'corners', None)
    for i in range(1, len(points)-1):
        if corners is not None:
            if any(math.dist(points[i], corner) < 1e-6 for corner in corners):
                indices.append(i)
            continue
        incoming = [points[i][k]-points[i-1][k] for k in (0, 1)]
        outgoing = [points[i+1][k]-points[i][k] for k in (0, 1)]
        product = math.hypot(*incoming)*math.hypot(*outgoing)
        cross = incoming[0]*outgoing[1]-incoming[1]*outgoing[0]
        dot = sum(x*y for x,y in zip(incoming, outgoing))
        if product == 0:
            continue
        if abs(cross) > product*1e-10 or dot <= 0:
            indices.append(i)
    indices.append(len(points)-1)
    return [points[start:end+1] for start,end in zip(indices, indices[1:])]


def synchronize(a, b, count):
    """Eckpaare in Laufrichtung koppeln und nur abschnittsweise interpolieren."""
    lines = [LineString(a), LineString(b)]
    if min(line.length for line in lines) < 1e-6:
        raise CamError('Kontur ist zu kurz.')
    parts = [corner_sections(points) for points in (a, b)]
    if len(parts[0]) != len(parts[1]):
        raise CamError('Eckzuordnung nicht eindeutig: Beide Konturen benötigen gleich viele '
                       'echte Ecken im Schnittverlauf. Start/Ende, Laufrichtung und '
                       'Profilunterteilung prüfen. Bei DXF oder Profildaten ohne SVG-Eckinformationen '
                       'zählen auch nichtkollineare Stützpunkte als Ecken.')
    result = [[list(a[0])], [list(b[0])]]
    for pair in zip(*parts):
        section_lines = [LineString(points) for points in pair]
        # Die längere relative Teilstrecke bestimmt die gewünschte Auflösung.
        steps = max(1, math.ceil(count*max(line.length/whole.length
                                         for line,whole in zip(section_lines, lines))))
        fractions = {i/steps for i in range(1, steps)}
        # Alle Kurvenstützpunkte beider Seiten erhalten; auch bei kleinem segments-Wert
        # darf aus einem Kreis kein grobes Vieleck werden.
        for points, line in zip(pair, section_lines):
            distance = 0.
            for p, q in zip(points, points[1:-1]):
                distance += math.dist(p, q)
                fractions.add(distance/line.length)
        merged = [0.]
        fraction_tolerance = 1e-7/max(line.length for line in section_lines)
        for fraction in sorted(fractions):
            if fraction-merged[-1] > fraction_tolerance and 1-fraction > fraction_tolerance:
                merged.append(fraction)
        fractions = merged[1:]
        if len(result[0])+len(fractions)+1 > 6000:
            raise CamError('Zu viele Liniensegmente; Profile bitte vereinfachen.')
        for output, points, line in zip(result, pair, section_lines):
            output.extend(point_at(line, fraction*line.length, False) for fraction in fractions)
            # Eckkoordinaten exakt übernehmen, ohne Bogenlängenrundung.
            output.append(list(points[-1]))
    return result


def prepared(data, name):
    profile = data.get(name)
    if not isinstance(profile, dict) or not isinstance(profile.get('contours'), list):
        raise CamError('Zwei importierte Profile sind erforderlich.')
    contours = profile['contours']
    if not 1 <= len(contours) <= 100:
        raise CamError('Ungültige Konturanzahl.')
    if any(not isinstance(c, list) or not 2 <= len(c) <= 20000 for c in contours):
        raise CamError('Ungültige Konturpunkte.')
    if sum(map(len, contours)) > 20000:
        raise CamError('Profil enthält zu viele Punkte.')
    contours = [clean(c) for c in contours]
    index = int(number(data, name+'_contour', 0, len(contours)-1, 0))
    scale = number(data, name+'_scale', .0001, 10000, 1)
    x = number(data, name+'_x', -1e6, 1e6)
    y = number(data, name+'_y', -1e6, 1e6)
    min_x = min(p[0] for c in contours for p in c)
    min_y = min(p[1] for c in contours for p in c)
    contours = [[[(p[0]-min_x)*scale+x, (p[1]-min_y)*scale+y] for p in c] for c in contours]
    points = contours[index]
    corner_data = profile.get('corners')
    corners = None
    if corner_data is not None:
        if not isinstance(corner_data, list) or len(corner_data) != len(contours):
            raise CamError('Ungültige SVG-Eckinformationen; Datei erneut importieren.')
        selected = corner_data[index]
        if not isinstance(selected, list) or len(selected) > len(points):
            raise CamError('Ungültige SVG-Eckinformationen; Datei erneut importieren.')
        corners = [clean_point(corner) for corner in selected]
        corners = [[(p[0]-min_x)*scale+x, (p[1]-min_y)*scale+y] for p in corners]
        if any(not any(math.dist(corner, p) < 1e-6 for p in points) for corner in corners):
            raise CamError('SVG-Eckinformationen passen nicht zur Kontur; Datei erneut importieren.')
    closed = points[0] == points[-1]
    if closed:
        polygon = Polygon(points)
        if not polygon.is_valid or polygon.area < 1e-6:
            raise CamError(f'{name.upper()}: geschlossene Kontur überschneidet sich oder hat keine Fläche.')
        points = list(map(list, orient(polygon, sign=1).exterior.coords))
    elif not LineString(points).is_simple:
        raise CamError(f'{name.upper()}: offene Kontur überschneidet sich.')
    if data.get(name+'_reverse') is True:
        points = list(reversed(points))
    start = number(data, name+'_start', 0, 100, 0)/100
    end = number(data, name+'_end', 0, 100, 100)/100
    return Contour(points, corners), closed, start, end, contours


def offset_corners(original, offset, closed, radius, mode):
    """Echte Ecken über den Schnitt ihrer versetzten Nachbarkanten übertragen."""
    corners = getattr(original, 'corners', None)
    if corners is None:
        return Contour(offset)
    mapped = []
    vertices = original[:-1] if closed else original
    sign = (1 if mode == 'left' else -1) if not closed else (
        (1 if Polygon(original).exterior.is_ccw else -1) * (1 if mode == 'inner' else -1))
    for corner in corners:
        i = min(range(len(vertices)), key=lambda k: math.dist(vertices[k], corner))
        p, q, r = vertices[i-1], vertices[i], vertices[(i+1) % len(vertices)]
        u = [(q[k]-p[k])/math.dist(p, q) for k in (0, 1)]
        v = [(r[k]-q[k])/math.dist(q, r) for k in (0, 1)]
        cross = u[0]*v[1]-u[1]*v[0]
        if abs(cross) < 1e-10:
            raise CamError('Abbrand verändert echte Ecken; Radius reduzieren oder Profil ändern.')
        a = [q[0]-sign*radius*u[1], q[1]+sign*radius*u[0]]
        b = [q[0]-sign*radius*v[1], q[1]+sign*radius*v[0]]
        t = ((b[0]-a[0])*v[1]-(b[1]-a[1])*v[0])/cross
        expected = [a[k]+t*u[k] for k in (0, 1)]
        nearest = min(offset, key=lambda p: math.dist(p, expected))
        if math.dist(nearest, expected) > 1e-5:
            raise CamError('Abbrand entfernt oder begrenzt echte Ecken; Radius reduzieren oder Profil ändern.')
        mapped.append(list(nearest))
    return Contour(offset, mapped)


def corrected(points, closed, radius, mode):
    if radius == 0 or mode == 'center':
        return points
    if closed and mode in ('outer', 'inner'):
        original = Polygon(points)
        result = original.buffer(radius if mode == 'outer' else -radius, join_style='mitre')
        if result.is_empty or result.geom_type != 'Polygon' or len(result.interiors):
            raise CamError('Abbrand lässt die Kontur kollabieren oder zerfallen; Form so nicht schneidbar.')
        # Auch verschwundene Engstellen/Details erkennen, die buffer() ansonsten entfernt.
        if mode == 'inner' and original.boundary.hausdorff_distance(result.boundary) > radius*5 + .03:
            raise CamError('Abbrand entfernt schmale Konturdetails. Radius reduzieren oder Profil ändern.')
        sign = 1 if Polygon(points).exterior.is_ccw else -1
        pts = list(map(list, orient(result, sign=sign).exterior.coords))
        pts = offset_corners(points, pts, closed, radius, mode)
        line = LineString(pts)
        # Den ursprünglichen Start auf die korrigierte Kontur abbilden.
        start = points[0]
        if pts.corners:
            for original_corner, offset_corner in zip(points.corners, pts.corners):
                if math.dist(original_corner, start) < 1e-6:
                    start = offset_corner
                    break
        t = line.project(Point(start))/line.length
        return section(pts, t, t, True)
    if not closed and mode in ('left', 'right'):
        result = LineString(points).offset_curve(radius if mode == 'left' else -radius, join_style='mitre')
        if result.is_empty or result.geom_type != 'LineString' or not result.is_simple:
            raise CamError('Abbrandkorrektur der offenen Kontur zerfällt oder überschneidet sich.')
        return offset_corners(points, list(map(list, result.coords)), closed, radius, mode)
    raise CamError('Außen/Innen benötigt geschlossene Konturen; offene Konturen verwenden Links/Rechts oder Kontur.')


def axes(a, b, span, z0, z1):
    return [*(a[i]+(b[i]-a[i])*(-z0)/(z1-z0) for i in (0,1)),
            *(a[i]+(b[i]-a[i])*(span-z0)/(z1-z0) for i in (0,1))]


def path_blocks(a, b, data):
    blocks = [list(p)+list(q) for p,q in zip(a,b)]
    if data.get('access') is True:
        entry = [number(data, 'entry_'+axis, -1e6, 1e6) for axis in ('x','y','u','v')]
        exit_point = [number(data, 'exit_'+axis, -1e6, 1e6) for axis in ('x','y','u','v')]
        blocks = [entry] + blocks + [exit_point]
    return blocks


def check_room(blocks, width, height):
    for p in blocks:
        if any(v < low-1e-7 or v > high+1e-7
               for v,low,high in zip(p, (-width/2,0,-width/2,0),
                                     (width/2,height,width/2,height))):
            raise CamError('Bauteil oder Drahtweg liegt außerhalb des Schneidraums (einschließlich Achsprojektion/Ein- und Ausfahrt).')


def automatic_access(nominal, compensated, full_pairs, block_width, block_height, closed,
                     entry_validator=None):
    """Gemeinsame Randpunkte mit sichtbaren Zugängen in 21 Drahtquerschnitten suchen.

    Die Konturstarts bleiben erhalten, damit die bestehende Eckzuordnung nicht
    durch eine unabhängige Startpunktwahl auf beiden Seiten verändert wird.
    """
    obstacles = []
    for full in full_pairs:
        samples = []
        for step in range(21):
            t = step/20
            pts = [[p[k]*(1-t)+q[k]*t for k in (0, 1)] for p, q in zip(*full)]
            samples.append(Polygon(pts).buffer(-1e-7) if closed else LineString(pts))
        obstacles.append(samples)

    def choose(index):
        endpoints = [pair[side][index] for pair in (nominal, compensated) for side in (0, 1)]
        candidates = []
        reachable = []
        for vertical in (True, False):
            limit = block_height if vertical else block_width
            low = 0 if vertical else -block_width/2
            coordinates = [p[1 if vertical else 0] for p in endpoints]
            for edge in (-block_width/2, block_width/2) if vertical else (block_height,):
                for value in sorted({low, low+limit, sum(coordinates)/len(coordinates), *coordinates}):
                    value = max(low, min(low+limit, value))
                    if vertical and value <= 1e-7:
                        continue  # Untere Ecken gehören zur gesperrten Auflagefläche.
                    access = [edge, value] if vertical else [value, edge]
                    valid = True
                    for pair, samples in zip((nominal, compensated), obstacles):
                        for step, obstruction in enumerate(samples):
                            t = step/20
                            target = [pair[0][index][k]*(1-t)+pair[1][index][k]*t for k in (0, 1)]
                            if math.dist(access, target) < 1e-7:
                                continue
                            lead = LineString([access, target])
                            if closed:
                                # Nur Berührung am Schnittstart zulassen, keine Fahrt durch das Bauteil.
                                blocked = lead.intersects(obstruction)
                            else:
                                # Endpunktkontakt ausnehmen, Überlappungen/vorzeitige Kontakte ablehnen.
                                trimmed = LineString([access, lead.interpolate(max(0, lead.length-1e-6)).coords[0]])
                                blocked = trimmed.intersects(obstruction)
                            if blocked:
                                valid = False
                                break
                        if not valid:
                            break
                    if valid:
                        score = sum(math.dist(access, p) for p in endpoints)
                        candidates.append((score, access))
                        if index == 0 and entry_validator is not None:
                            try:
                                entry_validator(access+access)
                                reachable.append((score, access))
                            except CamError:
                                pass
        if not candidates:
            raise CamError('Kein geradliniger automatischer Zugang von oben oder seitlich ohne Konturdurchquerung gefunden. '
                           'Start/Ende ändern oder manuelle Ein-/Ausfahrt verwenden.')
        # Ohne Heizvorlauf bleibt die Geometrie als Entwurf sichtbar; der
        # nachfolgende Anfahrtscheck sperrt das Programm mit genauer Erklärung.
        return min(reachable or candidates, key=lambda candidate: candidate[0])[1]

    entry, exit_point = choose(0), choose(-1)
    return entry+entry, exit_point+exit_point


def cold_approach(origin, target, block_width, block_height, width, height, clearance=0):
    """G0-Weg außen um den Block; keine Fahrt entlang der aufliegenden Unterseite.

    Jede Teilbewegung liegt mit ihrer gesamten Koordinatenhülle seitlich oder
    oberhalb des Blocks. Das erlaubt auch abweichende X-/U-Schalterlagen und
    verlangt keine geradlinige Interpolation gleichzeitig schnellfahrender Achsen.
    """
    def free(a, b):
        # Auch unabhängig verfahrende X/Y/U/V-Achsen durch die Hülle absichern.
        min_x = min(a[0], a[2], b[0], b[2])
        max_x = max(a[0], a[2], b[0], b[2])
        min_y = min(a[1], a[3], b[1], b[3])
        return (max_x <= -block_width/2+1e-7 or min_x >= block_width/2-1e-7
                or min_y >= block_height-1e-7)

    nodes = [list(origin), list(target)]
    for x,y in ((-block_width/2-clearance,block_height+clearance),
                (block_width/2+clearance,block_height+clearance),
                (-width/2,height), (width/2,height)):
        p = [x,y,x,y]
        if -width/2 <= x <= width/2 and 0 <= y <= height and p not in nodes:
            nodes.append(p)
    check_room(nodes, width, height)
    distances = {0: 0.}
    previous = {}
    pending = [(0., 0)]
    while pending:
        distance, i = heapq.heappop(pending)
        if distance != distances[i]:
            continue
        if i == 1:
            route = [nodes[i]]
            while i in previous:
                i = previous[i]
                route.append(nodes[i])
            return list(reversed(route))
        for j,p in enumerate(nodes):
            if i == j or not free(nodes[i], p):
                continue
            length = distance+math.dist(nodes[i],p)
            if length < distances.get(j, math.inf):
                distances[j] = length
                previous[j] = i
                heapq.heappush(pending, (length, j))
    raise CamError('Keine freie Kaltanfahrt vom Maschinennullpunkt möglich. '
                   'Schalterlage und Rohteil prüfen; Zugang muss außen seitlich oder oben liegen. '
                   'Die aufliegende Unterseite ist gesperrt.')


def heating_approach(origin, entry, block_width, block_height, width, height):
    """M3-Punkt mit mindestens 10 mm Luft bis zur Rohteilfläche bestimmen.

    Am automatisch gewählten Randpunkt ist der zusätzliche senkrechte G1-Weg
    genau 10 mm lang, auf beiden Seiten parallel. Ein bereits weiter außen
    liegender manueller Start bleibt erhalten; seine Distanz ist mindestens 10 mm.
    """
    options = []
    sides = [(0,-1,-block_width/2-max(entry[0],entry[2])),
             (0,1,min(entry[0],entry[2])-block_width/2),
             (1,1,min(entry[1],entry[3])-block_height)]
    for axis, direction, gap in sides:
        if gap < -1e-7:
            continue
        distance = max(0., HEAT_LEAD_MM-gap)
        start = list(entry)
        for offset in (0,2):
            start[axis+offset] += direction*distance
        try:
            check_room([start],width,height)
            approach = cold_approach(origin,start,block_width,block_height,width,height,HEAT_LEAD_MM)
        except CamError:
            continue
        options.append((distance,sum(math.dist(a,b) for a,b in zip(approach,approach[1:])),start,approach))
    if not options:
        raise CamError('Keine freie Kaltanfahrt mit 10 mm Heizvorlauf möglich. '
                       'Vor dem Materialeintritt werden seitlich oder oben mindestens 10 mm '
                       'Freiraum benötigt. Maschinennullpunkt, Rohteilmaße und Schalterlage prüfen.')
    _,_,start,approach = min(options,key=lambda option:option[:2])
    return start,approach


def gcode(blocks, feed, power, s_max, approach, machine_zero):
    # F ist die Länge des vierdimensionalen Achsvektors pro Minute (G94).
    lines = ['; HotWireCAM - generischer XYUV-Entwurf',
             '; Maschinennullpunkt: Kontaktschalter X/U positiv, Y/V unten.',
             '; Programm am zuvor gesetzten Maschinennullpunkt X0 Y0 U0 V0 starten.',
             '; Rohteilnullpunkt und Konturstart sind eigene Bezugspunkte.',
             '; G0-Kaltanfahrt nur seitlich oder oberhalb des aufliegenden Rohteils.',
             '; Stromregler: S linear zur eingestellten Leistung; Firmware muss dies unterstuetzen.',
             'G21', 'G90', 'G94', 'M5',
             '; Start: X0.00000 Y0.00000 U0.00000 V0.00000',
             '; Kaltanfahrt zum Einschaltpunkt, mindestens 10 mm vor Materialeintritt (M5, G0)']
    def coordinates(p):
        return ' '.join(f'{axis}{v-zero:.5f}' for axis,v,zero in zip('XYUV', p, machine_zero))
    for p in approach[1:]:
        lines.append('G0 ' + coordinates(p))
    lines.append('M3' if s_max is None else f'M3 S{power*s_max/100:.5f}')
    if approach[-1] != blocks[0]:
        lines.append('G1 ' + coordinates(blocks[0]) + f' F{feed:.5f}')
    for p in blocks[1:]:
        lines.append('G1 ' + coordinates(p) + f' F{feed:.5f}')
    return '\n'.join(lines + ['M5', 'M2', ''])


def plan(data):
    width = number(data, 'width', .01, 1e6)
    height = number(data, 'height', .01, 1e6)
    span = number(data, 'span', .01, 1e6)
    block_width = number(data, 'block_width', .01, width)
    block_height = number(data, 'block_height', .01, height)
    block_span = number(data, 'block_span', .001, span)
    z0 = (span-block_span)/2
    z1 = (span+block_span)/2
    machine_zero = [number(data, 'machine_zero_x', .000001, width/2, width/2), 0.,
                    number(data, 'machine_zero_u', .000001, width/2, width/2), 0.]
    count = int(number(data, 'segments', 4, 2000, 200))
    feed = number(data, 'feed', .001, 1e6)
    power = number(data, 'power', 0, 100)
    radius = number(data, 'burn_radius', 0, 100)
    mode = data.get('mode', 'outer')
    auto_access = data.get('auto_access') is True
    if auto_access and (data.get('access') is True or mode == 'inner'):
        raise CamError('Automatischer Randzugang ist nicht mit manuellem Zugang oder Innenkonturen kombinierbar.')
    if mode not in ('outer','inner','center','left','right'):
        raise CamError('Unbekannte Korrekturseite.')
    profiles = [prepared(data, name) for name in ('xy','uv')]
    for *_, contours in profiles:
        check_room([p+p for contour in contours for p in contour], block_width, block_height)
    if profiles[0][1] != profiles[1][1]:
        raise CamError('Beide gewählten Konturen müssen entweder offen oder geschlossen sein.')
    closed = profiles[0][1]
    if (closed and mode in ('left','right')) or (not closed and mode in ('outer','inner')):
        raise CamError('Korrekturseite passt nicht zu offenen/geschlossenen Profilen.')
    if mode == 'inner' and data.get('access') is not True:
        raise CamError('Für Innenkonturen Ein-/Ausfahrt aktivieren und Einfädel- oder Zugangspunkt festlegen.')
    # 1. Vollständiges Nennprogramm auf der Originalkontur aufbauen.
    nominal_profiles = [section(p, s, e, c) for p,c,s,e,_ in profiles]
    na, nb = synchronize(*nominal_profiles, count)
    nominal = path_blocks(na, nb, data)
    # 2. Erst danach Abbrand anwenden und die Bewegungsblöcke gemeinsam neu abtasten.
    compensated = [section(corrected(p,c,radius,mode), s,e,c) for p,c,s,e,_ in profiles]
    ca, cb = synchronize(*compensated, count)
    cut_sections = path_blocks(ca, cb, data)
    # Die gesamte ausgewählte Kontur prüfen, auch bei Teilschnitten.
    full_profiles = [section(p,s,s,True) if c else p for p,c,s,_,_ in profiles]
    full_corrected = [section(corrected(p,c,radius,mode),s,s,True) if c else corrected(p,c,radius,mode)
                      for p,c,s,_,_ in profiles]
    full_a, full_b = synchronize(*full_profiles, count)
    full_ca, full_cb = synchronize(*full_corrected, count)
    approach = None
    if auto_access:
        # Im Automatikmodus soll der komplette heiße Weg im Block bleiben.
        try:
            check_room([p+q for p,q in zip(full_ca, full_cb)], block_width, block_height)
        except CamError:
            raise CamError('Abbrandbahn liegt außerhalb des Blocks. Profil mit Abstand zum Rand platzieren '
                           'oder Blockmaße prüfen.') from None
        entry, exit_point = automatic_access(
            (na, nb), (ca, cb), ((full_a, full_b), (full_ca, full_cb)),
            block_width, block_height, closed,
            lambda entry: heating_approach(machine_zero,entry,block_width,block_height,width,height))
        nominal = [entry] + nominal + [exit_point]
        cut_sections = [entry] + cut_sections + [exit_point]
    for aa,bb in ((full_a,full_b),(full_ca,full_cb)):
        check_room([axes(p,q,span,z0,z1) for p,q in zip(aa,bb)], width,height)
    for aa,bb in ((full_a,full_b),(full_ca,full_cb)):
        for step in range(21):
            t = step/20
            pts = [[p[i]*(1-t)+q[i]*t for i in (0,1)] for p,q in zip(aa,bb)]
            shape = Polygon(pts) if closed else LineString(pts)
            if not shape.is_valid or (closed and shape.area < 1e-6) or (not closed and not shape.is_simple):
                raise CamError('Zwischen den Profilebenen kollabiert oder überschneidet sich die Drahtfläche. Startpunkte/Richtung prüfen.')
    # Auch Teilschnitte mit unterschiedlichen Endpunkten separat prüfen.
    for aa,bb in ((na,nb),(ca,cb)):
        for step in range(21):
            t = step/20
            line = LineString([[p[i]*(1-t)+q[i]*t for i in (0,1)] for p,q in zip(aa,bb)])
            if not line.is_simple or line.length < 1e-6:
                raise CamError('Der gewählte Teilschnitt kollabiert oder überschneidet sich zwischen den Profilebenen.')
    blocks = [axes(p[:2],p[2:],span,z0,z1) for p in cut_sections]
    nominal_axes = [axes(p[:2],p[2:],span,z0,z1) for p in nominal]
    check_room(nominal_axes, width,height)
    check_room(blocks, width,height)
    if data.get('access') is True:
        for p in (cut_sections[0], cut_sections[-1]):
            for x,y in (p[:2],p[2:]):
                if -block_width/2-1e-7 <= x <= block_width/2+1e-7 and y <= 1e-7:
                    raise CamError('Ein-/Austritt an der aufliegenden Unterseite ist gesperrt. '
                                   'Manuellen Zugang seitlich oder oberhalb des Rohteils wählen.')
    approach_error = None
    heating_start = None
    heat_lead = None
    try:
        heating_start,approach = heating_approach(machine_zero,blocks[0],block_width,block_height,width,height)
        try:
            cold_approach(machine_zero, blocks[-1], block_width, block_height, width, height)
        except CamError:
            raise CamError('Austritt liegt nicht frei seitlich oder oberhalb des Rohteils. '
                           'Ausfahrt bis außerhalb des Materials planen.') from None
    except CamError as error:
        approach_error = str(error)
        approach = None
        heating_start = None
    if heating_start is not None and heating_start != blocks[0]:
        heat_lead = [heating_start,blocks[0]]
    warnings = [
        'Geometrische Vorschau: 21 Zwischenquerschnitte geprüft. Keine vollständige thermische oder Kollisionssimulation.',
        'Konische Formen sind zulässig, solange Konturen und Achswege gültig bleiben. Drahtdurchhang, Werkstoff und Abbrand müssen praktisch ermittelt werden.',
        'Vorschub F: mm/min entlang des vierdimensionalen Achsvektors; Verhalten der Steuerung prüfen.',
        'Heizung mindestens 10 mm vor Materialeintritt einschalten; der äußere Heizvorlauf fährt '
        'mit G1 und Schnittvorschub. Keine zusätzliche Aufheizpause oder Temperaturregelung.',
    ]
    if mode == 'center' and radius:
        warnings.append('Modus Kontur: Der eingetragene Abbrandradius wird nicht angewendet.')
    if mode == 'inner':
        warnings.append('Innenkontur: Draht am Zugangspunkt einfädeln oder Zugangsschlitz vorsehen. Geradlinige Ein-/Ausfahrt schneidet Material; Zugang manuell prüfen.')
    if data.get('access') is True:
        warnings.append('Ein-/Ausfahrt erfolgt geradlinig mit eingeschaltetem Draht; keine automatische Hindernisumfahrung.')
    if auto_access:
        warnings.append('Automatischer Randzugang nur seitlich oder oben. Kaltanfahrt mit G0 ab Kontaktschalter-Maschinennullpunkt; '
                        'der Außenraum muss frei zugänglich sein. Keine Referenzfahrt oder Prüfung von Spannmitteln. '
                        'Ein-/Ausfahrt schneidet mit. Zugang in 21 Zwischenquerschnitten geprüft.')
    code = None
    program = None
    if approach_error:
        warnings.append(approach_error + ' Geometrische Schnittvorschau bleibt verfügbar; Export gesperrt.')
    if data.get('controller_confirmed') is True:
        s_max = number(data, 's_max', .001, 1e9)
        if approach is not None:
            code = gcode(blocks, feed, power, s_max, approach, machine_zero)
            program = verify_program(code, approach, blocks, machine_zero, feed,
                                     power*s_max/100, auto_access or data.get('access') is True)
    else:
        warnings.append('Export benötigt den S-Maximalwert und die bestätigte Zuordnung M3/S → Stromregler, XYUV und G94.')
        if approach is not None:
            # Gleicher Postprozessor, aber ohne erfundenen S-Bereich: M3 ohne S
            # ist ausschließlich eine interne, nicht herunterladbare Vorschauvorlage.
            preview_code = gcode(blocks, feed, power, None, approach, machine_zero)
            program = verify_program(preview_code, approach, blocks, machine_zero, feed,
                                     None, auto_access or data.get('access') is True, True)
    if program is not None:
        program['power_percent'] = power
    return {'nominal': nominal_axes, 'path': blocks, 'sections': cut_sections,
            'program': program,
            'gcode': code, 'warnings': warnings, 'segments': len(ca)-1,
            'room': {'width':width,'height':height,'span':span,'z_xy':z0,'z_uv':z1},
            'block': {'width':block_width,'height':block_height,'span':block_span},
            'start':blocks[0], 'end':blocks[-1], 'approach': approach,
            'heating_start': heating_start, 'heat_lead': heat_lead, 'heat_lead_mm': HEAT_LEAD_MM,
            'approach_error': approach_error, 'machine_zero': machine_zero,
            'raw_origin': [-block_width/2, 0., -block_width/2, 0.],
            'machine_path': [[v-zero for v,zero in zip(p,machine_zero)] for p in blocks],
            'access_enabled': auto_access or data.get('access') is True}
