"""Rückprüfung des tatsächlich formatierten Exports, insbesondere Ein-/Ausfahrt."""
import math
import unittest
from unittest.mock import patch

from app import app
from cam import plan, gcode, heating_approach
from nc_program import read_program, verify_program
from profiles import CamError
from tests.test_cam import job


class ProgramTests(unittest.TestCase):
    def setUp(self):
        self.result = plan(job(auto_access=True,controller_confirmed=True,s_max=2000))

    def verify(self, code):
        r = self.result
        return verify_program(code,r['approach'],r['path'],r['machine_zero'],100,600,True)

    def test_heater_switches_on_ten_mm_before_stock_in_emitted_code(self):
        r=self.result
        move=next(m for m in r['program']['moves'] if m['phase']=='preheat')
        self.assertEqual(move['command'],'G1')
        self.assertTrue(move['heater_on'])
        self.assertEqual(move['feed'],100)
        self.assertEqual(move['power_s'],600)
        for offset in (0,2):
            start=[move['from'][i]+r['machine_zero'][i] for i in (offset,offset+1)]
            end=[move['to'][i]+r['machine_zero'][i] for i in (offset,offset+1)]
            self.assertAlmostEqual(math.dist(start,end),10,delta=1e-5)
            self.assertAlmostEqual(abs(end[0]),r['block']['width']/2,delta=1e-5)
            self.assertAlmostEqual(abs(start[0]),r['block']['width']/2+10,delta=1e-5)
        self.assertEqual(r['approach'][-1],r['heating_start'])
        self.assertEqual(r['heat_lead'],[r['heating_start'],r['path'][0]])
        rows=r['gcode'].splitlines()
        self.assertTrue(rows[move['line']-2].startswith('M3 S'))
        self.assertTrue(rows[move['line']-3].startswith('G0 '))

    def test_top_entry_is_chosen_if_sides_lack_ten_mm_clearance(self):
        r=plan(job(auto_access=True,block_width=390,block_height=200,
                   xy_start=50,xy_end=50,uv_start=50,uv_end=50))
        self.assertIsNotNone(r['program'])
        self.assertEqual(r['start'][1],200)
        self.assertEqual(r['heating_start'][1],210)
        self.assertEqual(r['heating_start'][3],210)
        self.assertEqual(r['start'][0],r['heating_start'][0])

    def test_no_clearance_blocks_program_but_preserves_geometry(self):
        r=plan(job(auto_access=True,block_width=400,block_height=300,
                   controller_confirmed=True,s_max=2000))
        self.assertTrue(r['path'])
        self.assertIsNone(r['gcode'])
        self.assertIsNone(r['program'])
        self.assertIn('10 mm Heizvorlauf',r['approach_error'])

    def test_manual_access_maintains_minimum_ten_mm_air_gap(self):
        for entry in ([150,80,150,80],[158,80,158,80],[180,80,180,80]):
            with self.subTest(entry=entry):
                start,route=heating_approach([200,0,200,0],entry,300,200,400,300)
                self.assertEqual(route[-1],start)
                self.assertGreaterEqual(min(start[0],start[2])-150,10)
                self.assertEqual(start[1::2],entry[1::2])
                if entry[0] == 180:self.assertEqual(start,entry)

    def test_omitted_hot_air_segment_is_rejected_by_roundtrip_check(self):
        move=next(m for m in self.result['program']['moves'] if m['phase']=='preheat')
        with self.assertRaises(CamError):
            self.verify(self.result['gcode'].replace(move['text']+'\n','',1))

    def test_hot_entry_and_exit_are_g1_with_feed_and_heating(self):
        program = self.result['program']
        self.assertEqual(program['source'],'export')
        self.assertTrue(program['checked'])
        for phase in ('entry','exit'):
            move = next(m for m in program['moves'] if m['phase'] == phase)
            self.assertEqual(move['command'],'G1')
            self.assertTrue(move['heater_on'])
            self.assertEqual(move['power_s'],600)
            self.assertEqual(move['feed'],100)
            self.assertGreater(move['length'],1)
            self.assertAlmostEqual(move['duration_seconds'],math.dist(move['from'],move['to'])/100*60)
            self.assertEqual(move['text'],self.result['gcode'].splitlines()[move['line']-1])
        self.assertFalse(program['end_heater_on'])
        self.assertTrue(all(not m['heater_on'] for m in program['moves'] if m['command'] == 'G0'))

    def test_no_position_jump_between_rapid_entry_contour_and_exit(self):
        moves = self.result['program']['moves']
        self.assertEqual(moves[0]['from'],[0,0,0,0])
        for previous,current in zip(moves,moves[1:]):
            self.assertEqual(previous['to'],current['from'])
        expected = self.result['machine_path']
        cut = [m for m in moves if m['command'] == 'G1' and m['phase'] != 'preheat']
        for parsed,point in zip([cut[0]['from']]+[m['to'] for m in cut],expected):
            for a,b in zip(parsed,point):
                self.assertAlmostEqual(a,b,delta=5.01e-6)

    def test_cooling_or_rapid_in_entry_or_exit_is_rejected(self):
        for phase in ('entry','exit'):
            move = next(m for m in self.result['program']['moves'] if m['phase'] == phase)
            for replacement in ('M5\n'+move['text'],move['text'].replace('G1 ','G0 ',1)):
                with self.subTest(phase=phase,replacement=replacement),self.assertRaises(CamError):
                    self.verify(self.result['gcode'].replace(move['text'],replacement,1))

    def test_exported_motion_feed_and_power_are_verified(self):
        code = self.result['gcode']
        entry = next(m for m in self.result['program']['moves'] if m['phase'] == 'entry')
        altered_target = entry['text'].split()
        altered_target[1] = 'X999'
        for mutated in (code.replace(entry['text'],' '.join(altered_target),1),
                        code.replace('F100.00000','F200.00000',1),
                        code.replace('M3 S600.00000','M3 S601.00000'),
                        code.replace(entry['text']+'\n','',1),
                        code.replace('M5\nM2','M2')):
            with self.subTest(mutated=mutated),self.assertRaises(CamError):
                self.verify(mutated)

    def test_unknown_modes_and_invalid_words_are_rejected(self):
        for old,new in (('G90','G91'),('G21','G20'),('M3 S600.00000','M3'),
                        ('M3 S600.00000','M3 Snan'),('M3 S600.00000','M3 S600 S600'),
                        ('M2','M2\nG0 X0 Y0 U0 V0')):
            with self.subTest(new=new),self.assertRaises(CamError):
                read_program(self.result['gcode'].replace(old,new))

    def test_preview_uses_same_postprocessor_without_invented_s_value(self):
        result = plan(job(auto_access=True))
        self.assertIsNone(result['gcode'])
        self.assertEqual(result['program']['source'],'preview')
        export_moves = self.result['program']['moves']
        for preview,export in zip(result['program']['moves'],export_moves):
            for key in ('from','to','command','feed','heater_on','duration_seconds'):
                self.assertEqual(preview[key],export[key])
            self.assertIsNone(preview['power_s'])

    def test_zero_power_is_retained_as_commanded_not_assumed_hot(self):
        result = plan(job(auto_access=True,controller_confirmed=True,s_max=2000,power=0))
        self.assertTrue(all(m['power_s'] == 0 for m in result['program']['moves'] if m['heater_on']))
        self.assertEqual(result['program']['power_percent'],0)

    def test_corrupted_postprocessor_output_cannot_be_exported_by_api(self):
        def broken(*args,**kwargs):
            return gcode(*args,**kwargs).replace('M3 S600.00000','M5')
        with patch('cam.gcode',side_effect=broken):
            response=app.test_client().post('/api/plan',json=job(auto_access=True,controller_confirmed=True,s_max=2000))
        self.assertEqual(response.status_code,400)
        self.assertIn('G-Code-Prüfung',response.get_json()['error'])


if __name__ == '__main__':
    unittest.main()
