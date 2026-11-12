# Installation und lokaler Start

Für einen Debian-13-LXC-Container die separate
[Schritt-für-Schritt-Anleitung](INSTALLATION_DEBIAN.md) verwenden. Sie beschreibt
den GitHub-Installer, eigene Dienstbenutzer und systemd. Die folgenden Befehle
beziehen sich auf den lokalen Windows-Start.

## Voraussetzungen

- Python 3.10 oder neuer mit `pip` und `venv`.
- PowerShell unter Windows.
- Projektdateien auf dem lokalen Rechner.
- Ein moderner Browser mit JavaScript und Canvas.

Alle folgenden Befehle werden im Projektordner ausgeführt.

## Einrichtung

Python-Version prüfen:

```powershell
py --version
```

Virtuelle Umgebung anlegen und Abhängigkeiten installieren:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Die virtuelle Umgebung liegt ausschließlich lokal; `.gitignore` schließt sie aus.
Aktuell benötigt die Anwendung keine `.env`-Datei, Zugangsdaten oder Datenbank.
Die Anwendung lädt derzeit keine eigene Umgebungskonfiguration.
Neben Flask werden ezdxf, svgelements und Shapely einschließlich ihrer Abhängigkeiten
installiert. Für die Erstinstallation ist Zugriff auf den Python-Paketindex nötig.

## Start und Ende

Unter Windows `start.cmd` im Projektordner doppelklicken. Der Starter verwendet
die lokale virtuelle Umgebung und öffnet nach erfolgreicher Portbindung
`http://127.0.0.1:5001` im Standardbrowser. Er funktioniert auch dann, wenn
der Projektpfad Leerzeichen enthält. Das Terminal muss geöffnet bleiben.

Alternativ aus PowerShell im Projektordner mit Browseröffnung:

```powershell
.\.venv\Scripts\python.exe app.py --open-browser
```

Ohne automatische Browseröffnung:

```powershell
.\.venv\Scripts\python.exe app.py
```

