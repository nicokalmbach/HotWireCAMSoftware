# Änderungshistorie

Änderungen werden während der Entwicklung ergänzt. Einträge unter „Unveröffentlicht“
werden beim nächsten Release der jeweiligen Version zugeordnet. Die Versionsnummer
der Anwendung steht in `version.py`; eine Dokumentationsänderung erfordert allein
keinen Versionswechsel.

## Unveröffentlicht

### 0.2.5

- M3/S mindestens 10 mm vor Materialeintritt: G0 endet am äußeren Einschaltpunkt,
  anschließend G1 mit Schnittvorschub zur Rohteilkante und weiter ins Material.
  Automatisch gewählte Randzugänge erhalten auf beiden Seiten einen parallelen,
  genau 10 mm langen Vorlauf normal zur Rohteilfläche. Weiter außen liegende
  manuelle Zugangspunkte bleiben erhalten; fehlender Abstand wird ergänzt.
- Zugangssuche berücksichtigt Verfahrraum und Erreichbarkeit des Heizpunkts.
  Andere Eintrittsflächen werden bei fehlendem Seitenabstand geprüft; ohne
  Freiraum bleiben Export und Programmwiedergabe gesperrt, die Geometrie sichtbar.
- G-Code-Rückprüfung um den zusätzlichen heißen Luftweg erweitert; Wiedergabe
  und Markierung übernehmen diesen Satz als Heizvorlauf aus dem ausgegebenen
  Code. Keine zusätzliche Aufheizpause oder Temperaturregelung ergänzt.
- Version und betroffene Dokumentation konsistent auf 0.2.5 aktualisiert.
- Prüfung: fünf neue Regressionstests und erweiterter Chrome-Test außerhalb
  der Sandbox bestanden. Insgesamt 58/60 Tests erfolgreich; bekannte Fehler
  `test_partial_contour_start_end` und `test_crossed_wire_surface` bleiben offen.
  Keine Hardwareprüfung.

### 0.2.4

- G-Code-Ein-/Ausfahrt geprüft: Der untersuchte Export enthält M3/S vor der
  Einfahrt und G1 mit Schneidvorschub bis zur Rohteilkante, erst danach M5.
  Der sichtbare Sprung entstand durch die bisherige Anzeige eines Satzendpunkts
  je Animationsschritt, auch bei langen Ein-/Ausfahrtsätzen.
- Eigenen Postprozessor-Ausgang vor Export rücklesen und gegen freigegebene
  Positionen, G0/G1, F, S und Heizstatus prüfen. Manipulierte oder inkonsistente
  Ausgaben verhindern den Export. Kein allgemeiner Maschinen-G-Code-Interpreter.
- Programmwiedergabe aus genau diesen rückgelesenen Sätzen statt aus separaten
  Planungsstützpunkten. Kontinuierliche G1-Bewegung nach ausgegebenem F, auch
  innerhalb der Ein-/Ausfahrt; M3/M5 und Codezeile sichtbar. Draht orange bei
  angeforderter Heizleistung, blau bei ausgeschalteter Leistung.
- G1-Wiedergabe 1×/10×/50×; G0 ausdrücklich schematisch mit 1 s je nicht leerem
  Satz. Ohne S-Zuordnung dieselbe interne Vorlage ohne erfundenen Hardware-S-Wert;
  ohne freie Anfahrt nur Geometrie ohne Programmwiedergabe. Keine Thermik- oder
  Beschleunigungssimulation.
- Version und betroffene Dokumentation auf 0.2.4 aktualisiert.
- Prüfung: acht neue Python-Tests und erweiterter Chrome-Test außerhalb der
  Sandbox bestanden. Insgesamt 53/55 Tests erfolgreich; bekannte Fehler
  `test_partial_contour_start_end` und `test_crossed_wire_surface` bleiben offen.
  Keine Hardwareprüfung.

### 0.2.3

- Maschinen-, Rohteilnullpunkt und Schnittstart getrennt. Kontaktschalter setzen
  Y/V unten und X/U auf der positiven Seite; Standard ist +Raumbreite/2, eine
  frühere tatsächliche positive Schalterlage ist je X/U einstellbar. Vorschau
  und Profilfelder bleiben im mittigen Planungsraum; Exportkoordinaten werden
  um die Schalterlage versetzt.
- Jeder Export beginnt am Maschinennullpunkt X0/Y0/U0/V0 und fährt mit M5/G0
  ohne Schneidvorschub zum Schnittstart. Erst danach M3/S und G1 mit F.
- Automatische Ein-/Ausfahrt ausschließlich oben oder seitlich. Die aufliegende
  Unterseite samt unteren Ecken ist auch für manuelle Randzugänge gesperrt.
  Kaltanfahrt zur gegenüberliegenden Seite führt über den Block. Jede schnelle
  Teilbewegung bleibt mit ihrer gesamten Achskoordinatenhülle außerhalb des Rohteils.
