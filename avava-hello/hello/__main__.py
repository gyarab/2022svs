import os
from googleoauth import get_email, get_session_token
import pwd
import stat
import syslog
import sys
import traceback


def create_account(username):
    syslog.syslog(f"avava-hello: creating user {username}")
    print("Tvorba novych uctu je v tuto chvili pozastavena")


def recover_account(username):
    syslog.syslog(f"avava-hello: recovering user {username}")
    print(
        'Zadejte novy SSH klic ve forme "ssh-rsa AAAAB3NzaC1yc2E...Q02P1Eamz/nT4I3 root@localhost"'
    )
    key = input("> ")
    user_home = f"/home/{username}"
    os.makedirs(user_home + "/.ssh", exist_ok=True)
    with open(f"/home/{username}/.ssh/authorized_keys", "a+") as f:
        f.write(key + "\n")

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
        syslog.syslog("avava-hello: rejecting token; invalid length")
        print("Neplatny kod")
        return

    token = get_session_token("https://auth.svs.gyarab.cz/redirect", code)
    if token is None:
        syslog.syslog("avava-hello: rejecting token; rejected by google")
        print("Neplatny kod")
        return

    email = get_email(token)
    if email is None:
        syslog.syslog("avava-hello: rejecting token; invalid email?")
        print("Neplatny email?!")
        return
    username = email.split("@")[0]

    print(f"Uspesne prihlasen jako: {username}")
    syslog.syslog(f"avava-hello: user {username} logged in")
    try:
        pwd.getpwnam(username)
    except KeyError:
        ok = input(f"Ucet {username} neexistuje, prejete si ho vytvorit? [Y/n]")
        if ok == "" or ok.lower() == "y":
            create_account(username)
    else:
        ok = input(f"Ucet {username} jiz existuje, ztratili jste pristup? [Y/n]")
        if ok == "" or ok.lower() == "y":
            recover_account(username)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        stk = [
            f"{s[0].split('/')[-1]}:{s[1]}:{s[2]}"
            for s in traceback.extract_tb(sys.exc_info()[2])
        ][:5]
        syslog.syslog(f"avava-hello: ERROR: func stack: {stk}")
        syslog.syslog(f"avava-hello: ERROR: {e.__class__.__name__}: {e}")
        print("Nastala necekana chyba, prosim kontaktujte administratora")

    print()
