#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import subprocess, re, time, sys
from pluck import pluck


def plot_graph(values, height=15, point=u'▉', space=' '):
    numbers = [float(x) for x in values]
    max_value = max(numbers)
    numbers = [int(x / max_value * height) for x in numbers]

    # point = u'◼'
    # point = u'█'
    # point = u'▪'
    # point = u'▉'
    # space = ' '

    result = list()
    for v in numbers:
        line = list()
        line.extend((height - v) * ' ')
        line.extend(v * point)
        result.append(line)

    output_str = ''
    for h in range(height):
        for w in range(len(values)):
            output_str += result[w][h]
        output_str += '\n'

    print output_str
    vla = (len(values)) / 2
    vlb = (len(values)) - vla
    print ('{:<' + str(vla) + '}{:>' + str(vlb) + '}').format(values[0], values[-1])


def get_pid_history(items, pid):
    result = list()
    for item in items:
        if pid in item:
            result.append(int(item[pid]))
    return result


def get_name_by_pid(pid):
    return subprocess.check_output('ps -p {pid} -o comm='.format(pid=pids[0]), shell=True).strip()


limit = 800
duration = 0.1
history_size = 100
measurements = list()
points = (u'■', u'□')
measure_index = 0

args = sys.argv[1:]

if len(args) > 0:
    limit = int(args[0])

if len(args) > 1:
    duration = float(args[1])

print 'Watching memory usage (max: {limit}, sleep: {duration})'.format(limit=limit, duration=duration)
while True:
    output = subprocess.check_output("ps aux --sort '-rss' --cols 200 | head -n 200", shell=True)
    lines = output.splitlines()
    headers = re.split(r'\s+', lines[0], 10)
    del lines[0]

    processes = list()
    for line in lines:
        attrs = re.split(r'\s+', line, 10)

        processes.append(dict(zip(headers, attrs)))

    rsss = [int(x) / 1000 for x in pluck(processes, 'RSS')]
    pids = pluck(processes, 'PID')

    pairs = dict(zip(pids, rsss))
    measurements.append(pairs)
    if len(measurements) > history_size:
        del measurements[0]

    top = dict(
        pid=pids[0],
        rss=rsss[0],
        name=get_name_by_pid(pids[0])
    )
    measure_index = (measure_index + 1) % 2
    print '\r ' + points[measure_index] + ' Top process "{name}:{pid}" with {rss} MB'.format(**top),
    sys.stdout.flush()

    for pid, rss in pairs.items():
        if rss > limit:
            print '\nTerminating {name}:{pid} ({rss} MB)'.format(pid=pid, rss=rss, name=get_name_by_pid(pid))
            subprocess.check_call('kill -9 {pid}'.format(pid=pid), shell=True)

            values = get_pid_history(measurements, pid)
            plot_graph(values)
            print 'History: ' + ' '.join([str(x) for x in values])

    time.sleep(duration)