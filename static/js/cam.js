"use strict";
const navigation = [...document.querySelectorAll('.sidebar .nav-link')].map(link => ({
    link, section: document.querySelector(link.getAttribute('href'))
}));
function activateSection(active) {
    for (const {link, section} of navigation) {
        const selected = section === active;
        link.classList.toggle('active', selected);
        if (selected) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
    }
}
function updateNavigation() {
    let active = navigation[0].section;
    for (const {section} of navigation) {
        if (section.getBoundingClientRect().top <= 120) active = section;
    }
    // Auch der kurze Exportbereich muss am Seitenende aktiv werden können.
    if (window.scrollY > 0 && window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
        active = navigation.at(-1).section;
    }
    activateSection(active);
}
for (const {link, section} of navigation) {
    link.addEventListener('click', () => activateSection(section));
}
window.addEventListener('scroll', updateNavigation, {passive: true});
window.addEventListener('resize', updateNavigation);
window.addEventListener('load', updateNavigation);
window.addEventListener('hashchange', () => {
    const target = navigation.find(({link}) => link.hash === window.location.hash);
    if (target) activateSection(target.section);
    else updateNavigation();
});
updateNavigation();

const form = document.querySelector('#job-form');
const statusText = document.querySelector('#status');
const canvas = document.querySelector('#preview');
const ctx = canvas.getContext('2d');
const progress = document.querySelector('#progress');
const download = document.querySelector('#download');
const play = document.querySelector('#play');
const profiles = {xy: null, uv: null};
const filenames = {xy: '', uv: ''};
const sameProfile = document.querySelector('#same-profile');
let separateUVContour = '0';
const generations = {xy: 0, uv: 0};
let result = null, revision = 0, playing = false, lastFrame = null, animationFrame = null;
let liveTimer = null, liveAbort = null, dragging = null;
let placementState = 'idle', placementMessage = '';

function planningData() {
    const uvProfile = sameProfile.checked ? profiles.xy : profiles.uv;
    if (!profiles.xy || !uvProfile) return null;
    const data = {xy: profiles.xy, uv: uvProfile};
    for (const input of form.elements) {
        if (!input.name || input.disabled) continue;
        if (input.name.startsWith('machine_zero_') && input.value === '') continue;
        data[input.name] = input.type === 'checkbox' ? input.checked : input.type === 'number' ? (input.value === '' ? null : Number(input.value)) : input.value;
    }
    if (sameProfile.checked) data.uv_contour = form.elements.xy_contour.value;
    return data;
}
function showResult(dataResult) {
    result = dataResult;
    progress.max = result.program?.moves.length || 1; progress.value = 0;
    progress.disabled = play.disabled = !result.program;
    download.disabled = !result.gcode;
    document.querySelector('#code').textContent = result.gcode || result.approach_error || 'Vorschau berechnet. Zum Export S-Maximalwert und geprüftes Steuerungsprofil ergänzen.';
    document.querySelector('#warnings').replaceChildren(...result.warnings.map(warning => {
        const li = document.createElement('li'); li.textContent = warning; return li;
    }));
    placementState = result.approach_error ? 'invalid' : 'valid';
    placementMessage = result.approach_error || 'Geometrisch geprüft: Profile, Abbrand, Zugang, Kaltanfahrt und Achswege passen.';
    statusText.textContent = `${result.segments} gemeinsame Kontursegmente berechnet. ${result.gcode ? 'Export verfügbar.' : 'Vorschau verfügbar.'}`;
    draw();
}
function scheduleLivePlan() {
    clearTimeout(liveTimer);
    if (!planningData()) return;
    placementState = 'pending'; placementMessage = 'Geometrieprüfung läuft …';
    draw();
    liveTimer = setTimeout(async () => {
        const current = revision, data = planningData();
        // Fehlende Schnitt-/Maschinenparameter dürfen nicht als gültige Platzierung erscheinen.
        if (!data) return;
        const controller = new AbortController(); liveAbort = controller;
        try {
            const response = await responseJSON(await fetch('/api/plan', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data), signal:controller.signal}));
            if (current === revision) showResult(response);
        } catch (error) {
            if (current !== revision || error.name === 'AbortError') return;
            placementState = 'invalid'; placementMessage = error.message; statusText.textContent=error.message; draw();
        } finally { if (liveAbort === controller) liveAbort = null; }
    }, 250);
}

