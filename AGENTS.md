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
- `timeline.md`: für jede Version die tatsächlich durchgeführten Änderungen.
- `INSTALLATION_DEBIAN.md`: Debian-13-LXC-Installation und Betrieb; bei Änderungen
  am Installer oder systemd-Dienst parallel aktualisieren.

Nur betroffene Dateien ändern; unnötige Dopplungen vermeiden. Dokumentation auf
Deutsch schreiben und vorhandene Informationen erhalten. Implementiertes Verhalten,
Platzhalter und geplante Funktionen klar unterscheiden. Keine Testergebnisse,
Veröffentlichungen, Termine oder Hardwareparameter erfinden.

Bei Versionswechseln `version.py` und zugehörige Dokumentation konsistent halten.
Die Dokumentation anhand des Codes prüfen; bei geänderten Anleitungen die Befehle
nach Möglichkeit validieren und Einschränkungen offen benennen.

## Timeline verbindlich pflegen

`timeline.md` ist der dauerhafte Versionsverlauf des Projekts. Für jede neue
Version einen eigenen Abschnitt anlegen, neueste Version zuerst. Tatsächlich
durchgeführte Änderungen während der Arbeit im Abschnitt der zugehörigen Version
ergänzen; bestehende Einträge erhalten. Geplante Funktionen ausdrücklich als
geplant kennzeichnen und nicht als umgesetzt aufführen.

Bei jedem Versionswechsel `version.py`, `timeline.md`, `CHANGELOG.md` und betroffene
Anleitungen im selben Arbeitsschritt konsistent aktualisieren. Keine Version allein
für einen Dokumentationseintrag erhöhen. Prüfgrenzen offen nennen; keine
Veröffentlichungsdaten, GitHub-Releases oder Tags ohne Nachweis behaupten.
