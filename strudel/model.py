from strudel.evented import Evented

class Model(Evented):
    def __init__(self, **kwargs):
        for k,v in kwargs.iteritems():
            setattr(self, k, v)

def method_name(obj, func):
    matches = [key for key, val in obj.__class__.__dict__.iteritems() if val == func]
    if len(matches) > 0:
        return matches[0]
    else:
        return None

def many_to_one(backref):
    prop = None

    def getter(self):
        name = method_name(self, prop)
        return self.__dict__.get('_'+name)

    def setter(self, val):
        current = getter(self)
        if current is not None:
            getattr(current, backref).remove(self)

        name = method_name(self, prop)
        self.__dict__['_'+name] = val

        if val is not None:
            if not hasattr(val, backref):
                setattr(val, backref, [])
            getattr(val, backref).append(self)

    prop = property(getter, setter)
    return prop

def one_to_many(backref):
    prop = None

    def getter(self):
        name = method_name(self, prop)
        if not self.__dict__.has_key('_'+name):
            self.__dict__['_'+name] = []
        return self.__dict__.get('_'+name)

    def setter(self, val):
        current = getter(self)
        if current is not None:
            for obj in current:
                del obj.__dict__['_'+backref]

        name = method_name(self, prop)
        self.__dict__['_'+name] = val

    prop = property(getter, setter)
    return prop

def one_to_one(backref):
    prop = None

    def getter(self):
        name = method_name(self, prop)
        return self.__dict__.get('_'+name)

    def setter(self, val):
        name = method_name(self, prop)
        self.__dict__['_'+name] = val

        current = getter(self)
        if current is not None:
            if current == val: return
            del current.__dict__['_'+backref]
        val.__dict__['_'+backref] = self

    prop = property(getter, setter)
    return prop
