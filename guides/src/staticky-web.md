# Statický web

Hostování statických stránek je velmi jednoduché:

1. Přihlašte se na AVAVu přes SSH

2. Spusťte příkaz `sudo avava-web register <domena>`. Doména může být
   `<cokoliv>.svs.gyarab.cz`, nebo jakákoliv jiná správně nasměrovaná doména.
   IPv4 adresu serveru lze vidět po přihlášení přes SSH.

3. Nahrajte soubory do `/var/caddy.root.d/<domena>`. Toto můžete udělat
   například přes SFTP připojení ve FileZilla programu. Tento typ připojení
   využívá SSH, takže se přihlašte stejným způsobem, jako v příkazové řádce.

   Na síti gyarab je možné se přihlásit heslem, mimo interní síť je ale potřeba
   se přihlašovat pomocí SSH klíče.
