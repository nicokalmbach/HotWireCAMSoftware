# Versionsverlauf

Für jede neue Version einen eigenen Eintrag mit den tatsächlich durchgeführten
Änderungen ergänzen und `version.py`, Changelog und betroffene Anleitungen im
selben Arbeitsschritt aktualisieren. Eine Versionsnummer dokumentiert den
Projektstand; ein GitHub-Release oder Tag ist dadurch nicht automatisch erstellt.

## 0.1.1

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
