# Änderungshistorie

Änderungen werden während der Entwicklung ergänzt. Einträge unter „Unveröffentlicht“
werden beim nächsten Release der jeweiligen Version zugeordnet. Die Versionsnummer
der Anwendung steht in `version.py`; eine Dokumentationsänderung erfordert allein
keinen Versionswechsel.

## Unveröffentlicht

### 0.2.0

- Blockbreite, Blockhöhe und Blocklänge ersetzen die manuell eingegebenen
  Profilebenen. Der Block steht mittig in X/U und zwischen den Achsebenen.
  Gleiche Abstände je Seite werden automatisch berechnet und angezeigt.
- X/U-Nullpunkt in die Verfahrwegmitte verlegt; Y/V = 0 liegt auf der
  Auflageebene. Planung, Raumprüfung, Vorschau und G-Code verwenden diese Lage.
  Alle Nennkonturen werden gegen die Blockmaße geprüft; Blockstirnflächen und
  Mittellinie sind in der berechneten Vorschau markiert. Demo angepasst.
- Kontaktschalter und manuelles Anfahren per Pfeiltasten als Maschinenablauf
  beschrieben. Maschinenanbindung, Schalterauswertung und Tastatur-Jogging
  bleiben offen; der Hardware-Meilenstein ist damit noch nicht vollständig.
- Versionsnummer und betroffene Anleitungen auf 0.2.0 aktualisiert.
- Regressionstests für Zentrierung, negative Koordinaten, Raumgrenzen und
  ungültige Blockmaße ergänzt; Browserprüfungen an die neuen Felder angepasst.
- Prüfung: 28 von 30 automatisierten Tests bestanden, einschließlich aller
  neuen Tests. Zwei Fehler auch im unveränderten Git-Stand reproduziert
  (Teilschnitt/Eckzuordnung und erwartete Abweisung einer Drahtfläche).
  Edge-Browserprüfung ohne auswertbaren DOM-Bericht; Darstellung nicht abschließend geprüft.

### Bisherige Änderungen im Entwicklungsstand 0.1.1

- Schneidraumansicht nach visueller Vorlage als anschaulicheres Maschinenmodell
  überarbeitet: metallische Führungssäulen, Grundschienen, Schlitten, orangefarbener
  Schneiddraht und transparent gelber Arbeitsraum auf hellem Rasterboden.
  Weiße Maßlinien mit hellen Eingabekarten zeigen X/U entlang der Grundschienen,
  Y/V entlang der Säulen und den Abstand zwischen XY- und UV-Seite.
  Desktopansicht visuell geprüft; Edge-Browsertest für Maßeingabe, mobiles Layout,
  Planung und Export erneut außerhalb der Sandbox erfolgreich ausgeführt.
- Räumliche Schneidraumskizze bei den Maschinenparametern ergänzt: Eingaben für
  Breite X/U, Höhe Y/V und Achsebenenabstand liegen direkt auf den Maßlinien.
  Fokus hebt das jeweilige Maß hervor; auf kleinen Bildschirmen ist die Skizze
  horizontal scrollbar. Darstellung schematisch, bereits ohne Profilimport sichtbar.
  Edge-Browsertest einschließlich mobiler Darstellung und Übergabe der Maße an
  die Planung erfolgreich außerhalb der Sandbox ausgeführt; Desktopansicht visuell geprüft.
- Seitenablauf umgestellt: Maschinenparameter, Profilebenen und Ein-/Ausfahrtspunkte
  stehen vor dem Profilimport. Navigation und Schrittnummern folgen dieser
  Reihenfolge; die Berechnung bleibt hinter den Profileingaben.
- Hinweise zum lokalen Aktualisieren korrigiert: Auch geänderte HTML-Vorlagen
  benötigen beim laufenden Server ohne Debug-Modus einen Neustart.
- Checkbox bei der ersten Profileingabe ergänzt: XY-Datei und Konturauswahl
  auch für UV verwenden; übrige Profileinstellungen bleiben getrennt.
  Beim Abwählen wird ein zuvor geladenes UV-Profil wieder angezeigt.
  Übernahme, Konturwechsel und Wiederherstellung im Edge-Browsertest geprüft.
- Bestätigung des Steuerungsprofils verständlicher formuliert: unterstützte
  Achsen und G-Code-Modi von der Ansteuerung der Heizleistung unterschieden.
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
