#!/usr/bin/env python3

import nomad
import os
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import core, generate_latest, Gauge

allocation_exits_gauge = Gauge('nomad_allocation_exits', 'Allocation events', ['job', 'taskgroup', 'task', 'exitcode', 'alloc_id'])
allocation_restarts = Gauge('nomad_allocation_restarts', 'Number of allocations restarts', ['job', 'taskgroup', 'task', 'alloc_id', 'eval_id'])
deployments_gauge = Gauge('nomad_deployments', 'Nomad deployments', ['job', 'jobid', 'jobversion', 'status'])
jobs_gauge = Gauge('nomad_job_status', 'Status of nomad jobs', ['job', 'jobtype', 'jobstatus', 'taskgroup'])


class ExportRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            nomad_server = os.environ.get('NOMAD_SERVER', 'nomad.service.consul')
            nomad_port = os.environ.get('NOMAD_PORT', 4646)
            n = nomad.Nomad(host=nomad_server, port=nomad_port)
            get_allocs(n)
            get_deployments(n)
            get_jobs(n)
            stats = generate_latest(core.REGISTRY)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(stats)


def start_server(port=os.environ.get('PORT', 8888)):
    httpd = HTTPServer(('', int(port)), ExportRequestHandler)
    httpd.serve_forever()


def get_jobs(nomad_connection):
    for job in nomad_connection.jobs:
        jobname = job['Name']
        jobtype = job['Type']
        taskgroups = job['JobSummary']['Summary']
        for taskgroup in taskgroups:
            # Get rid of tasks that have no numbers assigned at all
            if sum([int(i) for i in taskgroups[taskgroup].values()]) == 0:
                continue
            for status in taskgroups[taskgroup]:
                jobs_gauge.labels(
                    job=jobname,
                    jobtype=jobtype,
                    jobstatus=status,
                    taskgroup=taskgroup,
                ).set(taskgroups[taskgroup][status])


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
            job=deployment['JobID'],
            jobid=deployment['ID'],
            jobversion=deployment['JobVersion'],
            status=deployment['Status'],
        ).set(count_dict[deployment['JobID']])


def get_allocs(nomad_connection):
    for alloc in nomad_connection.allocations:
        jobname = alloc['JobID']
        taskgroup = alloc['TaskGroup']
        alloc_id = alloc['ID']
        eval_id = alloc['EvalID']

        for t in alloc['TaskStates']:
            event_counter = defaultdict(int)
            for event in alloc['TaskStates'][t]['Events']:
                event_counter[event['ExitCode']] += 1
            for rc in event_counter:
                allocation_exits_gauge.labels(
                    job=jobname,
                    taskgroup=taskgroup,
                    task=t,
                    alloc_id=alloc_id,
                    exitcode=rc,
                ).set(event_counter[rc])
            allocation_restarts.labels(
                job=jobname,
                taskgroup=taskgroup,
                task=t,
                alloc_id=alloc_id,
                eval_id=eval_id,
            ).set(alloc['TaskStates'][t]['Restarts'])


if __name__ == '__main__':
    start_server()
