def qSystemInitErrors(init):
    def new_function(obj, **kwargs):
        init(obj, **kwargs)
        if obj.dimension is None:
            className = obj.__class__.__name__
            print(className + ' requires a dimension')
        elif obj.frequency is None:
            className = obj.__class__.__name__
            print(className + ' requires a frequency')
    return new_function