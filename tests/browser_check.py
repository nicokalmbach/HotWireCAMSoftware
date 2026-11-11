"""Optionaler UI-Smoke-Test mit lokal installiertem Edge (ohne Zusatzpakete)."""
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
        if(planned.xy_x!==60 || planned.uv_x!==70) throw new Error('Getrennte Positionen überschrieben');
        shared.click();
        if(d.querySelector('#file-uv').disabled || !form.elements.uv_contour.selectedOptions[0].textContent.includes('60.00')) throw new Error('Rechtes Profil nicht wiederhergestellt');
        form.elements.width.value=1;
        form.elements.width.dispatchEvent(new w.Event('input',{bubbles:true}));
        if(!d.querySelector('#download').disabled) throw new Error('Veralteter Export');
        form.requestSubmit();
        await waitFor(()=>d.querySelector('#status').textContent.includes('außerhalb'));
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
        if(failures.length) throw new Error(failures.join(';'));
        output.textContent='PASS: Demo, Planung, Vorschau, Regler, Ansichten, Export, Leistung, Invalidierung, Raumfehler, SVG-Uploads, Lochwerkzeug, beidseitige Profilübernahme';
    } catch(error) { output.textContent='FAIL: '+error.message+' | '+d.querySelector('#status').textContent; }
};
</script></body></html>'''


def main():
    edge = pathlib.Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')
    if not edge.exists():
        raise SystemExit('Edge nicht gefunden; Browserprüfung manuell durchführen.')
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
