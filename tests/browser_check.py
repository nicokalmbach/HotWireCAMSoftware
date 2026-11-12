"""Optionaler UI-Smoke-Test mit lokal installiertem Edge oder Chrome (ohne Zusatzpakete)."""
import pathlib
import subprocess
import tempfile
import threading

from werkzeug.serving import make_server

from app import app


HARNESS = '''<!doctype html><html><body><p id="result">RUNNING</p>
<iframe src="/" width="1280" height="900"></iframe><script>
const output = document.querySelector('#result');
const sleep = ms => new Promise(resolve => setTimeout(resolve,ms));
async function waitFor(check) {
    for(let i=0;i<150;i++) { if(check()) return; await sleep(40); }
    throw new Error('Zeitüberschreitung');
}
document.querySelector('iframe').onload = async function() {
    const d=this.contentDocument, w=this.contentWindow;
    const failures=[]; w.addEventListener('error',e=>failures.push(e.message));
    try {
        const form=d.querySelector('#job-form');
        let lastPlan;
        const captureFetch=w.fetch.bind(w);
        w.fetch=async(url,options)=>{
            const response=await captureFetch(url,options);
            if(url==='/api/plan' && response.ok) lastPlan=await response.clone().json();
            return response;
        };
        const diagram=d.querySelector('.machine-diagram');
        for(const name of ['width','height','span']) {
            const input=form.elements[name];
            if(!diagram.contains(input) || d.querySelectorAll('input[name="'+name+'"]').length!==1) throw new Error('Maßeingabe fehlt oder doppelt: '+name);
            if(input.value!=='' || !input.required) throw new Error('Maschinenmaß vorbelegt oder optional: '+name);
            input.focus();
            if(!input.closest('label').matches(':focus-within')) throw new Error('Maßeingabe nicht fokussierbar');
        }
        const canvas=d.querySelector('#preview'), context=canvas.getContext('2d');
        let drawnLabels=[];
        const fillText=context.fillText.bind(context);
        context.fillText=(text,...args)=>{drawnLabels.push(text);fillText(text,...args);};
        const change=(name,value)=>{
            drawnLabels=[]; form.elements[name].value=value;
            form.elements[name].dispatchEvent(new w.Event('input',{bubbles:true}));
        };
        for(const [key,value] of Object.entries({width:400,height:300,span:600,block_width:300,block_height:200,block_span:400})) change(key,value);
        if(!drawnLabels.includes('Rohteilnullpunkt') || !drawnLabels.some(text=>text.includes('Maschinennullpunkt'))) throw new Error('Getrennte Nullpunkte fehlen');
        if(!drawnLabels.includes('Block X/U 300 mm') || !drawnLabels.includes('XY-Abstand 100 mm') || !drawnLabels.includes('UV-Abstand 100 mm')) throw new Error('Blockmaße/Abstände nicht vor Import gezeichnet');
        if(!d.querySelector('#workspace-summary').textContent.includes('0 Profilseite(n)')) throw new Error('Arbeitsraum ohne Profil fehlt');
        const initialImage=canvas.toDataURL();
        change('block_span',300);
        if(!drawnLabels.includes('XY-Abstand 150 mm') || initialImage===canvas.toDataURL()) throw new Error('Live-Änderung des Blocks fehlt');
        change('block_span',400);
        const drop=new w.DataTransfer();
        drop.items.add(new w.File(['<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="70mm" viewBox="0 0 100 70"><rect width="100" height="70"/></svg>'],'direkt.svg',{type:'image/svg+xml'}));
        canvas.dispatchEvent(new w.DragEvent('drop',{bubbles:true,dataTransfer:drop}));
        await waitFor(()=>d.querySelector('#info-xy').textContent.includes('Kontur(en)'));
        if(Math.abs(Number(form.elements.xy_x.value)+50)>1e-3 || Math.abs(Number(form.elements.xy_y.value)-65)>1e-3) throw new Error('Import nicht im Block zentriert: '+form.elements.xy_x.value+' / '+form.elements.xy_y.value);
        if(!d.querySelector('#workspace-summary').textContent.includes('1 Profilseite(n)') || !d.querySelector('#play').disabled) throw new Error('Direktimport nicht als Entwurf sichtbar');
        const profileImage=canvas.toDataURL(); change('xy_x',-40);
        if(profileImage===canvas.toDataURL()) throw new Error('Profilposition nicht live sichtbar');
        change('xy_x',500);
        if(!d.querySelector('#workspace-summary').textContent.includes('außerhalb')) throw new Error('Kontur außerhalb des Blocks nicht markiert');
        d.querySelector('#center-profile').click();
        if(Math.abs(Number(form.elements.xy_x.value)+50)>1e-3) throw new Error('Zentrieren in Arbeitsraumansicht fehlt');
        this.style.width='360px';
        await sleep(60);
        if(d.documentElement.scrollWidth>d.documentElement.clientWidth) throw new Error('Seitenüberlauf bei mobiler Maßeingabe');
        const scroller=d.querySelector('.machine-diagram-scroll');
        if(scroller.scrollWidth<=scroller.clientWidth) throw new Error('Mobile Skizze nicht scrollbar');
        this.style.width='1280px';
        d.querySelector('#demo').click();
        if(form.elements.width.value!=='400' || form.elements.height.value!=='300' || form.elements.span.value!=='600') throw new Error('Demomaße in Skizze');
        if(form.elements.z_xy || form.elements.z_uv) throw new Error('Manuelle Profilebenen vorhanden');
        if(!d.querySelector('#block-distances').textContent.includes('100.000 mm')) throw new Error('Automatischer Abstand');
        form.requestSubmit();
        await waitFor(()=>!d.querySelector('#play').disabled);
        if(!drawnLabels.some(text=>text.includes('Start')) || !d.querySelector('#workspace-summary').textContent.includes('Geprüfter Drahtweg')) throw new Error('Schnittweg/Start nicht sichtbar');
        if(!drawnLabels.some(text=>text.includes('Kaltanfahrt'))) throw new Error('Automatische Anfahrt fehlt');
        if(d.querySelector('#placement-feedback').dataset.state!=='valid') throw new Error('Geometriefeedback fehlt');
        const program=lastPlan.program;
        if(!program?.checked || program.source!=='preview') throw new Error('Geprüfte Vorschauvorlage fehlt');
        const preheatIndex=program.moves.findIndex(move=>move.phase==='preheat');
        const preheat=program.moves[preheatIndex];
        if(preheatIndex<0 || preheat.command!=='G1' || !preheat.heater_on) throw new Error('Heizvorlauf vor Material fehlt');
        for(const offset of [0,2]) if(Math.abs(Math.hypot(preheat.to[offset]-preheat.from[offset],preheat.to[offset+1]-preheat.from[offset+1])-10)>1e-5) throw new Error('Heizvorlauf nicht 10 mm je Blockseite');
        d.querySelector('#progress').value=preheatIndex+.5;
        d.querySelector('#progress').dispatchEvent(new w.Event('input'));
        if(d.querySelector('#program-state').dataset.phase!=='preheat' || d.querySelector('#program-state').dataset.heater!=='on' || !d.querySelector('#program-state').textContent.includes('10 mm vor Materialeintritt')) throw new Error('Heizung vor Materialeintritt nicht sichtbar');
        for(const phase of ['entry','exit']) {
            const index=program.moves.findIndex(move=>move.phase===phase), move=program.moves[index];
            if(index<0 || !move.heater_on || move.command!=='G1') throw new Error('Kein heißer G1-Zugang: '+phase);
            const cursor=w.advanceProgramCursor(program,index,move.duration_seconds/2,1);
            if(Math.abs(cursor-index-.5)>1e-8) throw new Error('G1-Zugang wird nicht nach F durchfahren');
            const point=w.programPosition(lastPlan,cursor);
            if(point.machine.some((v,i)=>Math.abs(v-(move.from[i]+move.to[i])/2)>1e-7)) throw new Error('Zwischenposition im Zugang fehlt');
            d.querySelector('#progress').value=cursor;
            d.querySelector('#progress').dispatchEvent(new w.Event('input'));
            const state=d.querySelector('#program-state');
            if(state.dataset.heater!=='on' || state.dataset.command!=='G1' || state.dataset.phase!==phase) throw new Error('Heizung im Zugang nicht aus Programm übernommen');
        }
        const entryIndex=program.moves.findIndex(move=>move.phase==='entry');
        const realRAF=w.requestAnimationFrame, realCancel=w.cancelAnimationFrame;
        let frame;
        w.requestAnimationFrame=callback=>{frame=callback;return 1;};w.cancelAnimationFrame=()=>{};
        d.querySelector('#playback-speed').value='1';d.querySelector('#progress').value=entryIndex;
        d.querySelector('#play').click();frame(1000);frame(1500);
        const animated=Number(d.querySelector('#progress').value);
        if(animated<=entryIndex || animated>=entryIndex+1) throw new Error('Animation springt über Einfahrt');
        const expected=w.advanceProgramCursor(program,entryIndex,.5,1);
        if(Math.abs(animated-expected)>1e-7) throw new Error('Animation stimmt nicht mit G-Code-Vorschub überein');
        d.querySelector('#play').click();w.requestAnimationFrame=realRAF;w.cancelAnimationFrame=realCancel;
        d.querySelector('#playback-speed').value='10';
        const start=w.programPosition(lastPlan,0),end=w.programPosition(lastPlan,program.moves.length);
        if(start.heated || !end.finished || end.heated) throw new Error('M5 an Programmgrenzen fehlt');
        const view=d.querySelector('#view');
        view.value='xy'; view.dispatchEvent(new w.Event('change'));
        const transform=canvas.workspaceTransform, rect=canvas.getBoundingClientRect();
        const startX=(105+(0-transform.minX)*transform.scale)*rect.width/canvas.width+rect.left;
        const startY=(65+(-95-transform.minY)*transform.scale)*rect.height/canvas.height+rect.top;
        // Synthetische Pointer besitzen keine native Capture-ID; Koordinaten und Handler real prüfen.
        const capture=canvas.setPointerCapture;
        canvas.setPointerCapture=()=>{};
        canvas.dispatchEvent(new w.PointerEvent('pointerdown',{pointerId:7,button:0,clientX:startX,clientY:startY}));
        canvas.dispatchEvent(new w.PointerEvent('pointermove',{pointerId:7,clientX:startX+20*transform.scale*rect.width/canvas.width,clientY:startY+30*transform.scale*rect.height/canvas.height}));
        canvas.dispatchEvent(new w.PointerEvent('pointerup',{pointerId:7}));
        canvas.setPointerCapture=capture;
        if(Math.abs(Number(form.elements.xy_x.value)+30)>1e-3 || Math.abs(Number(form.elements.uv_x.value)+10)>1e-3 || Math.abs(Number(form.elements.xy_y.value)-30)>1e-3 || Number(form.elements.xy_y.value)!==Number(form.elements.uv_y.value)) throw new Error('Gekoppeltes Ziehen fehlt');
        await waitFor(()=>d.querySelector('#placement-feedback').dataset.state==='valid');
        view.value='uv'; view.dispatchEvent(new w.Event('change'));
        canvas.dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowLeft',shiftKey:true,bubbles:true}));
        if(Math.abs(Number(form.elements.xy_x.value)+40)>1e-3 || Math.abs(Number(form.elements.uv_x.value)+20)>1e-3) throw new Error('Gekoppelte Tastaturverschiebung UV fehlt');
        change('uv_scale',2);
        if(Math.abs((Number(form.elements.xy_x.value)+50)-(Number(form.elements.uv_x.value)+60))>1e-3 || Math.abs((Number(form.elements.xy_y.value)+35)-(Number(form.elements.uv_y.value)+70))>1e-3) throw new Error('Zentren nach Skalierung nicht gekoppelt');
        change('xy_x',500);
        if(d.querySelector('#placement-feedback').dataset.state!=='invalid' || !d.querySelector('#play').disabled) throw new Error('Ungültige Verschiebung nicht sofort markiert');
        await waitFor(()=>d.querySelector('#placement-feedback').textContent.includes('außerhalb'));
        const liveFetch=w.fetch.bind(w);
        let releaseOld;
        w.fetch=(url,options)=>{
            if(url!=='/api/plan') return liveFetch(url,options);
            w.fetch=liveFetch;
            // Eine nicht abbrechbare alte Antwort verzögern, um den Revisionsschutz zu prüfen.
            return liveFetch(url,{...options,signal:undefined}).then(async response=>{
                const body=await response.text();
                return new Promise(resolve=>{releaseOld=()=>resolve(new w.Response(body,{status:response.status}));});
            });
        };
        d.querySelector('#center-profile').click();
        await waitFor(()=>releaseOld);
        change('xy_x',500);
        releaseOld(); await sleep(80);
        if(!d.querySelector('#play').disabled || d.querySelector('#placement-feedback').dataset.state==='valid') throw new Error('Veraltete Live-Antwort überschreibt ungültige Position');
        d.querySelector('#demo').click();
        change('xy_y',0);
        await waitFor(()=>d.querySelector('#placement-feedback').textContent.includes('Abbrandbahn'));
        if(d.querySelector('#placement-feedback').dataset.state!=='invalid' || !d.querySelector('#play').disabled) throw new Error('Abbrandfehler bei passender Nennkontur nicht erkannt');
        d.querySelector('#demo').click();
        form.requestSubmit();
        await waitFor(()=>!d.querySelector('#play').disabled);
        if(!d.querySelector('#download').disabled) throw new Error('Export ohne Steuerungsprofil');
        d.querySelector('#progress').value=10;
        d.querySelector('#progress').dispatchEvent(new w.Event('input'));
        if(!d.querySelector('#step-label').textContent.includes('10 /')) throw new Error('Schieberegler');
        for(const view of ['xy','uv','wire']) {
            d.querySelector('#view').value=view;
            d.querySelector('#view').dispatchEvent(new w.Event('change'));
        }
        form.elements.s_max.value=2000;
        form.elements.controller_confirmed.click();
        form.requestSubmit();
        await waitFor(()=>!d.querySelector('#download').disabled);
        if(!d.querySelector('#code').textContent.includes('M3 S600.00000')) throw new Error('Leistungszuordnung');
        if(lastPlan.program.source!=='export' || lastPlan.program.moves.some(move=>move.command==='G1' && move.text!==lastPlan.gcode.split(String.fromCharCode(10))[move.line-1])) throw new Error('Simulation stammt nicht aus Exporttext');
        const code=d.querySelector('#code').textContent, beforeHeat=code.split('M3 S')[0];
        if(!beforeHeat.includes('G0 ') || beforeHeat.includes('G1 ') || !code.includes('; Start: X0.00000 Y0.00000 U0.00000 V0.00000')) throw new Error('G0-Anfahrt ab Maschinennullpunkt fehlt');
        change('machine_zero_x',120); change('machine_zero_u',120);
        await waitFor(()=>d.querySelector('#placement-feedback').textContent.includes('Keine freie Kaltanfahrt'));
        if(!d.querySelector('#download').disabled || d.querySelector('#placement-feedback').dataset.state!=='invalid') throw new Error('Rohteil blockiert G0 nicht');
        change('machine_zero_x',180); change('machine_zero_u',190);
        await waitFor(()=>!d.querySelector('#download').disabled);
        if(!d.querySelector('#coordinates').textContent.includes('Maschinenkoordinaten aktuell:')) throw new Error('Maschinenkoordinaten fehlen');
        const originalFetch=w.fetch.bind(w);
        let planned;
        w.fetch=(url,options)=>{
            if(url==='/api/plan') planned=JSON.parse(options.body);
            return originalFetch(url,options);
        };
        const shared=d.querySelector('#same-profile');
        shared.click();
        if(!d.querySelector('#download').disabled) throw new Error('Profilübernahme invalidiert Export nicht');
        if(!d.querySelector('#file-uv').disabled || !form.elements.uv_contour.disabled) throw new Error('UV-Import bei Profilübernahme aktiv');
        form.requestSubmit();
        await waitFor(()=>!d.querySelector('#download').disabled);
        if(JSON.stringify(planned.xy)!==JSON.stringify(planned.uv)) throw new Error('Profil nicht für beide Seiten übernommen');
        if(planned.width!==400 || planned.height!==300 || planned.span!==600) throw new Error('Skizzenmaße nicht an Planung übergeben');
        if(planned.block_width!==300 || planned.block_height!==200 || planned.block_span!==400) throw new Error('Blockmaße nicht übergeben');
        if(planned.xy_x!==-50 || planned.uv_x!==-50) throw new Error('Gemeinsame Profilzentren bei Übernahme fehlen');
        shared.click();
        if(d.querySelector('#file-uv').disabled || !form.elements.uv_contour.selectedOptions[0].textContent.includes('60.00')) throw new Error('Rechtes Profil nicht wiederhergestellt');
        form.elements.width.value=1;
        form.elements.width.dispatchEvent(new w.Event('input',{bubbles:true}));
        if(!d.querySelector('#download').disabled) throw new Error('Veralteter Export');
        form.requestSubmit();
        await waitFor(()=>d.querySelector('#status').textContent.includes('block_width'));
        d.querySelector('#demo').click();
        shared.click();
        for(const name of ['xy','uv']) {
            if(name==='uv') shared.click();
            const svg='<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="70mm" viewBox="0 0 100 70"><rect width="100" height="70"/><circle cx="35" cy="35" r="10"/></svg>';
            const transfer=new w.DataTransfer();
            transfer.items.add(new w.File([svg],name+'.svg',{type:'image/svg+xml'}));
            d.querySelector('#file-'+name).files=transfer.files;
            d.querySelector('#file-'+name).dispatchEvent(new w.Event('change',{bubbles:true}));
            await waitFor(()=>d.querySelector('#info-'+name).textContent.includes('Kontur(en)'));
            form.elements[name+'_contour'].value='1';
            form.elements[name+'_contour'].dispatchEvent(new w.Event('change',{bubbles:true}));
            if(name==='xy') {
                if(form.elements.uv_contour.value!=='1' || !d.querySelector('#info-uv').textContent.includes('von XY übernommen')) throw new Error('Übernahme nach XY-Import oder Konturwechsel');
                form.elements.mode.value='center';
                form.requestSubmit();
                await waitFor(()=>!d.querySelector('#play').disabled);
                if(planned.uv_contour!=='1' || JSON.stringify(planned.xy)!==JSON.stringify(planned.uv)) throw new Error('Importiertes Profil nicht beidseitig geplant');
            }
        }
        form.elements.mode.value='inner'; form.elements.access.click();
        for(const phase of ['entry','exit']) for(const axis of ['x','y','u','v']) {
            form.elements[phase+'_'+axis].value=axis==='u' ? 105 : 95;
        }
        form.requestSubmit();
        await waitFor(()=>d.querySelector('#program-state').textContent.includes('Nur geometrischer Entwurf'));
        if(!d.querySelector('#warnings').textContent.includes('Innenkontur')) throw new Error('Lochwerkzeug');
        if(!d.querySelector('#play').disabled) throw new Error('Nicht ausführbarer Entwurf wird als G-Code simuliert');
        if(!d.querySelector('#download').disabled || !d.querySelector('#warnings').textContent.includes('Keine freie Kaltanfahrt')) throw new Error('Innerer Einfädelpunkt wird als G0-Zugang exportiert');
        if(!drawnLabels.some(text=>text.includes('Einfahrt')) || !drawnLabels.some(text=>text.includes('Ausfahrt'))) throw new Error('Ein-/Ausfahrt nicht markiert');
        if(failures.length) throw new Error(failures.join(';'));
        output.textContent='PASS: 10-mm-Heizvorlauf vor Material, G-Code-Rückprüfung, kontinuierliche G1-Ein-/Ausfahrt nach F, Heizstatus aus M3/M5, Exportzeilen und Zwischenpositionen sowie bestehende Platzierungs-/Import-/Exportprüfungen';
    } catch(error) { output.textContent='FAIL: '+error.message+' | '+d.querySelector('#status').textContent; }
};
</script></body></html>'''


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', choices=['edge','chrome'], default='edge')
    args = parser.parse_args()
    edge = pathlib.Path('C:/Program Files/Google/Chrome/Application/chrome.exe' if args.browser == 'chrome'
                        else 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')
    if not edge.exists():
        raise SystemExit('Browser nicht gefunden; Browserprüfung manuell durchführen.')
    app.add_url_rule('/_ui_test', view_func=lambda: HARNESS)
    server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    temp_root = pathlib.Path(__file__).resolve().parents[1] / '.tmp'
    temp_root.mkdir(exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(dir=temp_root) as profile:
            result = subprocess.run([str(edge), '--headless', '--disable-gpu', '--no-first-run',
                '--no-default-browser-check', '--disable-extensions', '--disable-background-networking',
                '--user-data-dir='+profile, '--dump-dom', '--virtual-time-budget=15000',
                f'http://127.0.0.1:{server.server_port}/_ui_test'],
                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=45)
            import re
            match = re.search(r'<p id="result">(.*?)</p>', result.stdout)
            report = match.group(1) if match else result.stderr[-1500:]
            print(report)
            if not report.startswith('PASS:'):
                raise SystemExit(1)
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
