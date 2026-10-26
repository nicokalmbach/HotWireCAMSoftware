# HotWireCAMSoftware
PMK-A2

## Projektbeschreibung

HotWireCamSoftware ist ein Hochschulprojekt für eine browserbasierte CAM-Anwendung für eine CNC-Heißdrahtschneidemaschine. Die lokale Flask-Anwendung importiert zwei Vektorprofile, plant synchronisierte XYUV-Drahtwege und erzeugt G-Code.

Implementiert sind SVG-/DXF-Import, Konturauswahl, Skalierung und Positionierung, Start-/Endpunkte als Weganteile, Abbrandkorrektur, Innenkonturen mit geradliniger Ein-/Ausfahrt sowie ein animiertes Drahtmodell. Die Anwendung prüft Raumgrenzen, ungültige Konturen, kollabierende Abbrandkorrekturen und 21 Zwischenquerschnitte auf Überschneidungen.

Eine Maschinenanbindung und thermische Simulation sind nicht implementiert. Maschinenmaße und Schnittparameter trägt der Nutzer ein. Der generische G-Code setzt XYUV sowie G21/G90/G94 und M3/S/M5 zur Ansteuerung eines Stromreglers voraus; diese Zuordnung muss zur Hardware passen. Vorschau und Planung sind auch ohne Steuerungsprofil möglich.

## Schnittdaten vorbereiten

1. Für XY und UV jeweils eine SVG- oder DXF-Datei laden. Der Inhalt wird im Speicher verarbeitet; Dateipfade werden weder kontrolliert noch gespeichert. Jede Datei darf mehrere Konturen enthalten.
2. Je eine Kontur auswählen. Ein Auftrag bearbeitet ein Konturpaar; Löcher separat vor der Außenkontur planen. SVG-Maße/viewBox werden mit 96 dpi in mm umgerechnet und Y nach oben gespiegelt. DXF-Einheiten stammen aus dem Header; für einheitenlose DXF ist der Faktor einzugeben.
3. Schneidraum, Abstand der Achsebenen und Lage der beiden Profilebenen eintragen. Profilpositionen beziehen sich auf die untere linke Ecke der gesamten jeweiligen Datei; die Lage ihrer Innenkonturen bleibt erhalten.
4. Start/Ende in Prozent der Konturlänge und gegebenenfalls Laufrichtung einstellen. Geschlossene Profile werden zunächst gegen den Uhrzeigersinn orientiert. Gleiche Start-/Endwerte ergeben eine volle Runde; offene Profile benötigen Ende > Start nach Richtungswahl.
5. Vorschub, Leistung und Abbrandradius (halbe Schnittbreite) setzen. Außenkonturen werden nach außen, Löcher nach innen korrigiert. Offene Profile unterstützen Links/Rechts; „Direkt auf Kontur“ deaktiviert die Korrektur.
6. Für Löcher die Ein-/Ausfahrt aktivieren und Zugangspunkte in beiden Profilebenen festlegen. Draht einfädeln oder Zugangsschlitz vorsehen. Die geraden Verbindungen schneiden mit; ihre Zugänglichkeit wird nicht automatisch geprüft.
7. Schneidweg berechnen und mit Schieberegler oder Wiedergabe ansehen. Beide Profile erhalten gleich viele Liniensequenzen, einschließlich der Ecken beider Profile. Eine konische Form ist nicht pauschal ausgeschlossen; ungültige beziehungsweise kollabierende Geometrien werden abgewiesen.
8. Für den Export S-Maximalwert des Stromreglers eintragen und das passende Steuerungsprofil bestätigen. Leistung wird linear als `S = Prozent / 100 × S-Maximum` ausgegeben. Vor Ausführung die angezeigte Startposition bei ausgeschaltetem Draht manuell anfahren; der Export enthält keine automatische Anfahrt. Vorschub F ist als mm/min entlang des vierdimensionalen Achsvektors definiert und muss zur Firmware passen.

„Demobeispiel laden“ füllt einen Beispielauftrag. Dessen Maße, Vorschub und Leistung sind **keine Hardwareparameter**. Importierbare Beispieldateien stehen unter [examples/](examples/). Details und Grenzen beschreibt die [Architektur](ARCHITECTURE.md).

## Versionierung

Die aktuelle Versionsnummer steht zentral in `version.py` (`__version__`).
Die Website zeigt sie automatisch in der Fußzeile an. Bei einem Versionswechsel
wird nur dieser Wert geändert; anschließend die Anwendung neu starten.

Die Startversion ist `0.1.0`; die CAM-Erweiterungen stehen unter „Unveröffentlicht“
im Changelog. Die Achsensteuerung für den ersten Hardware-Meilenstein steht noch aus.

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
├── app.py                 # Flask-Anwendung, Import- und Planungs-API
├── profiles.py            # SVG-/DXF-Import in Millimeter
├── cam.py                 # Geometrie, Synchronisation und G-Code
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
├── static/css/style.css   # Gestaltung und responsives Layout
├── static/js/cam.js       # Bedienung, Drahtmodell und Download
├── examples/              # SVG-Beispielprofile
└── tests/                 # Import-, Geometrie-, API- und Browserprüfungen
```

## Zusammenarbeit mit Git

Das Projektverzeichnis enthält bereits ein Git-Repository und eine konfigurierte GitHub-Adresse. Änderungen können lokal versioniert und über Branches gemeinsam vorbereitet werden. Vor einem Push müssen Git installiert sowie Schreibrechte und die Freigabe für das Remote-Repository vorhanden sein. Es wird durch dieses Grundgerüst kein Repository erstellt und kein Push ausgeführt.

## Sinnvoller nächster Schritt

Mit der Hardwaregruppe G-Code-Dialekt, Vorschubinterpretation, Stromregler-Zuordnung und reale Maschinenmaße abstimmen. Abbrand für Material und Schnittparameter praktisch bestimmen. Maschinensteuerung, Referenzfahrt und thermische Effekte bleiben offen.
