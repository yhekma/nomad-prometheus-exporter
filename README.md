# nomad-exporter

uses environment variables to get its config:

* NOMAD_SERVER (default is `nomad.service.consul`)
* NOMAD_PORT (default is `4646`)
* PORT (no default, port to listen on)

Exposes allocations on `/metrics`

See the example nomad file.

For example, if you want to see which allocs died with non-zero exit codes in the last 5 minutes:

```sum by(job, taskgroup, task, dc, alloc_id) (delta(nomad_allocation_exits{exitcode!="0"}[5m]))```

to see the deployments in the last 10 minutes (assuming they were not collected by GC)

```delta(nomad_deployments[10m]) > 0```