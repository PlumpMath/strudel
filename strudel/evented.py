class Evented(object):
    def on(self, evid, func, *args):
        if not hasattr(self, 'handlers'):
            self.handlers = {}

        handler = { 'func': func, 'args': args }
        if not self.handlers.has_key(evid):
            self.handlers[evid] = []
        self.handlers[evid].append(handler)

    def emit(self, evid, *args):
        if not hasattr(self, 'handlers'):
            self.handlers = {}

        if self.handlers.has_key(evid):
            for handler in self.handlers[evid]:
                hargs = handler['args'] + args
                handler['func'](*hargs)

    def clear_handlers(self):
        self.handlers = {}
