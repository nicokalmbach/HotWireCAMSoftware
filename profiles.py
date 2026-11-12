"""Vektorimport nach Millimeter; Dateien bleiben ausschließlich im Speicher."""
import io
import math
import xml.etree.ElementTree as ET

import ezdxf
from ezdxf import units
from ezdxf.path import make_path
from shapely.geometry import LineString, Point
from svgelements import SVG, Path, Shape, Move

TOLERANCE = 0.03  # mm, Näherung beim Kurvenimport
MAX_POINTS = 20000


class CamError(ValueError):
    pass


class Contour(list):
    """Polygonzug mit optionalen echten SVG-Ecken (ohne Abflachungsstützpunkte)."""
    def __init__(self, points, corners=None):
        super().__init__(points)
        self.corners = corners


def svg_corners(segments):
    """Tangenten an Segmentübergängen vergleichen, auch am geschlossenen Anfang."""
    segments = [s for s in segments
                if any(abs(s.point(t)-s.start) > 1e-9 for t in (.25, .5, .75, 1))]
    corners = []
    pairs = list(zip(segments, segments[1:]))
    if segments and abs(segments[-1].end - segments[0].start) < 1e-7:
        pairs.append((segments[-1], segments[0]))
    for previous, following in pairs:
        # Kleine einseitige Sekanten funktionieren auch bei degenerierten Bezier-Griffen.
        incoming = previous.end - previous.point(1-1e-6)
        outgoing = following.point(1e-6) - following.start
        product = abs(incoming)*abs(outgoing)
        cross = incoming.x*outgoing.y-incoming.y*outgoing.x
        dot = incoming.x*outgoing.x+incoming.y*outgoing.y
        if product and (abs(cross) > product*1e-4 or dot <= 0):
            corners.append([previous.end.x*25.4/96, -previous.end.y*25.4/96])
    return corners


def clean_point(p):
    try:
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            raise ValueError
        p = [float(p[0]), float(p[1])]
    except (TypeError, ValueError) as exc:
        raise CamError('Profilpunkte müssen jeweils zwei gültige Koordinaten enthalten.') from exc
    if not all(math.isfinite(v) and abs(v) <= 1e7 for v in p):
        raise CamError("Ungültige oder zu große Profilkoordinaten.")
    return p


def clean(points):
    result = []
    for p in points:
        p = clean_point(p)
        if not result or math.dist(result[-1], p) > 1e-7:
            result.append(p)
    if len(result) < 2 or len(result) > MAX_POINTS:
        raise CamError("Eine Kontur benötigt 2 bis 20000 unterschiedliche Punkte.")
    if math.dist(result[0], result[-1]) < 1e-5:
        result[-1] = result[0][:]
    return result


def _flatten(segment, a=0., b=1., depth=0):
    p = segment.point(a)
    q = segment.point(b)
    line = LineString([(p.x, p.y), (q.x, q.y)])
    samples = [segment.point(a + (b-a)*t) for t in (.25, .5, .75)]
    error = max(line.distance(Point(s.x, s.y)) * 25.4 / 96 for s in samples)
    if error <= TOLERANCE:
        return [[q.x * 25.4 / 96, -q.y * 25.4 / 96]]
    if depth >= 16:
        raise CamError("SVG-Kurve zu komplex; bitte vereinfachen.")
    mid = (a+b)/2
    return _flatten(segment, a, mid, depth+1) + _flatten(segment, mid, b, depth+1)


def svg_contours(data):
    if b"<!doctype" in data.lower() or b"<!entity" in data.lower():
        raise CamError("SVG mit DTD/Entities wird nicht unterstützt.")
    root = ET.fromstring(data)
    if root.tag.split('}')[-1] != 'svg':
        raise CamError("Die Datei enthält kein SVG-Dokument.")
    for el in root.iter():
        tag = el.tag.split('}')[-1]
        if tag in {'text', 'image', 'clipPath', 'mask', 'script', 'foreignObject'}:
            raise CamError(f"SVG-Element {tag} nicht unterstützt. Bitte in einfache Pfade umwandeln.")
        for key, value in el.attrib.items():
            if key.split('}')[-1] == 'href' and not value.startswith('#'):
                raise CamError("SVG-Verweise müssen innerhalb der Datei liegen.")
    svg = SVG.parse(io.BytesIO(data), reify=True, ppi=96)
    contours = []
    corners = []
    for element in svg.elements():
        if not isinstance(element, Shape):
            continue
        if element.values.get('visibility') == 'hidden' or element.values.get('display') == 'none':
            continue
        path = Path(element)
        path.reify()
        current = []
        segments = []
        for segment in path:
            if isinstance(segment, Move):
                if len(current) > 1:
                    contours.append(clean(current))
                    corners.append(svg_corners(segments))
                current = [[segment.end.x * 25.4 / 96, -segment.end.y * 25.4 / 96]]
                segments = []
            else:
                if not current:
                    current = [[segment.start.x * 25.4 / 96, -segment.start.y * 25.4 / 96]]
                current.extend(_flatten(segment))
                segments.append(segment)
                if len(current) > MAX_POINTS:
                    raise CamError("SVG enthält zu viele Punkte; bitte vereinfachen.")
        if len(current) > 1:
            contours.append(clean(current))
            corners.append(svg_corners(segments))
    return contours, ['SVG: 96 dpi, physische Maße und viewBox berücksichtigt; Y nach oben gespiegelt.'], corners


