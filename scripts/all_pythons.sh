#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for VER in 2.7 3.2 3.3 #2.6 to be added later
do
    python${VER} ${DIR}/run_tests.py
done
