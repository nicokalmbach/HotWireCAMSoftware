# Versionsverlauf

Für jede neue Version einen eigenen Eintrag mit den tatsächlich durchgeführten
Änderungen ergänzen und `version.py`, Changelog und betroffene Anleitungen im
selben Arbeitsschritt aktualisieren. Eine Versionsnummer dokumentiert den
Projektstand; ein GitHub-Release oder Tag ist dadurch nicht automatisch erstellt.

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
