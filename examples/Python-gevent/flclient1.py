#
# Freelance Client - Model 1
# Uses REQ socket to query one or more services
#
# Author: Daniel Lundin <dln(at)eintr(dot)org>
# Author: Travis Cline <travis.cline@gmail.com> - gevent-zeromq adaption

import sys
import time

import gevent
from gevent_zeromq import zmq

REQUEST_TIMEOUT = 1000  # ms
MAX_RETRIES = 3   # Before we abandon

def try_request(ctx, endpoint, request):
    print "I: Trying echo service at %s..." % endpoint
    client = ctx.socket(zmq.REQ)
    client.setsockopt(zmq.LINGER, 0)  # Terminate early
    client.connect(endpoint)
    client.send(request)

    reply = ''
    with gevent.Timeout(REQUEST_TIMEOUT/1000.0, False):
        reply = client.recv_multipart()
    client.close()
    return reply

context = zmq.Context()
request = "Hello world"
reply = None

endpoints = len(sys.argv) - 1
if endpoints == 0:
    print "I: syntax: %s <endpoint> ..." % sys.argv[0]
elif endpoints == 1:
    # For one endpoint, we retry N times
    endpoint = sys.argv[1]
    for retries in xrange(MAX_RETRIES):
        reply = try_request(context, endpoint, request)
        if reply:
            break  # Success
        print "W: No response from %s, retrying" % endpoint
else:
    # For multiple endpoints, try each at most once
    for endpoint in sys.argv[1:]:
        reply = try_request(context, endpoint, request)
        if reply:
            break  # Success
        print "W: No response from %s" % endpoint

if reply:
    print "Service is running OK"

