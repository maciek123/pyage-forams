# coding=utf-8
from functools import partial

from pyage_forams.solutions.agent.remote_aggegate import create_remote_agent
from pyage_forams.conf.distributed3d.common import *

agents = partial(create_remote_agent, "upperrightfront")
neighbours = lambda: {"left": "upperleftfront", "lower": "lowerrightfront", "back": "upperrightback"}

