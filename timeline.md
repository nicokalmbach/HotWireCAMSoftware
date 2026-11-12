# Versionsverlauf

Für jede neue Version einen eigenen Eintrag mit den tatsächlich durchgeführten
Änderungen ergänzen und `version.py`, Changelog und betroffene Anleitungen im
selben Arbeitsschritt aktualisieren. Eine Versionsnummer dokumentiert den
Projektstand; ein GitHub-Release oder Tag ist dadurch nicht automatisch erstellt.

## 0.2.5

- Einschalten der Heizung mindestens 10 mm vor Materialeintritt implementiert.
  Bei automatischen Randzugängen gemeinsamer Einschaltpunkt 10 mm normal
  außerhalb der Rohteilfläche, dann G1 mit Schnittvorschub über die Luftstrecke
  zur Kante und weiter zur Kontur. G0 endet am Einschaltpunkt; dort M3/S vor G1.
- Manuelle Außenzugänge behalten größere Abstände bei; nur fehlender Freiraum
  bis mindestens 10 mm wird ergänzt. Verfahrraum und freie Kaltanfahrt geprüft,
  alternative automatische Eintrittsseiten bevorzugt. Ohne passenden Freiraum
  bleibt der Entwurf sichtbar, Export und Programmwiedergabe sind gesperrt.
- Äußeren Heizvorlauf getrennt vom Materialweg als `heat_lead` geführt und als
  zusätzlichen G1-Satz rückgeprüft. Wiedergabe übernimmt die neue Phase aus dem
  ausgegebenen Code; Einschaltpunkt und Luftweg markiert. Keine zusätzliche
  Aufheizpause, Temperaturregelung oder Hardwareparameter erfunden.
- Version, Bedienhinweise, Architektur und betroffene Anleitungen aktualisiert.
  Kein Release oder Tag angelegt.
- Prüfung: fünf neue Tests für 10 mm je Blockseite im ausgegebenen Code,
  oberen Eintritt bei fehlendem Seitenabstand, Exportsperre ohne Freiraum,
  manuelle Abstände und Rückprüfung bei entferntem Heizvorlauf bestanden.
  Insgesamt 58/60 Tests erfolgreich; die bekannten Fehler
  `test_partial_contour_start_end` und `test_crossed_wire_surface` bleiben offen.
  Erweiterter Chrome-Test mit Heizvorlauf, M3/G1 und Zwischenpositionen vor
  Materialeintritt außerhalb der Sandbox bestanden. Keine Hardwareprüfung
  oder LXC-Installation durchgeführt.

## 0.2.4

- Ausgegebenen Beispiel-G-Code zuerst geprüft: M3/S vor der Einfahrt,
  G1 mit F für Einfahrt/Kontur/Ausfahrt und M5 erst danach bereits vorhanden.
  Sichtbaren Sprung auf die bisherige Satzendpunkt-Wiedergabe zurückgeführt.
- `nc_program.py` ergänzt: eigenen Text rücklesen und Achspositionen,
  Bewegungsanzahl, G0/G1, F, S, M3/M5 und Programmende gegen die freigegebene
  Planung prüfen. Falscher Postprozessor-Ausgang verhindert den Download.
- Rückgelesene Satzfolge als `program` an den Browser übergeben. `program.js`
  interpoliert Positionen innerhalb eines Satzes und verwendet für G1 die
  ausgegebene XYUV-Weglänge und F. Kaltanfahrt, heiße Ein-/Ausfahrt und Kontur
  werden mit M3/M5-Zustand und zugehöriger G-Code-Zeile wiedergegeben.
- G1-Anzeigefaktoren 1×/10×/50× und ausdrücklich schematische G0-Anzeigezeit
  von 1 s je nicht leerem Satz ergänzt. Angeforderte Heizleistung orange, Leistung
  aus blau; M3 mit S0 wird nicht als positive Heizleistung dargestellt.
