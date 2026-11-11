# Fehlerbehebung

Die folgenden Hinweise beziehen sich auf den lokalen Start unter Windows/PowerShell.

Für Debian 13 LXC stehen Diagnosebefehle und Installationsfehler in
[INSTALLATION_DEBIAN.md](INSTALLATION_DEBIAN.md#6-wenn-etwas-nicht-funktioniert).
Der Installer überschreibt keine vorhandenen Benutzer, Installationen oder Dienste.

| Problem | Prüfung und Lösung |
| --- | --- |
| `py` wird nicht gefunden | Python-Installation und Python-Launcher prüfen. Wenn `python --version` eine Version ab 3.10 anzeigt, für das Anlegen der Umgebung `python -m venv .venv` verwenden. |
| `.venv\Scripts\python.exe` wird nicht gefunden | Im Projektordner arbeiten und die Umgebung mit `py -m venv .venv` anlegen. |
| `ModuleNotFoundError: No module named 'flask'` | `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` ausführen und die App mit demselben Interpreter starten. |
| PowerShell blockiert `Activate.ps1` | Direkt `.\.venv\Scripts\python.exe app.py` verwenden; dafür ist keine Aktivierung nötig. |
| Port 5001 ist belegt | Eine bereits laufende Projektinstanz im zugehörigen Terminal mit `Strg+C` beenden. Bei einer anderen Anwendung deren Portbelegung prüfen. |
| Browser kann die Seite nicht öffnen | Prüfen, ob der Server ohne Fehlermeldung läuft, und `http://127.0.0.1:5001` verwenden. |
| Browser öffnet sich beim Start nicht automatisch | `http://127.0.0.1:5001` manuell öffnen. Automatische Browseröffnung benötigt einen verfügbaren Standardbrowser und kann durch lokale Berechtigungen blockiert sein. |
| Gestaltung fehlt oder bleibt veraltet | Seite mit `Strg+F5` neu laden und prüfen, ob `static/css/style.css` vorhanden ist. |
| Neue Formularelemente fehlen trotz geänderter HTML-Datei | Der laufende Server kann noch die alte Vorlage im Speicher halten. Projektinstanz mit `Strg+C` beenden und über `start.cmd` neu starten, anschließend die Seite mit `Strg+F5` neu laden. Beim lokalen Fall auf Port 5001 lieferte der richtige Projektprozess eine alte Vorlage ohne die neue Profil-Checkbox aus; nach dem Neustart enthielt die HTTP-Antwort die Checkbox. |
| Angezeigte Version bleibt unverändert | `version.py` speichern, den Server beenden und erneut starten. |
| Import schlägt fehl | SVG oder ASCII-DXF mit unterstützten Konturen verwenden. Text in Pfade umwandeln, DXF-Blöcke auflösen. Z muss 0 sein; Details zum Formatumfang stehen in ARCHITECTURE.md. Maximal 4 MiB pro Anfrage und 20000 Punkte je Profil. |
| DXF ist falsch skaliert | Einheiten im DXF-Header prüfen. Nur bei einheitenlosen Dateien gilt „mm pro Einheit“; Faktor vor dem erneuten Import setzen. |
| SVG steht vertikal anders als im Editor | SVG-Y wird beim Import gespiegelt, damit Maschinen-Y nach oben zeigt. Die Datei wird danach mit ihrer unteren linken Ecke positioniert. |
| Bauteil liegt außerhalb des Schneidraums | Auch projizierte Achspositionen, Abbrand und Ein-/Ausfahrt müssen hineinpassen. Bei schrägem Draht können die Achsen weiter außen liegen als die Bauteilprofile. Positionen und Abstände der Profilebenen prüfen. |
| Abbrand lässt die Kontur kollabieren | Eingetragenen Radius prüfen: Er ist die halbe Schnittbreite. Zu kleine Innenkonturen oder Engstellen können nach der Korrektur verschwinden. Profil ändern oder einen realistisch gemessenen kleineren Radius verwenden. |
| Zwischenquerschnitt kollabiert oder überschneidet sich | Korrespondierende Startpunkte, Endpunkte und Laufrichtungen beider Profile prüfen. Unterschiedliche Ausgangspunkte können einen verdrehten Drahtweg erzeugen. |
| Eckzuordnung nicht eindeutig | Beide Schnittverläufe benötigen gleich viele Richtungswechsel in korrespondierender Reihenfolge. Start/Ende und Laufrichtung prüfen; Kurven müssen passend unterteilt sein, da auch ihre nichtkollinearen Stützpunkte zählen. Zusätzliche Punkte auf geraden Kanten sind unkritisch. Die Prüfung gilt auch nach Abbrandkorrektur und für vollständige Konturen bei Teilschnitten. Es wird kein Export mit unpassender Eckanzahl erzeugt. |
| Export bleibt deaktiviert | Nach Import/Einstellungsänderung neu berechnen. Für Export zusätzlich S-Maximum und passendes Steuerungsprofil eintragen/bestätigen. Ein Fehler verwirft den vorherigen Export. |
| Innenkontur wird abgewiesen | Ein-/Ausfahrt aktivieren und alle Zugangspunkte eintragen. Draht einfädeln oder Zugangsschlitz vorsehen; automatische Zugangsplanung gibt es nicht. |
| Fehlendes Modul ezdxf, shapely oder svgelements | Abhängigkeiten mit `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` aktualisieren. |
| ezdxf meldet fehlendes Cache-Verzeichnis | Der optionale Schriftcache kann in eingeschränkten Umgebungen nicht geschrieben werden. Für die hier unterstützten Geometrien wird kein Schriftcache benötigt; Text wird nicht importiert. |
| Optionaler Browsertest startet nicht | Microsoft Edge muss am im Testskript angegebenen Standardpfad installiert sein. Bei Browser-/GPU-Sandboxfehlern die manuelle Funktionsprüfung aus INSTALLATION.md verwenden. |

## Bestätigte DLL-Blockierung unter Windows

Am 09.11.2026 scheiterte der Start mit Python 3.15 ARM64 und Shapely 2.2.0
an `ImportError: DLL load failed while importing lib: Eine
Anwendungssteuerungsrichtlinie hat diese Datei blockiert.` Das Ereignis 3077
unter `Microsoft-Windows-CodeIntegrity/Operational` nennt die GEOS-C-DLL in
`.venv/Lib/site-packages/shapely.libs` und die Richtlinie
`VerifiedAndReputableDesktop`. Smart App Control war aktiviert. Auch ein Start
außerhalb der eingeschränkten Ausführungsumgebung scheiterte.

Die betroffenen Dateien haben Zeitstempel vom 26.10.2026; ihre Prüfsummen stimmen
mit den lokal gespeicherten Shapely-Installationsdaten (`RECORD`) überein.
Das belegt keine unabhängige Herkunftsprüfung und erklärt nicht, warum frühere
Starts funktionierten. Die Richtlinie wurde am 06.11.2026 erneut aktiviert,
mit derselben Kennung wie zuvor; eine ursächliche Änderung ist nicht nachgewiesen.
Eine bestätigte Lösung liegt bislang nicht vor.

Zur Diagnose im Projektordner:

```powershell
.\.venv\Scripts\python.exe -c "import shapely"
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-CodeIntegrity/Operational'; Id=3077} -MaxEvents 5 | Select-Object TimeCreated,Message | Format-List
```

Eine erneute Paketinstallation oder ein Portwechsel ist damit noch keine
bestätigte Lösung. Bei verwalteten Geräten die konkrete Blockierung mit der IT
klären. Sicherheitsrichtlinien werden vom Starter nicht verändert.

## Ein Problem nachvollziehbar festhalten

Bei ungelösten Problemen die Python-Version, Anwendungsversion, ausgeführten Befehle,
Fehlermeldung sowie erwartetes und tatsächliches Verhalten notieren. Keine Zugangsdaten
oder privaten Konfigurationswerte in Fehlerberichte übernehmen.

Neue wiederkehrende Probleme und bestätigte Lösungen werden bei ihrer Bearbeitung
in dieser Datei ergänzt. Die Einrichtung beschreibt [INSTALLATION.md](INSTALLATION.md).
