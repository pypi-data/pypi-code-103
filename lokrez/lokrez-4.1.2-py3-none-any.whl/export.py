import base64
import html
import io
import os
import subprocess
import tempfile
import urllib

import jinja2

# =============================================================================
def generate_pic(
        templatesdir,
        templatename,
        context,
        outform="svg",
        log = None,
        cachedir = None,
        options = {},
        ):

    if outform not in ["svg", "png"]:
        raise ValueError("unsupported output format '{}'".format(outform))

    # Template rendering
    # -------------------------------------------------------------------------
    log.info("Generating SVG using '{}' template".format(templatename))
    log.debug("Context : {}".format(context))

    log.debug(
            "Initializing jinja2 with template dir '{}'" \
                    .format(templatesdir)
                    )
    jj2_env = jinja2.Environment(
            loader = jinja2.FileSystemLoader(
                str(templatesdir),
                )
            )

    try:
        jj2_tpl = jj2_env.get_template(
                # Jinja specific path format
                "{}/template.svg.j2".format(templatename),
                )
    except jinja2.exceptions.TemplateNotFound as e:
        raise e
    except Exception as e:
        log.error("Could not find template '{}'".format(templatename))
        log.debug(e, exc_info=1)
        return None

    # To SVG
    # -------------------------------------------------------------------------
    if outform == "svg":

        out = io.StringIO()

        if options.get("svg_embed_png", False):
            log.debug("embedding png images")

            for line in jj2_tpl.render(context).splitlines():
                l = line.strip()

                if (     l.startswith("xlink:href=\"")
                     and l.endswith(".png\"") ):
                    l = html.parser.unescape(l)
                    image_url = urllib.parse.urlparse(
                            "=".join( l.split("=")[1:] )[1:-1],
                            )
                    log.debug("embedding image '{}'".format(image_url.path))
                    with open(image_url.path, "rb") as image:
                        line = "xlink:href=\"data:image/png;base64,{d}\"" \
                                .format(
                                        d = base64 \
                                                .b64encode(image.read()) \
                                                .decode("ascii"),
                                                )

                out.write(line)
                out.write("\n")
        else:
            out.write(jj2_tpl.render(context))

        out.seek(0)
        return out

    # To PNG with inkscape
    # -------------------------------------------------------------------------
    if outform == "png":

        if cachedir is None:
            cachedir_tmp = tempfile.TemporaryDirectory()
            cachedir = cachedir_tmp.name
        else:
            cachedir.mkdir(parents=True, exist_ok=True)

        tmpsvg = tempfile.NamedTemporaryFile(
                suffix=".svg",
                mode = "w",
                delete = False,
                dir = str(cachedir),
                )
        tmpsvg.close()
        tmppng = tempfile.NamedTemporaryFile(
                suffix = ".png",
                mode = "w",
                delete = False,
                dir = str(cachedir),
                )
        tmppng.close()
        try:
            log.info(
                    "Exporting to {} using inkscape" \
                            .format(outform),
                            )
            import subprocess

            jj2_tpl.stream(context).dump( tmpsvg.name )

            inkscape_process = subprocess.Popen(
                    [
                        "inkscape",
                        tmpsvg.name,
                        "--export-filename",
                        tmppng.name,
                        ],
                    stdout = subprocess.PIPE,
                    stderr = subprocess.STDOUT,
                    universal_newlines = True,
                    )

            for line_out in iter(inkscape_process.stdout.readline, ""):
                log.debug(line_out)

            inkscape_process.stdout.close()

            rv = inkscape_process.wait()

            if rv != 0:
                raise Exception(
                        "Bad inkscape return code '{}'" \
                                .format(inkscape_process.returncode)
                                )

            with open(tmppng.name, "rb") as fh:
                buf = io.BytesIO(fh.read())

            return buf

        except Exception as e:
            log.warning("Failed to export with inkscape")
            log.debug(e, exc_info=True)

        finally:
            os.unlink(tmpsvg.name)
            os.unlink(tmppng.name)

            try:
                cachedir_tmp.cleanup()
            except:
                pass

        return None
