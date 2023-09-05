# Jak nechat aplikaci spuštěnou na pozadí?

Existuje vícero způsobů. Nepůjdu tady moc do detailů... Na internetu je mnoho návodů.

1. Pomocí programu `screen`, nebo `tmux`.

2. Přidání `&` za příkaz. Tento způsob nedoporučuji, protože je pak obtížné se
   k procesu zpátky dostat.

3. Pomocí `systemd` služby (service). Každý uživatel může mít uživatelské
   služby (systemd user services), které mu běží na pozadí. Tento způsob má
   výhodu, že proces je pak plně automaticky spravován a může se pak například
   znovu nastartovat po restartu serveru, nebo po spadnutí aplikace.

Pokud se vám proces vypíná po odhlášení, musíte povolit `loginctl enable-linger`.
