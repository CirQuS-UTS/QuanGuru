def getAsList(value):
    if len(value)==1:
        return value[0]
    else:
        return value
    
def setAsList(value):
    if not hasattr(value, '__iter__'):
        return [value]
    else:
        return = value