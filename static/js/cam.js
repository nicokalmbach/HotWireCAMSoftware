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
    filenames[name] = filename;
    renderProfile(name, data, filename);
    if (name === 'xy' && sameProfile.checked) updateSharedProfile();
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
    updateBlockDistances(); invalidate();
});
function updateAccess() {
    document.querySelectorAll('#access-fields input').forEach(input => {
        input.disabled = !form.elements.access.checked;
        input.required = form.elements.access.checked;
    });
    document.querySelector('#s-max').required = form.elements.controller_confirmed.checked;
}
form.addEventListener('change', event => {
    if(event.target.closest('#vorschau')) return;
    updateAccess(); invalidate();
});
form.addEventListener('submit', async event => {
    event.preventDefault(); invalidate();
    const uvProfile = sameProfile.checked ? profiles.xy : profiles.uv;
    if (!profiles.xy || !uvProfile) {statusText.textContent = sameProfile.checked ? 'Bitte ein gültiges XY-Profil laden.' : 'Bitte zwei gültige Profildateien laden.'; return;}
    const current = revision;
    const data = {xy: profiles.xy, uv: uvProfile};
    for (const input of form.elements) {
        if (!input.name || input.disabled) continue;
        data[input.name] = input.type === 'checkbox' ? input.checked : input.type === 'number' ? (input.value === '' ? null : Number(input.value)) : input.value;
    }
    if (sameProfile.checked) data.uv_contour = form.elements.xy_contour.value;
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
    const access={};
    if(form.elements.access.checked) for(const phase of ['entry','exit']) {
        const values=['x','y','u','v'].map(axis=>read(phase+'_'+axis));
        if(values.every(Number.isFinite)) access[phase]=values;
    }
    const step=Number(progress.value);
    drawWorkspace(canvas,{room,block,profiles:visibleProfiles,result,step,
        view:document.querySelector('#view').value,
        showNominal:document.querySelector('#show-nominal').checked,
        access,accessEnabled:form.elements.access.checked});
    const outside=block && visibleProfiles.some(p=>p.contours.some(c=>c.some(([x,y])=>x < -bw/2 || x > bw/2 || y < 0 || y > bh)));
    const summary=!room ? 'Maschinenmaße eingeben.' : !block ? 'Arbeitsraum sichtbar. Gültige Blockmaße eingeben.'
        : `Block ${bw} × ${bh} × ${bs} mm. Abstand links/rechts zu den Achsebenen jeweils ${block.z0} mm; X/U je Seite ${(width-bw)/2} mm; oben ${height-bh} mm. ${visibleProfiles.length} Profilseite(n) eingefügt. ${outside?'Achtung: Nennkontur liegt außerhalb des Blocks. ':''}${result?'Geprüfter Drahtweg mit Start und Ende sichtbar.':'Konturentwurf, noch kein geprüfter Drahtweg.'}`;
    const summaryElement=document.querySelector('#workspace-summary');
    if(summaryElement.textContent!==summary) {
        summaryElement.textContent=summary;
        canvas.setAttribute('aria-label',summary);
    }
    if(!result) return;
    const p=result.path[step];
    document.querySelector('#step-label').textContent=`Schritt ${step} / ${result.path.length-1}`;
    document.querySelector('#coordinates').textContent='Aktuell: '+p.map((v,i)=>`${'XYUV'[i]} ${v.toFixed(3)}`).join(' · ')+' mm. Start: '+result.start.map(v=>v.toFixed(3)).join(' / ')+' · Ende: '+result.end.map(v=>v.toFixed(3)).join(' / ');
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
    separateUVContour = '0';
    for(const name of ['xy','uv']) {
        generations[name]++; document.querySelector(`#file-${name}`).value='';
        const size = name==='xy' ? 100 : 60;
        setProfile(name, {contours:[[[0,0],[size,0],[size,70],[0,70],[0,0]], [[20,20],[30,20],[30,30],[20,30],[20,20]]], notes:['Demogeometrie in mm; keine Maschinenvorgaben.']}, 'Demo: Rechteck mit Innenkontur');
    }
    const demo = {width:400,height:300,span:600,block_width:300,block_height:200,block_span:400,xy_x:-50,xy_y:60,uv_x:-30,uv_y:60,feed:100,power:30,burn_radius:.5};
    for(const [key,value] of Object.entries(demo)) form.elements[key].value=value;
    updateSharedProfile();
    updateAccess();
    updateBlockDistances();
    draw();
    statusText.textContent='Demobeispiel geladen. Alle Maße und Schnittparameter sind ausschließlich Beispieldaten. Schneidweg berechnen, um die Vorschau zu öffnen.';
});
updateBlockDistances();
draw();
