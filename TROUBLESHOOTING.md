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
| Bauteil liegt außerhalb des Schneidraums | Seit 0.2.0 gilt X/U zwischen −Raumbreite/2 und +Raumbreite/2, Y/V zwischen 0 und Raumhöhe. Alle Nennkonturen müssen zusätzlich in den zentrierten Block passen. Auch projizierte Achspositionen, Abbrand und Ein-/Ausfahrt müssen in den Maschinenraum passen. Bei schrägem Draht können die Achsen weiter außen liegen als die Bauteilprofile. Blockmaße und Profilpositionen prüfen. |
| Alte Aufträge melden fehlende Blockmaße | Seit 0.2.0 sind Blockbreite, Blockhöhe und Blocklänge Pflichtangaben. Die Profilebenen werden daraus automatisch berechnet; bisherige manuelle Abstände werden nicht übernommen. Profil- und Zugangspunkte auf den zentralen X/U-Nullpunkt umstellen. |
| Pfeiltasten bewegen keine Achse / Schalter setzt in der Website keinen Nullpunkt | Die CAM-Anwendung hat keine Maschinenanbindung. Pfeiltasten bei fokussierter XY-/UV-Vorschau verschieben nur die Profilplanung. Alle Maschinennullpunkte werden an der Maschinensteuerung per Kontaktschalter gesetzt: X/U positiv, Y/V unten. Die mittigen X/U-Werte der Vorschau sind Planungskoordinaten und werden für den Export umgerechnet. |
| Abbrand lässt die Kontur kollabieren | Eingetragenen Radius prüfen: Er ist die halbe Schnittbreite. Zu kleine Innenkonturen oder Engstellen können nach der Korrektur verschwinden. Profil ändern oder einen realistisch gemessenen kleineren Radius verwenden. |
| Zwischenquerschnitt kollabiert oder überschneidet sich | Korrespondierende Startpunkte, Endpunkte und Laufrichtungen beider Profile prüfen. Unterschiedliche Ausgangspunkte können einen verdrehten Drahtweg erzeugen. |
| Eckzuordnung nicht eindeutig | Beide Schnittverläufe benötigen gleich viele echte Ecken in korrespondierender Reihenfolge. Start/Ende und Laufrichtung prüfen. SVG-Kreise und SVG-Kurven dürfen seit der Korrektur unterschiedlich viele Stützpunkte haben. Server nach dem Update neu starten, Seite neu laden und beide SVG-Dateien erneut importieren, um die neuen Eckinformationen zu erhalten. DXF und alte Profildaten ohne Eckinformationen zählen weiterhin nichtkollineare Stützpunkte als Ecken; reine Linienpolygone liefern keine ursprünglichen Kurveninformationen. Zusätzliche Punkte auf geraden Kanten sind unkritisch. Die Prüfung gilt auch nach Abbrandkorrektur und für vollständige Konturen bei Teilschnitten. |
| Export bleibt deaktiviert | Automatische Geometrieprüfung abwarten oder „Schneidweg berechnen“ wählen. Für Export zusätzlich S-Maximum und passendes Steuerungsprofil eintragen/bestätigen. Fehlende Angaben oder ein Fehler verwerfen den vorherigen Export. |
| Innenkontur wird abgewiesen | Manuelle Ein-/Ausfahrt aktivieren und alle Zugangspunkte eintragen. Ein innerer Einfädelpunkt allein ist kalt ab Maschinennullpunkt nicht erreichbar und erlaubt nur die Schnittvorschau. Für den Export einen außen erreichbaren Start/Austritt und gegebenenfalls einen separat geplanten Zugangsschlitz vorsehen; Innenzugänge werden nicht automatisch geplant. |
| Fehlendes Modul ezdxf, shapely oder svgelements | Abhängigkeiten mit `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` aktualisieren. |
| ezdxf meldet fehlendes Cache-Verzeichnis | Der optionale Schriftcache kann in eingeschränkten Umgebungen nicht geschrieben werden. Für die hier unterstützten Geometrien wird kein Schriftcache benötigt; Text wird nicht importiert. |
| Optionaler Browsertest startet nicht | Microsoft Edge muss am im Testskript angegebenen Standardpfad installiert sein. Bei Browser-/GPU-Sandboxfehlern die manuelle Funktionsprüfung aus INSTALLATION.md verwenden. |
| Block oder importierte Kontur fehlt in der Sofortansicht | Gültige Maschinen- und Blockmaße eingeben. Für die Profilanzeige werden zusätzlich Position und positive Skalierung benötigt. Die Zielseite beim Direktimport prüfen; UV verwendet bei aktivierter Profilübernahme die XY-Datei. Außen liegende Profile werden mit Hinweis angezeigt. |
| Einfahrt ist nicht als Weg eingezeichnet | Bei automatischem Randzugang müssen beide Profile und alle Planungsparameter gültig sein. Feedback unter dem Canvas prüfen; nach 250 ms Eingabepause wird neu gerechnet. Für manuelle Zugänge alle Zugangspunkte eintragen. Ohne beide Zugangsoptionen beginnt der Weg auf der Kontur. |
| Profil lässt sich nicht ziehen | „Seitenschnitt XY“ oder „Seitenschnitt UV“ wählen und innerhalb der Profilausdehnung ziehen. Im räumlichen Drahtmodell gibt es keine Ziehfunktion. Alternativ Canvas fokussieren und Pfeiltasten verwenden (1 mm, mit Umschalt 10 mm). Beide Dateizentren werden gemeinsam verschoben. |
| Andere Profilseite ändert ihre Positionsfelder mit | Seit 0.2.2 sind die Mittelpunkte der gesamten Dateiausdehnungen gekoppelt. Verschiedene Skalierungen können deshalb unterschiedliche Werte für die unteren linken Ecken erfordern. Das gilt auch beim Wiederherstellen einer separaten UV-Datei. |
| Automatik meldet Abbrandbahn außerhalb des Blocks | Kontur und Materialschnitt müssen einschließlich Abbrand im Block bleiben; nur der separate Heizvorlauf liegt in der Luft davor. Profil weiter vom Rand platzieren; mindestens den tatsächlichen Abbrand berücksichtigen, an scharfen Ecken kann der Offset weiter reichen. |
| Kein automatischer Zugang gefunden | Die geprüften geraden Zugänge von oben oder seitlich würden das Bauteil vorzeitig durchqueren. Unterkante und untere Ecken sind gesperrt, da der Block aufliegt. Korrespondierende Konturstarts/-enden ändern oder manuelle Ein-/Ausfahrt planen. Es gibt keine globale Startpunktoptimierung. |
| Kaltanfahrt im Export verläuft am Materialrand | Jeder Export beginnt am per Schalter gesetzten Maschinennullpunkt und fährt mit M5/G0 außen seitlich oder oben zum Einschaltpunkt mindestens 10 mm vor Materialeintritt. Danach folgen M3/S und G1 mit Schnittvorschub. Die Unterseite ist gesperrt; Spannmittel und Hindernisse im Außenraum sind nicht modelliert. Freigängigkeit praktisch prüfen. |
| Keine freie Kaltanfahrt / Export trotz gültiger Kontur gesperrt | Schalterlagen und Rohteilmaße prüfen. X/U-Kontakte müssen positiv liegen, Y/V unten. Leere Schalterfelder bedeuten +Raumbreite/2. Liegt der Maschinenstart im aufliegenden Rohteil oder der Schnittstart im unzugänglichen Inneren, kann kein G0-Weg erzeugt werden. Die Schnittvorschau bleibt verfügbar. Start/Austritt außen seitlich oder oben planen. |
| G-Code-X/U sind gegenüber der Vorschau verschoben | Seit 0.2.3 gilt Maschinenkoordinate = Planungskoordinate − Schalterlage. Standardmäßig entspricht die positive Raumgrenze +Raumbreite/2 dem Maschinen-X/U = 0. Rohteilnullpunkt (Block links unten), Planungsraummitte und Schnittstart sind getrennte Punkte. Das Programm setzt keinen Nullpunkt am Rohteil. |
| Manueller Ein-/Austritt unten wird abgewiesen | Der Block liegt auf der Arbeitsfläche; die Unterseite einschließlich unterer Ecken ist kein Zugang. Zugang seitlich oder oben wählen. Auch manuelle Außenpunkte müssen eine freie Kaltanfahrt und einen frei liegenden Austritt ermöglichen. |
| Draht springt bei Ein-/Ausfahrt zur Rohteilkante | Bis 0.2.3 wurde je Animationsschritt nur ein Satzendpunkt gezeigt, auch bei langen G1-Verbindungen. Seit 0.2.4 wird der tatsächlich ausgegebene Code rückgelesen und jeder G1 nach seinem F kontinuierlich durchfahren. Server neu starten und mit Strg+F5 neu laden. In der Zustandszeile Einfahrt/Ausfahrt, G1 und Heizung EIN (M3) sowie die betreffende Codezeile prüfen. |
| Wiedergabe wirkt zu langsam oder G0-Zeit stimmt nicht mit Maschine überein | G1 verwendet die ideale Zeit aus XYUV-Weglänge und ausgegebenem F, ohne Beschleunigung. 1×/10×/50× verändert nur die Anzeige. Der echte Maschinen-Eilgang ist unbekannt; G0 wird ausdrücklich mit 1 s je nicht leerem Satz schematisch dargestellt. |
| G-Code-Prüfung verhindert den Export | Ausgegebene Satzfolge, Achspositionen, F oder M3/S/M5 weichen vom freigegebenen Modell ab, oder es steht ein nicht unterstützter Befehl im eigenen Postprozessor-Ausgang. Fehlermeldung und Auftrag sichern; die Rückprüfung nicht umgehen. Ein-/Ausfahrt müssen G1 unter M3, Kaltanfahrten G0 unter M5 sein. |
| Abspielen bleibt bei sichtbarer Kontur deaktiviert | Ohne freie Anfahrt/Ausfahrt gibt es nur den geometrischen Entwurf und kein ausführbares Programm. Hinweise zur Kaltanfahrt prüfen. Ohne bestätigten S-Bereich ist bei freiem Zugang die ausdrücklich gekennzeichnete interne Vorschauvorlage verfügbar; sie ist kein Export. |
| M3 aktiv, aber Draht als Leistung 0 dargestellt | Der rückgelesene S-Wert ist 0 beziehungsweise die geplante Vorschauleistung 0 %. M3 allein bedeutet keine positive Heizleistung und weist auch keine reale Drahttemperatur nach. |
| Keine freie Kaltanfahrt mit 10 mm Heizvorlauf möglich | Seit 0.2.5 muss der Draht mindestens 10 mm vor Materialeintritt eingeschaltet werden. Zwischen Rohteilfläche und Maschinenraum muss genug Platz liegen; die Automatik prüft auch andere Eintrittsflächen. Raum-/Blockmaße und Schalterlage prüfen. Ohne passenden Platz bleiben Export und Programmwiedergabe gesperrt, die Geometrie bleibt sichtbar. |
| Manueller Heizvorlauf ist kürzer als 10 mm oder fehlt als eigener Satz | Der manuelle Zugang liegt bereits teilweise oder vollständig außerhalb des Rohteils. Ergänzt wird nur der fehlende Abstand bis mindestens 10 mm Luft vor dem Material. Ein weiter außen liegender Startpunkt bleibt erhalten und schaltet entsprechend früher ein. Bei automatisch gewähltem Randzugang beträgt der zusätzliche G1-Weg genau 10 mm je Blockseite. |

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

