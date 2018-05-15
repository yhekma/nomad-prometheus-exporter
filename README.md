# nomad-exporter

uses environment variables to get its config:

* NOMAD_SERVER (default is `nomad.service.consul`)
* NOMAD_PORT (default is `4646`)
* PORT (no default, port to listen on)

Exposes allocations on `/metrics`

See the example nomad file.

For example, if you want to see which allocs restarted in the last 5 minutes:

```sum(delta(nomad_allocation_restarts[5m])) by (jobname, taskname) > 0```