def _join(paths):
    """Lose DXF-Linien an eindeutigen Endpunkten verbinden, keine Lücken schließen."""
    result = []
    while paths:
        chain = paths.pop(0)
        if chain[0] == chain[-1]:
            result.append(chain)
            continue
        while True:
            matches = [(i, rev) for i, p in enumerate(paths) if p[0] != p[-1]
                       for rev in (False, True)
                       if math.dist(chain[-1], p[-1] if rev else p[0]) < 1e-5]
            if len(matches) > 1:
                raise CamError("DXF hat verzweigte Konturen; bitte eindeutige Polylinien erstellen.")
            if not matches:
                break
            i, rev = matches[0]
            nxt = paths.pop(i)
            chain.extend((list(reversed(nxt)) if rev else nxt)[1:])
            if math.dist(chain[0], chain[-1]) < 1e-5:
                chain[-1] = chain[0][:]
                break
        result.append(clean(chain))
    # Falls die erste Linie mitten in einer offenen Kette lag, erneut an deren Anfang ansetzen.
    if len(result) < 2:
        return result
    for i, a in enumerate(result):
        if a[0] == a[-1]:
            continue
        for j in range(i+1, len(result)):
            b = result[j]
            if b[0] == b[-1]:
                continue
            for ra in (False, True):
                for rb in (False, True):
                    aa = list(reversed(a)) if ra else a
                    bb = list(reversed(b)) if rb else b
                    if math.dist(aa[-1], bb[0]) < 1e-5:
                        return _join([aa+bb[1:]] + [p for k,p in enumerate(result) if k not in (i,j)])
    return result


def dxf_contours(data, unit_scale):
    # DXF-Header nennt die Textkodierung; surrogateescape erhält alte Codepages für Geometrie.
    text = data.decode('utf-8-sig', errors='surrogateescape')
    doc = ezdxf.read(io.StringIO(text))
    factor = units.conversion_factor(doc.units, units.MM) if doc.units else unit_scale
    paths = []
    supported = {'LINE', 'ARC', 'CIRCLE', 'ELLIPSE', 'SPLINE', 'LWPOLYLINE', 'POLYLINE'}
    ignored = set()
    for entity in doc.modelspace():
        if entity.dxftype() not in supported:
            ignored.add(entity.dxftype())
            continue
        pts = list(make_path(entity).flattening(distance=TOLERANCE/factor))
        if any(abs(p.z*factor) > 1e-5 for p in pts):
            raise CamError("DXF muss ein ebenes Profil in der XY-Ebene (Z=0) enthalten.")
        paths.append(clean([[p.x*factor, p.y*factor] for p in pts]))
    if ignored:
        raise CamError("Nicht unterstützte DXF-Objekte: " + ', '.join(sorted(ignored)) + ". Bitte in Linien/Polylinien umwandeln.")
    return _join(paths), [f'DXF: Faktor {factor:g} mm/Einheit; ' + ('Dateieinheit aus Header.' if doc.units else 'einheitenlose Datei, Eingabefaktor verwendet.')]


def import_profile(filename, data, unit_scale=1.):
    extension = filename.lower().rsplit('.', 1)[-1]
    try:
        if extension == 'svg':
            contours, notes, corners = svg_contours(data)
        elif extension == 'dxf':
            contours, notes = dxf_contours(data, unit_scale)
            corners = None
        else:
            raise CamError("Bitte eine SVG- oder DXF-Datei wählen.")
        if not contours or len(contours) > 100 or sum(map(len, contours)) > MAX_POINTS:
            raise CamError("Keine nutzbaren Konturen oder mehr als 100 Konturen / 20000 Punkte.")
        result = {'contours': contours, 'notes': notes}
        if corners is not None:
            result['corners'] = corners
        return result
    except CamError:
        raise
    except Exception as exc:
        raise CamError("Vektordatei konnte nicht gelesen werden. Format und Geometrie prüfen.") from exc
