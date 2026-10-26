"use strict";
const form = document.querySelector('#job-form');
const statusText = document.querySelector('#status');
const canvas = document.querySelector('#preview');
const ctx = canvas.getContext('2d');
const progress = document.querySelector('#progress');
const download = document.querySelector('#download');
const play = document.querySelector('#play');
const profiles = {xy: null, uv: null};
const generations = {xy: 0, uv: 0};
let result = null, revision = 0, playing = false, lastFrame = 0;

function invalidate() {
    revision++;
    result = null;
    playing = false;
    download.disabled = play.disabled = progress.disabled = true;
    play.textContent = 'Abspielen';
    document.querySelector('#code').textContent = 'Nach Änderungen den Schneidweg erneut berechnen.';
    document.querySelector('#warnings').replaceChildren();
    document.querySelector('#coordinates').textContent = '';
    document.querySelector('#step-label').textContent = 'Kein aktueller Schneidweg';
    statusText.textContent = 'Eingaben geändert. Schneidweg neu berechnen.';
    draw();
}
async function responseJSON(response) {
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Anfrage fehlgeschlagen.');
    return data;
}
function setProfile(name, data, filename) {
    profiles[name] = data;
    const select = document.querySelector(`#contour-${name}`);
    select.replaceChildren();
    data.contours.forEach((points, i) => {
        const first = points[0], last = points.at(-1);
        const closed = first[0] === last[0] && first[1] === last[1];
        const xs = points.map(p => p[0]), ys = points.map(p => p[1]);
        const option = document.createElement('option');
        option.value = i;
        option.textContent = `${i+1}: ${closed ? 'geschlossen' : 'offen'} · ${(Math.max(...xs)-Math.min(...xs)).toFixed(2)} × ${(Math.max(...ys)-Math.min(...ys)).toFixed(2)} mm`;
        select.append(option);
    });
    select.disabled = false;
    document.querySelector(`#info-${name}`).textContent = `${filename} · ${data.contours.length} Kontur(en). ${data.notes.join(' ')}`;
}
for (const name of ['xy', 'uv']) {
    document.querySelector(`#file-${name}`).addEventListener('change', async event => {
        invalidate(); profiles[name] = null;
        const generation = ++generations[name];
        const select = document.querySelector(`#contour-${name}`);
        select.disabled = true; select.replaceChildren();
        const file = event.target.files[0];
        document.querySelector(`#info-${name}`).textContent = file ? 'Datei wird gelesen …' : 'Noch keine Datei geladen.';
        if (!file) return;
        const payload = new FormData();
        payload.append('file', file);
        payload.append('unit_scale', document.querySelector(`#unit-${name}`).value);
        try {
            const data = await responseJSON(await fetch('/api/import', {method: 'POST', body: payload}));
            if (generation !== generations[name]) return;
            setProfile(name, data, file.name);
            statusText.textContent = `${name.toUpperCase()}-Profil geladen. Eingaben prüfen und Schneidweg berechnen.`;
        } catch (error) {
            if (generation !== generations[name]) return;
            document.querySelector(`#info-${name}`).textContent = 'Import fehlgeschlagen.';
            statusText.textContent = error.message;
        }
    });
}
form.addEventListener('input', invalidate);
function updateAccess() {
    document.querySelectorAll('#access-fields input').forEach(input => {
        input.disabled = !form.elements.access.checked;
        input.required = form.elements.access.checked;
    });
    document.querySelector('#s-max').required = form.elements.controller_confirmed.checked;
}
form.addEventListener('change', updateAccess);
form.addEventListener('submit', async event => {
    event.preventDefault(); invalidate();
    if (!profiles.xy || !profiles.uv) {statusText.textContent = 'Bitte zwei gültige Profildateien laden.'; return;}
    const current = revision;
    const data = {xy: profiles.xy, uv: profiles.uv};
    for (const input of form.elements) {
        if (!input.name || input.disabled) continue;
        data[input.name] = input.type === 'checkbox' ? input.checked : input.type === 'number' ? (input.value === '' ? null : Number(input.value)) : input.value;
    }
    const calculate = document.querySelector('#calculate');
    calculate.disabled = true;
    statusText.textContent = 'Konturen, Abbrand und Schneidraum werden geprüft …';
    try {
        const dataResult = await responseJSON(await fetch('/api/plan', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)}));
        if (current !== revision) return;
        result = dataResult;
        progress.max = result.path.length-1; progress.value = 0;
        progress.disabled = play.disabled = false;
        download.disabled = !result.gcode;
        document.querySelector('#code').textContent = result.gcode || 'Vorschau berechnet. Zum Export S-Maximalwert und geprüftes Steuerungsprofil ergänzen.';
        document.querySelector('#warnings').replaceChildren(...result.warnings.map(warning => {
            const li = document.createElement('li'); li.textContent = warning; return li;
        }));
        statusText.textContent = `${result.segments} gemeinsame Kontursegmente berechnet. ${result.gcode ? 'Export verfügbar.' : 'Vorschau verfügbar.'}`;
        draw();
    } catch (error) {if (current === revision) statusText.textContent = error.message;}
    finally {calculate.disabled = false;}
});
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#8fa1ad'; ctx.font = '16px Segoe UI';
    if (!result) {ctx.fillText('Zwei Profile laden und Schneidweg berechnen.', 30, 48); return;}
    const {width, height, span} = result.room;
    const view = document.querySelector('#view').value;
    const projection = (x,y,z) => view === 'wire' ? [x+z*.65, -y+z*.25] : [x,-y];
    const box = [[0,0],[width,0],[width,height],[0,height],[0,0]];
    const corners = [0,span].flatMap(z => box.map(([x,y]) => projection(x,y,z)));
    const xs = corners.map(p=>p[0]), ys = corners.map(p=>p[1]);
    const minX = Math.min(...xs), minY = Math.min(...ys);
    const scale = Math.min((canvas.width-70)/(Math.max(...xs)-minX), (canvas.height-70)/(Math.max(...ys)-minY));
    const project = (x,y,z) => {const p=projection(x,y,z); return [35+(p[0]-minX)*scale,35+(p[1]-minY)*scale];};
    function stroke(points, color, dashed=false, lineWidth=1) {
        ctx.beginPath(); ctx.strokeStyle=color; ctx.lineWidth=lineWidth; ctx.setLineDash(dashed ? [5,5] : []);
        points.forEach((p,i)=>i ? ctx.lineTo(...p) : ctx.moveTo(...p)); ctx.stroke(); ctx.setLineDash([]);
    }
    for (const z of view === 'wire' ? [0,span] : [0]) stroke(box.map(([x,y])=>project(x,y,z)), '#52636f');
    if (view === 'wire') {
        box.slice(0,4).forEach(([x,y])=>stroke([project(x,y,0),project(x,y,span)], '#283845'));
        const every = Math.max(1, Math.floor(result.path.length/45));
        result.path.forEach((p,i)=>{if(i%every===0) stroke([project(p[0],p[1],0),project(p[2],p[3],span)], '#354c56');});
    }
    for (const offset of view === 'xy' ? [0] : view === 'uv' ? [2] : [0,2]) {
        const z = offset ? span : 0;
        if (document.querySelector('#show-nominal').checked) stroke(result.nominal.map(p=>project(p[offset],p[offset+1],z)), '#8fa1ad', true);
        stroke(result.path.map(p=>project(p[offset],p[offset+1],z)), offset ? '#68c6ae' : '#f0a45d', false, 2);
    }
    const step = Number(progress.value), p = result.path[step];
    if (view === 'wire') stroke([project(p[0],p[1],0),project(p[2],p[3],span)], '#f1f6fa', false, 3);
    for(const offset of view === 'xy' ? [0] : view === 'uv' ? [2] : [0,2]) {
        ctx.beginPath(); ctx.fillStyle = '#ffffff'; ctx.arc(...project(p[offset],p[offset+1],offset ? span : 0),4,0,Math.PI*2);ctx.fill();
    }
    document.querySelector('#step-label').textContent = `Schritt ${step} / ${result.path.length-1}`;
    document.querySelector('#coordinates').textContent = 'Aktuell: '+p.map((v,i)=>`${'XYUV'[i]} ${v.toFixed(3)}`).join(' · ')+' mm. Start: '+result.start.map(v=>v.toFixed(3)).join(' / ')+' · Ende: '+result.end.map(v=>v.toFixed(3)).join(' / ');
}
progress.addEventListener('input', draw);
document.querySelector('#view').addEventListener('change', draw);
document.querySelector('#show-nominal').addEventListener('change', draw);
play.addEventListener('click', () => {
    playing = !playing; play.textContent = playing ? 'Pause' : 'Abspielen';
    if (playing) {
        if (Number(progress.value) >= Number(progress.max)) progress.value=0;
        lastFrame=0; requestAnimationFrame(animate);
    }
});
function animate(time) {
    if (!playing || !result) return;
    if (time-lastFrame > 35) {
        progress.value = Math.min(Number(progress.max), Number(progress.value)+1);
        draw(); lastFrame=time;
        if (Number(progress.value) >= Number(progress.max)) {playing=false;play.textContent='Abspielen';return;}
    }
    requestAnimationFrame(animate);
}
download.addEventListener('click', () => {
    if (!result?.gcode) return;
    const url = URL.createObjectURL(new Blob([result.gcode], {type:'text/plain;charset=utf-8'}));
    const link = document.createElement('a'); link.href=url; link.download='hotwire-xyuv.nc'; link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
});
document.querySelector('#demo').addEventListener('click', () => {
    invalidate(); form.reset();
    for(const name of ['xy','uv']) {
        generations[name]++; document.querySelector(`#file-${name}`).value='';
        const size = name==='xy' ? 100 : 60;
        setProfile(name, {contours:[[[0,0],[size,0],[size,70],[0,70],[0,0]], [[20,20],[30,20],[30,30],[20,30],[20,20]]], notes:['Demogeometrie in mm; keine Maschinenvorgaben.']}, 'Demo: Rechteck mit Innenkontur');
    }
    const demo = {width:400,height:300,span:600,z_xy:100,z_uv:500,xy_x:60,xy_y:60,uv_x:70,uv_y:60,feed:100,power:30,burn_radius:.5};
    for(const [key,value] of Object.entries(demo)) form.elements[key].value=value;
    updateAccess();
    statusText.textContent='Demobeispiel geladen. Alle Maße und Schnittparameter sind ausschließlich Beispieldaten. Schneidweg berechnen, um die Vorschau zu öffnen.';
});
draw();
