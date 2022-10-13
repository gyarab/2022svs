
## Vítej na serveru AVAVA!

Bohužel není možné aby tady všichni měli `sudo` práva, takže tu je pár obvyklých
programů nainstalováno.

 - `Node.js 12` - globálně, pokud potřebujete jinou verzi použijte https://github.com/nvm-sh/nvm
   - k tomu je také globálně nainstalované npm
 - `Python 3.10`, `pip3` můžete také využívat
 - `PostgreSQL 14`
   - každý má jeden účet a databázi, vše je zaznamenané ve standradním souboru `~/.pgpass`.

Další limitací je možnost hostovat pouze webové stránky. Toto není moje volba,
ale ze strany GyArab. K hostování něčeho jiného, než webovky je potřeba se dohodnout
s profesorem Kahounem, aby otevřel požadovaný port. Asi mu nemusíte psát sami, můžu to zařídit
kdyžtak za vás :) (sám to také musím povolit ve firewall)

## Webové stránky
Na portu 443 (HTTPS) a 80 (HTTP) běží `caddy` server [1]. Konfigurační soubor lze pouze upravovat
jako root. Normální uživatelé mohou využít příkaz `sudo avava-web`, aby si zaregistrovali doménu
`<cokoliv>.svs.gyarab.cz`^.
```
cokoliv.gyarab.cz {
  # obsah souboru /var/caddy.conf.d/cokoliv
}
```

Caddy si automaticky obstará TLS certifikát, takže bude web fungovat i přes HTTPS. Výchozí
nastavení je zkusit nalézt soubor v `/var/caddy.root.d/cokoliv/` a pokud není nalezen,
tak zkusit reverse proxy.

^ `<cokoliv>` může obsahovat pouze znaky A-Z a-z 0-9 a "-"

[1] https://caddyserver.com/

## Kontakt
Sice je registrační proces automatizovaný, ale neočekávám, že nenastanou problémy, nebo
že tu bude všechno nainstalované, *ptejte se kdyby něco nefungovalo / když něco potřebujete*!

`adam.suchy<at>student.gyarab.cz`


A ještě jednou, prosím nedělejte neplechu :) Logů je dost na osobní identifikaci.

Díky a užívejte
