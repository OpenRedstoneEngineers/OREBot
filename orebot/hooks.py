hooks = []

def hook(fun):
    """A decorator for defining message hooks."""
    hooks.append(fun)
    return fun

def handle(client, sender, target, message):
    """Distributes the message among the decorated hooks."""
    for hook in hooks:
        hook(client, sender, target, message)
