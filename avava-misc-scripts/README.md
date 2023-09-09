# Miscellaneous scripts for avava management

## avava-db-admin

Should be linked to somewhere in `$PATH` as `avava-psql` and `avava-mysql`. Users should be allowed
to run it with `sudo`. The script then authorizes modifications through the `$SUDO_USER` environment variable.

## podman-recover

Script and a service that should be registered for each user globally. It tries to start all containers
that have their restart policy set to "always".

## avava-install-wordpress

Installs wordpress in a directory for the user...
