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
        if(planned.xy_x!==-50 || planned.uv_x!==-30) throw new Error('Getrennte Positionen überschrieben');
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
        await waitFor(()=>!d.querySelector('#play').disabled);
        if(!d.querySelector('#warnings').textContent.includes('Innenkontur')) throw new Error('Lochwerkzeug');
        if(!drawnLabels.some(text=>text.includes('Einfahrt')) || !drawnLabels.some(text=>text.includes('Ausfahrt'))) throw new Error('Ein-/Ausfahrt nicht markiert');
        if(failures.length) throw new Error(failures.join(';'));
        output.textContent='PASS: Live-Block und Maßlinien, automatische Abstände, Direktimport per Drop, Zentrierung, Live-Profilposition, Raumwarnung, Schnittstart und Ein-/Ausfahrt, mobiles Layout, Demo, Planung, Regler, Ansichten, Export, Invalidierung, SVG-Uploads und beidseitige Profilübernahme';
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