- Ohne S-Zuordnung interne Vorlage desselben Postprozessors ohne Hardware-S-Wert
  rückgelesen, ohne freien Zugang nur statische Geometrie. Keine Aufheiz-,
  Thermik- oder Beschleunigungssimulation ergänzt.
- Versionsnummer und betroffene Dokumentation konsistent aktualisiert.
  Kein Release oder Tag angelegt.
- Prüfung: acht neue Python-Tests für heiße Ein-/Ausfahrt, lückenlose Positionen,
  manipulierte Bewegungen/Vorschübe/Heizleistung, ungültige Modi, Vorschauvorlage,
  Leistung 0 und API-Exportsperre bestanden; insgesamt 53/55 erfolgreich.
  Die bekannten Fehler `test_partial_contour_start_end` und
  `test_crossed_wire_surface` bleiben offen. Erweiterter Chrome-Test mit
  Zwischenpositionen, G1-Zeitverlauf, M3/M5 und Exportzeilen außerhalb der Sandbox
  bestanden. Zwischenposition in der heißen Ausfahrt auch im Canvas visuell
  kontrolliert. Der untersuchte Beispiel-Export blieb gegenüber der ersten
  Prüfung textgleich. Keine Hardwareprüfung oder LXC-Installation durchgeführt.

## 0.2.3

- Maschinennullpunkt aus den Kontaktschaltern von Rohteilnullpunkt, mittigem
  Planungsraum und Schnittstart getrennt. X/U-Schalter positiv (Standard
  +Raumbreite/2, tatsächliche positive Lage bei Bedarf einstellbar), Y/V unten
  auf Auflagehöhe. Maschinenkoordinaten für den Export um die Schalterlage versetzt.
- Jeden Export auf Start X0/Y0/U0/V0 am zuvor gesetzten Maschinennullpunkt und
  Kaltanfahrt mit M5/G0 umgestellt; danach M3/S und G1 mit Schneidvorschub.
- Unterkante und beide unteren Ecken als Ein-/Austritt gesperrt. Automatische
  Zugänge nur seitlich oder oben; manuelle Randpunkte an der Unterseite ebenfalls
  abgewiesen. G0-Route außen beziehungsweise über das aufliegende Rohteil gesucht;
  die gesamte Achskoordinatenhülle jeder Teilbewegung wird berücksichtigt.
- Schnittvorschau und Exportsperre getrennt: blockierter Maschinenstart,
  innere Einfädelpunkte ohne freien Zugang und im Material endende Wege liefern
  keinen Export ab Maschinennullpunkt. Vorschau zeigt getrennte Nullpunkte und
  aktuelle Planungs-/Maschinenkoordinaten.
- Version und betroffene Dokumentation konsistent aktualisiert. Kein Release
  oder Tag angelegt.
- Prüfung: fünf neue Regressionstests bestanden, insgesamt 45/47 Tests erfolgreich.
  Die bekannten Fehler `test_partial_contour_start_end` und
  `test_crossed_wire_surface` bleiben offen. Erweiterter Chrome-Browsertest
  außerhalb der Sandbox bestanden: getrennte Nullpunkte, G0 vor Heizung,
  Koordinatenumrechnung und Sperre einer durch das Rohteil führenden Anfahrt
  einschließlich bestehender Platzierungs-/Import-/Exportprüfungen.
  Keine Hardwareprüfung oder LXC-Installation durchgeführt.

## 0.2.2

- Seitenschnitte um direktes Ziehen und Tastaturverschiebung (1 mm / Umschalt
  10 mm) ergänzt; Abbildung während des Ziehens stabil gehalten. Dateizentren
  beider Seiten sind auch bei verschiedener Skalierung und getrennten Dateien
  gekoppelt. Profilfelder, Import und Zentrierung verwenden dieselbe Kopplung.
