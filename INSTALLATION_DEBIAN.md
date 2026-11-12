# Installation auf Debian 13 im LXC-Container

Diese Anleitung installiert HotWireCAMSoftware innerhalb eines bereits vorhandenen
Debian-13-LXC-Containers. Der Installer erstellt keinen Container und verändert
keine Einstellungen des LXC-Hosts. Die Einrichtung erfolgt einmalig als `root`;
die Website läuft anschließend mit dem eigenen Benutzer `wyro` ohne Root-Rechte.

## 1. Vorbereitung

- Im LXC-Verwaltungsprogramm einen Debian-13-Container mit systemd bereitstellen
  und starten. Ein privilegierter Container oder Docker ist dafür nicht vorgesehen.
- Der Container benötigt eine IP-Adresse im lokalen Netzwerk, funktionierendes
  DNS und Internetzugriff auf Debian-Paketquellen, GitHub und den Python-Paketindex.
- Die folgenden Befehle in der **Konsole des Containers** ausführen, nicht in der
  Windows-PowerShell und nicht in der Konsole des LXC-Hosts.
- Die neuen Projektdateien müssen zuvor auf GitHub im verwendeten Branch stehen.
  Lokal erstellte Dateien werden nicht automatisch hochgeladen. Ein HTTP-404 beim
  Download kann bedeuten, dass die Installer-Datei noch nicht auf GitHub liegt.

Bei der Container-Konsole als `root` anmelden. Falls bereits als anderer Benutzer
angemeldet, mit diesem Befehl wechseln und das Root-Passwort eingeben:

```bash
su -
```

Die Passworteingabe zeigt keine Zeichen an; das ist normal. Als `root` benötigt
man kein `sudo`. Ein vorangestelltes `$` oder `#` muss bei keinem Befehl mitkopiert werden.

System und Anmeldung prüfen:

```bash
whoami
cat /etc/os-release
ps -p 1 -o comm=
```

Erwartet werden `root`, Debian mit `VERSION_ID="13"` und `systemd`.

## 2. Installer direkt von GitHub herunterladen

Die folgenden Befehle einzeln oder als ganzen Block kopieren. `&&` stellt sicher,
dass nach einem Fehler nicht mit dem nächsten Schritt fortgefahren wird.

```bash
apt-get update &&
apt-get install -y ca-certificates curl &&
curl --fail --location --proto '=https' --tlsv1.2 --retry 3 \
  --output /root/install-hotwirecam.sh \
  https://raw.githubusercontent.com/nicokalmbach/HotWireCAMSoftware/main/scripts/install-debian.sh &&
bash -n /root/install-hotwirecam.sh
```

`bash -n` prüft die Shell-Syntax und führt noch keine Installation aus. Die Datei
kann vor dem Start mit folgendem Befehl gelesen werden:

```bash
cat /root/install-hotwirecam.sh
```

Jetzt starten:

```bash
bash /root/install-hotwirecam.sh
```

Nicht direkt per `curl | bash` starten: Der Installer benötigt die Tastatureingabe.
Der Download des Installers und das anschließende Klonen erfolgen über HTTPS;
eine zusätzliche Signaturprüfung des GitHub-Standes ist nicht implementiert.

## 3. Vorschläge übernehmen

Bei jeder Frage steht der Vorschlag in eckigen Klammern. **Enter übernimmt ihn**.
Du kannst stattdessen einen anderen Wert eingeben und Enter drücken.

| Einstellung | Standard | Bedeutung |
| --- | --- | --- |
| Repository | `https://github.com/nicokalmbach/HotWireCAMSoftware.git` | Öffentliches GitHub-Repository mit allen Projektdateien |
| Branch oder Tag | `main` | Lädt den aktuellen Stand dieses Branches; ein vorhandener Tag ist ebenfalls möglich |
| Benutzer | `wyro` | Neuer Systembenutzer ohne Passwort-Login; kein Administratorkonto |
| Verzeichnis | `/opt/hotwirecam` | Neuer Ordner für Repository und Python-Umgebung |
| Bind-Adresse | `0.0.0.0` | Im lokalen Netzwerk erreichbar; `127.0.0.1` beschränkt auf den Container |
| HTTP-Port | `5001` | Browseradresse verwendet diesen Port; erlaubt sind 1024 bis 65535 |
| Installation beginnen | `j` | Nach angezeigter Zusammenfassung beginnen; `n` bricht ab |

Für die erste Installation kannst du alle Vorschläge mit Enter übernehmen.
Der Installer installiert die APT-Abhängigkeiten, lädt das Repository einschließlich
Dienstvorlage und Python-Anforderungen herunter, erstellt `.venv`, prüft App-Import
und vorhandene Tests und aktiviert den Dienst `hotwirecam.service`. Der Dienst
startet nach jedem Container-Neustart automatisch. Den Fortschritt abwarten;
erst nach erfolgreichem lokalen HTTP-Test erscheint „Installation erfolgreich“.

Das heruntergeladene Repository muss `requirements-debian.txt` und
`scripts/hotwirecam.service.in` enthalten. Bei Auswahl eines älteren Tags ohne
diese Dateien bricht der Installer mit einer Fehlermeldung ab. `main` bezeichnet
keinen festgeschriebenen Release: Für eine feste Version einen tatsächlich
vorhandenen Tag wählen. Ein Tag `v0.1.1` wird vom Installer nicht angelegt.

## 4. Website öffnen

IP-Adresse des Containers anzeigen:

```bash
hostname -I
```

