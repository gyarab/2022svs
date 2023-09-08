#!/bin/bash
# user login recovery script

user=$1;
[[ -n "$user" ]] || err "missing username";

ssh_key=$2;
[[ -n "$ssh_key" ]] || err "missing ssh key";

user_home=$(getent passwd "$user" | cut -d: -f6)

mkdir -p "$user_home/.ssh"
echo "$ssh_key" > "$user_home/.ssh/authorized_keys"

# change owner to $user and set the permissions to
# only allow r/w by owner
chown -R $user: "$user_home/.ssh"
chmod -R u=rwX,go= "$user_home/.ssh"
