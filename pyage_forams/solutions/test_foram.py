from unittest import TestCase
from pyage.core import inject
from pyage_forams.solutions.foram import Foram

class TestForam(TestCase):
    def test_step(self):
        inject.config = "pyage_forams.conf.dummy_conf"
        foram = Foram(10)
        # foram.step()