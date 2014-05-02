#!/bin/bash

#current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#jump to directory
cd $DIR

#activate virtual enviornment
ACTIVATE="source venv/bin/activate"
$ACTIVATE

osascript &>/dev/null <<EOF
        tell application "iTerm"
            tell current terminal
                launch session "Default Session"
                tell the last session
                    write text "rethinkdb"
                end tell
            end tell
        end tell
EOF

RUNSERVER="python runserver.py"
$RUNSERVER

