#!/bin/bash
ssh pi@192.168.178.59 <<'ENDSSH'
sudo shutdown -h now
sleep 1
ENDSSH
