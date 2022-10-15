from pathlib import Path
import sys
import os
import json
import re
import pwd
import stat
import shutil
import random
import requests_unixsocket
import syslog
import traceback


def reload_caddy_cfg():
    with requests_unixsocket.Session() as session:
        root_cfg = Path("/etc/caddy/Caddyfile").read_text()
        resp = session.post(
            "http+unix://%2Fvar%2Fcaddy%2Fcaddy-admin.sock/load",
            headers={"Content-type": "text/caddyfile", "Host": ""},
            data=root_cfg,
        )
        if resp.status_code != 200:
            raise Exception(
                f"Failed to reload caddy config, response code: {resp.status_code}\n{resp.text}"
            )
        return resp


def register(current_user, db) -> int:
    if len(sys.argv) < 3:
        help(None)
        return 0

    domain = sys.argv[2]
    domain_regex = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]$")
    if not re.match(domain_regex, domain):
        syslog.syslog(f"denied registration for {current_user} of '{domain}'")
        print(
            'Domena nesmi zacinat, ci koncit "-". Povolene znaky jsou A-Z, a-z, 0-9 a "-"'
        )
        return 1

    syslog.syslog(f"registering domain '{domain}' for {current_user}")

    if (
        len(list(filter(lambda x: x["user"] == current_user, db))) == 2
        and current_user != "root"
    ):
        syslog.syslog(
            f"denied registering domain for {current_user}, user already has 2 domains"
        )
        print("Kazdy uzivatel muze mit pouze 2 zaregistrovane domeny")
        return 1

    existing = next(filter(lambda x: x["domain"] == domain, db), None)
    if existing is not None:
        syslog.syslog(
            f"denied registering domain for {current_user}, domain already registered"
        )
        print("Tato domena je jiz zaregistrovana")
        return 1

    # create configuration and root
    conf_path = Path("/var/caddy.conf.d") / domain
    root_path = Path("/var/caddy.root.d") / domain
    conf_path.touch(exist_ok=True)
    root_path.mkdir(exist_ok=True)
    usr = pwd.getpwnam(current_user)
    os.chmod(conf_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IROTH | stat.S_IRGRP)
    os.chown(root_path, usr[2], usr[3])
    os.chmod(
        root_path,
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IROTH | stat.S_IXOTH,
    )

    random_port = None
    while (
        not random_port
        or next(filter(lambda x: x["port"] == random_port, db), None) is not None
    ):
        random_port = random.randint(1025, 65535)

    db_entry = {"domain": domain, "user": current_user, "port": random_port}
    db.append(db_entry)

    # write caddyfile and default index.html
    caddyfile = (
        Path("/opt/avava-web/default.Caddyfile")
        .read_text()
        .format(domain=domain, port=random_port)
    )
    conf_path.write_text(caddyfile)
    shutil.copy("/opt/avava-web/default.index.html", root_path / "index.html")
    os.chown(root_path / "index.html", usr[2], usr[3])

    # load new caddy config
    reload_caddy_cfg()
    print(
        f"Domena '{domain}' zaregistrovana. Aplikacni server muzete spustit na portu {random_port}."
    )
    syslog.syslog(
        f"domain '{domain}' registered for {current_user} on port {random_port}"
    )
    return 0


def unregister(current_user, db) -> int:
    if len(sys.argv) < 3:
        help(None)
        return 0

    domain = sys.argv[2]
    entry = next(filter(lambda x: x["domain"] == domain, db), None)
    if entry is None:
        syslog.syslog(
            f"refusing to unregister non-existant domain {domain=}, {current_user=}"
        )
        print("Domena neni zaregistrovana")
        return 1

    if current_user != "root" and entry["user"] != current_user:
        syslog.syslog(f"refusing to unregister domain {domain=}, {current_user=}")
        print("Toto neni vase domena")
        return 1

    ok = input(
        f"Opravdu si prejete odregistrovat domenu '{domain}' a smazat\n"
        f"vsechnu konfiguraci a staticke soubory? [y/N]"
    )
    if ok.lower() != "y":
        return 0

    conf_path = Path("/var/caddy.conf.d") / domain
    conf_path.unlink()
    reload_caddy_cfg()

    root_path = Path("/var/caddy.root.d") / domain
    shutil.rmtree(root_path)

    db.remove(entry)

    print("Domena uspesne odregistrovana")

    return 0


def list_(current_user, db) -> int:
    query = current_user
    if current_user == "root" and len(sys.argv) >= 3:
        query = sys.argv[2]

    domains = list(filter(lambda x: x["user"] == query, db))
    print(f"Domeny uzivatele '{query}':")
    for domain in domains:
        print(f'  - "{domain["domain"]}": port={domain["port"]}')
    if len(domains) == 0:
        print("  zadne")
    return 0


def help(*_) -> int:
    print(
        "Usage: avava-web register|unregister|help|list [cokoliv]\n"
        "  register     Registruje domenu [cokoliv]\n"
        "  unregister   Deregistruje domenu [cokoliv]\n"
        "  help         Vypise tuto zpravu\n"
        "  list         Vypise vsechny domeny aktualniho uzivatele\n\n"
        "Skript pro automatickou registraci domeny a HTTP(S) serveru."
    )
    return 0


def main():
    if pwd.getpwuid(os.getuid())[0] != "root":
        print("Tento skript lze pouze spustit jako root: sudo avava-web ...")
        return 1

    if len(sys.argv) < 2:
        help(None)
        return 0

    commands = {
        "register": register,
        "unregister": unregister,
        "help": help,
        "list": list_,
    }
    cmd = commands.get(sys.argv[1], help)

    db_file = Path("/var/avava-web/db.json")
    if not db_file.exists():
        os.makedirs("/var/avava-web", exist_ok=True)
        db = []
    else:
        with db_file.open("r") as f:
            db = json.load(f)

    current_user = os.getenv("SUDO_USER", "root")

    code = cmd(current_user, db)

    if code == 0:
        with db_file.open("w+") as f:
            json.dump(db, f)

    return code


if __name__ == "__main__":
    lockfile = Path("/tmp/avava-web.lock")
    if lockfile.exists():
        print("Zkuste to znovu. Jedna instance avava-web jiz bezi.")
        exit(1)
    lockfile.touch()
    try:
        code = main()
    except Exception as e:
        stk = [
            f"{s[0].split('/')[-1]}:{s[1]}:{s[2]}"
            for s in traceback.extract_tb(sys.exc_info()[2])
        ][:5]
        syslog.syslog(syslog.LOG_ERR, f"ERROR: func stack: {stk}")
        syslog.syslog(syslog.LOG_ERR, f"ERROR: {e.__class__.__name__}: {e}")
        print("Nastala neocekavana chyba, prosim kontaktujte administratora")
        exit(1)
    finally:
        lockfile.unlink()
    exit(code)