- Sofortige Blockgrenzenwarnung und automatische Serverprüfung nach 250 ms
  Eingabepause mit gültig/ungültig-Rückmeldung und neuem vollständigem Drahtweg.
  Alte Vorschauen/Exporte werden verworfen, laufende Live-Anfragen abgebrochen
  und verspätete Antworten durch einen Revisionszähler abgefangen.
- Automatische Ein-/Ausfahrt am Blockrand mit kurzen geraden Verbindungen zu
  bestehenden Konturstarts/-enden implementiert. Zugangskandidaten werden auf
  Nenn- und Abbrandkontur in 21 Zwischenquerschnitten gegen vorzeitige Durchquerung
  geprüft. Heißer Weg bleibt einschließlich Abbrand vollständig im Block.
  Innenkonturen verwenden weiterhin manuelle Zugangspunkte.
- Kaltanfahrt vom gesetzten Nullpunkt entlang des Blockrands als separate
  blaue Vorschau und im G-Code mit M5 vor dem Einschalten der Heizung ergänzt.
  Blockkanten müssen tatsächlich frei zugänglich sein; Auflage/Spannmittel,
  Referenzfahrt und Maschinenkommunikation sind nicht implementiert.
- Version und betroffene Anleitungen aktualisiert. Kein Release oder Tag angelegt.
- Prüfung: alle sechs neuen Planungstests bestanden; insgesamt 40/42 erfolgreich.
  Die bekannten Fehler `test_partial_contour_start_end` und
  `test_crossed_wire_surface` bleiben offen. Erweiterte Chrome-Prüfung außerhalb
  der Sandbox erfolgreich: gekoppeltes Ziehen/Tastatur/Skalierung, Block- und
  Abbrandfeedback, alte Live-Antworten, automatischer Randzugang/Kaltanfahrt und
  bestehende Import-/Export-/Innenkonturfunktionen. Canvas-Geometrie visuell
  kontrolliert. Keine Hardwareprüfung oder LXC-Installation durchgeführt.

## 0.2.1

- SVG-Import um echte Eckinformationen aus den ursprünglichen Segmenten erweitert.
  Kreise mit 100 und 200 mm Durchmesser sowie unterschiedlich abgetastete
  SVG-Kurven werden entlang ihrer Abschnittslängen synchronisiert. Kurvenstützpunkte
  bleiben in der gemeinsamen Bahn erhalten; echte Ecken werden weiterhin gekoppelt,
  auch nach Abbrand. Konturschluss vollständiger Runden numerisch stabilisiert.
- Sechs neue automatisierte Tests einschließlich Upload bis G-Code, Kreis-/Bogenpfad,
  Teilschnitt, Innen-/Außenoffset und offenen/gemischten Bezierkonturen bestanden.
  Gesamtprüfung: 34/36 erfolgreich. Die bereits vor der Änderung reproduzierten
  Fehler `test_partial_contour_start_end` und `test_crossed_wire_surface` bestehen
  weiterhin. DXF-Kurven ohne SVG-Eckinformationen bleiben bei der bisherigen
  Stützpunktzuordnung. Keine Hardware- oder neue Browserprüfung durchgeführt.
- Versionsnummer auf 0.2.1 gesetzt und den Fortschritt der direkten
  Arbeitsraumvorschau dieser Version zugeordnet. 0.2.0 bleibt als Stand der
  mittigen Werkstückausrichtung erhalten. Kein Release oder Tag angelegt.
- Arbeitsraumansicht unter den Blockeingaben aufgebaut: maßstäblicher Block
  samt Maßlinien für drei Maße, beide Achsebenenabstände, X/U-Freiraum und
  Abstand nach oben erscheint ohne Profil oder Planungsauftrag.
- SVG/DXF direkt in der Ansicht per Dateiauswahl oder Drag-and-drop einfügen;
  Zentrierung in X/U und Y/V anhand der gesamten Datei. Live-Änderungen über
  Positions-/Skalierungsfelder, Hervorhebung der Konturauswahl und Raumhinweis.
