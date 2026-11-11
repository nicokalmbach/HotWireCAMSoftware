# Architektur

## Aktueller Aufbau

HotWireCamSoftware ist derzeit eine lokale Flask-Anwendung. Python erzeugt die
HTML-Seite mit Jinja; der Browser bedient die Planungs-API per JavaScript und zeigt
ein Canvas-Drahtmodell. Es gibt keine Datenbank und keine Anbindung an eine Maschine.
Uploads und Aufträge bleiben im Speicher; Profile werden nach dem Import im Browser
gehalten und für jede Berechnung erneut gesendet.

| Bestandteil | Aufgabe |
| --- | --- |
| `start.cmd` | Windows-Starter: lokale Python-Umgebung, aktueller Projektordner und Browseröffnung |
| `scripts/install-debian.sh` | Interaktive Erstinstallation aus GitHub auf Debian 13 mit eigenem Dienstbenutzer |
| `scripts/hotwirecam.service.in` | Vorlage für Gunicorn und systemd im LXC-Container |
| `requirements-debian.txt` | Linux-Betrieb: bestehende Anforderungen plus Gunicorn |
| `app.py` | Flask-App: `GET /`, `POST /api/import`, `POST /api/plan`, Eingabefehler als JSON |
| `profiles.py` | Vektorimport mit ezdxf/svgelements; Kurvenannäherung und Einheiten |
| `cam.py` | Konturen, gemeinsame Liniensequenzen, Abbrand, Projektion, Raumprüfung, G-Code |
| `version.py` | Enthält `__version__` als zentrale Versionsnummer |
| `templates/index.html` | Deutschsprachiges Auftragsformular und Vorschau-/Exportbereich |
| `static/css/style.css` | Gestaltung und responsive Darstellung |
| `static/js/cam.js` | Imports, Formularzustand, Canvas-Vorschau, Animation, `.nc`-Download |
| `requirements.txt` | Flask, ezdxf, svgelements und Shapely; Versionsbereiche in der Datei |
| `tests/` | Import-, Planungs- und API-Tests sowie optionaler Edge-Browsertest |

## Ablauf einer Anfrage

Die Seitennavigation markiert den aktuellen Arbeitsbereich dynamisch in `cam.js`.
Ankerklicks und Hashwechsel aktualisieren die Auswahl direkt; beim Scrollen und
bei Größenänderungen folgt sie der Abschnittsposition im Browser. Am Seitenende
wird auch der kurze Exportbereich aktiv. `aria-current="location"` kennzeichnet
den aktiven Link zusätzlich für assistive Technologien.

1. Der Browser ruft `http://127.0.0.1:5001/` auf.
2. Die Route `index()` rendert `templates/index.html`.
3. Der Context Processor `inject_version()` stellt `app_version` aus `version.py` bereit.
4. Der Browser lädt das Stylesheet über die statische Flask-Route nach.

## Betrieb im Debian-13-LXC-Container

Der Installer läuft innerhalb des vorhandenen Containers als root. Er prüft Debian
13, systemd, neue Zielpfade und Benutzer, fragt GitHub-Quelle/Branch oder Tag,
Dienstbenutzer, Verzeichnis, Bind-Adresse und Port ab und zeigt die Auswahl vor
der Installation. Standard: `wyro`, `/opt/hotwirecam`, `0.0.0.0:5001` und `main`.
Er installiert Betriebssystempakete, klont das öffentliche HTTPS-Repository als
Dienstbenutzer, erstellt eine eigene Python-Umgebung und installiert
`requirements-debian.txt`. Der App-Import und die vorhandenen Unit-Tests müssen
vor der Dienstaktivierung erfolgreich sein.

Die aus dem geklonten Repository geladene Dienstvorlage wird nach
`/etc/systemd/system/hotwirecam.service` geschrieben. Gunicorn lädt `app:app`
direkt; der lokale `__main__`-Starter mit Browseröffnung wird nicht ausgeführt.
Zwei Worker mit je zwei Threads bedienen HTTP; das Zeitlimit beträgt 120 Sekunden.
Diese Werte sind Betriebsvorschläge, keine gemessenen Leistungsgrenzen.
Der Dienst läuft ohne Root-Rechte mit `NoNewPrivileges` und protokolliert in das
systemd-Journal. Die Vorlage verlangt für die LXC-Kompatibilität keine zusätzlichen
Mount-Namespaces. `/var/lib/hotwirecam` ist das Home-Verzeichnis des Dienstbenutzers.
Nach Aktivierung prüft der Installer Dienststatus und HTTP-Erreichbarkeit lokal.
Die Erreichbarkeit vom PC muss zusätzlich geprüft werden.

