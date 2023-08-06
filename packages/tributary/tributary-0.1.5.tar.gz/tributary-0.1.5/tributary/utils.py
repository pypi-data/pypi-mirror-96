import functools


def _either_type(f):
    """Utility decorator to allow for either no-arg decorator or arg decorator

    Args:
        f (callable): Callable to decorate
    """

    @functools.wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return f(args[0])
        else:
            # decorator arguments
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec


def LazyToStreaming(lazy_node):
    from .streaming import StreamingNode, Foo
    from .lazy import LazyNode
    from .base import TributaryException

    if isinstance(lazy_node, StreamingNode):
        return lazy_node
    if not isinstance(lazy_node, LazyNode):
        raise TributaryException("Malformed input:{}".format(lazy_node))

    return Foo(foo=lambda node=lazy_node: node())
