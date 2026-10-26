# Architektur

## Aktueller Aufbau

HotWireCamSoftware ist derzeit eine lokale Flask-Anwendung. Python erzeugt die
HTML-Seite mit Jinja; der Browser stellt sie mit CSS dar. Es gibt derzeit keine
Datenbank, Dateiverarbeitung, JavaScript-Logik oder Anbindung an eine Maschine.

| Bestandteil | Aufgabe |
| --- | --- |
| `app.py` | Erstellt die Flask-App und beantwortet `GET /` mit der Startseite |
| `version.py` | Enthält `__version__` als zentrale Versionsnummer |
| `templates/index.html` | Deutschsprachige Oberfläche mit deaktivierten Platzhaltern |
| `static/css/style.css` | Gestaltung und responsive Darstellung |
| `requirements.txt` | Flask-Abhängigkeit (`>=3.0,<4.0`) |

## Ablauf einer Anfrage

1. Der Browser ruft `http://127.0.0.1:5000/` auf.
2. Die Route `index()` rendert `templates/index.html`.
3. Der Context Processor `inject_version()` stellt `app_version` aus `version.py` bereit.
4. Der Browser lädt das Stylesheet über die statische Flask-Route nach.

## Bestehende Entscheidungen

- Flask liefert das lokale Grundgerüst und die serverseitigen Templates.
- Beim direkten Start mit `python app.py` bindet der Entwicklungsserver an
  `127.0.0.1:5000`; der Debug-Modus ist ausgeschaltet.
- Die Versionsnummer wird zentral gepflegt, damit Anzeige und Quellcode zusammenpassen.
- Nicht implementierte Funktionen sind als Platzhalter gekennzeichnet.

## Offene Architekturfragen

Vor der Implementierung sind Profilformate, Einheiten, Koordinatensystem,
Maschinenparameter und die Kommunikationsschnittstelle mit der Hardwaregruppe
abzustimmen. Modulgrenzen für Import, Geometrie, G-Code und Kommunikation sind noch
nicht festgelegt. Sie werden hier dokumentiert, sobald eine Entscheidung getroffen ist.

Den geplanten Ausbau beschreibt die [Roadmap](ROADMAP.md).
