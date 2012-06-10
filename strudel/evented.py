from copy import copy

class Handler(object):
    def __init__(self, event, func, args):
        self.event = event
        self.func = func
        self.args = args

    def execute(self, *args):
        self.func(*(self.args + args))

# HACK (Mispy): This is a really ugly way to ensure initialization. I
# can't figure out how to hook into the __init__ chain in a way that is
# clean and consistent with inheritance and pickling.
def evented(func):
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'evented'):
            self.handlers = {}
            self.delegates = {}
            self.evented = True
        return func(self, *args, **kwargs)
    return wrapper

class Evented(object):
    @evented
    def on(self, event, func, *args):
        handler = Handler(event, func, args)
        if not self.handlers.has_key(event):
            self.handlers[event] = []
        self.handlers[event].append(handler)
        return handler

    @evented
    def emit(self, event, *args):
        if self.handlers.has_key(event):
            for handler in self.handlers[event]:
                handler.execute(*args)

    @evented
    def off(self, event_or_handler):
        if isinstance(event_or_handler, basestring):
            del self.handlers[event_or_handler]
        elif isinstance(event_or_handler, Handler):
            for event, handlers in self.handlers.iteritems():
                if event_or_handler in handlers:
                    handlers.remove(event_or_handler)
        else:
            raise TypeError, "Expected instance of type basestring or Handler"

    @evented
    def delegate(self, target, *args):
        """Bind an event handler on another object but link it back to us for later cleanup."""
        if not self.delegates.has_key(target): self.delegates[target] = []
        self.delegates[target].append(target.on(*args))

    @evented
    def event_cleanup(self):
        for target, handlers in self.delegates.iteritems():
            for handler in handlers:
                target.off(handler)
        self.handlers = {}

    @evented
    def __getstate__(self):
        state = copy(self.__dict__)
        for prop in ['handlers', 'delegates', 'evented']:
            if state.has_key(prop): del state[prop]
        return state

