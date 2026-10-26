# Fehlerbehebung

Die folgenden Hinweise beziehen sich auf den lokalen Start unter Windows/PowerShell.

| Problem | Prüfung und Lösung |
| --- | --- |
| `py` wird nicht gefunden | Python-Installation und Python-Launcher prüfen. Wenn `python --version` eine Version ab 3.10 anzeigt, für das Anlegen der Umgebung `python -m venv .venv` verwenden. |
| `.venv\Scripts\python.exe` wird nicht gefunden | Im Projektordner arbeiten und die Umgebung mit `py -m venv .venv` anlegen. |
| `ModuleNotFoundError: No module named 'flask'` | `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` ausführen und die App mit demselben Interpreter starten. |
| PowerShell blockiert `Activate.ps1` | Direkt `.\.venv\Scripts\python.exe app.py` verwenden; dafür ist keine Aktivierung nötig. |
| Port 5000 ist belegt | Eine bereits laufende Projektinstanz im zugehörigen Terminal mit `Strg+C` beenden. Bei einer anderen Anwendung deren Portbelegung prüfen. |
| Browser kann die Seite nicht öffnen | Prüfen, ob der Server ohne Fehlermeldung läuft, und `http://127.0.0.1:5000` verwenden. |
| Gestaltung fehlt oder bleibt veraltet | Seite mit `Strg+F5` neu laden und prüfen, ob `static/css/style.css` vorhanden ist. |
| Angezeigte Version bleibt unverändert | `version.py` speichern, den Server beenden und erneut starten. |
| Import oder Export reagiert nicht | Diese Bereiche sind derzeit deaktivierte Platzhalter. Den Status in der Roadmap prüfen. |

## Ein Problem nachvollziehbar festhalten

Bei ungelösten Problemen die Python-Version, Anwendungsversion, ausgeführten Befehle,
Fehlermeldung sowie erwartetes und tatsächliches Verhalten notieren. Keine Zugangsdaten
oder privaten Konfigurationswerte in Fehlerberichte übernehmen.

Neue wiederkehrende Probleme und bestätigte Lösungen werden bei ihrer Bearbeitung
in dieser Datei ergänzt. Die Einrichtung beschreibt [INSTALLATION.md](INSTALLATION.md).
