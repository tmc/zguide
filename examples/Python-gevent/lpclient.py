#
#  Lazy Pirate client
#  Uses gevent-zeromq to work in a cooperative greenthread environment
#  To run, start lpserver and then randomly kill/restart it
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#   Author: Travis Cline <travis.cline@gmail.com> - gevent-zeromq adaption

import sys
import gevent
from gevent_zeromq import zmq

REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://localhost:5555"

context = zmq.Context(1)

print "I: Connecting to server..."
client = context.socket(zmq.REQ)
client.connect(SERVER_ENDPOINT)

sequence = 0
retries_left = REQUEST_RETRIES
while retries_left:
    sequence += 1
    request = str(sequence)
    print "I: Sending (%s)" % request
    client.send(request)

    expect_reply = True
    while expect_reply:
        t = gevent.Timeout(REQUEST_TIMEOUT/1000.0)
        t.start()
        try:
            reply = client.recv()
            t.cancel()
            if not reply:
                break
            if int(reply) == sequence:
                print "I: Server replied OK (%s)" % reply
                retries_left = REQUEST_RETRIES
                expect_reply = False
            else:
                    print "E: Malformed reply from server: %s" % reply
        except gevent.Timeout:
            print "W: No response from server, retrying..."
            # Socket is confused. Close and remove it.
            client.setsockopt(zmq.LINGER, 0)
            client.close()
            retries_left -= 1
            if retries_left == 0:
                print "E: Server seems to be offline, abandoning"
                break
            print "I: Reconnecting and resending (%s)" % request
            # Create new connection
            client = context.socket(zmq.REQ)
            client.connect(SERVER_ENDPOINT)
            client.send(request)

context.term()