- Ohne freie Kaltanfahrt oder außen liegenden Austritt bleibt die geometrische
  Schnittvorschau verfügbar, der Export jedoch gesperrt. Das gilt auch für
  innere Einfädelpunkte ohne von außen erreichbaren Zugang.
- Version, Bedienhinweise, Architektur und Versionsverlauf auf 0.2.3 aktualisiert.
- Prüfung: fünf neue Regressionstests und erweiterter Chrome-Browsertest
  außerhalb der Sandbox bestanden. Insgesamt 45/47 Tests erfolgreich; die
  bekannten Fehler `test_partial_contour_start_end` und
  `test_crossed_wire_surface` bleiben offen. Keine Hardwareprüfung.

### 0.2.2

- Profile im XY-/UV-Seitenschnitt per Maus/Touch oder Pfeiltasten verschiebbar.
  Zentren der gesamten Dateiausdehnungen bleiben für beide Seiten gekoppelt,
  auch bei verschiedenen Dateien und Skalierungen, Import und Zentrierung.
- Sofortige rote Blockwarnung und automatische vollständige Planungsprüfung
  nach 250 ms Eingabepause; grünes Feedback erst nach Servererfolg. Laufende
  Live-Anfragen werden abgebrochen und alte Antworten per Revision verworfen.
- Automatische kurze Randzugänge zu den eingestellten Konturstarts/-enden,
  für Nenn-/Abbrandbahn und 21 Zwischenquerschnitte auf Durchquerung geprüft.
  Der gesamte heiße Weg muss im Block bleiben. Manuelle Innenzugänge bleiben erhalten.
- Kaltanfahrt ab gesetztem Nullpunkt entlang freier Blockkanten blau gestrichelt
  dargestellt und als G1 mit M5 vor M3/S exportiert. Keine Referenzfahrt,
  Maschinenanbindung, globale Startpunktoptimierung oder Prüfung von Spannmitteln.
- Versionsnummer und betroffene Dokumentation konsistent auf 0.2.2 aktualisiert.
- Prüfung: sechs neue Planungstests erfolgreich; insgesamt 40/42 Tests bestanden.
  Die beiden bekannten Fehler `test_partial_contour_start_end` und
  `test_crossed_wire_surface` bestehen weiterhin. Erweiterter Chrome-Browsertest
  außerhalb der Sandbox bestanden, einschließlich Block-/Abbrandfeedback und
  verspäteter Live-Antworten. Keine Hardwareprüfung.

### 0.2.1

- SVG-Kreis-/Kurvenplanung korrigiert: echte Ecken aus ursprünglichen
  Segmentübergängen von Kurvenstützpunkten unterschieden. Unterschiedlich große
  Kreise benötigen keine identische Unterteilung mehr; Kurvenauflösung bleibt
  auch bei geringer angeforderter Segmentzahl erhalten. Eckinformationen werden
  durch Teilschnitt und Abbrand geführt; volle Runden exakt geschlossen.
- Sechs Regressionstests für 100-/200-mm-Kreise (SVG-Kreis und Bogenpfad),
  Teilschnitte, Innen-/Außenkorrektur, gemischte und offene Bezierkonturen,
  echte Eckanzahlfehler, API-Import/Export und ungültige Eckdaten ergänzt.
  Prüfung: 34 von 36 Tests bestanden, alle neuen Tests erfolgreich. Die beiden
  bereits vor der Änderung reproduzierten Fehler in `test_partial_contour_start_end`
  und `test_crossed_wire_surface` bleiben offen. Keine Hardwareprüfung.
- Versionsstand für die direkte Arbeitsraumvorschau auf 0.2.1 angehoben;
  Projekteinstieg, Versionsverlauf und Installationshinweise aktualisiert.
- Arbeitsraumansicht direkt bei den Blockeingaben ergänzt: Block erscheint
  sofort mit Breite, Höhe, Länge und Abständen. SVG/DXF lassen sich dort wählen
  oder auf die Ansicht ziehen; Zentrierung und Profilpositionen wirken direkt.
- Konturentwurf und geprüfte Bahn getrennt dargestellt. Berechneter Drahtweg
  erscheint an den Blockstirnflächen mit Start/Ende, Ein-/Ausfahrt und Pfeilen;
  Regler und Wiedergabe zeigen den Draht zwischen den Führungen.
- Erweiterter UI-Test mit Chrome außerhalb der Sandbox bestanden: Live-Block,
  Maßlinien und Abstandsänderungen, Drop-Import, Zentrierung, Live-Profilposition,
  Raumwarnung und Zugangsmarkierungen sowie bestehende Planung/Export-Funktionen.
  Browserwahl `--browser chrome` ergänzt; keine neue Laufzeitabhängigkeit.

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
