from starlette_prometheus import PrometheusMiddleware


def register(app):
    app.add_middleware(PrometheusMiddleware)
