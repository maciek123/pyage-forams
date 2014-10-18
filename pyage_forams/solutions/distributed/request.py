from collections import defaultdict
import logging

import Pyro4

from pyage.core.inject import Inject


logger = logging.getLogger(__name__)


class Request(object):
    def __init__(self, agent_address):
        super(Request, self).__init__()
        self.agent_address = agent_address

    def execute(self, agent):
        raise NotImplementedError()


class TakeAlgaeRequest(Request):
    def __init__(self, agent_address, cell_address, algae):
        super(TakeAlgaeRequest, self).__init__(agent_address)
        self.algae = algae
        self.cell_address = cell_address

    def execute(self, agent):
        if not self.algae == 0:
            agent.take_algae(self.cell_address, self.algae)


class RequestDispatcher(object):
    @Inject('ns_hostname')
    def __init__(self):
        self.requests = defaultdict(list)

    def submit_request(self, request):
        self.requests[request.agent_address].append(request)
        logger.info("request submited %s" % request)

    def send_requests(self):
        try:
            logger.info("sending %s" % self.requests)
            ns = Pyro4.locateNS(self.ns_hostname)
            for (agent_address, requests) in self.requests.iteritems():
                if requests:
                    logger.info("sending %s to %s" % ( requests, agent_address))
                    agent = Pyro4.Proxy(ns.lookup(agent_address))
                    agent.submit_requests(requests)
                    requests[:] = []
        except:
            logging.exception("could not send request")


def create_dispatcher():
    d = [None]

    def environ():
        if d[0] is None:
            d[0] = RequestDispatcher()
        return d[0]

    return environ


def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    if func_name.startswith('__') and not func_name.endswith('__'):
        cls_name = cls.__name__.lstrip('_')
        if cls_name: func_name = '_' + cls_name + func_name
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)


import copy_reg
import types

copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
