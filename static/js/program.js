"use strict";

// Ausschließlich die rückgelesenen, geprüften G-Code-Sätze bewegen den Draht.
function programPosition(result, cursor) {
    const program = result.program;
    if (!program?.moves.length) return null;
    const count = program.moves.length;
    const value = Math.max(0, Math.min(count, cursor));
    const finished = value === count;
    const index = finished ? count-1 : Math.floor(value);
    const move = program.moves[index];
    const fraction = finished ? 1 : value-index;
    const machine = move.from.map((v,i)=>v+(move.to[i]-v)*fraction);
    const axes = machine.map((v,i)=>v+result.machine_zero[i]);
    const sectionAt = z => [0,1].map(i=>axes[i]+(axes[i+2]-axes[i])*z/result.room.span);
    const heaterOn = !finished && move.heater_on;
    const heated = heaterOn && (move.power_s === null ? program.power_percent > 0 : move.power_s > 0);
    return {machine,axes,sections:[...sectionAt(result.room.z_xy),...sectionAt(result.room.z_uv)],
        move,index,fraction,finished,heated,heaterOn,command:finished?'M5 / M2':move.command,
        phase:finished?'end':move.phase};
}

function advanceProgramCursor(program, cursor, elapsedSeconds, speed) {
    const count = program.moves.length;
    let value = Math.max(0,Math.min(count,cursor));
    let remaining = Math.max(0,elapsedSeconds);
    while(value < count) {
        const index = Math.floor(value), move = program.moves[index];
        // Eilganggeschwindigkeit ist unbekannt: 1 s je G0 nur als Anzeigezeit.
        const duration = move.length === 0 ? 0 : move.command === 'G0' ? 1 : move.duration_seconds/speed;
        if (duration === 0) {value=index+1;continue;}
        const needed = (1-(value-index))*duration;
        if (remaining < needed) return value+remaining/duration;
        remaining -= needed;
        value = index+1;
    }
    return value;
}
