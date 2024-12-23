Description
Pund-IT-Stack is a dockerized monitoring stack for MSRV Clients.

Requirements:
Docker Compose

Install & Getting Started:
Clone this repository (or download zip with wget)
 ```
git clone https://github.com/crashf/punditstack.git
cd pundit-stack
 ```
Default stack
To go with default full stack, just run docker compose as described above:
 ```
docker compose  up -d
 ```

 After install, you must edit config files to add enpoints and install exporters (windws)
 ```
Windows - Prometheus 
1. Install windows exporter on each windows device that will be managed. This can be done from Ninja "Install Windows Exporter (monitoring)" or directly from the github release: https://github.com/prometheus-community/windows_exporter/releases

2. Edit prometheus/prometheus.yml to add in each windows machine by IP/Name (name resolution will only work if the device has ADDNS)
#### Windows Devices
#### Added windows devices with the following format
#### Windows Exporter can be installed from Ninja or https://github.com/prometheus-community/windows_exporter/releases/download/v0.29.2/windows_exporter-0.29.2-arm64.exe
#### msiexec /i <path-to-msi-file> --% ADDLOCAL=FirewallException

#  - job_name: 'DeviceName'
#    scrape_interval: 1m
#    metrics_path: /metrics
#    static_configs:
#    - targets: ['IP Address:9200']

```