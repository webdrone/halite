#!/bin/bash

if hash python3 2>/dev/null; then
    ./halite -q -d "30 30" -t "pypy3 MyBot.py" "pypy3 RandomBot.py"
else
    ./halite -d "30 30" "python MyBot.py" "python RandomBot.py"
fi
