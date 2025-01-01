#!/bin/sh
# Remove the existing default route
ip route del default || true

# Add the new default route via WireGuard
ip route add default via 192.168.254.10

# Start the original container process
exec "$@"
