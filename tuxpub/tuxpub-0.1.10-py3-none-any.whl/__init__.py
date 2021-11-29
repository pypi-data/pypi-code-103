# -*- coding: utf-8 -*-

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    jsonify,
    make_response,
    send_from_directory,
)
from flask_bootstrap import Bootstrap
from tuxpub.filters import datetimeformat, file_name, file_size, folder_name
from tuxpub.resources import s3_server
from tuxpub.config import TuxConfig
from re import sub

__version__ = "0.1.10"


def create_app():
    app = Flask(__name__, instance_relative_config=True, static_folder="static")
    Bootstrap(app)
    app.jinja_env.filters["datetimeformat"] = datetimeformat
    app.jinja_env.filters["file_name"] = file_name
    app.jinja_env.filters["file_size"] = file_size
    app.jinja_env.filters["folder_name"] = folder_name

    config = TuxConfig()
    s3_handler = s3_server(bucket=config.S3_BUCKET, region=config.S3_REGION)

    @app.context_processor
    def add_site_name():
        return {"SITE_TITLE": config.SITE_TITLE}

    @app.context_processor
    def add_app_version():
        return {"VERSION": __version__}

    @app.route("/robots.txt")
    def static_folder():
        return send_from_directory(app.static_folder, request.path[1:]), 200

    @app.route("/favicon.ico")
    def favicon():
        return render_template("404.html"), 404

    @app.route("/", defaults={"dummy": ""})
    @app.route("/<path:dummy>")
    def fallback(dummy=""):
        """Process an arbitrary request."""
        url = dummy

        # If the url is to a specific object, serve it.
        (exists, head) = s3_handler.key_exists(url)
        if exists:
            if request.method == "HEAD":
                resp = make_response("", 200)
                md = head["ResponseMetadata"]["HTTPHeaders"]
                resp.headers["Etag"] = md["etag"]
                resp.headers["Content-Length"] = md["content-length"]
                if "content-type" in md:
                    resp.headers["Content-Type"] = md["content-type"]
                resp.headers["Last-Modified"] = md["last-modified"]
                return resp
            else:
                return redirect(s3_handler.create_signed_url(url), code=302)

        # Add a trailing slash to turn the url into a directory, unless we're
        # serving the index page (in which case url will be empty, and adding a
        # / will break things)
        if not url.endswith("/") and url != "":
            destination = request.base_url + "/"
            if request.args:
                destination += "?"
                for key, value in request.args.items():
                    destination += f"{key}={value}&"
            return redirect(destination, 302)

        # If the request is for the index page and ROOT_INDEX_LISTING is disabled,
        # return root.html template
        if not config.ROOT_INDEX_LISTING and (url.count("/") < 1 or url in ["", "/"]):
            # Short circuit requests for the index page when ROOT_INDEX_LISTING
            # is disabled
            return render_template("root.html"), 200

        # Retrieve the files and folders in the local path
        (files, folders, next_continuation_token) = s3_handler.get_files_and_folders(
            sub("/+", "/", url)
        )

        # No files or folders found.
        if len(files) == 0 and len(folders) == 0:
            return render_template("404.html"), 404

        # Return file listing in the requested format (html by default)
        if request.args.get("export"):
            return export_files(
                export_format=request.args.get("export"),
                files=files,
                folders=folders,
                base_url=request.base_url,
            )
        else:
            return render_template(
                "files.html",
                files=files,
                folders=folders,
                base_url=request.base_url,
                show_parent=(url != ""),
            )

    def export_files(export_format, files=[], folders=[], base_url=""):
        """Return the list of files in an alternate format (like json)"""

        if export_format not in ["json"]:
            return "Export format not supported", 501

        if export_format == "json":
            json = {"files": [], "folders": []}
            for f in files:
                json["files"].append(
                    {
                        "Url": base_url + file_name(f["Key"]),
                        "Size": f["Size"],
                        "LastModified": f["LastModified"],
                        "ETag": f["ETag"],
                    }
                )
            for f in folders:
                json["folders"].append(
                    {
                        "Url": base_url + folder_name(f),
                    }
                )
            return make_response(jsonify(json), 200)

    return app
