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
3. Die Fußzeile zeigt die Versionsnummer aus `version.py` (aktuell `0.1.1`).
4. „Demobeispiel laden“ wählen, anschließend „Schneidweg berechnen“.
5. Das Drahtmodell erscheint; Schieberegler, Wiedergabe und XY-/UV-Ansicht ausprobieren.
6. Alternativ `examples/profil_xy.svg` und `examples/profil_uv.svg` laden, Maße und
   Schnittparameter eingeben und den Weg berechnen. Alle Beispielwerte sind Demodaten.
7. Ein Export benötigt zusätzlich den realen S-Maximalwert und ein passendes,
   bestätigtes Steuerungsprofil. Ohne diese Angaben bleibt die Vorschau verfügbar.

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

Die Browserprüfung startet einen eigenen lokalen Testserver auf einem freien Port
und Edge ohne sichtbares Fenster mit temporärem Profil unter `.tmp/`. Sie prüft
Demoauftrag, SVG-Uploads, beidseitige Profilübernahme samt Konturwechsel und
Wiederherstellung des separaten UV-Profils, Lochwerkzeug, Planung, Vorschau, Ansichten,
Leistung/Export und das Verwerfen veralteter Ergebnisse. Browser-Sandboxrestriktionen können ihren Start verhindern.
Dann die oben beschriebenen Schritte manuell im Browser prüfen.

## Nach Änderungen

Bei Änderungen an `requirements.txt` den Installationsbefehl erneut ausführen.
Nach Änderungen am Python-Code oder an `version.py` den Server neu starten,
da der Debug-Modus ausgeschaltet ist. Änderungen an HTML/CSS im Browser neu laden.

Bei Problemen hilft [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
