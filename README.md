# HotWireCAMSoftware
PMK-A2

## Projektbeschreibung

HotWireCamSoftware ist ein Hochschulprojekt für eine browserbasierte CAM-Anwendung für eine CNC-Heißdrahtschneidemaschine. Die lokale Flask-Anwendung importiert zwei Vektorprofile, plant synchronisierte XYUV-Drahtwege und erzeugt G-Code.

Implementiert sind SVG-/DXF-Import, Konturauswahl, gekoppelte Profilzentren mit Verschieben im Seitenschnitt, automatische Randzugänge mit Kaltanfahrt ab Nullpunkt, Start-/Endpunkte als Weganteile, Abbrandkorrektur, Innenkonturen mit manueller Ein-/Ausfahrt sowie ein animiertes Drahtmodell. Die Anwendung prüft Raumgrenzen, ungültige Konturen, kollabierende Abbrandkorrekturen und 21 Zwischenquerschnitte auf Überschneidungen.

Eine Maschinenanbindung und thermische Simulation sind nicht implementiert. Maschinenmaße und Schnittparameter trägt der Nutzer ein. Der generische G-Code setzt XYUV, G0/G1 sowie G21/G90/G94 und M3/S/M5 zur Ansteuerung eines Stromreglers voraus; diese Zuordnung muss zur Hardware passen. Vorschau und Planung sind auch ohne Steuerungsprofil möglich.

## Schnittdaten vorbereiten

