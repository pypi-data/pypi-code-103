from django.conf import settings


def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip


def allowed_ip(request):
    user_ip = get_ip(request)

    for allow_ip in settings.ALLOWED_IP:
        if user_ip == allow_ip or user_ip.startswith(allow_ip):
            return True
    return False
