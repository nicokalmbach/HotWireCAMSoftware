from flask import Flask, render_template, request, jsonify

from cam import plan, number
from profiles import CamError, import_profile

import version

HOST = "127.0.0.1"
PORT = 5001

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024


@app.context_processor
def inject_version():
    return {"app_version": version.__version__}


@app.get("/")
def index():
    return render_template("index.html")


@app.post('/api/import')
def upload_profile():
    upload = request.files.get('file')
    if upload is None or not upload.filename:
        raise CamError('Bitte eine Profildatei auswählen.')
    factor = number(request.form, 'unit_scale', .0001, 10000, 1)
    # Nur Dateiinhalte lesen. Lokale Dateipfade sind weder nötig noch geprüft.
    return jsonify(import_profile(upload.filename, upload.read(), factor))


@app.post('/api/plan')
def calculate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise CamError('Ungültiger Auftrag.')
    try:
        return jsonify(plan(data))
    except (TypeError, KeyError, IndexError, OverflowError) as exc:
        raise CamError('Ungültige Profil- oder Auftragsdaten.') from exc


@app.errorhandler(CamError)
def invalid_input(error):
    return jsonify(error=str(error)), 400


@app.errorhandler(413)
def too_large(error):
    return jsonify(error='Anfrage zu groß; maximal 4 MiB pro Anfrage.'), 413


if __name__ == "__main__":
    import argparse
    import webbrowser

    from werkzeug.serving import make_server

    parser = argparse.ArgumentParser(description="HotWireCAM lokal starten")
    parser.add_argument('--open-browser', action='store_true',
                        help='Website nach erfolgreichem Serverstart öffnen')
    args = parser.parse_args()
    # Erst binden, damit bei belegtem Port keine fremde/alte Seite geöffnet wird.
    with make_server(HOST, PORT, app, threaded=True) as server:
        url = f"http://{HOST}:{PORT}"
        print(f"HotWireCAM: {url} (Beenden mit Strg+C)", flush=True)
        if args.open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
