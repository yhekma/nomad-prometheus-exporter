job "nomad-exporter" {
  datacenters = ["zone1", "zone2", "zone3"]

  type = "service"

  constraint {
    attribute = "${node.class}"
    value     = "ops"
  }

  update {
    max_parallel     = 1
    auto_revert      = "true"
    health_check     = "checks"
    min_healthy_time = "10s"
    healthy_deadline = "90s"
    stagger          = "1m"
  }

  group "nomad-exporter" {
    count = 1

    task "nomad-exporter" {
      driver = "docker"

      config {
        image = "dock.es.ecg.tools/csi/nomad-exporter:0.1"

        auth {
          username = "[[.docker_username]]"
          password = "[[.docker_password]]"
        }

        network_mode = "host"
      }

      env {
        PORT = "${NOMAD_PORT_nomad_exporter_port}"
      }

      service {
        name = "nomadexporter"
        port = "nomad_exporter_port"

        tags = [
          "nomadexporter",
          "prometheus",
        ]

        check {
          type     = "http"
          name     = "nomadexporter"
          path     = "/metrics"
          port     = "nomad_exporter_port"
          interval = "10s"
          timeout  = "5s"
        }
      }

      resources {
        cpu    = 50
        memory = 50

        network {
          mbits = 10
          port "nomad_exporter_port" { }
        }
      }
    }
  }
}
