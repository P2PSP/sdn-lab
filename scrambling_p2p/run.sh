#!/bin/bash

pid_controller=0

#Config controller
team_size=$1
port=$2
rounds_to_shuffle=$3

cat <<EOM >./scrambling_p2p.conf
[DEFAULT]
team_size = $team_size
port = $port
rounds_to_shuffle = $rounds_to_shuffle
EOM

# Run controller
ryu-manager scrambling_p2p.py --config-file scrambling_p2p.conf --log-file controller.log& 
pid_controller=$!
echo "Preparing the simulation..."
sleep 4

# Run mininet
sudo ./net.py $team_size $port

# When finish, kill controller
kill -9 $pid_controller