`/etc/hotwirecam/install.conf` hält Repository, gewählten Ref, installierten Commit,
Benutzer, Pfad und Netzwerkparameter für ein späteres Update-Script fest; sie
steuert den Dienst nicht unmittelbar. Erstinstallation und späteres Update werden
getrennt: Vorhandene Pfade, Benutzer oder Dienste führen zum Abbruch, es gibt keinen
automatischen Rollback. Abgebrochene Installationen bleiben zur Diagnose erhalten.
Das Update-Script ist noch nicht implementiert. Python-Abhängigkeiten sind über
Versionsbereiche definiert, nicht vollständig durch eine Lockdatei festgeschrieben.

Der Standardbetrieb ist HTTP im vertrauenswürdigen LAN. Anmeldung, TLS und
öffentlicher Internetbetrieb sind nicht eingerichtet; Firewalls und LXC-Host
werden nicht verändert. Die vollständige Installation auf Debian 13 LXC ist noch
auf dem Zielsystem zu prüfen. Siehe [Installationsanleitung](INSTALLATION_DEBIAN.md).

## Import und Planungsdaten

Die Checkbox bei der XY-Eingabe verwendet im Browser dieselben importierten Daten
und dieselbe Konturauswahl für beide Seiten. UV-Import, Einheitenfaktor und
Konturauswahl sind währenddessen gesperrt; die übrigen UV-Felder bleiben unabhängig.
Ein separates UV-Profil samt Konturauswahl bleibt zum Wiederherstellen erhalten.
XY-Neuimporte und Konturwechsel aktualisieren die Übernahme; ein ungültiger oder
laufender XY-Import verhindert die Planung auch für UV. Die Planungsanfrage enthält
weiterhin beide Profile und übernimmt explizit `uv_contour` aus `xy_contour`.
Umschalten verwirft vorhandene Vorschau und Export. Das Demobeispiel setzt die
Option zurück und lädt wieder zwei getrennte Profile.

`POST /api/import` erhält ein Multipart-Feld `file` und optional `unit_scale`
(mm pro Einheit für einheitenlose DXF). Die Antwort enthält `contours` als Listen
von `[x,y]`-Punkten in mm und `notes`. Es wird kein Serverpfad geöffnet oder gespeichert.
Maximal 4 MiB pro Anfrage, 100 Konturen und insgesamt 20000 Punkte je Profil.
Dateiendung und Inhalte werden auf unterstütztes Format geprüft, nicht der Dateipfad.

SVG: physische Maße, viewBox und Transformationen über svgelements, 96 dpi und
Y-Spiegelung. Unterstützt werden Pfade und geometrische Grundformen; mehrere
Unterpfade werden getrennte Konturen. Text, Bilder, Masken, Clipping, Scripts und
externe Referenzen werden abgewiesen. Texte vorher in Pfade umwandeln.
Die Kurvenannäherung prüft Zwischenpunkte rekursiv mit 0,03 mm Zielabweichung;
dies ist keine garantierte maximale Gesamtabweichung für jede SVG-Geometrie.

DXF: ASCII-DXF im Modellbereich mit LINE, ARC, CIRCLE, ELLIPSE, SPLINE,
LWPOLYLINE und POLYLINE. ezdxf nähert Kurven mit 0,03 mm Abflachungstoleranz an.
Konturen müssen in Z=0 liegen. Eindeutige Endpunkte loser Linien werden innerhalb
von 0,00001 mm verbunden; Lücken werden nicht automatisch überbrückt.
Andere Objekte (z. B. INSERT, TEXT, HATCH) werden mit Fehler abgewiesen und müssen
vorher aufgelöst werden. Header-Einheiten haben Vorrang vor dem Eingabefaktor.

