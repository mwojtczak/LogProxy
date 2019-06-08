#!/bin/bash

# get default gateway
DEF=$(route | grep default | awk '/default/ {print $2}')

# setup vpn
cp vpn.conf /etc/vpnc/vpn.conf
vpnc vpn
sleep 5

IP_ADDR=$(ifconfig tun0 | grep "inet" | awk '{print $2}')

# restore default route
route add -net 0.0.0.0/0 gw $DEF

# add new route for vpn traffic
route add -net 10.110.0.0/16 gw $IP_ADDR

# run LogProxy app
python3.6 -t logproxy.py