"""Rücklesen und Prüfen ausschließlich des eigenen generischen XYUV-Exports.

Kein allgemeiner Maschineninterpreter: unbekannte Befehle werden abgewiesen.
Die angenommene Ausgangsposition ist der zuvor gesetzte Maschinennullpunkt.
"""
import math

from profiles import CamError


def read_program(code, allow_unmapped_power=False):
    position = [0., 0., 0., 0.]
    modes = set()
    heating = None
    power = None
    ended = False
    moves = []
    for line_number, original in enumerate(code.splitlines(), 1):
        words = original.split(';', 1)[0].strip().split()
        if not words:
            continue
        def fail(message):
            raise CamError(f'G-Code-Prüfung, Zeile {line_number}: {message}')
        if ended:
            fail('Befehl nach Programmende.')
        command = words[0]
        parameters = {}
        for word in words[1:]:
            key = word[0]
            if key in parameters:
                fail('Doppelter Parameter.')
            try:
                value = float(word[1:])
            except ValueError:
                fail('Ungültiger Zahlenwert.')
            if not math.isfinite(value):
                fail('Nicht endlicher Zahlenwert.')
            parameters[key] = value
        if command in ('G21', 'G90', 'G94'):
            if parameters:
                fail('Unerwarteter Parameter beim Koordinatenmodus.')
            modes.add(command)
        elif command == 'M5':
            if parameters:
                fail('Unerwarteter Parameter bei M5.')
            heating = False
        elif command == 'M3':
            if set(parameters) - {'S'} or ('S' not in parameters and not allow_unmapped_power):
                fail('M3 benötigt einen gültigen S-Wert.')
            power = parameters.get('S')
            if power is not None and power < 0:
                fail('Negativer S-Wert.')
            heating = True
        elif command in ('G0', 'G1'):
            if modes != {'G21', 'G90', 'G94'}:
                fail('G21/G90/G94 müssen vor der Bewegung gesetzt sein.')
            expected = set('XYUV') | ({'F'} if command == 'G1' else set())
            if set(parameters) != expected:
                fail('Vollständige XYUV-Position und bei G1 Vorschub F erforderlich.')
            if heating is None or (command == 'G0' and heating) or (command == 'G1' and not heating):
                fail('G0 muss nach M5, G1 bei aktivem M3 erfolgen.')
            target = [parameters[axis] for axis in 'XYUV']
            feed = parameters.get('F')
            if feed is not None and feed <= 0:
                fail('G1 benötigt einen positiven Vorschub.')
            distance = math.dist(position, target)
            moves.append({'from': position, 'to': target, 'command': command,
                          'heater_on': heating, 'power_s': power if heating else None,
                          'feed': feed, 'length': distance,
                          'duration_seconds': distance/feed*60 if feed else None,
                          'line': line_number, 'text': original.strip()})
            position = target
        elif command == 'M2':
            if parameters or heating is not False:
                fail('Programmende muss nach M5 erfolgen.')
            ended = True
        else:
            fail('Nicht unterstützter Befehl: ' + command)
    if not ended or not moves:
        raise CamError('G-Code-Prüfung: vollständiges Programm mit Bewegungen und M5/M2 erforderlich.')
    return {'moves': moves, 'start': [0., 0., 0., 0.], 'end': position,
            'end_heater_on': heating}


def verify_program(code, approach, path, machine_zero, feed, power_s, access_enabled,
                   allow_unmapped_power=False):
    """Text einschließlich Rundung und M-Zustand gegen die freigegebene Bahn prüfen."""
    program = read_program(code, allow_unmapped_power)
    has_preheat = approach[-1] != path[0]
    expected = ([('G0', p) for p in approach[1:]]
                + ([('G1',path[0])] if has_preheat else [])
                + [('G1', p) for p in path[1:]])
    if len(program['moves']) != len(expected):
        raise CamError('G-Code-Prüfung: Bewegungsanzahl stimmt nicht mit der Planung überein.')
    cut_index = -1 if has_preheat else 0
    for move, (command, world) in zip(program['moves'], expected):
        machine = [v-zero for v, zero in zip(world, machine_zero)]
        if move['command'] != command or any(abs(a-b) > 5.01e-6 for a,b in zip(move['to'], machine)):
            raise CamError('G-Code-Prüfung: ausgegebene Achsposition oder Bewegungsart weicht von der Planung ab.')
        if command == 'G1':
            if abs(move['feed']-feed) > 5.01e-6 or (
                    power_s is not None and abs(move['power_s']-power_s) > 5.01e-6):
                raise CamError('G-Code-Prüfung: ausgegebener Vorschub oder Heizleistung weicht von der Planung ab.')
            if cut_index == -1:
                move['phase'] = 'preheat'
            else:
                move['phase'] = ('entry' if cut_index == 0 else 'exit' if cut_index == len(path)-2 else 'cut') if access_enabled else 'cut'
            cut_index += 1
        else:
            move['phase'] = 'approach'
    # Erster heißer Satz beginnt lückenlos am erreichten Einschaltpunkt.
    first_cut = next(m for m in program['moves'] if m['command'] == 'G1')
    entry = [v-zero for v,zero in zip(approach[-1],machine_zero)]
    if any(abs(a-b) > 5.01e-6 for a,b in zip(first_cut['from'],entry)):
        raise CamError('G-Code-Prüfung: Heizvorlauf beginnt nicht am erreichten Einschaltpunkt.')
    program['checked'] = True
    program['source'] = 'preview' if allow_unmapped_power else 'export'
    return program
