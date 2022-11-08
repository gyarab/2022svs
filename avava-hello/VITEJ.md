
# Vítej na serveru AVAVA!

> Soubor lze otevřít na webu:
> https://svs.gyarab.cz/VITEJ.md

## Jak je možné se připojit?

Ze školní sítě je možné se připojit pomocí vašeho hesla. Mimo školní síť je potřeba použít
veřejný klíč. avava-hello podporuje jen veřejné klíče.

## Co je tu nainstalované?

Bohužel není možné aby tady všichni měli `sudo` práva, takže tu je pár obvyklých
programů nainstalováno.

 - `Node.js 12` - globálně, pokud potřebujete jinou verzi použijte https://github.com/nvm-sh/nvm
   - k tomu je také globálně nainstalované npm
 - `Python 3.10`, `pip3` můžete také využívat
 - `PostgreSQL 14`
   - každý má jeden účet a databázi, vše je zaznamenané ve standradním souboru `~/.pgpass`.
   - V `~/.profile` je také přednastavené PGUSER, takže je možné se na DB
     jednoduše připojit pomocí `psql`.

Pokud je potřeba něco doinstalovat, napište administrátorovi.

## Co je tu možné hostovat?

Hostovat je možné jen webové stránky. Toto není moje volba, ale ze strany
GyArab. K hostování něčeho jiného, než webovky je potřeba se dohodnout s
profesorem Kahounem, aby otevřel požadovaný port. Asi mu nemusíte psát sami,
můžu to zařídit kdyžtak za vás :) (sám to také musím povolit ve firewall)

Není ale však všeho konec! Přes SSH si můžete služby na svůj počítač protunelovat,
nebo popřípadě z počítače tunelovat na server.

## Webové stránky

Na portu 443 (HTTPS) a 80 (HTTP) běží `caddy` server [1]. Konfigurační soubor lze pouze upravovat
jako root. Normální uživatelé mohou využít příkaz `sudo avava-web`, aby si zaregistrovali doménu
`<cokoliv>.svs.gyarab.cz`^.

Caddy si automaticky obstará TLS certifikát, takže bude web fungovat i přes HTTPS. Výchozí
nastavení je zkusit nalézt soubor v `/var/caddy.root.d/cokoliv/` a pokud není nalezen,
tak zkusit reverse proxy na zvolený port.

Schéma:
```
   Uživatel           |           Caddy (cokoliv.svs.gyarab.cz:443)   |     Aplikační server (localhost:<zvoleny port>)
   GET /index.html ---|-->  Je soubor /index.html                     |
                      |     v /var/caddy.root.d/cokoliv?              |
                      |     ANO!                                      |
                   <--|---  200 OK ... (soubor)                       |
                      |                                               |
   GET /api/status ---|-->  Je soubor /api/status                     |
                      |     v /var/caddy.root.d/cokoliv?              |
                      |     NE =>                  GET /api/status ---|-->   Interní logika
                      |                                               |      zpracuje request
                   <--|---              Přeposílám                 <--|---   200 OK ... (něco)
                      |                                               |
```

^ `<cokoliv>` může obsahovat pouze znaky A-Z a-z 0-9 a "-"

[1] https://caddyserver.com/

## Kontakt

Sice je registrační proces automatizovaný, ale neočekávám, že nenastanou problémy, nebo
že tu bude všechno nainstalované, *ptejte se kdyby něco nefungovalo / když něco potřebujete*!

`adam.suchy<at>student.gyarab.cz`


A ještě jednou, prosím nedělejte neplechu :) Logů je dost na osobní identifikaci.

Díky a užívejte
