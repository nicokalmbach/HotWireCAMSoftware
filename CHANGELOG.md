# Änderungshistorie

Änderungen werden während der Entwicklung ergänzt. Einträge unter „Unveröffentlicht“
werden beim nächsten Release der jeweiligen Version zugeordnet. Die Versionsnummer
der Anwendung steht in `version.py`; eine Dokumentationsänderung erfordert allein
keinen Versionswechsel.

## Unveröffentlicht

- Eckpaare beider Profile werden in Laufrichtung im selben XYUV-Block erreicht;
  Interpolation erfolgt abschnittsweise statt über die gesamte Konturlänge.
  Dies gilt für Nennbahn, Abbrandbahn und die geometrischen Prüfungen.
- Unterschiedliche Anzahlen von Richtungswechseln werden mit Hinweis auf
  Start/Ende, Richtung und Unterteilung abgewiesen; Kurvenstützpunkte zählen mit,
  kollineare Zusatzpunkte nicht. Regressionstests für Eckpaare und Export ergänzt.
- Lokaler Gesamttest weiterhin beim Shapely-Import durch die Windows-
  Anwendungssteuerungsrichtlinie blockiert.

## 0.1.1

Projektstand ohne Behauptung eines bereits veröffentlichten GitHub-Releases.

### Debian-Installation und Versionierung

- Debian-13-LXC-Erstinstaller mit übernehmbaren Standardwerten, eigenem Benutzer
  `wyro`, GitHub-Download, Python-Umgebung und Gunicorn/systemd-Dienst ergänzt.
- Installationsmetadaten und Git-Commit als Vorbereitung eines späteren
  Update-Scripts gespeichert; bestehende Installationen werden nicht überschrieben.
- Linux-Anfängeranleitung mit kopierbaren Befehlen, Betrieb und Fehlerdiagnose.
- `timeline.md` mit Einträgen für 0.1.0 und 0.1.1 eingeführt; Versionsnummer und
  betroffene Projektdokumentation auf 0.1.1 aktualisiert.
- Linux-Scripte und Dienstvorlagen erhalten über `.gitattributes` LF-Zeilenenden.
- Vollständige Installation in einem Debian-13-LXC-Container noch nicht geprüft.

- Diagnose der Windows-Blockierung der Shapely-/GEOS-DLL in
  `TROUBLESHOOTING.md` dokumentiert; Ursache des geänderten Zulassungsverhaltens
  und Lösung sind noch offen.

### Behoben

- Die Seitennavigation hebt beim Anklicken und Scrollen den aktuellen Bereich
  hervor; die Markierung bleibt nicht mehr dauerhaft beim Profilimport.

### Lokaler Start

- Einheitlicher Standardport 5001 für die aktuelle lokale Anwendung.
- Windows-Starter `start.cmd` und `app.py --open-browser` öffnen nach
  erfolgreicher Portbindung automatisch die passende Adresse im Browser.
  Bei belegtem Port bricht der Start ab.

### Ergänzt

- Zwei SVG-/DXF-Dateien mit Konturauswahl und Einheitenumrechnung importieren.
- Nutzerdefinierter Schneidraum, Lage der Profilebenen, Positionierung, Skalierung,
  Start-/Endpunkte und Laufrichtung für XY und UV.
- Gemeinsame Liniensequenzen mit Erhalt der Ecken für unterschiedliche Profile.
- Vollständiges Nennprogramm vor nachgelagerter Abbrandkorrektur; Außen-/Innenkonturen,
  offene Links-/Rechtswege und Lochwerkzeug mit geradliniger Ein-/Ausfahrt.
- Raum- und Achsprojektionsprüfung, Kollaps-/Überschneidungsprüfung mit 21 Zwischenquerschnitten.
- Canvas-Drahtmodell mit XY-/UV-Ansicht, Schrittregler und Bewegungswiedergabe.
- Generischer XYUV-G-Code-Export mit konfigurierbarer Prozentleistung über M3/S;
  reale Stromregelung und Firmware-Zuordnung bleiben Hardwareaufgaben.
- Demogeometrie, SVG-Beispieldateien sowie automatisierte Import-, Geometrie-, API-
  und optionale Edge-Browserprüfungen. Änderungen verwerfen veraltete Exporte.
- Geometrie-Abhängigkeiten ezdxf, svgelements und Shapely.
- Technische Dokumentation für Architektur, Installation, Fehlerbehebung und Roadmap.
- Arbeitsregeln zur begleitenden Dokumentationspflege in `AGENTS.md`.
- `.gitignore` um IDE-Einstellungen, temporäre Dateien, lokale
  Umgebungskonfigurationen und weitere Test-Caches ergänzt; `.env.example`,
  `.env.sample` und `.env.template` bleiben versionierbar.

## Ursprünglicher Grundstand: 0.1.0

Ein Veröffentlichungsdatum ist bisher nicht dokumentiert. Dieser Abschnitt beschreibt
den vorhandenen Implementierungsstand.

- Lokal startbare Flask-Anwendung mit deutschsprachiger Oberfläche.
- Platzhalter für Profilimport, Profileinstellungen, Schneidvorschau und G-Code-Export.
- Zentrale Versionsnummer mit Anzeige in der Fußzeile.
- Noch keine Achsensteuerung, Maschinenkommunikation oder G-Code-Erzeugung.
