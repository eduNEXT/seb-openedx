from django.http import HttpRequest


def always_allow_staff(fn):
    def wrapper_func(*args, **kwargs):
        request = next((x for x in args if isinstance(x, HttpRequest)), None)
        if hasattr(request, 'user') and request.user.is_authenticated() and request.user.is_staff:
            return
        return fn(*args, **kwargs)

    return wrapper_func
