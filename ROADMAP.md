# Roadmap

Die Anwendung trägt Version `0.2.5`. Sie berechnet bereits synchronisierte
Vierachs-Drahtwege, erzeugt XYUV-G-Code und gibt den eigenen Export in der
Vorschau wieder. Eine Verbindung zur Maschine, reale Achsbewegungen und
Referenzfahrten sind noch nicht implementiert.

Die künftigen Versionsziele sind auf diesen Stand abgestimmt. Es sind geplante
Meilensteine ohne festgelegte Termine; Schnittstelle und Zuständigkeiten müssen
mit der Hardwaregruppe abgestimmt werden. Die Versionsnummer wird durch diese
Planungsänderung nicht erhöht.

## Bisheriger Stand bis 0.2.5

Die Einträge bis 0.2.0 enthalten auch die ursprünglichen Hardwareziele. Ihre
offenen Anteile werden in der künftigen Planung ab 0.3.0 weitergeführt.

| Zielversion | Schwerpunkt | Stand |
| --- | --- | --- |
| 0.1.0 | Projektstruktur und eine Achse | Grundgerüst vorhanden; Achsensteuerung offen |
| 0.1.1 | CAM-Stand und Debian-LXC-Installation | CAM und Installer implementiert; vollständige LXC-Installation noch zu prüfen |
| 0.2.0 | Referenzschalter und zentriertes Werkstück | CAM-Koordinaten und automatische Blockabstände umgesetzt; Schalterauswertung und Tastatursteuerung offen |
| 0.2.1 | Direkte Arbeitsraumvorschau | Live-Block mit Bemaßung, Direktimport und zentrierten Profilen sowie Darstellung des vollständigen berechneten Drahtwegs umgesetzt |
| 0.2.2 | Platzierung und Randzugang | Gekoppelte Profilzentren, Ziehen im Seitenschnitt, automatische Geometrieprüfung, vollständiger heißer Weg im Block und Kaltanfahrt im Export umgesetzt; keine Hardwareprüfung |
| 0.2.3 | Maschinenbezug und aufliegendes Rohteil | G0 ab Kontaktschalter-Maschinennullpunkt, getrennte Bezugspunkte und Zugänge nur oben/seitlich; Unterseite gesperrt |
| 0.2.4 | G-Code-Prüfung und Programmwiedergabe | Eigenen Export rücklesen und gegen Planung prüfen; G1-Ein-/Ausfahrt kontinuierlich nach F, Heizstatus aus M3/M5 |
| 0.2.5 | Heizung vor Materialeintritt | M3/S mindestens 10 mm vor Eintritt, äußerer G1-Heizvorlauf, Freiraumprüfung und Wiedergabe aus Code |

## Künftige Versionsziele

| Zielversion | Schwerpunkt | Geplanter Umfang |
| --- | --- | --- |
| 0.3.0 | Maschinenanbindung und Status | Kommunikationsschnittstelle mit der Hardwaregruppe festlegen und anbinden; Verbindungszustand, Rückmeldungen und unterstützten G-Code-Dialekt prüfen. Grundlegende Verbindungsfehler von Beginn an behandeln. |
| 0.4.0 | Einzelachssteuerung und Referenzfahrt für X/Y/U/V | Alle vier realen Achsen einzeln manuell verfahren; Schalterzustände auswerten und Referenzfahrt mit definiertem Maschinennullpunkt umsetzen. Achsrichtungen, Verfahrgrenzen und Freigaben mit der Hardwaregruppe prüfen. |
| 0.5.0 | Koordinierte XYUV-Programmausführung | Den bereits erzeugten G-Code an der Maschine ausführen; abgestimmte Vierachsbewegungen, Vorschubinterpretation und M3/S/M5-Zuordnung prüfen. Programmstart, Halt und Abbruch sowie tatsächlichen Ausführungsstatus anbinden. |
| 0.6.0 | Robuster Maschinenbetrieb und Fehlerbehandlung | Verhalten bei Verbindungsabbruch, Schalter- und Steuerungsfehlern ausarbeiten; Bewegungs- und Heizfreigaben sowie Wiederanlauf nach Fehlern mit der Hardwaregruppe abstimmen und prüfen. |
| 0.7.0 | Praktische Schnittvalidierung und Parameterabgleich | Geplante Bahn und reale Schnitte vergleichen; Maschinenmaße, Vorschub, Heizleistung, Heizvorlauf und materialabhängigen Abbrand praktisch prüfen und dokumentieren. Grenzen durch Thermik und Drahtdurchhang erfassen. |
| 0.8.0 | Systemtests und Betriebsvalidierung | Gesamtablauf vom Profilimport bis zum Schnitt einschließlich Fehlerfällen prüfen; offene Regressionen bearbeiten, Debian-13-LXC-Installation und LAN-Betrieb vollständig prüfen sowie Update und Wiederherstellung umsetzen und testen. |
| 0.9.0 | Beta im abgestimmten Maschinenbetrieb | Einen festgelegten Funktionsumfang unter realen Einsatzbedingungen erproben, Rückmeldungen einarbeiten und bekannte Einschränkungen dokumentieren. |
| 1.0.0 | Abgenommener Funktionsumfang und stabiler Betrieb | Vereinbarte Prüfkriterien für CAM, Maschinenanbindung und Betrieb erfüllen; Bedienung, Installation und Fehlerbehebung für die unterstützte Konfiguration abschließen. |