1. Raumbreite X/U, Raumhöhe Y/V und Abstand der Achsebenen direkt an den Maßlinien des räumlichen Maschinenmodells eintragen (mm). Führungssäulen, Schlitten und Grundschienen zeigen die Orientierung; der Arbeitsraum ist transparent gelb und der Schneiddraht orange dargestellt. Das Modell ist bereits ohne Profile sichtbar und nicht maßstabsgetreu. Auf kleinen Bildschirmen lässt es sich horizontal scrollen. Blockbreite X/U, Blockhöhe Y/V und Blocklänge zwischen den Achsebenen eingeben. Der Block steht mittig in X/U und zwischen den Drahtführungen, mit seiner Unterseite auf Y/V = 0. Die Abstände zu den Achsebenen berechnen sich automatisch: je Seite `(Achsebenenabstand − Blocklänge) / 2`. Die Profile liegen auf den beiden Stirnflächen des Blocks.
2. Für XY und UV jeweils eine SVG- oder DXF-Datei laden. Alternativ bei der ersten Profileingabe „Dieses Profil für beide Seiten verwenden“ aktivieren: Datei und Konturauswahl von XY gelten dann auch für UV. Die Mittelpunkte der gesamten Dateiausdehnungen bleiben gekoppelt, auch bei verschiedenen Skalierungen. Positionen führen die andere Seite mit; Start/Ende und Laufrichtung bleiben separat. Nach dem Abwählen steht ein zuvor geladenes UV-Profil wieder zur Verfügung und wird am gemeinsamen Zentrum ausgerichtet. Der Inhalt wird im Speicher verarbeitet; Dateipfade werden weder kontrolliert noch gespeichert. Jede Datei darf mehrere Konturen enthalten.
3. Je eine Kontur auswählen. Ein Auftrag bearbeitet ein Konturpaar; Löcher separat vor der Außenkontur planen. SVG-Maße/viewBox werden mit 96 dpi in mm umgerechnet und Y nach oben gespiegelt. DXF-Einheiten stammen aus dem Header; für einheitenlose DXF ist der Faktor einzugeben. Profilpositionen beziehen sich auf die untere linke Ecke der gesamten jeweiligen Datei; die Lage ihrer Innenkonturen bleibt erhalten.
4. Start/Ende in Prozent der Konturlänge und gegebenenfalls Laufrichtung einstellen. Geschlossene Profile werden zunächst gegen den Uhrzeigersinn orientiert. Gleiche Start-/Endwerte ergeben eine volle Runde; offene Profile benötigen Ende > Start nach Richtungswahl.
5. Vorschub, Leistung und Abbrandradius (halbe Schnittbreite) setzen. Außenkonturen werden nach außen, Löcher nach innen korrigiert. Offene Profile unterstützen Links/Rechts; „Direkt auf Kontur“ deaktiviert die Korrektur.
6. Standardmäßig ermittelt die Planung kurze gerade Ein-/Ausfahrten von oben oder seitlich zum eingestellten Konturstart/-ende, ohne das Bauteil vorzeitig zu durchqueren. Die aufliegende Unterseite einschließlich unterer Ecken ist gesperrt. Kontur, Abbrand und Materialschnitt bleiben dabei im Block; der zusätzliche Heizvorlauf liegt davor in der Luft. Für Löcher stattdessen die manuelle Ein-/Ausfahrt aktivieren. Für den Export müssen Start und Ende außen erreichbar sein; ein innerer Einfädelpunkt allein erlaubt keine Kaltanfahrt ab Maschinennullpunkt. Zugangsschlitze gegebenenfalls separat planen. Die geraden Verbindungen schneiden mit; manuelle Zugänge selbst prüfen.
7. Schneidweg berechnen und mit Schieberegler oder Wiedergabe ansehen. Korrespondierende Ecken werden in Laufrichtung paarweise zugeordnet und im selben XYUV-Bewegungsblock erreicht, auch bei unterschiedlichen Seitenlängen und nach Abbrandkorrektur. Start/Ende und Laufrichtung müssen fachlich zusammenpassen. SVG-Kreise und SVG-Kurven dürfen unterschiedlich viele Stützpunkte haben; nur echte Ecken an Segmentübergängen müssen zusammenpassen. Nach dem Update SVG-Dateien erneut laden, damit ihre Eckinformationen vorliegen. Bei DXF und älteren Profildaten zählen weiterhin alle nichtkollinearen Stützpunkte als Ecken. Eine konische Form ist nicht pauschal ausgeschlossen; ungültige beziehungsweise kollabierende Geometrien werden abgewiesen.
8. Für den Export S-Maximalwert des Stromreglers eintragen und das passende Steuerungsprofil bestätigen. Leistung wird linear als `S = Prozent / 100 × S-Maximum` ausgegeben. Jeder Export beginnt am per Kontaktschalter gesetzten Maschinennullpunkt X0/Y0/U0/V0: Y/V unten auf Auflagehöhe, X/U auf der positiven Seite. Standardmäßig wird für X/U die positive Planungsraumgrenze +Breite/2 verwendet; bei abweichenden Kontakten deren tatsächliche positive Schalterlage eintragen. G-Code-Koordinaten werden um diese Lage versetzt. M5/G0 fahren außen zum Einschaltpunkt mindestens 10 mm vor Materialeintritt. Dort M3/S, dann G1 mit Schnittvorschub über die Luftstrecke zur Rohteilkante und weiter zur Kontur. Bei automatischem Eintritt sind es senkrecht zur Eintrittsfläche genau 10 mm, auf beiden Seiten parallel. Bereits weiter außen liegende manuelle Startpunkte bleiben erhalten. Ohne passenden Freiraum oder außen liegenden Austritt bleibt der Export gesperrt. Es wird keine zusätzliche Aufheizpause eingefügt; Spannmittel und reale Temperatur sind nicht modelliert. Eine Referenzfahrt ist nicht enthalten. Vorschub F gilt für G1 als mm/min entlang des vierdimensionalen Achsvektors und muss zur Firmware passen; G0 verwendet den Eilgang der Steuerung.

„Demobeispiel laden“ füllt einen Beispielauftrag. Dessen Maße, Vorschub und Leistung sind **keine Hardwareparameter**. Importierbare Beispieldateien stehen unter [examples/](examples/). Details und Grenzen beschreibt die [Architektur](ARCHITECTURE.md).

Die maßstäbliche Ansicht „Arbeitsraum & Drahtweg“ erscheint direkt unter den
Blockeingaben: Maschinenraum bereits mit gültigen Maschinenmaßen, Block mit
gültigen Blockmaßen. Maßlinien zeigen Blockbreite, Höhe, Länge sowie Abstände
zu beiden Achsebenen, X/U-Freiraum je Seite und Freiraum nach oben.

