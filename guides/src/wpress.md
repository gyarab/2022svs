# Jak nainstalovat wordpress

Instalace wordpressu se provede jednoduše pomocí `avava-install-wordpress`.

Stačí se přihlásit na server a spustit příkaz
`/opt/avava-misc-scripts/avava-install-wordpress ~/wordpress`. Ten za vás
nainstaluje wordpress do složky `wordpress` ve vašem domovském adresáři.

Po spuštění instalátoru stačí následovat pokyny:
```bash
pepa.zdepa@avava:~$ /opt/avava-misc-scripts/avava-install-wordpress ~/wordpress
Jakou si prejete mit domenu? Zdarma muzete mit <cokoliv>.sys.gyarab.cz,
jinak musite domenu vlastnit a mit spravne nastaveny
CNAME zaznam na "svs.gyarab.cz.", nebo A zaznam na IP adresu SVS (viditelna pri prihlaseni)
Domena (napr. mujwp.svs.gyarab.cz, nebo mojedomena.cz): pepuv-wordpress.svs.gyarab.cz
Nainstalovat wordpress do "/home/pepa.zdepa/wordpress"? [y/N]y
~/wprs ~
[+] Running 1/1
 ⠿ Container wordpress-server-1  Started
~
Wordpress úspěšně spuštěn na adrese "https://pepuv-wordpress.svs.gyarab.cz/"
```
> Zkopírovaný výstup z konzole při instalace wordpressu do adresáře `~/wordpress` a s doménou `pepuv-wordpress.svs.gyarab.cz`.

## Odinstalování

Smazání instalace je o něco složitější.

1. Vypnout server pomocí `docker-compose down` v adresáři, kde je nainstalovaný (je v něm soubor `docker-compose.yml`).
2. Smazat adresář s instalací `podman unshare rm -r <adresar s instalaci>`.
3. Smazat domenu `sudo avava-web unregister <domena>`.
4. Smazat databazi, kterou dohledame pomocí `sudo avava-mysql list`, a pak smažeme pomocí `sudo avava-mysql delete dbXXXX`.
