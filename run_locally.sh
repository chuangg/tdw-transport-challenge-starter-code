#!/bin/bash
./TDW/TDW.x86_64 -port=$1 &
conda run --no-capture-output -n transport_challenge_env python tdw-transport-challenge/agent.py  --port $1