- Berechnete Schnittwege auf den Blockstirnflächen, dünne Führungsbahnen,
  Start/Ende und Ein-/Ausfahrt mit Richtungspfeilen sowie aktuelle Drahtposition
  dargestellt. Änderungen erhalten den Entwurf und verwerfen die geprüfte Bahn.
- Live-Zeichnung in `static/js/workspace.js` ausgelagert. Erweiterter Chrome-
  Browsertest außerhalb der Sandbox bestanden, einschließlich Drop-Import,
  Sofortbemaßung, Positionierung, Zugangspunkten und bestehendem Exportablauf.
  Gezeichnetes Canvas zur Kontrolle angesehen; keine Hardwareprüfung.

## 0.2.0

- Mittige Werkstückausrichtung umgesetzt: Blockbreite X/U, Blockhöhe Y/V und
  Blocklänge zwischen den Drahtführungen sind Pflichtangaben. Beide Stirnflächen
  werden automatisch symmetrisch zwischen den Achsebenen angeordnet.
- X/U-Koordinaten reichen von −Raumbreite/2 bis +Raumbreite/2; Y/V beginnt
  auf der Auflageebene bei 0. Raumprüfung, Planung, G-Code und Canvas-Vorschau
  angepasst; Blockstirnflächen und Mittellinie dargestellt. Demowerte angepasst.
- Nennkonturen aller Dateien müssen in den Block passen; Abbrand und Zugänge
  dürfen über den Block hinausreichen, solange die Achswege im Maschinenraum bleiben.
- Nullpunktsetzen per Kontaktschalter mit manuellem Anfahren über Pfeiltasten
  der Maschinensteuerung dokumentiert. Schalterlage bzw. Schalterversatz muss
  zum zentralen X/U-Nullpunkt passen. Keine Maschinenanbindung implementiert.
- Versionsnummer, Projekteinstieg, Architektur, Roadmap und betroffene
  Installations- und Fehlerhinweise konsistent aktualisiert.
- Regressionstests für automatische Abstände, negative Koordinaten, beidseitige
  Raumgrenzen und Blockvalidierung ergänzt; UI-Test auf neue Eingaben umgestellt.

Prüfstand: 28 von 30 automatisierten Tests bestanden, einschließlich aller neuen
Tests. Zwei bereits im unveränderten Git-Stand
reproduzierbare Fehler bleiben offen: `test_partial_contour_start_end`
(unterschiedliche Eckanzahl im Teilschnitt) und `test_crossed_wire_surface`
(erwartete Abweisung erfolgt nicht). Edge lieferte bei der Browserprüfung
keinen auswertbaren DOM-Bericht; zusätzlich trat ein Fehler beim Aufräumen
des Browserprofils auf. Keine Hardwareprüfung oder LXC-Installation durchgeführt.

## 0.1.1

- Räumliche Maßeingabe nach visueller Vorlage zu einem illustrativen Maschinenmodell
  mit Metalloberflächen, Führungssäulen, Grundschienen, Schlitten und Schneiddraht
  überarbeitet. Transparenter gelber Arbeitsraum, heller Rasterboden und weiße
  Maßlinien mit direkt editierbaren Eingabekarten ergänzen die Anschauung.
  Desktopdarstellung visuell geprüft; bestehender Edge-Browsertest einschließlich
  Maßeingabe, mobilem Layout, Planung und Export außerhalb der Sandbox erneut bestanden.
- Schematische räumliche Schneidraumskizze mit Eingabefeldern direkt auf den
  Maßlinien für Breite, Höhe und Achsebenenabstand ergänzt. XY-/UV-Ebenen und
  Achsen beschriftet, Fokusmarkierung und horizontales Scrollen auf kleinen
  Bildschirmen umgesetzt; bestehende Formularwerte und Validierung weiterverwendet.
  Erweiterter Edge-Browsertest außerhalb der Sandbox erfolgreich, einschließlich
  mobiler Darstellung, Maßeübergabe, Planung und Export; Desktopansicht visuell geprüft.
