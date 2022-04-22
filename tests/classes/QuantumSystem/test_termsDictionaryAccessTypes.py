import quanguru.classes.QSystem as QSys

def test_termDictionaryWithTermName():
    qsys = QSys.QuantumSystem()
    secondTerm = qsys.createTerm(operator=None)

    assert qsys.terms[qsys._firstTerm.name] is qsys._firstTerm
    assert qsys.terms[secondTerm.name] is secondTerm

def test_termDictionaryWithTermAlias():
    qsys = QSys.QuantumSystem()
    qsys._firstTerm.alias = 'firstTerm'
    assert qsys.terms[qsys._firstTerm.name] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[0]] is qsys._firstTerm

    qsys._firstTerm.alias = ['listAlias1', 'listAlias2']
    assert qsys.terms[qsys._firstTerm.name] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[0]] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[1]] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[2]] is qsys._firstTerm

    secondTerm = qsys.createTerm(operator=None)
    secondTerm.alias = ['secondTerm', 'anotherAlias']

    assert qsys.terms[qsys._firstTerm.name] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[0]] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[1]] is qsys._firstTerm
    assert qsys.terms[qsys._firstTerm.alias[2]] is qsys._firstTerm
    assert qsys.terms[secondTerm.name] is secondTerm
    assert qsys.terms[secondTerm.alias[0]] is secondTerm
    assert qsys.terms[secondTerm.alias[1]] is secondTerm