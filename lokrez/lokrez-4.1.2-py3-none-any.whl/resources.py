import io
import os
import pathlib
import sys
import urllib
import zipfile

import requests

# -----------------------------------------------------------------------------
def download_file(url, with_progressbar = True, proxy = None):

    r = requests.get(
            url,
            stream = with_progressbar,
            proxies = { "https": proxy, "http": proxy },
            )

    if not with_progressbar:
        return io.BytesIO(r.content)

    total = r.headers.get("content-length")

    f = io.BytesIO()

    if total is not None:
        downloaded = 0
        total = int(total)
        for data in r.iter_content(
                chunk_size = max(int(total/1000), 1024*1024),
                ):
            f.write(data)
            downloaded += len(data)
            done = int(50*downloaded/total)
            sys.stdout.write( "\r[{}{}] ({:02d}%)".format(
                "█" * done,
                " " * (50-done),
                done*2,
                ) )
            sys.stdout.flush()
        sys.stdout.write("\n")
    else:
        f = write(r.content)

    return f

# -----------------------------------------------------------------------------
def download_res(
        dstdir,
        game = None,
        source = None,
        store_raw = False,
        proxy = None,
        log = None,
        ):
    """TODO: Docstring for download_res_pplus.
    :returns: TODO

    """
    if not game:
        return

    # Select default source if needed
    if not source:
        if game.GAME.name in [ "pplus", "melee" ]:
            source = "smashlyon"
        elif game.GAME.name == "ssbu":
            source = "spriters"

        log.info("Using default source {}".format(source))

    if source not in ["smashlyon", "spriters"]:
        raise NotImplementedError(
                "The only working sources are 'smashlyon' and 'spriters'",
                )

    gamedir = dstdir / game.GAME.name

    try:
        gamedir.mkdir(parents=True)
    except FileExistsError:
        log.debug("Game directory already exist")

    # A cache to save time
    cache = {}

    # Iter over each character
    for character in game.EVERYONE:
        log.warning("Downloading images for {}...".format(character.name))

        chardir = gamedir /  character.name

        if not store_raw:
            try:
                chardir.mkdir(parents=True)
            except FileExistsError:
                log.info(
                        "Directory already exists for {}" \
                                .format(character.name)
                        )

                try:
                    next(chardir.iterdir())
                    log.warning(
                            "Directory not empty for {}, skipping" \
                                    .format(character.name)
                            )
                    continue
                except StopIteration:
                    log.info(
                            "Directory empty, downloading",
                            )

        # Download urls & write image files
        for url_nb, url in enumerate(character.res_urls[source]):

            # If we have the file in cache, just get it
            if url in cache and cache[url] is not None:
                log.debug("Found url '{}' in cache".format(url))
                f = cache[url]

            else:
                try:
                    f = download_file(url, proxy = proxy)

                except Exception as e:
                    try:
                        # Try the download a 2nd time
                        log.warning("Download failed ({}), retrying".format(e))
                        f = download_file(url, proxy = proxy)
                    except Exception as e:
                        log.error("Download failed({})".format(e))
                        log.debug(e, exc_info = True)
                        continue

                # We save the file in cache if it's the second time we need
                # to download it.
                if url in cache:
                    log.debug("Saving url '{}' in cache".format(url))
                    cache[url] = f
                else:
                    log.debug("Marking url '{}' in cache".format(url))
                    cache[url] = None


            # if store_raw: we just save the raw zip file
            if store_raw:
                outfile_name = pathlib.Path(
                        urllib.parse.urlparse(url).path
                        ) \
                                .name
                with open(str(gamedir/outfile_name), "wb") as outfile:
                    outfile.write(f.getbuffer())

                # Add symlink for readablity
                os.symlink(
                        str(outfile_name),
                        str( gamedir/
                        "{charname}.{nb}.zip".format(
                            charname = character.name,
                            nb = url_nb+1,
                            )),
                        )

                continue

            # otherwise: get the characters pictures and write them in the
            # outdir
            with zipfile.ZipFile(f) as zf:
                for source_file in zf.filelist:

                    if source_file.is_dir():
                        continue

                    source_filename = source_file.filename

                    if "No Gamma Fix" in source_filename:
                        continue

                    if not any(c in source_filename for c in character.codenames):
                        continue

                    target_filename = pathlib.Path(source_filename).name

                    if target_filename in ["","Tag.txt"]:
                        continue

                    target_filename = pathlib.Path(source_filename).name

                    for codename in character.codenames:
                        target_filename = target_filename.replace(
                                codename,
                                character.name,
                                )

                    log.debug("Writing file '{}'".format(target_filename))

                    target_filename = chardir / target_filename

                    with open(str(target_filename), "wb") as tf:
                        tf.write(zf.read(source_filename))

# =============================================================================
if __name__ == '__main__':

    import argparse
    import logging
    import tempfile

    logging.basicConfig(
            level = logging.DEBUG,
            format = "%(message)s",
            )

    parser = argparse.ArgumentParser()

    parser.add_argument(
            "dstdir",
            default = None,
            help = "directory where to store the downloaded resources " \
                   "(default to a temporary file)",
                   )

    args = parser.parse_args()

    if args.dstdir is None:
        args.dstdir = tempfile.mkdtemp()
        logging.warning(
                "Storing in temporary directory : {}".format(args.dstdir)
                )

    download_res_ssbu(
            dstdir = args.dstdir,
            log = logging,
            )
