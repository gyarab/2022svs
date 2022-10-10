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
# TODO: could collide, check that the user does not already exist
db_id=`shuf -i 1000-9999 -n 1`;
db_pass=`pwgen -B -1 15`
{
    echo "CREATE ROLE "db$db_id" LOGIN PASSWORD '$db_pass';";
    echo "CREATE DATABASE "db$db_id" WITH OWNER "db$db_id";";
    echo "REVOKE ALL ON DATABASE "db$db_id" FROM PUBLIC;";
} | psql -h localhost -U postgres
touch "/home/$user/.pgpass";
chown "$user:$user" "/home/$user/.pgpass";
chmod 600 "/home/$user/.pgpass";
echo "localhost:*:*:db$db_id:$db_pass" > "/home/$user/.pgpass";
