# HotWireCAMSoftware
PMK-A2

## Projektbeschreibung

HotWireCamSoftware ist ein Hochschulprojekt für eine browserbasierte CAM-Anwendung für eine CNC-Heißdrahtschneidemaschine. Dieses Repository enthält zunächst ein lokal startbares Flask-Grundgerüst mit einer deutschsprachigen Benutzeroberfläche.

Profilimport, Profileinstellungen, Schneidvorschau und G-Code-Export sind derzeit **Platzhalter**. Die Anwendung steuert keine Maschine und erzeugt keine Maschinendaten. Technische Maschinenparameter werden erst ergänzt, wenn sie mit der Hardwaregruppe abgestimmt sind.

## Versionierung

Die aktuelle Versionsnummer steht zentral in `version.py` (`__version__`).
Die Website zeigt sie automatisch in der Fußzeile an. Bei einem Versionswechsel
wird nur dieser Wert geändert; anschließend die Anwendung neu starten.

Die Startversion ist `0.1.0`. Bisher ist das Projektgrundgerüst vorhanden;
die Achsensteuerung für den ersten Meilenstein steht noch aus.

Die geplanten Meilensteine und ihr Status stehen in der [Roadmap](ROADMAP.md).

## Technische Dokumentation

Die Dokumentation entsteht parallel zur Implementierung. Änderungen an Verhalten,
Installation oder Architektur werden im selben Arbeitsschritt dokumentiert.

| Datei | Inhalt |
| --- | --- |
| [CHANGELOG.md](CHANGELOG.md) | Änderungen und Versionshistorie |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Aufbau, Datenfluss und technische Entscheidungen |
| [INSTALLATION.md](INSTALLATION.md) | Einrichtung, Start und Funktionsprüfung |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Häufige Probleme und Lösungen |
| [ROADMAP.md](ROADMAP.md) | Geplante Meilensteine und offene Abstimmungen |

Für die Arbeit mit KI hält [AGENTS.md](AGENTS.md) die Pflege dieser Dateien fest.

## Voraussetzungen

- Python 3.10 oder neuer
- Ein Terminal (unter Windows zum Beispiel PowerShell)

## Installation unter Windows

Öffne PowerShell im Projektordner und führe die folgenden Befehle aus:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Die virtuelle Umgebung enthält die für dieses Projekt installierten Python-Pakete. Sie liegt im ignorierten Ordner `.venv` und wird nicht in Git eingecheckt.

## Anwendung starten

```powershell
.\.venv\Scripts\python.exe app.py
```

Öffne anschließend [http://127.0.0.1:5000](http://127.0.0.1:5000) im Browser. Zum Beenden drückst du im Terminal `Strg+C`.

Wenn PowerShell das Aktivieren der Umgebung erlaubt, kannst du alternativ erst `.\.venv\Scripts\Activate.ps1` ausführen und danach `python app.py` starten.

## Projektstruktur

```text
.
├── app.py                 # Flask-Anwendung und Startpunkt
├── version.py             # Zentrale Versionsnummer
├── requirements.txt       # Python-Abhängigkeiten
├── README.md              # Einstieg und Dokumentationsverzeichnis
├── CHANGELOG.md           # Änderungshistorie
├── ARCHITECTURE.md        # Technischer Aufbau
├── INSTALLATION.md        # Einrichtung und Start
├── TROUBLESHOOTING.md     # Fehlerbehebung
├── ROADMAP.md             # Meilensteine
├── AGENTS.md              # Arbeitsregeln für KI-Assistenten
├── templates/
│   └── index.html         # Startseite
└── static/
    └── css/
        └── style.css      # Gestaltung und responsives Layout
```

## Zusammenarbeit mit Git

Das Projektverzeichnis enthält bereits ein Git-Repository und eine konfigurierte GitHub-Adresse. Änderungen können lokal versioniert und über Branches gemeinsam vorbereitet werden. Vor einem Push müssen Git installiert sowie Schreibrechte und die Freigabe für das Remote-Repository vorhanden sein. Es wird durch dieses Grundgerüst kein Repository erstellt und kein Push ausgeführt.

## Sinnvoller nächster Schritt

Mit der Hardwaregruppe die benötigten Profileingabeformate und die fachlichen Anforderungen an Profileinstellungen abstimmen. Danach kann ein erster, unabhängig von einer Maschinensteuerung testbarer Profilimport umgesetzt werden.