- Maschinenparameter und Bezugspunkte vor den Profilimport verschoben;
  Navigation und Schrittnummern angepasst, Berechnung hinter den Profileingaben.
- Veraltete HTML-Ausgabe der laufenden lokalen Instanz auf Port 5001 diagnostiziert;
  Neustarthinweis für HTML-Vorlagen in Installation und Fehlerbehebung ergänzt.
  Projektinstanz neu gestartet; Checkbox anschließend in der HTTP-Antwort bestätigt.
- Option „Dieses Profil für beide Seiten verwenden“ bei der XY-Eingabe ergänzt.
  Datei und Kontur werden für UV übernommen, weitere Einstellungen bleiben
  getrennt; ein vorheriges UV-Profil bleibt beim Abwählen verfügbar.
  Edge-Browsertest um Übernahme, Konturwechsel und Wiederherstellung erweitert
  und erfolgreich außerhalb der Sandbox ausgeführt.
- Bestätigungstext zum Steuerungsprofil präzisiert: XYUV und G21/G90/G94
  betreffen die Bewegung; M3/S und M5 steuern die Heizleistung.
- Eckensynchronisierung korrigiert: korrespondierende Richtungswechsel werden
  abschnittsweise gekoppelt und gemeinsam erreicht, auch auf der Abbrandbahn.
  Unpassende Eckanzahlen werden abgewiesen; kollineare Zusatzpunkte ignoriert.
  Regressionstests für unterschiedliche Seitenlängen, offene Konturen,
  unpassende Eckfolgen und gemeinsame G-Code-Eckblöcke ergänzt.

- Debian-13-LXC-Erstinstaller mit interaktiven Vorschlägen für GitHub-Repository,
  Branch/Tag, eigenen Benutzer (Standard `wyro`), Pfad, Bind-Adresse und Port.
- Automatischer Download des Repositorys samt Dienstvorlage; Python-Umgebung,
  Linux-Abhängigkeiten und Gunicorn, App-Import, Tests und lokaler HTTP-Starttest.
- systemd-Dienst mit Autostart und Betrieb als eigener Benutzer statt root.
- Installationseinstellungen und Git-Commit als Grundlage für spätere Updates;
  vorhandene Installationen werden nicht überschrieben. Update-Script noch offen.
- Anleitung für Linux-Anfänger mit kopierbaren Installations-, Betriebs- und
  Diagnosebefehlen; Linux-Scriptdateien mit LF-Zeilenenden.
- CAM-Erweiterungen gegenüber dem ursprünglichen 0.1.0-Grundstand: SVG-/DXF-Import,
  Profilbearbeitung, gemeinsame XYUV-Wege, Abbrandkorrektur, Raum- und
  Zwischenquerschnittsprüfung, Drahtvorschau und generischer G-Code-Export.
- Demoprofile und automatisierte Import-, Planungs-, API- und optionale Browsertests.
- Windows-Starter mit Browseröffnung und Standardport 5001; aktive Seitennavigation.
- Diagnose der Windows-Smart-App-Control-Blockierung der GEOS-DLL dokumentiert.

Prüfgrenze: Keine vollständige Installation unter Debian 13 LXC in dieser
Entwicklungsumgebung. Shell-Syntax, Konfigurationseingaben und Dienstplatzhalter
geprüft; CAM-Tests unter Windows durch die Anwendungsrichtlinie beim NumPy-Import
blockiert. Keine Aussage über einen bereits veröffentlichten Release.

## 0.1.0

- Flask-Grundgerüst und deutschsprachige Website mit Navigation und Gestaltung.
- Zentrale Versionsnummer mit Anzeige in der Fußzeile.
- Import, Planung und Export im ursprünglichen Grundstand als Platzhalter.
- Projekt-, Installations-, Architektur-, Fehlerbehebungs- und Planungsdokumentation.

Ein Veröffentlichungsdatum ist für diesen Grundstand nicht dokumentiert.
