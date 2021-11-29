import aiohttp_cors
from aiohttp import web
import asyncio

def create_dashboard_api(app, db_connection):
    cors = aiohttp_cors.setup(app)

    @asyncio.coroutine
    def handler(request):
        messages = db_connection.get_all()
        return web.json_response(messages)

    resource = cors.add(app.router.add_resource("/api"))

    cors.add(
        resource.add_route("GET", handler), {
            "http://localhost:3000": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers=("X-Custom-Server-Header",),
                allow_headers=("X-Requested-With", "Content-Type"),
                max_age=3600,
            )
        })


def setup_cors(app):
    # The `cors` instance will store CORS configuration for the
    # application.
    cors = aiohttp_cors.setup(app)

    # To enable CORS processing for specific route you need to add
    # that route to the CORS configuration object and specify its
    # CORS options.
    cors.add(app.router.add_resource("/api"), {
        "http://localhost:3000": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Custom-Server-Header",),
            allow_headers=("X-Requested-With", "Content-Type"),
            max_age=3600,
            allow_methods=["GET"]
        )
    })

    # cors.add(app.router.add_resource("/api2"), {
    #     "http://localhost:3000": aiohttp_cors.ResourceOptions(
    #         allow_credentials=True,
    #         expose_headers=("X-Custom-Server-Header",),
    #         allow_headers=("X-Requested-With", "Content-Type"),
    #         max_age=3600,
    #         allow_methods=["GET"]
    #     )
    # })

    # cors.add(app.router.add_resource("/socket.io/"), {
    #     "http://localhost:3000": aiohttp_cors.ResourceOptions(
    #          allow_credentials=True,
    #          expose_headers=("X-Custom-Server-Header",),
    #          allow_headers=("X-Requested-With", "Content-Type"),
    #          max_age=3600,
    #          allow_methods=["GET"]
    #          )
    # })
