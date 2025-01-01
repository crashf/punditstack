#!/bin/bash
# This script will be run during container initialization

# Add NAT rule for traffic routing through WireGuard
iptables -t nat -A POSTROUTING -o wg0 -j MASQUERADE
