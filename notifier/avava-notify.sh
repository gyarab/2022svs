#!/bin/bash
# Toggle email notifications

EMAIL_FILE="/opt/notifier/emails";
USR="$SUDO_USER";
if [ -z "$USR" ]; then
    echo "this script must be run with sudo";
    exit 1;
fi

if grep -q "$USR" "$EMAIL_FILE"; then
    # Disable
    sed -i "/^$USR@/d" "$EMAIL_FILE";
    echo "notifications disabled";
else
    # Enable
    echo "$USR@student.gyarab.cz" >> "$EMAIL_FILE";
    echo "notifications enabled";
fi

