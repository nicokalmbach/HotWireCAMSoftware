# Änderungshistorie

Änderungen werden während der Entwicklung ergänzt. Einträge unter „Unveröffentlicht“
werden beim nächsten Release der jeweiligen Version zugeordnet. Die Versionsnummer
der Anwendung steht in `version.py`; eine Dokumentationsänderung erfordert allein
keinen Versionswechsel.

## Unveröffentlicht

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

## Aktueller Grundstand: 0.1.0

Ein Veröffentlichungsdatum ist bisher nicht dokumentiert. Dieser Abschnitt beschreibt
den vorhandenen Implementierungsstand.

- Lokal startbare Flask-Anwendung mit deutschsprachiger Oberfläche.
- Platzhalter für Profilimport, Profileinstellungen, Schneidvorschau und G-Code-Export.
- Zentrale Versionsnummer mit Anzeige in der Fußzeile.
- Noch keine Achsensteuerung, Maschinenkommunikation oder G-Code-Erzeugung.