Beim Prüfstand 0.2.0 bestehen 28 von 30 Tests. Die Fehler in
`test_partial_contour_start_end` (Eckzuordnung im Teilschnitt) und
`test_crossed_wire_surface` (erwartete Abweisung fehlt) sind auch mit Code und
Tests aus dem unveränderten vorherigen Git-Stand reproduzierbar. Eine Lösung
ist noch offen. Der Edge-Test lieferte in dieser Prüfung keinen DOM-Bericht;
das ist kein erfolgreicher Nachweis der Browserdarstellung.
Die für 0.2.1 erweiterte UI-Prüfung konnte mit lokal installiertem Chrome
(`--browser chrome`) außerhalb der Sandbox erfolgreich ausgeführt werden,
einschließlich Sofortanzeige, Drop-Import, Zentrierung und Ein-/Ausfahrt.
Für 0.2.2 bestehen 40 von 42 automatisierten Tests, einschließlich aller sechs
neuen Planungstests; dieselben zwei bekannten Fehler bleiben offen. Der erweiterte
Chrome-Test lief außerhalb der Sandbox erfolgreich, einschließlich gekoppelter
Platzierung, Block-/Abbrandfeedback, alter Live-Antworten und automatischem Zugang.
In der Sandbox scheiterte der Chrome-Start am GPU-Prozess; das ist kein
Anwendungsfehler und kein Nachweis einer erfolgreichen Darstellung in der Sandbox.
Für 0.2.3 bestehen 45 von 47 Tests; alle fünf zusätzlichen Regressionstests
für Maschinen-/Rohteilbezug, G0-Umfahrung und gesperrte Unter-/Innenzugänge sind
erfolgreich. Die beiden bekannten Fehler bleiben offen. Die erweiterte
Chrome-Prüfung mit getrennten Nullpunkten, G0-Export und blockierter Anfahrt
lief außerhalb der Sandbox erfolgreich. Keine Hardwareprüfung.
Für 0.2.4 bestehen 53 von 55 Tests; alle acht zusätzlichen Prüfungen des
rückgelesenen Codes sind erfolgreich. Die beiden bekannten Fehler bleiben
offen. Die erweiterte Chrome-Prüfung für G1-Zwischenpositionen, kontinuierliche
Ein-/Ausfahrt, M3/M5 und tatsächliche Exportzeilen bestand außerhalb der Sandbox.
Der anfänglich untersuchte Beispiel-Export enthielt bereits M3/S vor Einfahrt,
G1/F bis zur Ausfahrt und M5 danach; der Sprung stammte von der Satzendpunkt-Wiedergabe.
Für 0.2.5 bestehen 58 von 60 Tests, einschließlich aller fünf neuen Prüfungen
für den 10-mm-Heizvorlauf und fehlenden Freiraum. Die beiden bekannten Fehler
bleiben offen. Der erweiterte Chrome-Test für Heizvorlauf und M3/G1 vor dem
Rohteileintritt bestand außerhalb der Sandbox. Keine Hardwareprüfung.

Bei ungelösten Problemen die Python-Version, Anwendungsversion, ausgeführten Befehle,
Fehlermeldung sowie erwartetes und tatsächliches Verhalten notieren. Keine Zugangsdaten
oder privaten Konfigurationswerte in Fehlerberichte übernehmen.

Neue wiederkehrende Probleme und bestätigte Lösungen werden bei ihrer Bearbeitung
in dieser Datei ergänzt. Die Einrichtung beschreibt [INSTALLATION.md](INSTALLATION.md).
