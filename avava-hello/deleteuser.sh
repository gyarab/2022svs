#!/bin/bash
# Safe user deletion script

set -e

function err() {
    echo "ERROR: $@"
    exit 1
}

user=$1
[[ -n "$user" ]] || err "Invalid username"

# Ensure the user exists
if ! id "$user" &>/dev/null; then
    err "User '$user' does not exist."
fi

# Prevent accidental deletion of system users
if [[ "$user" == "root" || "$user" == "$(whoami)" ]]; then
    err "Refusing to delete critical system user: $user"
fi

# Stop all user processes
echo "Terminating all processes for user '$user'..."
pkill -u "$user" || true  # Don't fail if no processes are running

# Remove the user's PostgreSQL database if it exists
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "$user"; then
    echo "Dropping PostgreSQL database for '$user'..."
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS \"$user\";"
    sudo -u postgres psql -c "DROP ROLE IF EXISTS \"$user\";"
fi

# Remove user quotas
echo "Removing quota for '$user'..."
setquota -u "$user" 0 0 0 0 -a || true

# Delete the user and their home directory
echo "Deleting user '$user'..."
userdel -r "$user"

echo "User '$user' has been successfully deleted."
