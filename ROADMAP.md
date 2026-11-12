# Roadmap

Die Versionsziele stammen aus der bisherigen Projektplanung. Sie sind geplante
Meilensteine ohne festgelegte Termine. Die Anwendung trägt Version `0.2.1`,
der ursprüngliche Hardware-Meilenstein 0.1.0 ist aber erst teilweise umgesetzt.

| Zielversion | Schwerpunkt | Stand |
| --- | --- | --- |
| 0.1.0 | Projektstruktur und eine Achse | Grundgerüst vorhanden; Achsensteuerung offen |
| 0.1.1 | CAM-Stand und Debian-LXC-Installation | CAM und Installer implementiert; vollständige LXC-Installation noch zu prüfen |
| 0.2.0 | Referenzschalter und zentriertes Werkstück | CAM-Koordinaten und automatische Blockabstände umgesetzt; Schalterauswertung und Tastatursteuerung offen |
| 0.2.1 | Direkte Arbeitsraumvorschau | Live-Block mit Bemaßung, Direktimport und zentrierten Profilen sowie Darstellung des vollständigen berechneten Drahtwegs umgesetzt |
| 0.3.0 | Referenzfahrt | Geplant |
| 0.4.0 | Mehrere Achsen | Geplant |
| 0.5.0 | Koordinierte Bewegungen | Geplant |
| 0.6.0 | Fehlerbehandlung | Geplant |
| 0.7.0 | Kommunikation | Geplant |
| 0.8.0 | Erweiterte Tests | Geplant |
| 0.9.0 | Beta | Geplant |
| 1.0.0 | Stabile Version | Geplant |

## Nächste Abstimmungen und Schritte

- Mit der Hardwaregruppe Profilformate, Einheiten, Achsen und Maschinenparameter klären.
- Schnittstelle und Zuständigkeiten für die Maschinenkommunikation abstimmen.
  Kommunikation steht bisher bei `0.7.0`; die für frühere Achsenfunktionen nötige
  Schnittstelle muss vorher geklärt werden.
- Anforderungen und Prüfkriterien für den ersten Achsen-Meilenstein festhalten.
- G-Code-Dialekt, F-Vorschubinterpretation und M3/S/M5-Zuordnung zum Stromregler
  bestätigen; Maschinenmaße und Material-Abbrand praktisch ermitteln.

## Umgesetzte CAM-Funktionen (Stand 0.2.1)

Die bisherige Zielversionstabelle beschreibt Hardware-Meilensteine. Unabhängig
davon sind folgende lokale CAM-Funktionen implementiert:

- Zwei SVG-/DXF-Profile, Einheitenumrechnung und Auswahl einzelner Konturen.
- Wahlweise XY-Datei und Kontur für beide Seiten verwenden; weitere
  Profileinstellungen bleiben je Seite einstellbar.
- Skalierung, Positionierung und nutzerdefinierter Schneidraum; X/U-Nullpunkt mittig,
  Y/V = 0 auf der Auflageebene. Zentrierter Block mit drei Maßen, automatisch
  berechneten Profilebenen und Prüfung der Nennkonturen gegen die Blockmaße.
- Räumliches Maschinenmodell mit Führungssäulen, Schlitten, Grundschienen,
  Schneiddraht und transparent gelbem Arbeitsraum; Maßeingaben direkt an Breite
  X/U, Höhe Y/V und Achsebenenabstand. Illustrativ und vor dem Profilimport verfügbar.
- Start/Ende als Weganteile, Laufrichtung und abschnittsweise Synchronisierung
  korrespondierender Ecken; unpassende Eckanzahlen werden abgewiesen.
- Nennprogramm vor Abbrandkorrektur; Außen-/Innenoffsets und offene Links-/Rechtswege.
- Innenkonturen mit gerader Ein-/Ausfahrt und benutzerdefiniertem Zugangspunkt.
- Raum-/Achsprojektionsprüfung, Kollapsprüfung und 21 Zwischenquerschnitte.
- Statisches Drahtmodell, Schrittregler und geometrische Bewegungswiedergabe.
- Sofortanzeige von Raum, Block und Maßlinien ohne Schneidwegberechnung;
  Direktimport per Dateiauswahl oder Drag-and-drop auf die Arbeitsraumansicht,
  Zentrierung und Live-Positionierung über die Profilfelder. Berechnete Wege
  an den Blockstirnflächen mit Start/Ende sowie markierter Ein-/Ausfahrt.
- Generischer XYUV-G-Code-Download und Prozentleistung mit konfigurierbarem S-Maximum.
- Automatisierte Import-, Planungs-, API-Tests und optionaler Edge-Browsertest.

Weiter offen: automatische Lochzuordnung und Auftragsverkettung, automatische
Zugangsplanung, vollständiger Schneidbarkeitsnachweis, Thermik und Drahtdurchhang.
Eine explizite Zuordnung von Formmerkmalen bei unterschiedlich unterteilten Kurven
oder abweichenden Eckanzahlen ist ebenfalls offen; derzeit zählen alle
nichtkollinearen Kurvenstützpunkte als Ecken.
Die Software kommuniziert weiterhin nicht mit einer Maschine.

## Linux-Betrieb und Updates

- Implementiert: interaktiver GitHub-Erstinstaller für Debian 13 LXC, eigener
  Benutzer, Python-Umgebung, Gunicorn/systemd und Anleitung für Linux-Anfänger.
- Offen: vollständige Installation und LAN-Zugriff auf dem Debian-13-Zielcontainer
  prüfen; Installer-Dateien auf GitHub bereitstellen.
- Geplant: separates Update-Script mit Prüfung, Sicherung und Wiederherstellung.
  Der Installer speichert dafür bereits Installationseinstellungen und Git-Commit.
- Bei jeder neuen Version [timeline.md](timeline.md) und Changelog mitpflegen.

## Begleitende Dokumentation

Bei jedem umgesetzten Schritt den tatsächlichen Stand hier und die Änderungen im
[Changelog](CHANGELOG.md) aktualisieren. Technische Entscheidungen gehören in
[ARCHITECTURE.md](ARCHITECTURE.md); neue Einrichtungs- oder Betriebsanforderungen
in die Installationsanleitung und Fehlerbehebung.
