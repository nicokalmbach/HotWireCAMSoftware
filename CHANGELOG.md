# Änderungshistorie

Änderungen werden während der Entwicklung ergänzt. Einträge unter „Unveröffentlicht“
werden beim nächsten Release der jeweiligen Version zugeordnet. Die Versionsnummer
der Anwendung steht in `version.py`; eine Dokumentationsänderung erfordert allein
keinen Versionswechsel.

## Unveröffentlicht

### Ergänzt

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
