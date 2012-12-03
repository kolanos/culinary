import functools

import types

import fabric.api


def dispatch(prefix=None):
    """Dispatches the current function to specific implementation. The `prefix`
    parameter indicates the common option prefix, and the `option_select()`
    function will determine the function suffix.

    For instance the package functions are defined like that:

    {{{
    @dispatch("package")
    def package_ensure(...):
        ...
    def package_ensure_apt(...):
        ...
    def package_ensure_yum(...):
        ...
    }}}

    and then when a user does

    {{{
    cuisine.option_select("package", "yum")
    cuisine.package_ensure(...)
    }}}

    then the `dispatch` function will dispatch `package_ensure` to
    `package_ensure_yum`.

    If your prefix is the first word of the function name before the
    first `_` then you can simply use `@dispatch` without parameters.
    """
    def dispatch_wrapper(function, prefix=prefix):
        def wrapper(*args, **kwargs):
            function_name = function.__name__
            _prefix = prefix or function_name.split("_")[0].replace(".", "_")
            select = fabric.api.env.get("CUISINE_OPTION_" + _prefix.upper())
            assert select, \
                ("No option defined for: %s, call select_%s(<YOUR OPTION>) "
                 "to set it") % (_prefix.upper(),
                                 prefix.lower().replace(".", "_"))
            function_name = function.__name__ + "_" + select
            specific = eval(function_name)
            if specific:
                if type(specific) == types.FunctionType:
                    return specific(*args, **kwargs)
                else:
                    raise Exception("Function expected for: " + function_name)
            else:
                raise Exception("Function variant not defined: " \
                        + function_name)
        # We copy name and docstring
        functools.update_wrapper(wrapper, function)
        return wrapper
    if type(prefix) == types.FunctionType:
        return dispatch_wrapper(prefix, None)
    else:
        return dispatch_wrapper
