# Installation und lokaler Start

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

```powershell
.\.venv\Scripts\python.exe app.py
```

Im Browser [http://127.0.0.1:5000](http://127.0.0.1:5000) öffnen.
Mit `Strg+C` im Terminal wird der Server beendet.

Eine Aktivierung der Umgebung ist für diese Befehle nicht erforderlich. Optional:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

## Funktionsprüfung

1. Die Startseite zeigt „HotWireCamSoftware“ an.
2. Gestaltung und Navigation werden dargestellt.
3. Die Fußzeile zeigt die Versionsnummer aus `version.py` (aktuell `0.1.0`).
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
Demoauftrag, SVG-Uploads, Lochwerkzeug, Planung, Vorschau, Ansichten,
Leistung/Export und das Verwerfen veralteter Ergebnisse. Browser-Sandboxrestriktionen können ihren Start verhindern.
Dann die oben beschriebenen Schritte manuell im Browser prüfen.

## Nach Änderungen

Bei Änderungen an `requirements.txt` den Installationsbefehl erneut ausführen.
Nach Änderungen am Python-Code oder an `version.py` den Server neu starten,
da der Debug-Modus ausgeschaltet ist. Änderungen an HTML/CSS im Browser neu laden.

Bei Problemen hilft [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
