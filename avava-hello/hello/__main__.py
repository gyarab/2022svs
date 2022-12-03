import os
from googleoauth import get_email, get_session_token
import pwd
import stat
import syslog
import sys
import traceback
import signal
import subprocess
from base64 import b64decode
import binascii


def check_ssh_key_format(key: str) -> bool:
    """
    Checks if input is a correct ssh key, it must not have any ssh options before it.

    Follows:
    https://man.openbsd.org/sshd#AUTHORIZED_KEYS_FILE_FORMAT
    """
    parts = key.split(" ")

    # the key may or may not have a comment
    if len(parts) < 2 or len(parts) > 3:
        return False

    type = parts[0]
    b64key = parts[1]

    # check that the key starts correctly with
    # a known type
    if type not in (
        "sk-ecdsa-sha2-nistp256@openssh.com",
        "ecdsa-sha2-nistp256",
        "ecdsa-sha2-nistp384",
        "ecdsa-sha2-nistp521",
        "sk-ssh-ed25519@openssh.com",
        "ssh-ed25519",
        "ssh-dss",
        "ssh-rsa",
    ):
        return False

    try:
        # try to decode the base64 encoded string
        b64decode(b64key)
    except binascii.Error:
        return False

    return True


def create_account(username):
    syslog.syslog(f"creating user {username}")

    # ignore all kill/interrupt/hup signals, we must now quit during the
    # user creation process
    sighup_orig = signal.signal(signal.SIGHUP, signal.SIG_IGN)
    sigint_orig = signal.signal(signal.SIGINT, signal.SIG_IGN)
    sigter_orig = signal.signal(signal.SIGTERM, signal.SIG_IGN)
    try:
        output = subprocess.check_output(["/opt/avava-hello/createuser.sh", username])
        syslog.syslog(f"createuser.sh output:\n{output.decode()}")
    except subprocess.CalledProcessError as e:
        syslog.syslog(
            syslog.LOG_ERR,
            f"ERROR: createuser.sh returned code {e.returncode}:\n{e.output.decode()}",
        )
        print(
            "Nastala neocekavana chyba pri tvorbe uctu. Prosim kontaktujte administratora."
        )
        return

    # restore kill signals
    signal.signal(signal.SIGHUP, sighup_orig)
    signal.signal(signal.SIGINT, sigint_orig)
    signal.signal(signal.SIGTERM, sigter_orig)

    print(
        f"\nUcet {username} byl uspesne vytvoren, prihlaseni je mozne pouze pres\n"
        "SSH klice (Google: SSH private/public key authentication).\n\n"
        "Prosim vytvorte si klic a vlozte sem jeho verejnou cast\n"
        've forme "ssh-rsa AAAAB3NzaC1yc2E...Q02P1Eamz/nT4I3 root@localhost" (OpenSSH format)'
    )

    ssh_key = ""
    while True:
        ssh_key = input("> ").strip().strip('"')
        if check_ssh_key_format(ssh_key):
            break
        print("Toto nevypada jako spravne naformatovany klic. Zkuste to znovu:")

    with open(f"/home/{username}/.ssh/authorized_keys", "a+") as f:
        f.write(ssh_key + "\n")

    print(
        "\nKlic pridan do authorized_keys, zkuste se prihlasit. Vice informaci\n"
        "muzete nalezt v souboru ~/VITEJ.md (nebo web: svs.gyarab.cz/vitej) pote\n"
        "co se prihlasite. Pokud mate problemy s prihlasenim, obratte se na\n"
        "adam.suchy<at>student.gyarab.cz, rad vam pomuzu :)\n\n"
        f"ssh {username}@svs.gyarab.cz"
    )


