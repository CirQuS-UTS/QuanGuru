import pytest
import quanguru.classes.QSystem as QSys

def test_createTermKwargs():
    qs1 = QSys.QuantumSystem()
    t1ofqs1 = qs1.createTerm(operator=None, alias='term1Ofqs1')
    assert qs1.getByNameOrAlias('term1Ofqs1') is t1ofqs1

@pytest.mark.parametrize('resetTerms', [False, True])
def test_termDictionaryWithTermName(resetTerms):
    qsys = QSys.QuantumSystem()
    if resetTerms:
        qsys.resetTerms()
    secondTerm = qsys.createTerm(operator=None)

    assert qsys.terms[qsys._firstTerm.name] is qsys._firstTerm
    assert qsys.terms[secondTerm.name] is secondTerm

@pytest.mark.parametrize('resetTerms', [False, True])
def test_termDictionaryWithTermAlias(resetTerms):
    qsys = QSys.QuantumSystem()
    if resetTerms:
        qsys.resetTerms()
    qsys._firstTerm.alias = 'firstTerm' + str(resetTerms)
    assert qsys.terms[qsys._firstTerm.name] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[0]] is qsys._firstTerm

    qsys._firstTerm.alias = ['listAlias1' + str(resetTerms), 'listAlias2' + str(resetTerms)]
    assert qsys.terms[qsys._firstTerm.name] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[0]] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[1]] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[2]] is qsys._firstTerm

    secondTerm = qsys.createTerm(operator=None)
    secondTerm.alias = ['secondTerm' + str(resetTerms), 'anotherAlias' + str(resetTerms)]

    assert qsys.terms[qsys._firstTerm.name] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[0]] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[1]] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[2]] is qsys._firstTerm
    assert qsys.terms[secondTerm.name] is secondTerm
    assert qsys.terms[secondTerm.alias[0]] is secondTerm
    assert qsys.terms[secondTerm.alias[1]] is secondTerm
