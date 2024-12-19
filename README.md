
### Description
MKTXP-Stack is a dockerized monitoring stack for [MKTXP Exporter](https://github.com/akpw/pundit). 

As an out-of-the-box solution, it lets you quickly get up & running with [MKTXP](https://github.com/akpw/pundit), [Prometheus](https://prometheus.io/), and [Grafana](https://grafana.com/) and have multiple Mikrotik RouterOS devices monitored with least amount of configuration. 

While complementary to [MKTXP](https://github.com/akpw/pundit), this project also adds some extra capabilities such an [centralized Mikrotik log processing](https://github.com/akpw/pundit-stack#snmp-centralized-logging-configuration) based on a preconfigured  [syslog-ng](https://www.syslog-ng.com/) / [promtail](https://grafana.com/docs/loki/latest/clients/promtail/) / [Loki](https://grafana.com/docs/loki/latest) stack. 

The project offers multiple [docker compose configurations](https://github.com/akpw/pundit-stack/blob/main/README.md#alternative-docker-compose-configurations), for loading only relevant parts of the stack as well as for multiple log management options.


### Requirements:
[Docker Compose](https://docs.docker.com/compose/install/)


### Install & Getting Started:
 - Clone this repository (or download zip with wget)
```
git clone https://github.com/akpw/pundit-stack.git
cd pundit-stack
```

### Default stack
To go with default full stack, just run docker compose as described above:
```
docker compose -f ./docker-compose-pundit-stack.yml up -d
```

