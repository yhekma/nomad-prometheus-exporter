#!/usr/bin/env python3

import nomad
import sys
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import core, generate_latest, Gauge


allocation_restarts_gauge = Gauge('nomad_allocation_restarts', 'Number of restarts for given allocation',
                                  ['jobname', 'groupname', 'taskname', 'alloc_id', 'eval_id'],
                                  )
deployments_gauge = Gauge('nomad_deployments', 'Nomad deployments', ['jobname', 'jobid', 'jobversion', 'status'])
jobs_gauge = Gauge('nomad_job_status', 'Status of nomad jobs', ['jobname', 'jobtype', 'jobstatus'])


class ExportRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            nomad_server = os.environ.get('NOMAD_SERVER', 'nomad.service.consul')
            nomad_port = os.environ.get('NOMAD_PORT', 4646)
            n = nomad.Nomad(host=nomad_server, port=nomad_port)
            get_allocs(n)
            get_deployments(n)
            get_tasks(n)
            stats = generate_latest(core.REGISTRY)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(stats)


def start_server(port):
    httpd = HTTPServer(('', port), ExportRequestHandler)
    httpd.serve_forever()


def get_tasks(nomad_connection):
    for job in nomad_connection.jobs:
        jobname = job['Name']
        jobtype = job['Type']
        for taskgroup in job['JobSummary']['Summary']:
            for status in job['JobSummary']['Summary'][taskgroup]:
                jobs_gauge.labels(
                    jobname=jobname,
                    jobtype=jobtype,
                    jobstatus=status,
                ).set(job['JobSummary']['Summary'][taskgroup][status])


def get_deployments(nomad_connection):
    count_dict = {}
    deployments = list(nomad_connection.deployments)
    for deployment in deployments:
        jobname = deployment['JobID']
        try:
            count_dict[jobname] += 1
        except KeyError:
            count_dict[jobname] = 1

    for deployment in deployments:
        deployments_gauge.labels(
            jobname=deployment['JobID'],
            jobid=deployment['ID'],
            jobversion=deployment['JobVersion'],
            status=deployment['Status'],
        ).set(count_dict[deployment['JobID']])


def get_allocs(nomad_connection):
    for alloc in nomad_connection.allocations:
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
            ).set(alloc['TaskStates'][task]['Restarts'])


if __name__ == '__main__':
    port = int(os.environ['PORT'])
    start_server(port)