X/Y bewegen ein Drahtende horizontal und vertikal, U/V das andere. 0.4.0
betrifft das einzelne Verfahren und Referenzieren dieser realen Achsen; 0.5.0
betrifft ihre koordinierte Ausführung durch die Maschinensteuerung. Die
Vierachsplanung, Synchronisierung der Profile und G-Code-Wiedergabe sind bereits
Teil des CAM-Stands 0.2.5.

Fehlerbehandlung und passende Tests gehören zu jedem Umsetzungsschritt; 0.6.0
vertieft den robusten Betrieb, 0.8.0 prüft das Zusammenspiel des Gesamtsystems.
Die praktische Erfassung thermischer Grenzen in 0.7.0 bedeutet noch keine
Implementierung einer Thermiksimulation oder Drahtdurchhangkompensation.

## Nächste Abstimmungen und Schritte

- Mit der Hardwaregruppe Profilformate, Einheiten, Achsen und Maschinenparameter klären.
- Schnittstelle und Zuständigkeiten für die Maschinenkommunikation abstimmen.
  Die grundlegende Anbindung ist als Voraussetzung für reale Achsbewegungen
  jetzt bei `0.3.0` eingeplant.
- Anforderungen und Prüfkriterien für Einzelachssteuerung und Referenzfahrt
  aller vier Achsen in `0.4.0` festhalten, einschließlich Schaltern und Freigaben.
- G-Code-Dialekt, F-Vorschubinterpretation und M3/S/M5-Zuordnung zum Stromregler
  bestätigen; Maschinenmaße und Material-Abbrand praktisch ermitteln.

## Umgesetzte CAM-Funktionen (Stand 0.2.5)

Folgende lokale CAM-Funktionen sind bereits implementiert und bilden die
Grundlage für die geplante Maschinenanbindung:

- Zwei SVG-/DXF-Profile, Einheitenumrechnung und Auswahl einzelner Konturen.
- Wahlweise XY-Datei und Kontur für beide Seiten verwenden; gekoppelte Zentren
  der gesamten Dateiausdehnungen auch bei verschiedenen Dateien/Skalierungen.
  Start/Ende und Richtung bleiben je Seite einstellbar.
- Skalierung, Positionierung und nutzerdefinierter Schneidraum; Planungs-X/U mittig,
  Y/V = 0 auf der Auflageebene. Zentrierter Block mit drei Maßen, automatisch
  berechneten Profilebenen und Prüfung der Nennkonturen gegen die Blockmaße.
- Räumliches Maschinenmodell mit Führungssäulen, Schlitten, Grundschienen,
  Schneiddraht und transparent gelbem Arbeitsraum; Maßeingaben direkt an Breite
  X/U, Höhe Y/V und Achsebenenabstand. Illustrativ und vor dem Profilimport verfügbar.
- Start/Ende als Weganteile, Laufrichtung und abschnittsweise Synchronisierung
  korrespondierender Ecken; unpassende Eckanzahlen werden abgewiesen.
- SVG-Kurvenstützpunkte von echten Segmentübergangsecken unterschieden;
  unterschiedlich große Kreise und unterschiedlich abgetastete SVG-Kurven
  einschließlich Abbrand und Teilschnitten synchronisierbar.
- Nennprogramm vor Abbrandkorrektur; Außen-/Innenoffsets und offene Links-/Rechtswege.
- Innenkonturen mit gerader Ein-/Ausfahrt und benutzerdefiniertem Zugangspunkt.
- Automatische kurze Randzugänge zu den eingestellten Start-/Endpunkten,
  ohne Durchquerung des Bauteilinneren in 21 geprüften Querschnitten; vollständiger
  Materialschnitt einschließlich Abbrand im Block. Ein-/Austritt oben oder seitlich;
  die aufliegende Unterseite ist gesperrt.
