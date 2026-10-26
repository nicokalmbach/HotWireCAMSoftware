# Installation und lokaler Start

## Voraussetzungen

- Python 3.10 oder neuer mit `pip` und `venv`.
- PowerShell unter Windows.
- Projektdateien auf dem lokalen Rechner.

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
4. Import und Export sind deaktiviert und als Platzhalter erkennbar.

Diese Prüfung bestätigt das Grundgerüst; Maschinenfunktionen sind noch nicht implementiert.

## Nach Änderungen

Bei Änderungen an `requirements.txt` den Installationsbefehl erneut ausführen.
Nach Änderungen am Python-Code oder an `version.py` den Server neu starten,
da der Debug-Modus ausgeschaltet ist. Änderungen an HTML/CSS im Browser neu laden.

Bei Problemen hilft [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
