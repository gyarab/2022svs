### avava-web

`avava-web` je skript pro zprostředkování konfigurace http proxy `caddy` pro normální uživatele.

Každý si pomocí `sudo avava-web register <cokoliv>` může zaregistrovat subdoménu `<cokoliv>.svs.gyarab.cz`.
`avava-web` vytvoří nový konfigurační soubor `/var/caddy.conf.d/cokoliv` a složku `/var/caddy.root.d/cokoliv/` pro
HTML root. Každý uživatel může mít nanejvýš 2 zaregistrované domény.

Uživatelé si kvůli bezpečnosti nemohou konfigurační soubor upravovat. Je-li ho potřeba upravit,
kontaktujte administrátora. Výchozí konfigurace zkouší najít soubor v HTML root složce, pokud ho nenajde, zkusí
reverse proxy.

`avava-web unregister <cokoliv>` odregistruje doménu. Tuto funkci může použít pouze původní uživatel, který doménu
registroval, nebo `root`.
