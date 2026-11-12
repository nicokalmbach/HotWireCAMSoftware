import io
import math
from pathlib import Path
import unittest

import ezdxf

from app import app
from cam import plan, synchronize, check_room, prepared, corrected
from profiles import CamError, import_profile


def rectangle(w=100, h=70):
    return [[0, 0], [w, 0], [w, h], [0, h], [0, 0]]


def job(**changes):
    data = dict(xy={'contours': [rectangle()]}, uv={'contours': [rectangle(60)]},
                width=400, height=300, span=600, block_width=400, block_height=300, block_span=400,
                xy_x=60, xy_y=60, uv_x=70, uv_y=60, feed=100, power=30,
                burn_radius=.5, segments=40, mode='outer')
    data.update(changes)
    return data


class ImportTests(unittest.TestCase):
    def test_svg_circles_100_and_200_mm_plan_and_export(self):
        def circle(diameter, path=False):
            r = diameter/2
            shape = (f'<path d="M{diameter} {r} A{r} {r} 0 1 0 0 {r} '
                     f'A{r} {r} 0 1 0 {diameter} {r} Z"/>' if path else
                     f'<circle cx="{r}" cy="{r}" r="{r}"/>')
            return import_profile('circle.svg',
                (f'<svg xmlns="http://www.w3.org/2000/svg" width="{diameter}mm" '
                 f'height="{diameter}mm" viewBox="0 0 {diameter} {diameter}">'
                 f'{shape}</svg>').encode())
        xy, uv = circle(100), circle(200)
        self.assertNotEqual(len(xy['contours'][0]), len(uv['contours'][0]))
        self.assertEqual(xy['corners'], [[]])
        self.assertEqual(uv['corners'], [[]])
        for mode in ('center', 'outer', 'inner'):
            for partial in (False, True):
                with self.subTest(mode=mode, partial=partial):
                    result = plan(job(xy=xy, uv=circle(200, path=True),
                        xy_x=-50, uv_x=-100, xy_y=100, uv_y=50, segments=4,
                        mode=mode, burn_radius=.5, controller_confirmed=True, s_max=1000,
                        xy_start=75 if partial else 0, xy_end=25 if partial else 100,
                        uv_start=75 if partial else 0, uv_end=25 if partial else 100,
                        access=mode == 'inner', entry_x=0, entry_y=150, entry_u=0, entry_v=150,
                        exit_x=0, exit_y=150, exit_u=0, exit_v=150))
                    self.assertIn('G1 ', result['gcode'])
                    self.assertGreater(result['segments'], 40)
                    # Kreisform auch bei nur vier angeforderten Segmenten erhalten.
                    section_points = result['sections'][1:-1] if mode == 'inner' else result['sections']
                    radius_delta = {'center': 0, 'outer': .5, 'inner': -.5}[mode]
                    for p in section_points:
                        self.assertAlmostEqual(math.hypot(p[0], p[1]-150), 50+radius_delta, delta=.04)
                        self.assertAlmostEqual(math.hypot(p[2], p[3]-150), 100+radius_delta, delta=.04)

    def test_svg_curve_junctions_preserve_real_corners(self):
        def profile(size):
            return import_profile('arch.svg',
                (f'<svg width="{size}mm" height="{size}mm" viewBox="0 0 100 100">'
                 '<path d="M0 0 H100 V50 C100 100 0 100 0 50 Z"/></svg>').encode())
        xy, uv = profile(100), profile(200)
        self.assertEqual(len(xy['corners'][0]), 2)
        self.assertEqual(len(uv['corners'][0]), 2)
        for mode in ('center', 'outer'):
            with self.subTest(mode=mode):
                data = job(xy=xy, uv=uv, mode=mode, xy_x=-50, uv_x=-100,
                           xy_y=70, uv_y=40)
                result = plan(data)
                self.assertGreater(result['segments'], 40)
                # Echte Ecken trotz unterschiedlich abgetasteter Kurve gemeinsam erreichen.
                a, b = [corrected(prepared(data, name)[0], True, .5, mode)
                        for name in ('xy', 'uv')]
                for ca, cb in zip(a.corners, b.corners):
                    self.assertTrue(any(math.dist(p, ca+cb) < 1e-6 for p in result['sections']))

    def test_svg_real_corner_counts_still_rejected(self):
        xy = import_profile('rect.svg', b'<svg><path d="M0 0 H100 V100 H0 Z"/></svg>')
        uv = import_profile('triangle.svg', b'<svg><path d="M0 0 H100 L50 100 Z"/></svg>')
        with self.assertRaisesRegex(CamError, 'Eckzuordnung'):
            plan(job(xy=xy, uv=uv))

    def test_svg_open_curve_offsets(self):
        xy = import_profile('curve.svg', b'<svg><path d="M0 0 C0 100 100 100 100 0"/></svg>')
        uv = import_profile('curve.svg', b'<svg><path d="M0 0 C0 200 200 200 200 0"/></svg>')
        self.assertNotEqual(len(xy['contours'][0]), len(uv['contours'][0]))
        for mode in ('left', 'right'):
            with self.subTest(mode=mode):
                result = plan(job(xy=xy, uv=uv, mode=mode))
                self.assertNotEqual(result['start'], result['end'])

    def test_svg_units_viewbox_transform_and_hole(self):
        data = b'<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 200 100"><g transform="translate(10 0)"><path d="M0 0 H100 V80 H0 Z M20 20 H40 V40 H20 Z"/></g></svg>'
        result = import_profile('a.svg', data)
        self.assertEqual(len(result['contours']), 2)
        pts = result['contours'][0]
        self.assertAlmostEqual(max(p[0] for p in pts)-min(p[0] for p in pts), 50, delta=.0001)
        self.assertAlmostEqual(min(p[0] for p in pts), 5, delta=.0001)
        self.assertAlmostEqual(min(p[1] for p in pts), -40, delta=.0001)

    def test_curves_and_shapes(self):
        result = import_profile('a.svg', b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="10" cx="20" cy="20"/><path d="M0 0 C0 50 50 50 50 0"/></svg>')
        self.assertEqual(len(result['contours']), 2)
        self.assertGreater(len(result['contours'][0]), 20)
        self.assertEqual(result['contours'][0][0], result['contours'][0][-1])

    def test_example_profiles_and_round_holes(self):
        root = Path(__file__).resolve().parents[1] / 'examples'
        xy = import_profile('xy.svg', (root/'profil_xy.svg').read_bytes())
        uv = import_profile('uv.svg', (root/'profil_uv.svg').read_bytes())
        outer = plan(job(xy=xy, uv=uv))
        self.assertGreater(outer['segments'], 40)
        inner = plan(job(xy=xy,uv=uv,xy_contour=1,uv_contour=1,mode='inner',access=True,
                         entry_x=95,entry_y=95,entry_u=100,entry_v=95,
                         exit_x=95,exit_y=95,exit_u=100,exit_v=95))
        self.assertGreater(inner['segments'], 40)

    def test_unsupported_svg_rejected(self):
        for data in [b'<!DOCTYPE svg><svg/>', b'<svg><image href="http://example.com/a"/></svg>',
                     b'<svg><text>Test</text></svg>', b'<svg/>', b'not svg']:
            with self.subTest(data=data), self.assertRaises(CamError):
                import_profile('x.svg', data)

    def test_dxf_units_and_unordered_lines(self):
        doc = ezdxf.new()
        doc.units = 1  # inch
        points = rectangle(2, 1)
        for i in (2, 0, 3, 1):
            doc.modelspace().add_line(points[i], points[i+1])
        stream = io.StringIO()
        doc.write(stream)
        contours = import_profile('part.dxf', stream.getvalue().encode())['contours']
        self.assertEqual(len(contours), 1)
        self.assertEqual(contours[0][0], contours[0][-1])
        self.assertAlmostEqual(max(p[0] for p in contours[0]), 50.8)

    def test_unitless_dxf_and_bulge(self):
        doc = ezdxf.new()
        doc.units = 0
        doc.modelspace().add_lwpolyline([(0,0,1),(2,0,0)], format='xyb', close=True)
        stream = io.StringIO()
        doc.write(stream)
        contours = import_profile('x.dxf', stream.getvalue().encode(), 10)['contours']
        self.assertGreater(len(contours[0]), 6)
        self.assertAlmostEqual(max(p[0] for p in contours[0]), 20)

    def test_nonplanar_dxf_rejected(self):
        doc = ezdxf.new()
        doc.modelspace().add_line((0,0,1), (1,1,1))
        stream = io.StringIO()
        doc.write(stream)
        with self.assertRaisesRegex(CamError, 'XY-Ebene'):
            import_profile('x.dxf', stream.getvalue().encode())


class PlanTests(unittest.TestCase):
    def test_centered_machine_boundaries(self):
        check_room([[-200,0,200,300]], 400,300)
        for point in [[-200.01,0,0,0], [200.01,0,0,0],
                      [0,0,-200.01,0], [0,0,200.01,0], [0,-.01,0,0]]:
            with self.subTest(point=point), self.assertRaises(CamError):
                check_room([point], 400,300)

    def test_centered_block_distances_and_signed_coordinates(self):
        profile = {'contours': [rectangle(100,70)]}
        result = plan(job(xy=profile, uv=profile, xy_x=-50, uv_x=-50,
                          block_width=100, block_height=130, block_span=300,
                          burn_radius=0, controller_confirmed=True, s_max=1000))
        self.assertEqual(result['room']['z_xy'], 150)
        self.assertEqual(result['room']['z_uv'], 450)
        self.assertEqual(min(p[0] for p in result['path']), -50)
        self.assertEqual(max(p[0] for p in result['path']), 50)
        self.assertIn('X-50.00000', result['gcode'])
        changed = plan(job(xy=profile, uv=profile, xy_x=-50, uv_x=-50,
                           block_width=100, block_height=130, block_span=600,
                           burn_radius=0))
        self.assertEqual(changed['room']['z_xy'], 0)
        self.assertEqual(changed['room']['z_uv'], 600)

    def test_invalid_block_dimensions_and_profile_fit(self):
        for change in [dict(block_width=401), dict(block_height=301),
                       dict(block_span=601), dict(block_span=float('nan')),
                       dict(block_width=None), dict(block_height=-1),
                       dict(block_width=100), dict(block_height=100)]:
            with self.subTest(change=change), self.assertRaises(CamError):
                plan(job(**change))

    def test_legacy_distances_cannot_override_centering(self):
        result = plan(job(z_xy=0, z_uv=1))
        self.assertEqual(result['room']['z_xy'], 100)
        self.assertEqual(result['room']['z_uv'], 500)

    def test_conical_part_and_full_round(self):
        result = plan(job())
        self.assertEqual(len(result['path']), len(result['sections']))
        for a,b in zip(result['start'],result['end']):
            self.assertAlmostEqual(a,b)
        self.assertIsNone(result['gcode'])
        self.assertTrue(all(math.isfinite(v) for p in result['path'] for v in p))

    def test_corner_preservation_and_equal_sequences(self):
        a,b = synchronize(rectangle(19,7), rectangle(11,23), 4)
        self.assertEqual(len(a),len(b))
        for original in rectangle(19,7):
            self.assertTrue(any(math.dist(original,p)<1e-8 for p in a))
        for original in rectangle(11,23):
            self.assertTrue(any(math.dist(original,p)<1e-8 for p in b))
        for corner_a,corner_b in zip(rectangle(19,7), rectangle(11,23)):
            self.assertIn((corner_a,corner_b), list(zip(a,b)))

    def test_open_corners_with_different_lengths_and_collinear_points(self):
        a = [[0,0],[10,0],[90,0],[90,10]]
        b = [[0,0],[5,0],[5,80]]
        left,right = synchronize(a,b,40)
        index = left.index([90,0])
        self.assertEqual(right[index], [5,0])
        self.assertTrue(all(p[1] == q[1] == 0 for p,q in zip(left[:index],right[:index])))
        self.assertTrue(all(p[0] == 90 and q[0] == 5
                            for p,q in zip(left[index:],right[index:])))

    def test_different_corner_counts_rejected(self):
        with self.assertRaisesRegex(CamError, 'Eckzuordnung'):
            synchronize(rectangle(), [[0,0],[40,0],[20,30],[0,0]], 40)

    def test_compensated_corners_reached_in_same_gcode_block(self):
        result = plan(job(controller_confirmed=True,s_max=2000,segments=4))
        moves = [line for line in result['gcode'].splitlines() if line.startswith('G1 ')]
        # Beide Rechtecke beginnen nach dem Offset auf der unteren Kante.
        # Jede folgende Ecke muss auf beiden Seiten im selben Satz liegen.
        for corner in ([160.5,59.5,130.5,59.5], [160.5,130.5,130.5,130.5],
                       [59.5,130.5,69.5,130.5], [59.5,59.5,69.5,59.5]):
            index = next(i for i,p in enumerate(result['sections'])
                         if math.dist(p,corner) < 1e-8)
            axis_point = result['path'][index]
            self.assertTrue(all(f'{axis}{v:.5f}' in moves[index-1]
                                for axis,v in zip('XYUV',axis_point)))

    def test_postprocessing_changes_path_not_nominal(self):
        uncompensated = plan(job(burn_radius=0))
        compensated = plan(job(burn_radius=1))
        self.assertEqual(uncompensated['nominal'],compensated['nominal'])
        self.assertLess(min(p[0] for p in compensated['path']),min(p[0] for p in uncompensated['path']))

    def test_partial_contour_start_end(self):
        result = plan(job(burn_radius=0, xy_start=25,xy_end=50,uv_start=25,uv_end=50))
        self.assertNotEqual(result['start'], result['end'])

    def test_small_hole_collapses(self):
        profile = {'contours':[rectangle(1,1)]}
        with self.assertRaisesRegex(CamError, 'kollabieren'):
            plan(job(xy=profile,uv=profile,mode='inner',burn_radius=1,access=True,
                     entry_x=60,entry_y=60,entry_u=70,entry_v=60,
                     exit_x=60,exit_y=60,exit_u=70,exit_v=60))

    def test_hole_access_and_return(self):
        data = job(mode='inner', access=True,entry_x=80,entry_y=80,entry_u=90,entry_v=80,
                   exit_x=80,exit_y=80,exit_u=90,exit_v=80)
        result = plan(data)
        self.assertEqual(result['start'],result['end'])
        self.assertEqual(result['sections'][0],[80,80,90,80])
        with self.assertRaisesRegex(CamError, 'Innenkonturen'):
            plan(job(mode='inner'))

    def test_open_profile_left_offset(self):
        profile = {'contours':[[[0,0],[40,0],[40,20]]]}
        result = plan(job(xy=profile,uv=profile,mode='left'))
        self.assertNotEqual(result['start'],result['end'])
        with self.assertRaises(CamError):
            plan(job(xy=profile,uv=profile,mode='outer'))

    def test_out_of_room_projection_and_access(self):
        for changes in [dict(width=20),dict(xy_x=-201),dict(block_span=1),
                        dict(access=True,entry_x=-210,entry_y=0,entry_u=-210,entry_v=0,
                             exit_x=60,exit_y=60,exit_u=70,exit_v=60)]:
            with self.subTest(changes=changes), self.assertRaises(CamError):
                plan(job(**changes))

    def test_crossed_wire_surface(self):
        with self.assertRaisesRegex(CamError, 'kollabiert|überschneidet'):
            plan(job(uv_reverse=True,burn_radius=0))

    def test_different_start_positions_collapse(self):
        profile = {'contours': [rectangle(70,70)]}
        with self.assertRaisesRegex(CamError, 'kollabiert|überschneidet'):
            plan(job(xy=profile,uv=profile,uv_start=50,uv_end=50,burn_radius=0))

    def test_invalid_parameters_and_profiles(self):
        for changes in [dict(width=float('nan')),dict(feed=0),dict(power=101),
                        dict(block_span=0),dict(burn_radius=-1),dict(xy={'contours':[]}),
                        dict(xy={'contours':[[[0,0],[10,10],[0,10],[10,0],[0,0]]]})]:
            with self.subTest(changes=changes), self.assertRaises(CamError):
                plan(job(**changes))

    def test_generic_gcode_power_axes_and_shutdown(self):
        result = plan(job(controller_confirmed=True,s_max=2000))
        code = result['gcode']
        self.assertIn('M3 S600.00000', code)
        self.assertIn('G21\nG90\nG94\nM5', code)
        self.assertTrue(code.endswith('M5\nM2\n'))
        moves = [line for line in code.splitlines() if line.startswith('G1 ')]
        self.assertEqual(len(moves), len(result['path'])-1)
        for move in moves:
            self.assertEqual([word[0] for word in move.split()[1:]],list('XYUVF'))
        with self.assertRaises(CamError):
            plan(job(controller_confirmed=True))


class APITests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_page_and_assets(self):
        self.assertEqual(self.client.get('/').status_code,200)
        with self.client.get('/static/js/cam.js') as response:
            self.assertEqual(response.status_code,200)

    def test_upload_no_server_path(self):
        response = self.client.post('/api/import',data={'file':(io.BytesIO(b'<svg><rect width="10mm" height="5mm"/></svg>'),'../../part.svg')})
        self.assertEqual(response.status_code,200,response.get_json())
        self.assertEqual(len(response.get_json()['contours']),1)

    def test_plan_and_errors(self):
        self.assertEqual(self.client.post('/api/plan',json=job()).status_code,200)
        for payload in [[],{},dict(job(),xy={'contours':[[[0],[1,2]]]}),
                        dict(job(),xy={'contours':[[['abc',0],[1,2]]]})]:
            response = self.client.post('/api/plan',json=payload)
            self.assertEqual(response.status_code,400)
            self.assertIn('error',response.get_json())
        self.assertEqual(self.client.post('/api/import').status_code,400)
        self.assertEqual(self.client.post('/api/plan',data='{bad',content_type='application/json').status_code,400)

    def test_svg_circle_upload_to_plan(self):
        profiles = []
        for r in (50, 100):
            svg = f'<svg><circle r="{r}mm"/></svg>'.encode()
            response = self.client.post('/api/import', data={'file': (io.BytesIO(svg), 'circle.svg')})
            self.assertEqual(response.status_code, 200)
            profiles.append(response.get_json())
        response = self.client.post('/api/plan', json=job(xy=profiles[0], uv=profiles[1],
            xy_x=-50, uv_x=-100, xy_y=100, uv_y=50, controller_confirmed=True, s_max=1000))
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertIn('G1 ', response.get_json()['gcode'])

    def test_invalid_svg_corner_metadata(self):
        for corners in ({}, [None], [[[float('nan'), 0]]], [[[500, 500]]], [[[0]]]):
            with self.subTest(corners=corners):
                response = self.client.post('/api/plan', json=job(xy={'contours': [rectangle()], 'corners': corners}))
                self.assertEqual(response.status_code, 400)

    def test_request_limit(self):
        response = self.client.post('/api/import', data=b'x'*(4*1024*1024+1),content_type='multipart/form-data')
        self.assertEqual(response.status_code,413)


if __name__ == '__main__':
    unittest.main()
