class propdict(dict):
    def __getattr__(self, name):
        return self.get(name, None)

    def __setattr__(self, name, val):
        self[name] = val