Dort XY oder UV als Ziel wählen und eine SVG-/DXF-Datei einfügen oder auf die
Ansicht ziehen. Die Dateifelder unter „Profilimport“ bleiben verfügbar. Neue
Dateien werden bei gültiger Blockhöhe anhand ihrer gesamten Ausdehnung in X/U
und Y/V zentriert. „Profil im Block zentrieren“ richtet beide Dateizentren erneut aus.
In „Seitenschnitt XY“ oder „Seitenschnitt UV“ das Profil direkt ziehen. Bei
fokussierter Ansicht verschieben Pfeiltasten um 1 mm, mit Umschalt um 10 mm.
Positions- und Skalierungsfelder wirken ebenfalls auf die gekoppelten Zentren.
Für eine eigene UV-Datei muss die Übernahme des XY-Profils ausgeschaltet sein.

Blocküberschreitungen werden sofort rot markiert. Nach 250 ms Eingabepause
prüft der Server automatisch die vollständige Geometrie einschließlich Abbrand,
Zugang und Achsprojektion. Erst bei Erfolg erscheint das grüne Platzierungsfeedback
und der vollständige heiße Weg; fehlende Pflichtangaben werden als Fehler gemeldet.
„Schneidweg berechnen“ löst dieselbe Prüfung sofort aus. Grün und Violett markieren
Ein-/Ausfahrt samt Richtungspfeilen; Blau gestrichelt zeigt die Kaltanfahrt.
Seit 0.2.4 wird der ausgegebene G-Code vor dem Export rückgelesen und gegen die
geplante Bahn geprüft. Genau diese Rücklesung steuert den bewegten Draht:
Orange bei angeforderter Heizleistung, Blau bei ausgeschalteter Leistung.
Zustandszeile, G-Code-Zeilennummer und G0/G1 zeigen den tatsächlichen Programmablauf.
Auch die Strecke von Rohteilkante zur Kontur und zurück wird als heißer
G1-Satz mit dem ausgegebenen F kontinuierlich durchfahren. Wiedergabe 1×/10×/50×
ändert nur die Anzeige. G1-Zeiten sind ideal ohne Beschleunigung; G0 ist mangels
bekanntem Maschinen-Eilgang ausdrücklich mit 1 s je nicht leerem Satz schematisch.
Ohne S-Zuordnung wird dieselbe Ausgabevorlage intern ohne Hardware-S-Wert geprüft;
sie ist kein herunterladbarer Export. Bei gesperrter Anfahrt bleibt nur die
geometrische Ansicht ohne Programmwiedergabe. Alte Ergebnisse und Exporte werden
bei Änderungen sofort verworfen. Ohne Zugang beginnt der Schnitt auf der Kontur.
Die Geometrie-/Codeprüfung ersetzt keine thermische oder Hardwareprüfung.

Der Einschaltpunkt und der äußere Heizvorlauf werden seit 0.2.5 ebenfalls
markiert. Die Wiedergabe zeigt dort „Heizvorlauf · 10 mm vor Materialeintritt“
mit M3 und G1 aus dem rückgelesenen Code. Kann eine Eintrittsseite die 10 mm
nicht aufnehmen, prüft die Automatik andere zugängliche Seiten. Fehlt der Platz
überall, bleibt der geometrische Entwurf sichtbar, ohne Export oder Wiedergabe.

## Versionierung

Die aktuelle Versionsnummer steht zentral in `version.py` (`__version__`).
Die Website zeigt sie automatisch in der Fußzeile an. Bei einem Versionswechsel
diesen Wert sowie Changelog, [timeline.md](timeline.md) und betroffene Anleitungen
aktualisieren; anschließend die Anwendung neu starten.

Die aktuelle Version ist `0.2.5`, die ursprüngliche Startversion war `0.1.0`.
Die Achsensteuerung für den ersten Hardware-Meilenstein steht noch aus.

Seit 0.2.0 gilt X/U = 0 in der Mitte des Verfahrwegs; die Raumgrenzen sind
`−Breite/2` bis `+Breite/2`. Y/V beginnt auf der Auflageebene bei 0 und reicht
bis zur Raumhöhe. Profilpositionen und Ein-/Ausfahrtspunkte verwenden dieses
Koordinatensystem; alte Positionen müssen entsprechend angepasst werden.
Seit 0.2.3 werden die Bezugspunkte ausdrücklich getrennt:

