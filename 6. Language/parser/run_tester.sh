#!/bin/sh
#
# usage: ./run_tester
#
# runs "python3 parser.py" for each txt file in sentences

clear
for x in $( ls sentences/ | sort -n )
do
    echo "$x\n"
    cat "sentences/$x"
    echo "\n"
    python3 parser.py sentences/$x
    echo "\n*************************************************"
    echo "*************************************************\n"
done