function invalidate() {
    clearTimeout(liveTimer); liveAbort?.abort();
    revision++;
    placementState = 'idle'; placementMessage = '';
    result = null;
    stopPlayback();
    download.disabled = play.disabled = progress.disabled = true;
    play.textContent = 'Abspielen';
    document.querySelector('#code').textContent = 'Geänderte Eingaben werden automatisch geprüft. Noch kein aktueller Export.';
    document.querySelector('#warnings').replaceChildren();
    document.querySelector('#coordinates').textContent = '';
    document.querySelector('#program-state').textContent = 'Noch kein aktuelles geprüftes Bewegungsprogramm.';
    for(const key of ['heater','command','phase']) delete document.querySelector('#program-state').dataset[key];
    document.querySelector('#step-label').textContent = 'Kein aktueller Schneidweg';
    statusText.textContent = 'Eingaben geändert. Schneidweg wird automatisch neu geprüft.';
    draw();
    scheduleLivePlan();
}
async function responseJSON(response) {
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Anfrage fehlgeschlagen.');
    return data;
}
function setProfile(name, data, filename) {
    profiles[name] = data;
    filenames[name] = filename;
    renderProfile(name, data, filename);
    if (name === 'xy' && sameProfile.checked) updateSharedProfile();
    coupleCenters(name);
    draw();
}
function renderProfile(name, data, filename) {
    const select = document.querySelector(`#contour-${name}`);
    select.replaceChildren();
    select.disabled = !data;
    document.querySelector(`#info-${name}`).textContent = filename;
    if (!data) return;
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
function updateSharedProfile() {
    const shared = sameProfile.checked;
    document.querySelector('#file-uv').disabled = shared;
    document.querySelector('#unit-uv').disabled = shared;
    renderProfile('uv', shared ? profiles.xy : profiles.uv,
        shared ? (profiles.xy ? `${filenames.xy} (von XY übernommen)` : 'Zuerst das XY-Profil laden.')
            : (filenames.uv || 'Noch keine Datei geladen.'));
    const select = document.querySelector('#contour-uv');
    if (shared) {
        select.value = document.querySelector('#contour-xy').value;
        select.disabled = true;
    } else if (profiles.uv) select.value = separateUVContour;
    coupleCenters('xy');
    draw();
}
sameProfile.addEventListener('change', () => {
    if (sameProfile.checked) separateUVContour = document.querySelector('#contour-uv').value || '0';
    invalidate();
    updateSharedProfile();
});
document.querySelector('#contour-xy').addEventListener('change', () => {
    if (sameProfile.checked) updateSharedProfile();
});
function profileSize(name) {
    const profile = name === 'uv' && sameProfile.checked ? profiles.xy : profiles[name];
    const scale = Number(form.elements[name+'_scale'].value);
    if (!profile || !Number.isFinite(scale) || scale <= 0) return null;
    const points = profile.contours.flat(), xs = points.map(p=>p[0]), ys = points.map(p=>p[1]);
    return [(Math.max(...xs)-Math.min(...xs))*scale, (Math.max(...ys)-Math.min(...ys))*scale];
}
function coupleCenters(source) {
    const target = source === 'xy' ? 'uv' : 'xy';
    const a = profileSize(source), b = profileSize(target);
    if (!a || !b) return;
    for (const [i,axis] of ['x','y'].entries()) {
        const input = form.elements[source+'_'+axis];
        if (input.value === '' || !Number.isFinite(Number(input.value))) continue;
        form.elements[target+'_'+axis].value = Number(input.value)+(a[i]-b[i])/2;
    }
}
function centerProfile(name) {
    const profile = name === 'uv' && sameProfile.checked ? profiles.xy : profiles[name];
    if (!profile) {statusText.textContent='Zuerst eine Profildatei einfügen.'; return;}
    const height = Number(form.elements.block_height.value);
    const scale = Number(form.elements[name+'_scale'].value);
    if (!form.elements.block_height.value || !Number.isFinite(height) || height <= 0 || !Number.isFinite(scale) || scale <= 0) {
        statusText.textContent='Zum Zentrieren gültige Blockhöhe und Skalierung eingeben.'; return;
    }
    const points = profile.contours.flat();
    const xs=points.map(p=>p[0]), ys=points.map(p=>p[1]);
    form.elements[name+'_x'].value=-(Math.max(...xs)-Math.min(...xs))*scale/2;
    form.elements[name+'_y'].value=(height-(Math.max(...ys)-Math.min(...ys))*scale)/2;
    coupleCenters(name);
    invalidate();
}
async function loadProfile(name, file) {
        if (name === 'uv' && sameProfile.checked) {
            statusText.textContent='UV verwendet gerade die XY-Datei. Für eine eigene UV-Datei „Dieses Profil für beide Seiten verwenden“ abwählen.'; return;
        }
        invalidate(); profiles[name] = null;
        filenames[name] = '';
        if (name === 'xy' && sameProfile.checked) updateSharedProfile();
        const generation = ++generations[name];
        const select = document.querySelector(`#contour-${name}`);
        select.disabled = true; select.replaceChildren();
        document.querySelector(`#info-${name}`).textContent = file ? 'Datei wird gelesen …' : 'Noch keine Datei geladen.';
        draw();
        if (!file) return;
        const payload = new FormData();
        payload.append('file', file);
        payload.append('unit_scale', document.querySelector(`#unit-${name}`).value);
        try {
            const data = await responseJSON(await fetch('/api/import', {method: 'POST', body: payload}));
            if (generation !== generations[name]) return;
            setProfile(name, data, file.name);
            centerProfile(name);
            if (name === 'xy' && sameProfile.checked) centerProfile('uv');
            if (name === 'uv' && sameProfile.checked) updateSharedProfile();
            statusText.textContent = `${name.toUpperCase()}-Profil geladen. Eingaben prüfen und Schneidweg berechnen.`;
        } catch (error) {
            if (generation !== generations[name]) return;
            document.querySelector(`#info-${name}`).textContent = 'Import fehlgeschlagen.';
            statusText.textContent = error.message;
        }
}
for (const name of ['xy', 'uv']) {
    document.querySelector(`#file-${name}`).addEventListener('change', event => loadProfile(name,event.target.files[0]));
}
document.querySelector('#insert-profile').addEventListener('click', () => {
    const name=document.querySelector('#insert-side').value;
    if(name==='uv' && sameProfile.checked) {
        statusText.textContent='Für eine eigene UV-Datei zuerst „Dieses Profil für beide Seiten verwenden“ abwählen.';return;
    }
    const input=document.querySelector(`#file-${name}`);
    input.value=''; input.click();
});
document.querySelector('#center-profile').addEventListener('click', () => centerProfile(document.querySelector('#insert-side').value));
canvas.addEventListener('dragover', event => {event.preventDefault();canvas.classList.add('drag-over');});
canvas.addEventListener('dragleave', () => canvas.classList.remove('drag-over'));
canvas.addEventListener('drop', event => {
    event.preventDefault();canvas.classList.remove('drag-over');
    const files=event.dataTransfer.files;
    if(files.length!==1) {statusText.textContent='Bitte genau eine SVG- oder DXF-Datei auf die Ansicht ziehen.';return;}
    loadProfile(document.querySelector('#insert-side').value,files[0]);
});
function updateBlockDistances() {
    const values = ['width','height','span','block_width','block_height','block_span'].map(key => Number(form.elements[key].value));
    const [width,height,span,bw,bh,bs] = values;
    const valid = values.every(v => Number.isFinite(v) && v > 0) && bw <= width && bh <= height && bs <= span;
    document.querySelector('#block-distances').textContent = valid
        ? `Abstand je Seite zwischen Block und Achsebene: ${((span-bs)/2).toFixed(3)} mm. Profilebenen ab linker Achsebene: XY ${((span-bs)/2).toFixed(3)} mm, UV ${((span+bs)/2).toFixed(3)} mm. Freiraum in X/U je Seite: ${((width-bw)/2).toFixed(3)} mm.`
        : 'Gültige Maschinen- und Blockmaße eingeben. Der Block muss vollständig in den Arbeitsraum passen.';
}
form.addEventListener('input', event => {
    if(event.target.closest('#vorschau')) return;
    const match = event.target.name?.match(/^(xy|uv)_(x|y|scale)$/);
    if (match) coupleCenters(match[1]);
    updateBlockDistances(); invalidate();
});
function updateAccess() {
    if (form.elements.mode.value === 'inner') form.elements.auto_access.checked = false;
    form.elements.auto_access.disabled = form.elements.mode.value === 'inner';
    document.querySelectorAll('#access-fields input').forEach(input => {
        input.disabled = !form.elements.access.checked;
        input.required = form.elements.access.checked;
    });
    document.querySelector('#s-max').required = form.elements.controller_confirmed.checked;
}
form.addEventListener('change', event => {
    if(event.target.closest('#vorschau')) return;
    if (event.target === form.elements.access && event.target.checked) form.elements.auto_access.checked = false;
    if (event.target === form.elements.auto_access && event.target.checked) form.elements.access.checked = false;
    updateAccess(); invalidate();
});
form.addEventListener('submit', async event => {
    event.preventDefault(); invalidate();
    clearTimeout(liveTimer);
    const uvProfile = sameProfile.checked ? profiles.xy : profiles.uv;
    if (!profiles.xy || !uvProfile) {statusText.textContent = sameProfile.checked ? 'Bitte ein gültiges XY-Profil laden.' : 'Bitte zwei gültige Profildateien laden.'; return;}
    const current = revision;
    const data = planningData();
    const calculate = document.querySelector('#calculate');
    calculate.disabled = true;
    statusText.textContent = 'Konturen, Abbrand und Schneidraum werden geprüft …';
    try {
        const dataResult = await responseJSON(await fetch('/api/plan', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)}));
        if (current !== revision) return;
        showResult(dataResult);
        statusText.textContent = `${result.segments} gemeinsame Kontursegmente berechnet. ${result.gcode ? 'Export verfügbar.' : 'Vorschau verfügbar.'}`;
        draw();
    } catch (error) {if (current === revision) {statusText.textContent = error.message; placementState='invalid'; placementMessage=error.message; draw();}}
    finally {calculate.disabled = false;}
});
function liveProfile(name, block) {
    const profile = name === 'uv' && sameProfile.checked ? profiles.xy : profiles[name];
    if (!profile || !block) return null;
    if(['_x','_y','_scale'].some(suffix=>form.elements[name+suffix].value==='')) return null;
    const scale = Number(form.elements[name+'_scale'].value);
    const x = Number(form.elements[name+'_x'].value), y = Number(form.elements[name+'_y'].value);
    if (![x,y,scale].every(Number.isFinite) || scale <= 0) return null;
    const points = profile.contours.flat();
    const minX = Math.min(...points.map(p=>p[0])), minY = Math.min(...points.map(p=>p[1]));
    return {name, z:name==='xy'?block.z0:block.z1,
        selected:Number(form.elements[name+'_contour'].value),
        contours:profile.contours.map(c=>c.map(p=>[(p[0]-minX)*scale+x,(p[1]-minY)*scale+y]))};
}
function draw() {
    const read = key => form.elements[key].value === '' ? NaN : Number(form.elements[key].value);
    const width=read('width'), height=read('height'), span=read('span');
    const validRoom=[width,height,span].every(v=>Number.isFinite(v)&&v>=.01&&v<=1e6);
    const room=validRoom?{width,height,span}:null;
    const bw=read('block_width'), bh=read('block_height'), bs=read('block_span');
    const validBlock=validRoom && [bw,bh,bs].every(Number.isFinite) && bw>=.01 && bh>=.01 && bs>=.001 && bw<=width && bh<=height && bs<=span;
    const block=validBlock?{width:bw,height:bh,span:bs,z0:(span-bs)/2,z1:(span+bs)/2}:null;
    const visibleProfiles=['xy','uv'].map(name=>liveProfile(name,block)).filter(Boolean);
    const machineZero=room ? ['x','u'].flatMap(axis=>[form.elements['machine_zero_'+axis].value===''?width/2:read('machine_zero_'+axis),0]) : null;
    const access={};
    if(form.elements.access.checked) for(const phase of ['entry','exit']) {
        const values=['x','y','u','v'].map(axis=>read(phase+'_'+axis));
        if(values.every(Number.isFinite)) access[phase]=values;
    }
    const step=Number(progress.value);
    const playback=result ? programPosition(result,step) : null;
    drawWorkspace(canvas,{room,block,profiles:visibleProfiles,result,step,machineZero,playback,
        view:document.querySelector('#view').value,
        showNominal:document.querySelector('#show-nominal').checked,
        access,accessEnabled:form.elements.access.checked,
        placementState, fixedTransform:dragging?.transform});
    const outside=block && visibleProfiles.some(p=>p.contours.some(c=>c.some(([x,y])=>x < -bw/2 || x > bw/2 || y < 0 || y > bh)));
    const summary=!room ? 'Maschinenmaße eingeben.' : !block ? 'Arbeitsraum sichtbar. Gültige Blockmaße eingeben.'
        : `Block ${bw} × ${bh} × ${bs} mm. Abstand links/rechts zu den Achsebenen jeweils ${block.z0} mm; X/U je Seite ${(width-bw)/2} mm; oben ${height-bh} mm. ${visibleProfiles.length} Profilseite(n) eingefügt. ${outside?'Achtung: Nennkontur liegt außerhalb des Blocks. ':''}${result?'Geprüfter Drahtweg mit Start und Ende sichtbar.':'Konturentwurf, noch kein geprüfter Drahtweg.'}`;
    const summaryElement=document.querySelector('#workspace-summary');
    const feedback = document.querySelector('#placement-feedback');
    feedback.dataset.state = outside ? 'invalid' : placementState;
    feedback.textContent = outside ? 'Position ungültig: Mindestens eine Profilkontur liegt außerhalb des Blocks.'
        : placementMessage || 'Profile in der XY- oder UV-Seitenansicht ziehen. Beide Zentren bewegen sich gemeinsam.';
    if(summaryElement.textContent!==summary) {
        summaryElement.textContent=summary;
        canvas.setAttribute('aria-label',summary);
    }
    if(!result) return;
    const state=document.querySelector('#program-state');
    if (!playback) {
        state.textContent = 'Nur geometrischer Entwurf: kein ausführbares Bewegungsprogramm. '+(result.approach_error || '');
        document.querySelector('#step-label').textContent='Keine Programmwiedergabe';
        return;
    }
    const phase={approach:'Kaltanfahrt',preheat:'Heizvorlauf · 10 mm vor Materialeintritt',entry:'Einfahrt',cut:'Konturschnitt',exit:'Ausfahrt',end:'Programmende'}[playback.phase];
    const heat=playback.heated?'Heizung EIN (M3)':playback.heaterOn?'M3 aktiv, Heizleistung 0':'Heizung AUS (M5)';
    const stateText=`${result.program.source==='export'?'Export rückgelesen und geprüft':'Vorschauvorlage geprüft · S-Zuordnung noch offen'} · ${phase} · ${playback.command} · ${heat}${playback.finished?'':` · Zeile ${playback.move.line} · ${playback.move.command==='G0'?'Eilgang schematisch':`F${playback.move.feed} mm/min`}`}`;
    if(state.textContent!==stateText)state.textContent=stateText;
    state.dataset.heater = playback.heated ? 'on' : 'off';
    state.dataset.command = playback.command;
    state.dataset.phase = playback.phase;
    document.querySelector('#step-label').textContent=`Schritt ${Math.floor(step)} / ${result.program.moves.length}`;
    document.querySelector('#coordinates').textContent='Planungsraum aktuell: '+playback.axes.map((v,i)=>`${'XYUV'[i]} ${v.toFixed(3)}`).join(' · ')+' mm. Maschinenkoordinaten aktuell: '+playback.machine.map((v,i)=>`${'XYUV'[i]} ${v.toFixed(3)}`).join(' · ')+' mm. Programmstart: Maschinennullpunkt X0 Y0 U0 V0. Schnittstart im Planungsraum: '+result.start.map(v=>v.toFixed(3)).join(' / ');
}
function canvasPoint(event) {
    const rect = canvas.getBoundingClientRect();
    return [(event.clientX-rect.left)*canvas.width/rect.width, (event.clientY-rect.top)*canvas.height/rect.height];
}
canvas.addEventListener('pointerdown', event => {
    if (event.button !== 0 || document.querySelector('#view').value === 'wire') return;
    const name = document.querySelector('#view').value, size = profileSize(name);
    const transform = canvas.workspaceTransform;
    if (!size || !transform) return;
    const [px,py] = canvasPoint(event), [x,y] = transform.unproject(px,py);
    const left = Number(form.elements[name+'_x'].value), bottom = Number(form.elements[name+'_y'].value);
    const tolerance = 10/transform.scale;
    if (x < left-tolerance || x > left+size[0]+tolerance || y < bottom-tolerance || y > bottom+size[1]+tolerance) return;
    if (dragging) return;
    dragging = {id:event.pointerId, name, start:[px,py], left, bottom, transform};
    canvas.focus({preventScroll:true});
    canvas.setPointerCapture(event.pointerId); canvas.classList.add('moving'); event.preventDefault();
});
canvas.addEventListener('pointermove', event => {
    if (!dragging || event.pointerId !== dragging.id) return;
    const [x,y] = canvasPoint(event), d = dragging;
    form.elements[d.name+'_x'].value = (d.left+(x-d.start[0])/d.transform.scale).toFixed(4);
    form.elements[d.name+'_y'].value = (d.bottom-(y-d.start[1])/d.transform.scale).toFixed(4);
    coupleCenters(d.name); invalidate();
});
function finishDrag(event) {
    if (!dragging || dragging.id !== event.pointerId) return;
    dragging = null; canvas.classList.remove('moving');
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    draw();
}
canvas.addEventListener('pointerup', finishDrag);
canvas.addEventListener('pointercancel', finishDrag);
canvas.addEventListener('lostpointercapture', finishDrag);
canvas.addEventListener('keydown', event => {
    const directions = {ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,1],ArrowDown:[0,-1]};
    const direction = directions[event.key], name = document.querySelector('#view').value;
    if (!direction || name === 'wire' || !profileSize(name)) return;
    event.preventDefault();
    for (const [i,axis] of ['x','y'].entries()) form.elements[name+'_'+axis].value = Number(form.elements[name+'_'+axis].value)+direction[i]*(event.shiftKey?10:1);
    coupleCenters(name); invalidate();
});
progress.addEventListener('input', () => {lastFrame=null;draw();});
document.querySelector('#view').addEventListener('change', draw);
document.querySelector('#show-nominal').addEventListener('change', draw);
play.addEventListener('click', () => {
    if (playing) {stopPlayback();return;}
    if (!result?.program) return;
    playing = true; play.textContent = 'Pause';
    if (Number(progress.value) >= Number(progress.max)) progress.value=0;
    lastFrame=null; animationFrame=requestAnimationFrame(animate);
});
function stopPlayback() {
    playing=false;lastFrame=null;
    if(animationFrame !== null) cancelAnimationFrame(animationFrame);
    animationFrame=null;play.textContent='Abspielen';
}
function animate(time) {
    if (!playing || !result?.program) return;
    if(lastFrame !== null) progress.value=advanceProgramCursor(result.program,Number(progress.value),(time-lastFrame)/1000,Number(document.querySelector('#playback-speed').value));
    lastFrame=time;draw();
    if(Number(progress.value) >= Number(progress.max)) {stopPlayback();return;}
    animationFrame=requestAnimationFrame(animate);
}
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopPlayback();});
download.addEventListener('click', () => {
    if (!result?.gcode) return;
    const url = URL.createObjectURL(new Blob([result.gcode], {type:'text/plain;charset=utf-8'}));
    const link = document.createElement('a'); link.href=url; link.download='hotwire-xyuv.nc'; link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
});
document.querySelector('#demo').addEventListener('click', () => {
    invalidate(); form.reset();
    separateUVContour = '0';
    for(const name of ['xy','uv']) {
        generations[name]++; document.querySelector(`#file-${name}`).value='';
        const size = name==='xy' ? 100 : 60;
        setProfile(name, {contours:[[[0,0],[size,0],[size,70],[0,70],[0,0]], [[20,20],[30,20],[30,30],[20,30],[20,20]]], notes:['Demogeometrie in mm; keine Maschinenvorgaben.']}, 'Demo: Rechteck mit Innenkontur');
    }
    const demo = {width:400,height:300,span:600,block_width:300,block_height:200,block_span:400,xy_x:-50,xy_y:60,uv_x:-30,uv_y:60,feed:100,power:30,burn_radius:.5};
    for(const [key,value] of Object.entries(demo)) form.elements[key].value=value;
    coupleCenters('xy');
    updateSharedProfile();
    updateAccess();
    updateBlockDistances();
    draw();
    scheduleLivePlan();
    statusText.textContent='Demobeispiel geladen. Alle Maße und Schnittparameter sind ausschließlich Beispieldaten. Schneidweg berechnen, um die Vorschau zu öffnen.';
});
updateBlockDistances();
updateAccess();
draw();
