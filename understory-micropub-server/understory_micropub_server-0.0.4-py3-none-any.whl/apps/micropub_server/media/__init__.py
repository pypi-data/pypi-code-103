""""""

import pathlib

import sh
from micropub import server
from understory import web
from understory.web import tx

app = web.application(
    __name__,
    prefix="media",
    args={"filename": rf"{web.nb60_re}{{4}}.\w{{1,10}}"},
    model=server.media_model.schemas,
)


@app.control("")
class MediaEndpoint:
    """Your media files."""

    def get(self):
        """"""
        media = tx.m.pub.get_media()
        try:
            query = web.form("q").q
        except web.BadRequest:
            pass
        else:
            if query == "source":
                # {
                #   "url": "https://media.aaronpk.com/2020/07/file-20200726XXX.jpg",
                #   "published": "2020-07-26T09:51:11-07:00",
                #   "mime_type": "image/jpeg"
                # }
                return {
                    "items": [
                        {
                            "url": (
                                f"{tx.request.uri.scheme}://{tx.request.uri.netloc}"
                                f"/media/{filepath.name}"
                            ),
                            "published": "TODO",
                            "mime_type": "TODO",
                        }
                        for filepath in media
                    ]
                }
        return app.view.media(media)

    def post(self):
        """"""
        media_dir = pathlib.Path(tx.host.name)
        media_dir.mkdir(exist_ok=True, parents=True)
        while True:
            mid = web.nbrandom(4)
            filename = media_dir / mid
            if not filename.exists():
                filename = web.form("file").file.save(filename)
                break
        if str(filename).endswith(".heic"):
            sh.convert(
                filename,
                "-set",
                "filename:base",
                "%[basename]",
                f"{media_dir}/%[filename:base].jpg",
            )
        sha256 = str(sh.sha256sum(filename)).split()[0]
        try:
            tx.db.insert("media", mid=mid, sha256=sha256, size=filename.stat().st_size)
        except tx.db.IntegrityError:
            mid = tx.db.select("media", where="sha256 = ?", vals=[sha256])[0]["mid"]
            filename.unlink()
        path = f"/posts/media/{mid}"
        raise web.Created(f"File can be found at <a href={path}>{path}</a>", path)


@app.control("{filename}")
class MediaFile:
    """A media file."""

    def get(self):
        """"""
        content_types = {
            (".jpg", ".jpeg"): "image/jpg",
            ".heic": "image/heic",
            ".png": "image/png",
            ".mp3": "audio/mpeg",
            ".mov": "video/quicktime",
            ".mp4": "video/mp4",
        }
        for suffix, content_type in content_types.items():
            if self.filename.endswith(suffix):
                web.header("Content-Type", content_type)
                break
        relative_path = f"{tx.host.name}/{self.filename}"
        if tx.host.server[0] == "gunicorn":
            with open(relative_path, "rb") as fp:
                return fp.read()
        else:  # assumes Nginx context
            web.header("X-Accel-Redirect", f"/X/{relative_path}")

    def delete(self):
        """"""
        filepath = tx.m.pub.get_filepath(self.filename)
        tx.db.delete("media", where="mid = ?", vals=[filepath.stem])
        filepath.unlink()
        return "deleted"
