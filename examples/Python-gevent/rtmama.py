# encoding: utf-8
#
#   Custom routing Router to Mama (XREP to REQ)
#
#   Author: Jeremy Avnet (brainsik) <spork(dash)zmq(at)theory(dot)org>
#   Author: Travis Cline <travis.cline@gmail.com> - gevent-zeromq adaption


import gevent
import gevent_zeromq
gevent_zeromq.monkey_patch() # patching required because of zmq import in zhelpers


import time
import random

import zhelpers

NBR_WORKERS = 10


def worker_thread(context):
    worker = context.socket(zmq.REQ)

    # We use a string identity for ease here
    zhelpers.set_id(worker)
    worker.connect("ipc://routing.ipc")

    total = 0
    while True:
        # Tell the router we're ready for work
        worker.send("ready")

        # Get workload from router, until finished
        workload = worker.recv()
        finished = workload == "END"
        if finished:
            print "Processed: %d tasks" % total
            break
        total += 1

        # Do some random work
        time.sleep(random.random() / 10 + 10 ** -9)


context = zmq.Context()
client = context.socket(zmq.XREP)
client.bind("ipc://routing.ipc")

for _ in xrange(NBR_WORKERS):
    gevent.spawn(worker_thread, context)

for _ in xrange(NBR_WORKERS * 10):
    # LRU worker is next waiting in the queue
    address = client.recv()
    empty = client.recv()
    ready = client.recv()

    client.send(address, zmq.SNDMORE)
    client.send("", zmq.SNDMORE)
    client.send("This is the workload")

# Now ask mama to shut down and report their results
for _ in xrange(NBR_WORKERS):
    address = client.recv()
    empty = client.recv()
    ready = client.recv()

    client.send(address, zmq.SNDMORE)
    client.send("", zmq.SNDMORE)
    client.send("END")

time.sleep(1)  # Give 0MQ/2.0.x time to flush output
