


def checkClass(classOf, universal):
    def addDecorator(addRemoveFunction):
        def wrapper(obj, inp):
            if isinstance(inp, classOf):
                addRemoveFunction(inp)
            elif isinstance(inp, str):
                addRemoveFunction(obj.addSubSys(universal.instNames[inp]))
            elif isinstance(inp, dict):
                for sys in inp.values():
                    addRemoveFunction(sys)
            elif inp is None:
                addRemoveFunction(inp)
            else:
                for sys in inp:
                    addRemoveFunction(sys)
        return wrapper
    return addDecorator