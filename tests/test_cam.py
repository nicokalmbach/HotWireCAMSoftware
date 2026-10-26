import io
import math
from pathlib import Path
import unittest

import ezdxf

from app import app
from cam import plan, synchronize
from profiles import CamError, import_profile


def rectangle(w=100, h=70):
    return [[0, 0], [w, 0], [w, h], [0, h], [0, 0]]


def job(**changes):
    data = dict(xy={'contours': [rectangle()]}, uv={'contours': [rectangle(60)]},
                width=400, height=300, span=600, z_xy=100, z_uv=500,
                xy_x=60, xy_y=60, uv_x=70, uv_y=60, feed=100, power=30,
                burn_radius=.5, segments=40, mode='outer')
    data.update(changes)
    return data


class ImportTests(unittest.TestCase):
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
        for changes in [dict(width=20),dict(xy_x=-1),dict(z_xy=300,z_uv=301),
                        dict(access=True,entry_x=-10,entry_y=0,entry_u=-10,entry_v=0,
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
                        dict(z_uv=100),dict(burn_radius=-1),dict(xy={'contours':[]}),
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

    def test_request_limit(self):
        response = self.client.post('/api/import', data=b'x'*(4*1024*1024+1),content_type='multipart/form-data')
        self.assertEqual(response.status_code,413)


if __name__ == '__main__':
    unittest.main()
