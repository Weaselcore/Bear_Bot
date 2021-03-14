class Singleton(object):

    # Dictionary to hold the list of instances,
    _instances = {}

    # The NEW magic method creates an object by object.__new__(cls) this initialises before INIT magic method.
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]
