#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for VER in 2.7 3.3 3.4 3.5
do
    echo
    echo "testing python${VER}"
    python${VER} ${DIR}/run_tests.py
done
