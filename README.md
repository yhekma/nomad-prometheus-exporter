# nomad-exporter

uses environment variables to get its config:

* NOMAD_SERVER (default is `nomad.service.consul`)
* NOMAD_PORT (default is `4646`)
* PORT (no default, port to listen on)

Exposes allocations on `/metrics`

See the example nomad file.

For example, if you want to see which allocs restarted in the last 5 minutes (assuming they were not collected by GC):

```sum(delta(nomad_allocation_restarts[5m])) by (jobname, taskname) > 0```

to see the deployments in the last 10 minutes (assuming they were not collected by GC)

```delta(nomad_deployments[10m]) > 0```