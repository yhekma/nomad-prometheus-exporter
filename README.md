# nomad-exporter

uses environment variables to get its config:

* NOMAD_SERVER (default is `nomad.service.consul`)
* NOMAD_PORT (default is `4646`)
* PORT (no default, port to listen on)

Exposes allocations on `/metrics`

See the example nomad file.