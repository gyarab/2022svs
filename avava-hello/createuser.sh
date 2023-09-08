#!/bin/bash
# user creation and restriction script
# AT NO POINT SHOULD THE EXECUTION OF THIS SCRIPT BE AFFECTED
# BY A USER, IT SHALL NOT BE KILLED BEFORE IT FINISHES EXECUTION

set -e;

function err() {
    echo "ERROR: $@";
    exit 1;
}

user=$1;
[[ -n "$user" ]] || err "Invalid username";

# create user
useradd "$user";

# change default shell to bash
usermod --shell /bin/bash "$user";

# create user home folder
mkdir "/home/$user";
chown "$user:$user" "/home/$user";
chmod u=rwx,g=,o= "/home/$user";

# copy VITEJ file
sudo -u "$user" cp /opt/avava-hello/VITEJ.md "/home/$user/VITEJ.md"

# set quotas to 15G soft 20G hard, do not restrict
# inode counts
setquota -u "$user" 15G 20G 0 0 -a;

# create authorized_keys file
sudo -u "$user" mkdir -p "/home/$user/.ssh";
sudo -u "$user" touch "/home/$user/.ssh/authorized_keys";
chmod 600 "/home/$user/.ssh/authorized_keys";

# create database user
check_collision() {
    psql -U postgres -lqt | cut -d \| -f 1 | grep -qw $1
}

# create a default DB for the user if we have the script for it
if [[ -x "/opt/avava-misc-scripts/avava-psql" ]]; then
    db="$(SUDO_USER="$user" /opt/avava-misc-scripts/avava-psql --script new default-db)"
    db_id="$(cut -d " " -f 1 <<< "$db")"
    db_pass="$(cut -d " " -f 2 <<< "$db")"

    # Add DB login info to .pgpass and set PGUSER in .profile
    touch "/home/$user/.pgpass";
    chown "$user:$user" "/home/$user/.pgpass";
    chmod 600 "/home/$user/.pgpass";
    echo "localhost:*:*:$db_id:$db_pass" > "/home/$user/.pgpass";
    echo -e "# Set default psql user to the one generated by avava-hello\nexport PGUSER=\"$db_id\"" >> "/home/$user/.profile";
fi;
