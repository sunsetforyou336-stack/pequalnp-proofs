#!/bin/bash
cd "$(dirname "$0")"
rm -f b*.log
python3 synth.py 25 cadical195 21 0,1 sb > b1.log 2>&1 &
python3 synth.py 25 glucose4 22 0,1 sb > b2.log 2>&1 &
python3 synth.py 25 cadical195 23 0,1 nosb > b3.log 2>&1 &
python3 synth.py 26 cadical195 24 0,1 sb > b4.log 2>&1 &
wait