Im Browser [http://127.0.0.1:5001](http://127.0.0.1:5001) öffnen.
Mit `Strg+C` im Terminal wird der Server beendet.

Port 5001 ist die feste lokale Adresse, keine Versionsnummer. Nach Änderungen
am Python-Code den laufenden Server mit `Strg+C` beenden und erneut starten,
um die aktuellen lokalen Dateien zu laden. Es werden keine Updates heruntergeladen.
Eine bereits laufende Instanz wird nicht automatisch ersetzt; bei belegtem Port
bricht der Start ab, ohne eine möglicherweise alte Seite zu öffnen.

Eine Aktivierung der Umgebung ist für diese Befehle nicht erforderlich. Optional:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

## Funktionsprüfung

1. Die Startseite zeigt „HotWireCamSoftware“ an.
2. Gestaltung und Navigation werden dargestellt.
3. Die Fußzeile zeigt die Versionsnummer aus `version.py` (aktuell `0.2.5`).
4. „Demobeispiel laden“ wählen: Block, Bemaßung und importierte Konturen erscheinen
   sofort unter den Blockeingaben. Blocklänge ändern und beide Abstände prüfen.
5. „Seitenschnitt XY“ oder „Seitenschnitt UV“ wählen und das Profil ziehen oder
   mit Pfeiltasten verschieben. Beide Dateizentren müssen gemeinsam folgen,
   auch bei unterschiedlicher Skalierung. Außerhalb des Blocks sofort rote
   Rückmeldung prüfen. Nach kurzer Eingabepause erscheint bei gültiger Geometrie
   der vollständige heiße Weg mit automatischer Ein-/Ausfahrt, dazu die blau
   gestrichelte G0-Kaltanfahrt ab Maschinennullpunkt auf der positiven X/U-Seite
   bei Y/V = 0. Rohteilnullpunkt links unten ist separat markiert. Ein-/Austritt
   darf nur seitlich oder oben liegen; Anfahrt zur linken Seite führt über den
   Block. Bei Bedarf tatsächliche positive Schalterlagen X/U eintragen;
   leere Felder verwenden +Raumbreite/2. „Schneidweg berechnen“ prüft sofort.
   Start/Ende, Schieberegler und Wiedergabe ausprobieren. Für manuelle Zugänge
   die entsprechende Option aktivieren und gültige Zugangspunkte eintragen.
   Während Ein-/Ausfahrt muss die Zustandszeile G1 und Heizung EIN (M3) anzeigen;
   der orange Draht muss auch innerhalb dieses Satzes kontinuierlich fahren.
   G1-Wiedergabe 1×/10×/50× prüfen. Die Zeit wird aus ausgegebenem F ermittelt;
   G0 bleibt mit 1 s je nicht leerem Satz ausdrücklich schematisch.
6. Alternativ `examples/profil_xy.svg` und `examples/profil_uv.svg` laden, Maße und
   Schnittparameter eingeben und den Weg berechnen. Alle Beispielwerte sind Demodaten.
7. Ein Export benötigt zusätzlich den realen S-Maximalwert und ein passendes,
   bestätigtes Steuerungsprofil. Ohne diese Angaben bleibt die Vorschau verfügbar.
   G-Code prüfen: Start X0/Y0/U0/V0 am zuvor per Kontaktschalter gesetzten
   Maschinennullpunkt; nach M5 nur G0 bis zum Einschaltpunkt mindestens 10 mm
   vor dem Rohteil. Danach M3/S und G1 mit Schneidvorschub über die Luftstrecke
   zur Eintrittskante und weiter zur Kontur. Markierung und Programmphase
   „Heizvorlauf“ prüfen. Ohne 10 mm Freiraum, freie Kaltanfahrt oder außen liegenden Austritt
   bleibt der Export gesperrt. Die Programmausführung ist keine Referenzfahrt.
   Die Zustandszeile muss bei verfügbarem Export „Export rückgelesen und geprüft“
   anzeigen. Die angezeigten G-Code-Zeilennummern mit der Textansicht vergleichen.
   Ohne S-Zuordnung wird eine interne Vorlage ohne erfundenen Hardware-S-Wert
   geprüft; ohne freie Anfahrt bleibt nur die geometrische Ansicht, ohne Wiedergabe.

Diese Prüfung bestätigt die lokale Schnittplanung; Maschinenanbindung und reale
Stromregelung sind nicht implementiert.

## Automatisierte Prüfungen

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Optional unter Windows mit lokal installiertem Microsoft Edge (kein zusätzlicher
WebDriver erforderlich):

```powershell
.\.venv\Scripts\python.exe -m tests.browser_check
```

Mit lokal installiertem Chrome alternativ:

```powershell
.\.venv\Scripts\python.exe -m tests.browser_check --browser chrome
```

Die Browserprüfung startet einen eigenen lokalen Testserver auf einem freien Port
und den gewählten Browser ohne sichtbares Fenster mit temporärem Profil unter `.tmp/`. Sie prüft
Demoauftrag, SVG-Uploads, beidseitige Profilübernahme samt Konturwechsel und
Wiederherstellung des separaten UV-Profils, Lochwerkzeug, Planung, Vorschau, Ansichten,
Leistung/Export und das Verwerfen veralteter Ergebnisse. Zusätzlich prüft sie
Live-Block und Maßlinien vor dem Import, Änderungen der Abstände, Drop-Import,
Zentrierung, sofortige Profilpositionierung und Ein-/Ausfahrtsmarkierungen.
Außerdem prüft sie gekoppeltes Ziehen, Tastatur und Skalierung, automatisches
Platzierungsfeedback, Randzugang/Kaltanfahrt und den Schutz vor alten Live-Antworten.
Seit 0.2.3 zusätzlich getrennte Nullpunkte, G0 vor M3/S, umgerechnete
Maschinenkoordinaten und Exportsperre bei im Rohteil liegendem Maschinenstart.
Seit 0.2.4 zusätzlich Rücklesung der tatsächlichen Exportzeilen, M3/M5-Heizstatus,
G1-Zwischenpositionen und kontinuierliche Ein-/Ausfahrt nach ausgegebenem F.
Die Python-Tests verändern außerdem gezielt Codeausgaben, um eine Exportsperre
bei falschem Vorschub, Positionen oder kalten G1-Ein-/Ausfahrten zu prüfen.
Seit 0.2.5 zusätzlich der rückgelesene 10-mm-Heizvorlauf, alternative
Eintrittsseiten bei fehlendem Seitenabstand und Exportsperre ohne Freiraum.
Browser-Sandboxrestriktionen können ihren Start verhindern.
Dann die oben beschriebenen Schritte manuell im Browser prüfen.

## Nach Änderungen

Bei Änderungen an `requirements.txt` den Installationsbefehl erneut ausführen.
Nach Änderungen am Python-Code, an `version.py` oder an HTML-Vorlagen den Server
neu starten, da der Debug-Modus ausgeschaltet ist und Vorlagen im Speicher bleiben.
Anschließend die Seite neu laden; bei Änderungen an CSS oder JavaScript mit
`Strg+F5` neu laden, damit der Browser aktuelle Dateien verwendet.

Bei Problemen hilft [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
