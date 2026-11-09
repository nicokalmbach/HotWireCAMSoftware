#!/usr/bin/env bash
# Erstinstallation innerhalb eines Debian-13-Containers, nicht auf dem LXC-Host.
set -Eeuo pipefail
export LC_ALL=C.UTF-8
umask 022

die() { printf 'Fehler: %s\n' "$*" >&2; exit 1; }
trap 'printf "Installation abgebrochen (Zeile %s). Bereits ausgefuehrte Schritte bleiben erhalten; siehe INSTALLATION_DEBIAN.md.\n" "$LINENO" >&2' ERR

if [[ ${1:-} == --help ]]; then
    printf 'Aufruf: bash install-debian.sh\nInteraktive Erstinstallation auf Debian 13 mit systemd. Enter uebernimmt Vorschlaege.\n'
    exit 0
fi
[[ $# == 0 ]] || die 'Unbekannte Argumente. Hilfe: --help'
[[ $EUID == 0 ]] || die 'Bitte innerhalb des Containers als root ausfuehren (su -).'
[[ -r /etc/os-release ]] || die '/etc/os-release fehlt.'
# shellcheck source=/dev/null
source /etc/os-release
[[ ${ID:-} == debian && ${VERSION_ID:-} == 13 ]] || die 'Dieser Installer ist fuer Debian 13 vorgesehen.'
[[ -d /run/systemd/system ]] || die 'systemd muss im Container als Init-System laufen.'
[[ -t 0 ]] || die 'Interaktives Terminal erforderlich. Datei herunterladen, dann mit bash starten; nicht curl | bash verwenden.'

ask() {
    local reply
    read -r -p "$2 [$3]: " reply || die 'Eingabe abgebrochen.'
    printf -v "$1" '%s' "${reply:-$3}"
}

printf 'HotWireCAM: Debian-13-Erstinstallation\nEnter uebernimmt jeweils den Wert in eckigen Klammern.\n'
ask repo 'Oeffentliches GitHub-Repository' 'https://github.com/nicokalmbach/HotWireCAMSoftware.git'
ask ref 'Git-Branch oder Tag' 'main'
ask app_user 'Neuer Dienstbenutzer (ohne Login)' 'wyro'
ask app_dir 'Neues Installationsverzeichnis unter /opt' '/opt/hotwirecam'
ask bind_host 'Bind-Adresse (0.0.0.0 = lokales Netzwerk; 127.0.0.1 = nur Container)' '0.0.0.0'
ask port 'HTTP-Port (1024 bis 65535)' '5001'

[[ $repo =~ ^https://github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+\.git$ ]] || die 'Erwartet wird https://github.com/OWNER/REPO.git (ohne Zugangsdaten).'
[[ $ref =~ ^[A-Za-z0-9][A-Za-z0-9._/-]*$ && $ref != *..* ]] || die 'Ungueltiger Branch/Tag.'
[[ $app_user =~ ^[a-z][a-z0-9_-]{0,30}$ ]] || die 'Benutzername: Kleinbuchstaben, Ziffern, _ oder -; mit Buchstaben beginnen.'
[[ $app_dir =~ ^/opt/[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]] || die 'Erwartet wird /opt/NAME ohne Leerzeichen oder Unterverzeichnisse.'
[[ $bind_host == 0.0.0.0 || $bind_host == 127.0.0.1 ]] || die 'Als Bind-Adresse ist 0.0.0.0 oder 127.0.0.1 erlaubt.'
[[ $port =~ ^[0-9]{4,5}$ ]] || die 'Ungueltiger Port.'
port=$((10#$port))
(( port >= 1024 && port <= 65535 )) || die 'Port muss zwischen 1024 und 65535 liegen.'

config_dir=/etc/hotwirecam
state_dir=/var/lib/hotwirecam
unit=/etc/systemd/system/hotwirecam.service
for target in "$app_dir" "$config_dir" "$state_dir" "$unit"; do
    [[ ! -e $target && ! -L $target ]] || die "Bereits vorhanden: $target. Keine Neuinstallation ueber bestehende Daten; Update-Script ist noch geplant."
done
! getent passwd "$app_user" >/dev/null || die 'Benutzer existiert bereits. Einen neuen, eigenen Dienstbenutzer waehlen.'
! getent group "$app_user" >/dev/null || die 'Gruppe existiert bereits. Einen anderen Namen waehlen.'
! systemctl cat hotwirecam.service >/dev/null 2>&1 || die 'Ein Dienst hotwirecam.service existiert bereits.'

printf '\nRepository: %s\nBranch/Tag: %s\nBenutzer: %s\nVerzeichnis: %s\nAdresse: %s:%s\n' "$repo" "$ref" "$app_user" "$app_dir" "$bind_host" "$port"
printf 'Installiert APT-Pakete, Git-Quellcode und Python-Pakete; aktiviert hotwirecam.service.\nDie Website hat keine Anmeldung: nur in einem vertrauenswuerdigen Netz betreiben.\n'
ask confirm 'Installation beginnen? j = ja, n = nein' 'j'
[[ $confirm == j || $confirm == J ]] || { printf 'Keine Aenderungen vorgenommen.\n'; exit 0; }

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl git python3 python3-venv python3-dev build-essential libgeos-dev iproute2
if ss -H -ltn "sport = :$port" | grep -q .; then
    die "Port $port ist bereits belegt. Es wurde kein Dienst angelegt."
fi
# Vor Benutzeranlage pruefen, ob der gewaehlte Branch/Tag herunterladbar ist.
export GIT_TERMINAL_PROMPT=0
git ls-remote --exit-code "$repo" "refs/heads/$ref" "refs/tags/$ref" >/dev/null || die 'Repository oder Branch/Tag nicht erreichbar.'
useradd --system --user-group --home-dir "$state_dir" --create-home --shell /usr/sbin/nologin "$app_user"
install -d -o "$app_user" -g "$app_user" -m 0755 "$app_dir"
as_app() { runuser -u "$app_user" -- env HOME="$state_dir" GIT_TERMINAL_PROMPT=0 "$@"; }
as_app git clone --branch "$ref" --single-branch -- "$repo" "$app_dir"
for required in app.py version.py requirements-debian.txt scripts/hotwirecam.service.in; do
    [[ -f $app_dir/$required ]] || die "Im GitHub-Stand fehlt $required. Zuerst die Installer-Dateien auf GitHub bereitstellen."
done
as_app python3 -m venv "$app_dir/.venv"
as_app "$app_dir/.venv/bin/python" -m pip install -r "$app_dir/requirements-debian.txt"
(
    cd "$app_dir"
    as_app .venv/bin/python -c 'from app import app; import version; print("Installierte Version:", version.__version__)'
    as_app .venv/bin/python -m unittest discover -s tests -v
)

commit=$(as_app git -C "$app_dir" rev-parse HEAD)
install -d -m 0755 "$config_dir"
# Metadaten fuer das spaetere Update-Script. Root-eigene Datei, kein Passwort.
printf 'REPOSITORY=%s\nGIT_REF=%s\nINSTALLED_COMMIT=%s\nAPP_USER=%s\nAPP_DIR=%s\nBIND_HOST=%s\nPORT=%s\n' \
    "$repo" "$ref" "$commit" "$app_user" "$app_dir" "$bind_host" "$port" > "$config_dir/install.conf"
chmod 0644 "$config_dir/install.conf"
sed -e "s|@APP_USER@|$app_user|g" -e "s|@APP_DIR@|$app_dir|g" \
    -e "s|@BIND_HOST@|$bind_host|g" -e "s|@PORT@|$port|g" \
    "$app_dir/scripts/hotwirecam.service.in" > "$unit"
chmod 0644 "$unit"
systemctl daemon-reload
systemctl enable --now hotwirecam.service
healthy=false
for ((attempt=0; attempt<30; attempt++)); do
    if systemctl is-active --quiet hotwirecam.service && curl --fail --silent --max-time 2 "http://127.0.0.1:$port/" >/dev/null; then
        healthy=true
        break
    fi
    sleep 1
done
if [[ $healthy != true ]]; then
    journalctl -u hotwirecam.service -n 40 --no-pager >&2
    die 'Dienst nicht erreichbar. Installation bleibt zur Diagnose erhalten.'
fi
printf '\nInstallation erfolgreich. Dienst startet beim Containerstart automatisch.\n'
if [[ $bind_host == 0.0.0.0 ]]; then
    printf 'Container-IP(s): %s\nIm Browser: http://CONTAINER-IP:%s\n' "$(hostname -I)" "$port"
else
    printf 'Nur im Container erreichbar: http://127.0.0.1:%s\n' "$port"
fi
printf 'Status: systemctl status hotwirecam --no-pager\nLogs: journalctl -u hotwirecam -n 50 --no-pager\nEinstellungen: %s/install.conf\n' "$config_dir"
