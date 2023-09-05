# Kontejnery na AVAVě

Na serveru je nainstalovaný `podman` [1]. Vzhledem k tomu, že normální
uživatelé nemají přístup k rootu, musí kontejnery běžet v tzv. rootless
módu. To může věci trochu komplikovat, ale většinou to nedělá moc problémů.

Příkaz `podman` funguje úplně stejně jako `docker`.

## Nastavení porstředí

1. `loginctl enable-linger` - povolení zanechání běžících procesů po odhlášení
2. `systemctl --user enable --now podman.socket` - zapnutí podman serveru pro
   `docker-compose` a restartovací službu.

   Každý uživatel má také nastavenou službu pro restartování kontejnerů, který
   mají restart policy nastavenou na `always`.

## docker-compose

Nejlepší způsob, jak interagovat s podmanem pokud už umíte docker, je přes
`docker-compose`. Aby příkaz fungoval musíte mít spuštěný podman server (viz výše).

## Síť

V kontejnerech by měla být standardní síť a porty by měli jít otevírat stejně,
jako za normálních podmínek.

Ve výchozím stavu ale není povoleno se připojovat na hostovací stroj. Pokud se
potřebujete připojit na host (třeba kvůli databázi), pak je potžeba
specifikovat parametr pro `slirp4netns`:

1. V podman CLI pomocí parametru `--network slirp4netns:allow_host_loopback=true`
2. V `docker-compose.yml`:

```
services:
  tvuj-kontejner:
    [...]
    network_mode: "slirp4netns:allow_host_loopback=true"
    [...]
```

Host pak bude mít uvnitř kontejneru adresu `10.0.2.2`.


[1] https://podman.io/