`POST /api/plan` erhält zwei importierte Profile (`xy`, `uv`) und die Formularfelder
als JSON. Fehlerhafte Eingaben ergeben HTTP 400 mit `error`, zu große Anfragen 413.
Die Antwort enthält die nominelle Achsbahn `nominal`, korrigierte Achsbahn `path`,
Punkte in den Profilebenen `sections`, Start/Ende, Raummaße, Hinweise und optional `gcode`.

## Geometrie und Abbrand

1. Gesamte Datei an ihrer unteren linken Ecke normalisieren, skalieren und im Raum
   positionieren. Eine ausgewählte Kontur je Datei verwenden. Geschlossene Konturen
   gegen den Uhrzeigersinn orientieren; danach optionale Umkehr und Start-/Endanteile.
2. Konturen an Richtungswechseln aufteilen und die Ecken ab dem gewählten Start
   in Laufrichtung paarweise zuordnen. Zusätzliche kollineare Punkte zählen nicht
   als Ecken (relative Kreuzprodukt-Toleranz 1e-10); Kurvenstützpunkte zählen mit.
   Bei unterschiedlicher Anzahl der Teilabschnitte wird die Planung abgewiesen.
   Nur innerhalb jedes Eckpaars proportional zur jeweiligen Abschnittslänge
   interpolieren: Beide Profile erreichen die nächste Ecke im selben G1-Block.
   Die längere relative Teilstrecke bestimmt die Unterteilung aus der gewünschten
   Mindestanzahl. Eckkoordinaten werden exakt übernommen. Maximal 5999 gemeinsame
   Segmente; bei Überschreitung Geometrie vereinfachen. Diese konservative Zuordnung
   setzt korrespondierende Start-/Endpunkte, Laufrichtungen und Profilunterteilungen
   voraus; eine semantische Erkennung von Formmerkmalen ist nicht implementiert.
3. Zuerst das vollständige **Nennprogramm als strukturierte Bewegungsblöcke** auf der
   Kontur einschließlich gerader Ein-/Ausfahrt erzeugen. Danach Abbrand anwenden:
   Shapely-Polygonbuffer außen positiv/innen negativ, offene Linien mit offset_curve.
   Ecken verwenden Mitre-Verbindungen mit dem Bibliothekslimit. Leere/zerfallene
   Offsets und stark entfernte innere Details werden abgewiesen. Den ursprünglichen
   Anfang auf die korrigierte Kontur projizieren, Start/Endanteile dort anwenden und
   erneut über Eckpaare unterteilen. Auch durch Offsets veränderte Eckanzahlen
   müssen zusammenpassen; andernfalls wird abgebrochen. Erst zum Schluss werden
   die G-Code-Textzeilen geschrieben.
4. Bauteilprofile liegen bei `z_xy` und `z_uv` innerhalb des Achsabstands `span`.
   Der gerade Draht wird linear auf die Achsebenen bei z=0 und z=span extrapoliert.
   Auch dort müssen nominelle und korrigierte Wege inklusive Ein-/Ausfahrt im Raum
   bleiben. Der Raum ist ein Quader mit Ursprung 0/0 und gleicher Breite/Höhe an beiden
   Achsebenen. Alle Konturen der Dateien müssen in den Profilebenen hinein passen;
   die Achsprojektion wird für das ausgewählte Konturpaar geprüft.
5. Nominelle und korrigierte vollständige Profile und tatsächliche Teilschnitte
   werden an 21 Positionen zwischen den Profilebenen auf Überschneidung/Kollaps geprüft.
   Eine konische Form ist zulässig; auf einen Punkt kollabierte Profile sind es nicht.

Ein Auftrag bearbeitet genau ein Konturpaar. Löcher werden durch explizite Wahl
einer Innenkontur mit Ein-/Ausfahrt bearbeitet. Automatische Lochzuordnung,
Auftragsverkettung und Zugangssuche sind nicht implementiert. Ein-/Ausfahrt bleibt
bei der Abbrandkorrektur am benutzerdefinierten Zugangspunkt verankert.

Die Prüfung von 21 Querschnitten ist eine Stichprobe, kein vollständiger Nachweis
der Schneidbarkeit. Thermik, Drahtdurchhang, lokale Schnittgeschwindigkeit,
Neigungsabhängigkeit des Abbrands, Spannmittel und Hindernisse sind nicht modelliert.
Der Abbrandradius gilt konstant in beiden Profilebenen. Er ist ein Mess-/Erfahrungswert.

