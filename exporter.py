#!/usr/bin/env python3

import nomad
import sys
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
from prometheus_client import core, generate_latest, Gauge


allocation_restarts_gauge = Gauge('allocation_restarts', 'Number of restarts for given allocation', ['jobname', 'groupname', 'taskname', 'alloc_id', 'eval_id'])


class ExportRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        options = {
            'nomad_server': os.environ.get('NOMAD_SERVER', 'nomad.service.consul'),
            'nomad_port': os.environ.get('NOMAD_PORT', 4646),
        }
        if self.path == '/metrics':
            stats = get_allocs(options)
            if stats:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(stats)
            else:
                self.send_error(500, "Could not retrieve data")
                print('Could not retrieve data', file=sys.stderr)


def start_server(port):
    httpd = HTTPServer(('', port), ExportRequestHandler)
    httpd.serve_forever()


def retryer(f):
    def wrapper(*args, **kwargs):
        for __ in range(5):
            try:
                return f(*args, **kwargs)
            except KeyError:
                sleep(0.5)
                print('Could not contact nomad, retrying in 0.5 seconds', file=sys.stderr)
    return wrapper


@retryer
def get_allocs(options):
    n = nomad.Nomad(host=options['nomad_server'], port=options['nomad_port'])
    for alloc in n.allocations:
        jobname = alloc['JobID']
        groupname = alloc['TaskGroup']
        alloc_id = alloc['ID']
        eval_id = alloc['EvalID']
        for task in alloc['TaskStates']:
            allocation_restarts_gauge.labels(
                jobname=jobname,
                groupname=groupname,
                taskname=task,
                alloc_id=alloc_id,
                eval_id=eval_id,
            ).set(task['Restarts'])
    return generate_latest(core.REGISTRY)


if __name__ == '__main__':
    port = int(os.environ['PORT'])
    start_server(port)
