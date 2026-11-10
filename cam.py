"""Synchronisierte Konturplanung, nachgelagerte Abbrandkorrektur und G-Code."""
import math

from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient

from profiles import CamError, clean


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
    return [point_at(line, d, closed) for d in distances]


def corner_sections(points):
    """An jedem Richtungswechsel trennen; kollineare Stützpunkte ignorieren."""
    indices = [0]
    for i in range(1, len(points)-1):
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
                       'Richtungswechsel im Schnittverlauf. Start/Ende, Laufrichtung und '
                       'Profilunterteilung prüfen; auch Kurvenstützpunkte zählen als Richtungswechsel.')
    result = [[list(a[0])], [list(b[0])]]
    for pair in zip(*parts):
        section_lines = [LineString(points) for points in pair]
        # Die längere relative Teilstrecke bestimmt die gewünschte Auflösung.
        steps = max(1, math.ceil(count*max(line.length/whole.length
                                         for line,whole in zip(section_lines, lines))))
        if len(result[0])+steps > 6000:
            raise CamError('Zu viele Liniensegmente; Profile bitte vereinfachen.')
        for output, points, line in zip(result, pair, section_lines):
            output.extend(point_at(line, i*line.length/steps, False) for i in range(1, steps))
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
    return points, closed, start, end, contours


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
        line = LineString(pts)
        # Den ursprünglichen Start auf die korrigierte Kontur abbilden.
        t = line.project(Point(points[0]))/line.length
        return section(pts, t, t, True)
    if not closed and mode in ('left', 'right'):
        result = LineString(points).offset_curve(radius if mode == 'left' else -radius, join_style='mitre')
        if result.is_empty or result.geom_type != 'LineString' or not result.is_simple:
            raise CamError('Abbrandkorrektur der offenen Kontur zerfällt oder überschneidet sich.')
        return list(map(list, result.coords))
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
        if any(v < -1e-7 or v > limit+1e-7 for v,limit in zip(p, (width,height,width,height))):
            raise CamError('Bauteil oder Drahtweg liegt außerhalb des Schneidraums (einschließlich Achsprojektion/Ein- und Ausfahrt).')


def gcode(blocks, feed, power, s_max):
    # F ist die Länge des vierdimensionalen Achsvektors pro Minute (G94).
    lines = ['; HotWireCAM - generischer XYUV-Entwurf',
             '; Startposition vor dem Einschalten manuell bei ausgeschaltetem Draht anfahren.',
             '; Stromregler: S linear zur eingestellten Leistung; Firmware muss dies unterstuetzen.',
             'G21', 'G90', 'G94', 'M5',
             '; Start: ' + ' '.join(f'{axis}{v:.5f}' for axis,v in zip('XYUV', blocks[0])),
             f'M3 S{power*s_max/100:.5f}']
    for p in blocks[1:]:
        lines.append('G1 ' + ' '.join(f'{axis}{v:.5f}' for axis,v in zip('XYUV', p)) + f' F{feed:.5f}')
    return '\n'.join(lines + ['M5', 'M2', ''])


def plan(data):
    width = number(data, 'width', .01, 1e6)
    height = number(data, 'height', .01, 1e6)
    span = number(data, 'span', .01, 1e6)
    z0 = number(data, 'z_xy', 0, span)
    z1 = number(data, 'z_uv', 0, span)
    if z1-z0 < .001:
        raise CamError('Profilebenen müssen mindestens 0,001 mm auseinanderliegen (XY vor UV).')
    count = int(number(data, 'segments', 4, 2000, 200))
    feed = number(data, 'feed', .001, 1e6)
    power = number(data, 'power', 0, 100)
    radius = number(data, 'burn_radius', 0, 100)
    mode = data.get('mode', 'outer')
    if mode not in ('outer','inner','center','left','right'):
        raise CamError('Unbekannte Korrekturseite.')
    profiles = [prepared(data, name) for name in ('xy','uv')]
    for *_, contours in profiles:
        check_room([p+p for contour in contours for p in contour], width, height)
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
    warnings = [
        'Geometrische Vorschau: 21 Zwischenquerschnitte geprüft. Keine vollständige thermische oder Kollisionssimulation.',
        'Konische Formen sind zulässig, solange Konturen und Achswege gültig bleiben. Drahtdurchhang, Werkstoff und Abbrand müssen praktisch ermittelt werden.',
        'Vorschub F: mm/min entlang des vierdimensionalen Achsvektors; Verhalten der Steuerung prüfen.',
    ]
    if mode == 'center' and radius:
        warnings.append('Modus Kontur: Der eingetragene Abbrandradius wird nicht angewendet.')
    if mode == 'inner':
        warnings.append('Innenkontur: Draht am Zugangspunkt einfädeln oder Zugangsschlitz vorsehen. Geradlinige Ein-/Ausfahrt schneidet Material; Zugang manuell prüfen.')
    if data.get('access') is True:
        warnings.append('Ein-/Ausfahrt erfolgt geradlinig mit eingeschaltetem Draht; keine automatische Hindernisumfahrung.')
    code = None
    if data.get('controller_confirmed') is True:
        s_max = number(data, 's_max', .001, 1e9)
        code = gcode(blocks, feed, power, s_max)
    else:
        warnings.append('Export benötigt den S-Maximalwert und die bestätigte Zuordnung M3/S → Stromregler, XYUV und G94.')
    return {'nominal': nominal_axes, 'path': blocks, 'sections': cut_sections,
            'gcode': code, 'warnings': warnings, 'segments': len(ca)-1,
            'room': {'width':width,'height':height,'span':span,'z_xy':z0,'z_uv':z1},
            'start':blocks[0], 'end':blocks[-1]}