## G-Code und Vorschau

Die Maschinenparameter enthalten ein statisches SVG-Maschinenmodell in räumlicher
Projektion. Zwei Führungssäulen mit Schlitten und parallelen Grundschienen,
Metallverläufe, Schatten und ein Bodenraster veranschaulichen den Maschinenaufbau.
Ein transparenter gelber Quader markiert den Arbeitsraum, eine orange Linie den
Schneiddraht. Breite X/U liegt entlang der Grundschienen, Höhe Y/V entlang der
Säulen und der Achsebenenabstand zwischen den Maschinenseiten XY und UV.
Reguläre HTML-Zahlenfelder für `width`, `height` und `span`
liegen auf den zugehörigen Maßlinien; Feldnamen, Pflichtangaben und Grenzwerte
bleiben Teil des Auftragsformulars. CSS hebt bei Fokus die jeweilige Maßlinie hervor.
Das illustrative Modell benötigt weder Profile noch eine Berechnung und ist ausdrücklich nicht
maßstabsgetreu: Eingegebene Werte verändern ihre Proportionen nicht. Auf kleinen
Bildschirmen ist nur der Skizzenbereich horizontal scrollbar. Es entstehen keine
zusätzlichen Bibliotheksabhängigkeiten.

Generisches Profil: G21 (mm), G90 (absolut), G94; synchronisierte G1-Sätze mit
X/Y/U/V und konstantem F, M3/S für Leistung und M5/M2 am Ende. F ist als mm/min
entlang des vierdimensionalen Achsvektors definiert. Die Firmware muss diese
Interpretation unterstützen. `S = Leistung / 100 × s_max` nimmt eine lineare
Zuordnung zum Stromregler an; eine Stromregelung wird hier nicht implementiert.
Es gibt bewusst keinen erfundenen S-Maximalwert. Die Oberfläche benötigt ihn und
die Bestätigung des Steuerungsprofils für den Export. Die Startkoordinaten stehen
als Kommentar im Programm und numerisch in der Vorschau: manuell mit ausgeschaltetem
Draht anfahren, bevor der Export ausgeführt wird. Es gibt keine automatische Anfahrt.

Canvas zeigt beide Achsbahnen und die Drahtverbindungen in fester räumlicher
Projektion oder als XY-/UV-Ansicht. Der Schieberegler und die Wiedergabe laufen
durch die Bewegungsblöcke, ohne physikalische Zeitdarstellung. Die Nennbahn lässt
sich zusätzlich anzeigen. Änderungen verwerfen Vorschau und Export; veraltete
asynchrone Antworten dürfen keine aktuellen Ergebnisse überschreiben.

## Bestehende Entscheidungen

- Flask liefert das lokale Grundgerüst und die serverseitigen Templates.
- Beim direkten Start mit `python app.py` bindet der Entwicklungsserver an
  `127.0.0.1:5001`; der Debug-Modus ist ausgeschaltet. Der lokale, mehrthreadige
  Werkzeug-Server bindet den Port vor der optionalen Browseröffnung
  (`--open-browser`). `start.cmd` verwendet diese Option. Port und Host sind
  zentral in `app.py` festgelegt; bei belegtem Port wird der Start abgebrochen.
- Die Versionsnummer wird zentral gepflegt, damit Anzeige und Quellcode zusammenpassen.
- Maschinenmaße und Schnittparameter sind nutzerdefiniert. Demoangaben sind Beispiele.
- Bibliotheksgrundlagen: [ezdxf Path](https://ezdxf.readthedocs.io/en/stable/path.html),
  [svgelements](https://github.com/meerk40t/svgelements),
  [Shapely buffer](https://shapely.readthedocs.io/en/stable/reference/shapely.buffer.html)
  und [offset_curve](https://shapely.readthedocs.io/en/stable/reference/shapely.offset_curve.html).

## Offene Architekturfragen

Mit der Hardwaregruppe sind das tatsächliche Koordinatensystem, G-Code-Dialekt,
Vorschubinterpretation, Stromregler-Anbindung und Kommunikationsschnittstelle
abzustimmen. Der vorhandene Export ist ein konfigurierbarer generischer Entwurf.

Den geplanten Ausbau beschreibt die [Roadmap](ROADMAP.md).