Auf dem eigenen PC im Browser `http://CONTAINER-IP:5001` öffnen. `CONTAINER-IP`
dabei durch die angezeigte LAN-Adresse ersetzen, beispielsweise
`http://192.168.1.50:5001` (nur ein Beispiel, keine vorgegebene Adresse).
`127.0.0.1` auf deinem PC würde auf den PC selbst zeigen, nicht auf den Container.
Bei einem anderen gewählten Port diesen statt `5001` verwenden.

Die Website hat bisher keine Anmeldung und kein HTTPS. Der Standard ist für ein
vertrauenswürdiges lokales Netzwerk vorgesehen, nicht für eine öffentliche
Internetfreigabe. Firewall und Router werden vom Installer nicht verändert.
Falls nötig, am Container beziehungsweise LXC-Host gezielt TCP-Port 5001 für
das eigene Netzwerk erlauben. Ein Portwechsel ersetzt keine Sicherheitsfreigabe.

In der Website die Version `0.2.5` kontrollieren, wenn genau dieser Git-Stand
installiert wurde. Danach „Demobeispiel laden“ und „Schneidweg berechnen“ wählen.
Demoangaben sind keine bestätigten Maschinenparameter. Eine Maschinenanbindung
ist weiterhin nicht implementiert.

## 5. Betrieb: wichtigste Befehle

Diese Befehle wieder als `root` **im Container** ausführen. Der Dienst läuft
selbständig weiter, auch wenn du die Konsole schließt.

Status anzeigen (`active (running)` bedeutet gestartet):

```bash
systemctl status hotwirecam --no-pager
```

Neu starten, stoppen oder starten:

```bash
systemctl restart hotwirecam
```

```bash
systemctl stop hotwirecam
```

```bash
systemctl start hotwirecam
```

Die letzten Fehlermeldungen anzeigen:

```bash
journalctl -u hotwirecam -n 50 --no-pager
```

Lokal im Container prüfen (Port bei Bedarf anpassen):

```bash
curl --fail http://127.0.0.1:5001/
```

HTML-Text ist hier das erwartete Ergebnis; die gestaltete Seite siehst du im Browser.
Installationseinstellungen und tatsächlich heruntergeladenen Git-Commit anzeigen:

```bash
cat /etc/hotwirecam/install.conf
```

Diese Datei enthält Metadaten für ein späteres Update-Script. Eine Änderung dort
ändert den laufenden Dienst noch nicht. Seine aktuelle Konfiguration zeigt:

```bash
systemctl cat hotwirecam
```

## 6. Wenn etwas nicht funktioniert

- **HTTP 404 beim Installer-Download:** Prüfen, ob die neuen Dateien auf GitHub
  im Branch `main` veröffentlicht wurden und das Repository öffentlich lesbar ist.
- **Repository/Branch nicht erreichbar:** Schreibweise, Internetzugang und
  vorhandenen Branch/Tag prüfen. Private Repositories benötigen einen anderen,
  noch nicht implementierten Authentifizierungsablauf; keine Tokens in URLs eingeben.
- **Port belegt:** Der Installer legt keinen Dienst an, wenn bereits ein Prozess
  auf dem gewählten Port lauscht. Prüfen mit `ss -ltnp`; nicht blind fremde Prozesse beenden.
- **Dienst läuft, aber vom PC nicht erreichbar:** Container-IP, gewählten Port,
  Bind-Adresse, LXC-Netzwerk und Firewall prüfen. Funktioniert `curl` im Container,
  ist die Website lokal erreichbar; die Verbindung vom PC muss separat geprüft werden.
- **Installation bricht ab:** Die erste Fehlermeldung und gegebenenfalls die Logs
  notieren. Bereits installierte Pakete, Benutzer und Dateien bleiben erhalten.
  Ein zweiter Installerlauf überschreibt keine Installation. Bei einem Fehler nach
  der Dienstaktivierung kann der Dienst noch aktiviert sein; mit
  `systemctl stop hotwirecam` stoppen und den Fehler untersuchen.
- **systemd-/Berechtigungsfehler im LXC:** Mit der Containerverwaltung prüfen,
  ob Debian 13 mit systemd korrekt läuft. Die Vorlage fordert keine zusätzlichen
  Mount-Namespaces an; eine Ausweitung der Containerprivilegien ist nicht Teil der Anleitung.

## 7. Updates und Prüfstand

Ein Update-Script mit Prüfung, Sicherung und Wiederherstellung ist **geplant**,
aber noch nicht implementiert. Den Erstinstaller nicht zum Aktualisieren verwenden.
Vor Änderungen am installierten System bietet sich ein Container-Backup oder
Snapshot in der Containerverwaltung an. Es gibt noch keinen automatischen Rollback.
Die Python-Abhängigkeiten verwenden Versionsbereiche, keine vollständige Lockdatei.

Der Installer wurde in der Entwicklungsumgebung auf Shell-Syntax, Standardwerte,
Abbruch, eigene Einstellungen und die Ablehnung ungültiger URLs, Benutzer, Pfade
und Ports geprüft. Platzhalter der Dienstvorlage und LF-Zeilenenden sind geprüft.
Die CAM-Tests konnten hier wegen der Windows-Anwendungsrichtlinie beim Laden
von NumPy nicht ausgeführt werden. Eine vollständige Installation in einem echten
Debian-13-LXC-Container ist hier nicht ausgeführt worden. Das muss auf dem
Zielsystem noch validiert werden.

Grundlagen: [Debian 13](https://www.debian.org/releases/trixie/),
[Flask mit Gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/).