- Maschinen-, Rohteilnullpunkt und Schnittstart getrennt. X/U-Kontakte positiv
  (Standard +Raumbreite/2, alternativ tatsächliche Schalterlage), Y/V unten.
  Jeder Export mit freier G0-Kaltanfahrt ab Maschinennullpunkt und anschließender
  G1-Schnittbahn; Koordinaten auf die Schalterlage umgerechnet. Nicht kalt
  erreichbare innere Einfädelpunkte erlauben nur eine Schnittvorschau.
- Raum-/Achsprojektionsprüfung, Kollapsprüfung und 21 Zwischenquerschnitte.
- Drahtmodell mit Regler und kontinuierlicher Wiedergabe der rückgelesenen
  G-Code-Sätze, einschließlich heißer Ein-/Ausfahrt und Heizstatus aus M3/M5.
  G1-Zeit aus ausgegebenem F; G0 nur mit schematischer Anzeigezeit.
- Eigene G-Code-Ausgabe auf Positionen, Satzfolge, G0/G1, F und S rückgeprüft;
  falsche Postprozessor-Ausgabe verhindert den Export. Kein allgemeiner Import
  oder Interpreter beliebiger Maschinenprogramme.
- Heizung mindestens 10 mm vor Materialeintritt, bei automatischen Zugängen
  genau 10 mm normal zur Rohteilfläche; paralleler G1-Heizvorlauf in der Luft
  mit Schnittvorschub. Freiraum berücksichtigt, alternative Eintrittsseiten
  geprüft; keine zusätzliche Aufheizpause oder Temperaturregelung.
- Sofortanzeige von Raum, Block und Maßlinien ohne Schneidwegberechnung;
  Direktimport per Dateiauswahl oder Drag-and-drop auf die Arbeitsraumansicht,
  gemeinsame Zentrierung, Ziehen/Pfeiltasten im Seitenschnitt und gekoppelte
  Positionsfelder mit sofortiger Blockwarnung und automatischer Serverprüfung.
  Berechnete Wege
  an den Blockstirnflächen mit Start/Ende sowie markierter Ein-/Ausfahrt.
- Generischer XYUV-G-Code-Download und Prozentleistung mit konfigurierbarem S-Maximum.
- Automatisierte Import-, Planungs-, API-Tests und optionaler Edge-Browsertest.

Weiter offen: automatische Lochzuordnung und Auftragsverkettung, globale
Optimierung von Konturstarts/Materialausnutzung, automatische Innenzugänge und
Umfahrung zusätzlicher Hindernisse, vollständiger Schneidbarkeitsnachweis,
Thermik und Drahtdurchhang.
Eine explizite Zuordnung von Formmerkmalen bei abweichenden echten Eckanzahlen
ist ebenfalls offen. Für DXF und Profildaten ohne SVG-Eckinformationen zählen
weiterhin alle nichtkollinearen Stützpunkte als Ecken; eine Unterscheidung von
Kurven und Ecken beim DXF-Import bleibt offen.
Die Software kommuniziert weiterhin nicht mit einer Maschine.

## Linux-Betrieb und Updates

- Implementiert: interaktiver GitHub-Erstinstaller für Debian 13 LXC, eigener
  Benutzer, Python-Umgebung, Gunicorn/systemd und Anleitung für Linux-Anfänger.
- Offen: vollständige Installation und LAN-Zugriff auf dem Debian-13-Zielcontainer
  prüfen; Installer-Dateien auf GitHub bereitstellen.
- Geplant: separates Update-Script mit Prüfung, Sicherung und Wiederherstellung.
  Umsetzung und Betriebsprüfung sind dem Ziel `0.8.0` zugeordnet. Der Installer
  speichert dafür bereits Installationseinstellungen und Git-Commit.
- Bei jeder neuen Version [timeline.md](timeline.md) und Changelog mitpflegen.

## Begleitende Dokumentation

Bei jedem umgesetzten Schritt den tatsächlichen Stand hier und die Änderungen im
[Changelog](CHANGELOG.md) aktualisieren. Technische Entscheidungen gehören in
[ARCHITECTURE.md](ARCHITECTURE.md); neue Einrichtungs- oder Betriebsanforderungen
in die Installationsanleitung und Fehlerbehebung.
