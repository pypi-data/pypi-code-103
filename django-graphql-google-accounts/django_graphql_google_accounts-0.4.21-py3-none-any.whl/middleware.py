from django.contrib.auth import authenticate

from accounts.auth.token import JSONWebToken


def has_token(context):
    bearer_token = context.META.get('HTTP_AUTHORIZATION', '')
    _token = bearer_token.split('Bearer ')
    return _token[-1]


def _authenticate(request):
    is_anonymous = not hasattr(request, 'user') or request.user and request.user.is_anonymous
    return is_anonymous and has_token(request) is not None


class TokenMiddleware(JSONWebToken):

    def resolve(self, next, root, info, **kwargs):
        ctx = info.context
        if _authenticate(ctx):
            token = has_token(ctx)
            claim = self.extra_data(token)
            user = authenticate(request=ctx, uid=claim.get('uid', ''))
            ctx.user = user
        return next(root, info, **kwargs)
