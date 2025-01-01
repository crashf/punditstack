#!/bin/bash
iptables -t nat -A POSTROUTING -o wg0 -j MASQUERADE