def recover_account(username):
    syslog.syslog(f"recovering user {username}")
    print(
        'Zadejte novy SSH klic ve forme "ssh-rsa AAAAB3NzaC1yc2E...Q02P1Eamz/nT4I3 root@localhost" (OpenSSH format)'
    )
    ssh_key = ""
    while True:
        ssh_key = input("> ").strip().strip('"')
        if check_ssh_key_format(ssh_key):
            break
        print("Toto nevypada jako spravne naformatovany klic. Zkuste to znovu:")

    user_home = f"/home/{username}"
    os.makedirs(user_home + "/.ssh", exist_ok=True)

    # overwrite old authorized_keys file in case it got corrupted
    with open(f"/home/{username}/.ssh/authorized_keys", "w+") as f:
        f.write(ssh_key + "\n")

    # fix permissions
    user = pwd.getpwnam(username)
    os.chown(user_home + "/.ssh", user[2], user[3])
    os.chown(user_home + "/.ssh/authorized_keys", user[2], user[3])
    os.chmod(user_home + "/.ssh/authorized_keys", stat.S_IRUSR | stat.S_IWUSR)

    print("Klic pridan do authorized_keys, zkuste se prihlasit")


def main():
    code = os.getenv("SSH_ORIGINAL_COMMAND", "")

    print(
        """\u001b[0;34m
            .:-========-:
          -===+=+***+==+===.
        :+-=+-.:#%%%%=.:==-+:     \u001b[1mVitejte na serveru AVAVA!\u001b[0;34m
       -*:+=   ##%+*#%-  ::       \u001b[0mRegistrace a administrace\u001b[0;34m
      :#.*-  .##%= .##%=
      +=-*  .##%=   .#%%=
      +=-* .###*====-+*+*=
      :#.*=*%%*========+:+=
       -*.*%%=         :#:+=
        -#:-*-.       .:+= +=
       .#%%+=++==---===+==*:+=
       =++- .:-===++===-: := =.
    \u001b[0m
    Pro vytvoreni noveho uctu se prihlaste pomoci sveho studentskeho 
    @student.gyarab.cz Google uctu zde: \u001b[4mhttps://auth.svs.gyarab.cz/\u001b[0m.
"""
    )

    if len(code) == 0:
        code = input("Vygenerovany kod: ")

    if len(code) > 128 or len(code) <= 0:
        syslog.syslog("rejecting token; invalid length")
        print("Neplatny kod")
        return

    token = get_session_token("https://auth.svs.gyarab.cz/redirect", code)
    if token is None:
        syslog.syslog("rejecting token; rejected by google")
        print("Neplatny kod")
        return

    email = get_email(token)
    if email is None:
        syslog.syslog(syslog.LOG_WARNING, "rejecting token; invalid email?")
        print("Neplatny email?!")
        return
    username, domain = email.split("@")
    if domain != "student.gyarab.cz":
        syslog.syslog(
            syslog.LOG_WARNING,
            f"rejecting token; email not from gyarab {username}@{domain}",
        )
        print("Ucet neni z gyarab. Prosim pouzijte svuj studentsky ucet.")
        return
    if "+" in username:
        syslog.syslog(
            syslog.LOG_WARNING, f"rejecting token; email has contains a + '{username}'"
        )
        print(
            'The "+" character is not allowed in emails. Please use your address directly.'
        )
        return

    print(f"Uspesne prihlasen jako: {username}")
    syslog.syslog(f"user {username} logged in")
    try:
        pwd.getpwnam(username)
    except KeyError:
        ok = input(f"Ucet {username} neexistuje, prejete si ho vytvorit? [Y/n]")
        if ok == "" or ok.lower() == "y":
            create_account(username)
    else:
        ok = input(
            f"Ucet {username} jiz existuje, ztratili jste pristup?\n(tato akce smaze vsechny predchozi nahrane klice) [Y/n]"
        )
        if ok == "" or ok.lower() == "y":
            recover_account(username)


if __name__ == "__main__":
    syslog.openlog("avava-hello")

    try:
        main()
    except Exception as e:
        stk = [
            f"{s[0].split('/')[-1]}:{s[1]}:{s[2]}"
            for s in traceback.extract_tb(sys.exc_info()[2])
        ][:5]
        syslog.syslog(syslog.LOG_ERR, f"ERROR: func stack: {stk}")
        syslog.syslog(syslog.LOG_ERR, f"ERROR: {e.__class__.__name__}: {e}")
        print("Nastala neocekavana chyba, prosim kontaktujte administratora")
    except KeyboardInterrupt:
        pass

    print()
