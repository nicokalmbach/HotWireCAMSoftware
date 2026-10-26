# Arbeitsregeln für KI-Assistenten

## Dokumentation parallel entwickeln

Technische Dokumentation wird mit der Implementierung gepflegt, nicht erst am
Projektende. Bei jeder fachlichen oder technischen Änderung die betroffenen
Dokumente prüfen und im selben Arbeitsschritt aktualisieren:

- `README.md`: Projekteinstieg, Funktionsumfang und Verweise.
- `CHANGELOG.md`: relevante Änderungen unter „Unveröffentlicht“ festhalten.
- `ARCHITECTURE.md`: Komponenten, Datenfluss, Schnittstellen und Entscheidungen.
- `INSTALLATION.md`: Voraussetzungen, Abhängigkeiten, Einrichtung und Start.
- `TROUBLESHOOTING.md`: neue bekannte Probleme und bestätigte Lösungen.
- `ROADMAP.md`: tatsächlicher Fortschritt und offene Planung.

Nur betroffene Dateien ändern; unnötige Dopplungen vermeiden. Dokumentation auf
Deutsch schreiben und vorhandene Informationen erhalten. Implementiertes Verhalten,
Platzhalter und geplante Funktionen klar unterscheiden. Keine Testergebnisse,
Veröffentlichungen, Termine oder Hardwareparameter erfinden.

Bei Versionswechseln `version.py` und zugehörige Dokumentation konsistent halten.
Die Dokumentation anhand des Codes prüfen; bei geänderten Anleitungen die Befehle
nach Möglichkeit validieren und Einschränkungen offen benennen.
