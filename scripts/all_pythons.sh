#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for VER in 2.7 3.6 3.7 3.8
do
    echo
    echo "testing python${VER}"
    python${VER} ${DIR}/run_tests.py
done
