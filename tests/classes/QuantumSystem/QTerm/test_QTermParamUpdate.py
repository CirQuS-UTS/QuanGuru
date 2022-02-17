import pytest
from quanguru.classes.QTerms import QTerm
from quanguru.classes.base import named

def test_paramUpdatedOfQTerm():
    named1 = named()
    named2 = named()
    named3 = named()
    named4 = named()

    t1 = QTerm()
