# Simple request-reply broker utilizing the gevent-zeromq library
#
# Author: Travis Cline <travis.cline@gmail.com>

import gevent
from gevent_zeromq import zmq

context = zmq.Context()
frontend = context.socket(zmq.XREP)
backend = context.socket(zmq.XREQ)
frontend.bind("tcp://*:5559")
backend.bind("tcp://*:5560")

def front_to_back():
    while True:
        message = frontend.recv()
        more = frontend.getsockopt(zmq.RCVMORE)
        if more:
            backend.send(message, zmq.SNDMORE)
        else:
            backend.send(message)

def back_to_front():
    while True:
        message = backend.recv()
        more = backend.getsockopt(zmq.RCVMORE)
        if more:
            frontend.send(message, zmq.SNDMORE)
        else:
            frontend.send(message)

gevent.joinall([gevent.spawn(front_to_back), gevent.spawn(back_to_front)])