| Bezug | Lage / Bedeutung |
| --- | --- |
| Planungsraum | X/U = 0 mittig im Raum, Y/V = 0 auf der Auflage; Vorschau und Profilfelder |
| Rohteilnullpunkt | Untere linke Ecke des Blocks, im Planungsraum X/U = −Blockbreite/2, Y/V = 0 |
| Maschinennullpunkt | Per Kontaktschalter gesetzt: X/U positiv, Y/V unten; Programmstart bei X0/Y0/U0/V0 |
| Schnittstart | Gewählter Blockeintritt beziehungsweise manueller Zugang, Ende der G0-Anfahrt |

Maschinenkoordinaten im Export ergeben sich aus Planungskoordinate minus
Schalterlage. Die Anwendung setzt keinen neuen Nullpunkt am Rohteil oder
Konturstart. Schalterauswertung, Tastatursteuerung realer Achsen und
Maschinenkommunikation sind noch nicht implementiert.

Die geplanten Meilensteine und ihr Status stehen in der [Roadmap](ROADMAP.md).

## Technische Dokumentation

Die Dokumentation entsteht parallel zur Implementierung. Änderungen an Verhalten,
Installation oder Architektur werden im selben Arbeitsschritt dokumentiert.

| Datei | Inhalt |
| --- | --- |
| [CHANGELOG.md](CHANGELOG.md) | Änderungen und Versionshistorie |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Aufbau, Datenfluss und technische Entscheidungen |
| [INSTALLATION.md](INSTALLATION.md) | Einrichtung, Start und Funktionsprüfung |
| [INSTALLATION_DEBIAN.md](INSTALLATION_DEBIAN.md) | Debian-13-LXC-Installation für Linux-Anfänger |
| [timeline.md](timeline.md) | Durchgeführte Änderungen je Version |
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

## Installation auf Debian 13 LXC

Der interaktive [Installer](scripts/install-debian.sh) lädt das Repository direkt
von GitHub und schlägt `wyro`, `/opt/hotwirecam` und Port `5001` vor. Gunicorn läuft
als eigener Benutzer unter systemd und startet mit dem Container. Die Website ist
standardmäßig im lokalen Netzwerk erreichbar. Kopierbare Befehle und alle Schritte
stehen in [INSTALLATION_DEBIAN.md](INSTALLATION_DEBIAN.md).

Die Installer-Dateien müssen zuvor auf GitHub bereitgestellt sein. Eine vollständige
LXC-Installation wurde hier noch nicht durchgeführt. Ein Update-Script ist geplant;
der Erstinstaller überschreibt keine bestehende Installation.

## Anwendung starten

Unter Windows `start.cmd` doppelklicken. Der Starter lädt die aktuellen lokalen
Projektdateien und öffnet die Website auf Port 5001 im Standardbrowser. Das
Terminal geöffnet lassen; mit `Strg+C` beenden. Alternativ in PowerShell:

```powershell
.\.venv\Scripts\python.exe app.py
```

Öffne anschließend [http://127.0.0.1:5001](http://127.0.0.1:5001) im Browser. Zum Beenden drückst du im Terminal `Strg+C`.

Wenn PowerShell das Aktivieren der Umgebung erlaubt, kannst du alternativ erst `.\.venv\Scripts\Activate.ps1` ausführen und danach `python app.py` starten.

## Projektstruktur

```text
.
├── app.py                 # Flask-Anwendung, Import- und Planungs-API
├── profiles.py            # SVG-/DXF-Import in Millimeter
├── cam.py                 # Geometrie, Synchronisation und G-Code
├── nc_program.py          # G-Code rücklesen und vor Export gegenprüfen
├── version.py             # Zentrale Versionsnummer
├── requirements.txt       # Python-Abhängigkeiten
├── requirements-debian.txt # Zusätzlich Gunicorn für Linux
├── scripts/               # Debian-Installer und systemd-Vorlage
├── timeline.md            # Änderungen je Version
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
