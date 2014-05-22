def counted(fn):
    def wrapper(*args, **kwargs):
        wrapper.called += 1
        return fn(*args, **kwargs)

    wrapper.called = 0
    wrapper.__name__ = fn.__name__
    return wrapper