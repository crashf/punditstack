#!/bin/sh
# Remove the existing default route
ip route del default || true

# Add the new default route via WireGuard
ip route add default via 192.168.254.10
ip route add 10.8.0.0/24 via 192.168.254.10
ip route add 10.0.0.0/8 via 192.168.254.1
ip route add 172.16.0.0/12 via 192.168.254.1
ip route add 192.168.0.0/16 via 192.168.254.1
# Start the original container process
exec "$@"
