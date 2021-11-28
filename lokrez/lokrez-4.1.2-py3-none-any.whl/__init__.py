import argparse
import configparser
import copy
import datetime
import html
import io
import json
import logging
import pathlib
import pprint
import requests
import sys
import urllib

import appdirs

from . import export
from . import resources
from . import smashgg
from . import version

from .games import ssbu, pplus, melee

# =============================================================================
__version__ = version.__version__
__license__ = version.__license__

ROOTDIR = pathlib.Path(__file__).absolute().parent

APPDIRS = appdirs.AppDirs(version.NAME, version.ENTITY)

LOG_DUMMY = logging.getLogger("dummy")
LOG_DUMMY.addHandler(logging.NullHandler())

DEFAULT_DIR_TEMPLATES = ROOTDIR / "templates"

# =============================================================================
class StoreOptionKeyPair(argparse.Action):
    def __init__(
            self,
            option_strings,
            dest,
            nargs=1,
            const=None,
            default=None,
            type=None,
            choices=None,
            required=False,
            help=None,
            metavar="KEY=VALUE",
            ):

        if nargs == 0:
            raise ValueError(
                    'nargs for append actions must be > 0; if arg '
                    'strings are not supplying the value to append, '
                    'the append const action may be more appropriate'
                    )
        if const is not None and nargs != '?':
            raise ValueError('nargs must be %r to supply const' % '?')

        super(StoreOptionKeyPair, self).__init__(
                option_strings=option_strings,
                dest=dest,
                nargs=nargs,
                const=const,
                default=default,
                type=type,
                choices=choices,
                required=required,
                help=help,
                metavar=metavar,
                )

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            options = getattr(namespace, self.dest)
        except AttributeError:
            options = {}

        for kv in values:
            try:
                k,v = kv.split("=")
            except ValueError:
                k = kv
                v = True

            options[k] = v

        setattr(namespace, self.dest, options)


# =============================================================================
def get_templates_list(
        dir_templates = DEFAULT_DIR_TEMPLATES,
        ):

    templates_list = []

    dir_templates_path = pathlib.Path(dir_templates)

    for potential_template in dir_templates_path.iterdir():

        if (potential_template / "template.svg.j2").is_file():
            templates_list.append(potential_template.name)

    return templates_list

# =============================================================================
def get_infos_from_file(
        lkrz_file_path,
        options = {},
        outform = "dict",
        log = LOG_DUMMY,
        ):

    if not lkrz_file_path.exists():
        raise IOError( "lkrz file '{}' does not exist" \
                .format(str(lkrz_file_path)) )

    lkrz = configparser.ConfigParser()
    lkrz.read(str(lkrz_file_path))

    log.info("Loading data from '{}'".format(str(lkrz_file_path)))

    top_players = {}
    tournament = None

    for s in lkrz:
        section = lkrz[s]
        if s == "Tournament":
            tournament = smashgg.Tournament(
                    id = 0,
                    name = section["name"],
                    game = section["game"],
                    slug = section["slug"],
                    startAt = datetime.datetime.strptime(
                        section["date"],
                        "%Y-%m-%d %H:%M:%S",
                        ),
                    numEntrants = int(section["numEntrants"]),
                    venueName = section["location"],
                    ) \
                            .clean_name(
                                    options.get("name_seo_delimiter", None)
                                    )

        elif s.startswith("player "):
            chars = {}
            for char in section["characters"].split(","):
                c = char.strip()
                charname = c.split("_")[0]
                charskin = c.split("_")[1].split(" ")[0]
                charscore = float(c.split("(")[1].split(")")[0])

                chars[(charname,charskin)] = charscore

            player = smashgg.Player(
                    id = 0,
                    prefix = section["team"],
                    gamerTag = section["tag"],
                    placement = section["placement"],
                    seeding = section["seeding"],
                    twitterHandle = section["twitter"],
                    chars = chars,
                    )

            top_players[player.gamerTag] = player

    # Re-sort top players by their placement
    top_players = sorted(
            top_players.values(),
            key = lambda p: p.placement,
            )

    return format_infos(
            outform,
            tournament,
            top_players,
            )

# =============================================================================
def get_infos_from_url(
        url,
        token,
        options = {},
        outform = "dict",
        top = 8,
        proxy = None,
        log = LOG_DUMMY,
        ):

    url_parsed = urllib.parse.urlparse(url)

    if url_parsed.netloc not in [ "smash.gg" ]:
        raise ValueError("Unsupported domain name")
    if outform not in [ "dict", "lkrz" ]:
        raise ValueError("Unsupported outform")

    # -------------------------------------------------------------------------
    tournament = None
    event = None

    # -------------------------------------------------------------------------
    if url_parsed.netloc == "smash.gg":

        if (url_parsed.path.split("/")[1] != "tournament"):
            log.error("Incomplete URL '{}'".format(url))
            raise Exception("No tournament found in url {}".format(url))

        try:
            tournament = url_parsed.path.split("/")[2]
        except:
            log.error("Incomplete URL '{}'".format(url))
            raise Exception("No tournament slug found in url {}".format(url))

        try:
            if (url_parsed.path.split("/")[3] == "event"):
                event = url_parsed.path.split("/")[4]
        except:
            log.info("No event slug found in url")

    # -------------------------------------------------------------------------
    return get_infos_from_id_or_slug(
            id_or_slug = tournament,
            event_slug = event,
            token = token,
            options = options,
            outform = outform,
            top = top,
            proxy = proxy,
            log = log,
            )

# =============================================================================
def get_infos_from_id_or_slug(
        id_or_slug,
        event_slug = None,
        token = "",
        options = [],
        outform = "dict",
        top = 8,
        proxy = None,
        log = LOG_DUMMY,
        ):
    # Get infos from smash.gg and write the config file
    tournament, top_players = getTournamentTop(
            id_or_slug = id_or_slug,
            event_slug = event_slug,
            import_options = options,
            top = top,
            token = token,
            proxy = proxy,
            log = log,
            )

    if tournament is None or top_players is None:
        log.error("Could not load data from smash.gg")
        raise Exception("Could not load data from smash.gg")

    return format_infos(outform, tournament, top_players)


# =============================================================================
def format_infos(
        outform,
        tournament,
        top_players,
        ):

    # -------------------------------------------------------------------------
    if outform == "dict":
        return {
                "tournament": tournament,
                "players": top_players,
                }

    # -------------------------------------------------------------------------
    if outform == "lkrz":
        return "\n".join(
                [ tournament.conf() ] \
                        + list(map(
                            lambda p:p.conf(),
                            top_players,
                            ))
                        )

# =============================================================================
def init_resources(
        imgdir,
        game,
        source = None,
        store_raw = False,
        proxy = None,
        log = LOG_DUMMY,
        ):

    # Create imgdir
    imgdir.mkdir(parents=True, exist_ok=True)

    # Start resources download according to game
    if game in ssbu.GAME.list_names():
        game = ssbu
    elif game in melee.GAME.list_names():
        game = melee
    elif game in pplus.GAME.list_names():
        game = pplus
    else:
        log.error("Unknown game '{}'".format(game))
        return 1

    resources.download_res(
            dstdir = imgdir,
            game = game,
            source = source,
            store_raw = store_raw,
            proxy = proxy,
            log = log,
            )

    return 0

# =============================================================================
def generate_pic(
        infos_or_lkrzfile = None,
        template = None,
        outform = "svg",
        options = {},
        dir_templates = DEFAULT_DIR_TEMPLATES,
        dir_res = None,
        dir_cache = None,
        log = LOG_DUMMY,
        ):

    if outform.startswith("."):
        outform = outform[1:]

    if outform not in ["svg", "png"]:
        raise Exception("Unsupported outform")

    if type(infos_or_lkrzfile) == str:
        # load lkrz as dict infos
        infos = get_infos_from_file(
                lkrz_file_path = pathlib.Path(infos_or_lkrzfile),
                options = options,
                outform = "dict",
                log = log,
                )
    else:
        infos = infos_or_lkrzfile

    # -------------------------------------------------------------------------
    # Build the context which will be passed to the template
    context = {
            "tournament": infos["tournament"].clean_name(
                options.get(
                    "name_seo_delimiter",
                    None
                    )
                ),
            "players" : sorted(
                infos["players"],
                key = lambda p: p.placement,
                ),
            "dir_res_ssbu": dir_res,
            "dir_template": str(dir_templates/template),
            "options": options,
            }

    pic = export.generate_pic(
            dir_templates,
            template,
            context,
            outform,
            log = log,
            cachedir = dir_cache,
            options = options,
            )

    if pic is None:
        raise Exception("Failed to generate pic")

    return pic

# =============================================================================
def main():

    # -------------------------------------------------------------------------
    parser = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            )

    subparsers = parser.add_subparsers(
            dest = "command",
            help = "commands",
            )

    parser.add_argument(
            "--proxy", "-p",
            default = None,
            help = "the proxy to use",
            )

    # -------------------------------------------------------------------------
    init_parser = subparsers.add_parser(
            "init",
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            )

    init_parser.add_argument(
            "game",
            default = "ssbu",
            help = "The game you want to initialize the resources for",
            )

    init_parser.add_argument(
            "--source", "-s",
            default = None,
            choices = ["spriters", "smashlyon"],
            help = "From where should the resources images be downloaded",
            )

    init_parser.add_argument(
            "--imgdir", "-ID",
            type = pathlib.Path,
            default = pathlib.Path(APPDIRS.user_data_dir) / "res",
            help = "The directory we should download the resources to",
            )

    init_parser.add_argument(
            "--raw", "-r",
            action = "store_true",
            help = "Download the raw zipfiles instead of extracting them",
            )

    # -------------------------------------------------------------------------
    top8_parser = subparsers.add_parser(
            "top8",
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            )

    top8_parser.add_argument(
            "tournament",
            default = None,
            help = "The tournament url, slug or id",
            )

    top8_parser.add_argument(
            "--token", "-t",
            default = None,
            help = "the authentication token to use ; needed if you're " \
                   "generating the top8 from a smash.gg url",
            )

    top8_parser.add_argument(
            "--playerskinsdb", "-P",
            type = (lambda s: s if s.startswith("http") else pathlib.Path(s)),
            default = ROOTDIR / "data" / "playerskinsdb.json",
            help = "A JSON file path or url matching player tags, characters,"\
                   " sponsors, and preferred skins",
            )

    top8_parser.add_argument(
            "--imgdir", "-ID",
            type = pathlib.Path,
            default = pathlib.Path(APPDIRS.user_data_dir) / "res",
            help = "The directories containing images, be careful whether " \
                   "you specify an absolute path or a relative one.",
            )
    top8_parser.add_argument(
            "--cachedir", "-CD",
            type = pathlib.Path,
            default = pathlib.Path(APPDIRS.user_cache_dir),
            help = "A directory to use for temporary files",
            )
    top8_parser.add_argument(
            "--templatesdir", "-TD",
            type = pathlib.Path,
            default = DEFAULT_DIR_TEMPLATES,
            help = "The local result templates directory",
            )

    top8_parser.add_argument(
            "--template", "-T",
            default = "rebootlyon2020",
            help = "The local result template to use",
            )
    top8_parser.add_argument(
            "--template-options", "-TO",
            nargs="+",
            action = StoreOptionKeyPair,
            default = {},
            help = "Template-specific options (like 'covid' or 'animated')",
            )
    top8_parser.add_argument(
            "--export-options", "-EO",
            nargs="+",
            action = StoreOptionKeyPair,
            default = {},
            help = "Export options (like 'svg_embed_png')",
            )

    top8_parser.add_argument(
            "--import-options", "-IO",
            nargs="+",
            action = StoreOptionKeyPair,
            default = {},
            help = "Import options (like 'use_smashgg_prefixes')",
            )

    top8_parser.add_argument(
            "--outfile", "-o",
            type = pathlib.Path,
            default = None,
            help = "The SVG or PNG local result file to output to ; if it's " \
                   "not specified, it will default to SVG and use the "       \
                   "tournament slug as name ; if you're generating a "        \
                   "localresult from a url, a LKRZ file with the same name "  \
                   "will also be generated along the image file (unless you " \
                   "use the --no-lkrz flag).",
            )

    parser.add_argument( "--no-lkrz", "-nl",
                         default = False,
                         action = "store_true",
                         help = "Do not output a LKRZ file" )

    # -------------------------------------------------------------------------
    parser.add_argument( "--verbose", "-v",
                         default = 0,
                         action = "count",
                         help = "increase verbosity" )

    parser.add_argument( "--version", "-V",
                         default = False,
                         action = "store_true",
                         help = "show version number" )

    # -------------------------------------------------------------------------
    args = parser.parse_args()

    # Set log level
    # -------------------------------------------------------------------------
    log = logging.getLogger(version.NAME)
    log.setLevel(logging.DEBUG)

    log_handler_console = logging.StreamHandler()
    log_handler_console.setLevel(logging.WARNING)

    if(args.verbose >= 2):
        log_handler_console.setLevel(logging.DEBUG)
    elif(args.verbose >=1):
        log_handler_console.setLevel(logging.INFO)
    else:
        log_handler_console.setLevel(logging.WARNING)

    log_formatter_console = logging.Formatter("%(name)s:%(levelname)s: %(message)s")

    log_handler_console.setFormatter(log_formatter_console)

    log.addHandler(log_handler_console)

    # Print all arguments in debug
    # -------------------------------------------------------------------------
    log.debug( "Command arguments:\n{}".format( pprint.pformat(vars(args))) )

    # Print version if required
    # -------------------------------------------------------------------------
    if args.version:
        print(version.VERSION_NAME)
        return 0

    # Check if command is recognized
    # -------------------------------------------------------------------------
    if args.command not in [ "init", "top8" ]:
        parser.print_help()
        return 1

    # -- init
    # -------------------------------------------------------------------------
    if args.command == "init":

        rv = init_resources(
                imgdir = args.imgdir,
                game = args.game,
                source = args.source,
                store_raw = args.raw,
                proxy = args.proxy,
                log = log,
                )

        return rv

    # -- top8
    # -------------------------------------------------------------------------
    if args.command == "top8":

        # Initialize PLAYERSKINS db
        log.debug("loading playerskins db from '{}'" \
                .format(args.playerskinsdb))
        try:
            PLAYERSKINS =  requests.get(args.playerskinsdb).json()
            smashgg.GET_PLAYERDATA = (lambda tag: PLAYERSKINS[tag.lower()])
        except:
            with args.playerskinsdb.open("r", encoding="utf8") as f:
                PLAYERSKINS = json.load(f)
                smashgg.GET_PLAYERDATA = (lambda tag: PLAYERSKINS[tag.lower()])

        #
        tournament = None
        top_players = {}
        lkrz_file = None

        all_options = {
                **args.import_options,
                **args.template_options,
                **args.export_options,
                }

        # Determine the nature of the 'tournament' argument :
        # - url
        # - id or slug
        # - lkrz file
        # url
        if (    args.tournament.startswith("http://")
             or args.tournament.startswith("https://") ):
            infos = get_infos_from_url(
                    url = args.tournament,
                    token = args.token,
                    options = args.import_options,
                    outform = "dict",
                    top = 8,
                    proxy = args.proxy,
                    log = log,
                    )

        # lkrz file
        elif pathlib.Path(args.tournament).exists():
            infos = get_infos_from_file(
                    lkrz_file_path = pathlib.Path(args.tournament),
                    options = args.import_options,
                    outform = "dict",
                    log = log,
                    )

        # id or slug
        else:
            infos = get_infos_from_id_or_slug(
                    id_or_slug = args.tournament,
                    token = args.token,
                    options = args.import_options,
                    outform = "dict",
                    top = 8,
                    proxy = args.proxy,
                    log = log,
                    )

        tournament = infos["tournament"]
        top_players = infos["players"]

        if tournament is None or top_players is None:
            log.error("Could not load data")
            return 1

        # Default outfile is 'tournament-slug.svg'
        if args.outfile is None:
            args.outfile = pathlib.Path(
                    "{}.svg".format(tournament.slug),
                    )

        # Save a lkrz file
        if not args.no_lkrz:
            lkrz_data = format_infos("lkrz", tournament, top_players)
            lkrz_file = args.outfile.with_suffix(".lkrz")

            with lkrz_file.open("w", encoding="utf8") as f:
                f.write(lkrz_data)

        # If the outfile we were asked for was a .lkrz, we're done
        if args.outfile.suffix == ".lkrz":
            return 0

        # Otherwise, let's generate the picture file
        # First build the context which will be passed to the template
        try:
            dir_res = (args.imgdir / tournament.game.name).as_uri() # not absolute => error
        except ValueError:
            dir_res = (args.imgdir / tournament.game.name).as_posix()

        pic = generate_pic(
                infos_or_lkrzfile = infos,
                template = args.template,
                outform = args.outfile.suffix,
                options = all_options,
                dir_templates = args.templatesdir,
                dir_res = dir_res,
                dir_cache = args.cachedir,
                log = log,
                )

        if pic is None:
            return 1

        log.info("Saving picture as '{}'".format(args.outfile))

        if type(pic) == io.StringIO:
            openmode = "w"
        else:
            openmode = "wb"
        with args.outfile.open(openmode) as f:
            f.write(pic.read())

        return 0

# -----------------------------------------------------------------------------
def getTournamentTop(
        id_or_slug,
        event_slug = None,
        import_options = [],
        top = 8,
        token = "",
        proxy = None,
        log=LOG_DUMMY,
        ):
    """Returns a tuple : the smashgg.Tournament object and a list of the top
    smashgg.Player in that tournament."""

    # TODO if url matches challonge
    #
    #data = challonge.get_participants(
    #        api_key = token,
    #        tournament = id_or_slug,
    #        )
    #
    #top_array = []*top
    #for p in data:
    #   top_array[p["participant"]["final_rank"]] = ...

    # -------------------------------------------------------------------------
    # Select the right event (the one with the most entrants or the most sets)
    def selectBiggestEvent(data, log=LOG_DUMMY):

        try:
            event = data["events"][0]
        except:
            log.error("No event found in data")
            log.debug(data)
            return None

        try:
            numEntrants = event["numEntrants"]
        except KeyError:
            numEntrants = event["standings"]["pageInfo"]["total"]

        for e in data["events"]:
            try:
                ne = e["numEntrants"]
            except KeyError:
                ne = e["standings"]["pageInfo"]["total"]

            if ne > numEntrants:
                event = e
                numEntrants = ne

        log.info("Selected Event '{}' with {} entrants" \
                .format(
                    event["name"],
                    numEntrants,
                    ))

        return event

    # -------------------------------------------------------------------------
    # Select the specified event
    def selectEventBySlug(data, slug, log=LOG_DUMMY):

        try:
            event = data["events"][0]
        except:
            log.error("No event found in data")
            log.debug(data)
            return None

        for e in data["events"]:
            try:
                slug_full = e["slug"]
            except KeyError:
                continue

            if (    slug == slug_full
                 or slug == slug_full.split("/")[-1] ):
                log.info("Selected Event '{}' by slug '{}'" \
                        .format(
                            e["name"],
                            slug,
                            ))
                return e


        log.error("No Event matching slug '{}' found".format(slug))
        return None

    # -------------------------------------------------------------------------
    data = None

    try:
        data = smashgg.run_query(
                query_name = "getTournamentTopById",
                variables = {
                    "id" : int(id_or_slug), # If this fails, it's a slug
                    "top": top,
                    },
                query_dir = ROOTDIR / "queries",
                token = token,
                proxy = proxy,
                log = log,
                )

    except ValueError:
        data = smashgg.run_query(
                query_name = "getTournamentTopBySlug",
                variables = {
                    "slug" : id_or_slug,
                    "top": top,
                    },
                query_dir = ROOTDIR / "queries",
                token = token,
                proxy = proxy,
                log = log,
                )

    try:
        tournament_data = data["tournament"]
    except:
        log.error("Failed to load Tournaments")
        return None,None

    if tournament_data is None:
        log.error("Failed to load Tournament")
        return None,None

    event = None
    if event_slug is None:
        event = selectBiggestEvent(tournament_data, log)
    else:
        event = selectEventBySlug(tournament_data, event_slug, log)

    if event is None :
        return None,None

    # Get the tournament
    tournament = smashgg.Tournament(
            id = tournament_data["id"],
            slug = tournament_data["slug"],
            game = event["videogame"],
            name = tournament_data["name"],
            startAt = \
                    datetime.datetime. \
                    fromtimestamp(tournament_data["startAt"]),
            numEntrants = event["standings"]["pageInfo"]["total"],
            venueAddress = tournament_data["venueAddress"],
            venueName = tournament_data["venueName"],
            city = tournament_data["city"],
            countryCode = tournament_data["countryCode"],
            hashtag = tournament_data["hashtag"],
            ) \
                    .clean_name(
                            import_options.get("name_seo_delimiter", None)
                            )


    # Get the top players
    top_players = {}

    standings = event["standings"]["nodes"]

    for standing in standings :

        seeding = None
        seeding32 = None
        for seed in standing["entrant"]["seeds"]:
            # Take the seeding from the phase with *all* Event entrants
            if seed["phase"]["numSeeds"] == tournament.numEntrants:
                seeding = seed["groupSeedNum"]
            if seed["phase"]["numSeeds"] == 32:
                seeding32 = seed["groupSeedNum"]
        if seeding is None:
            log.info("no global seeding found, using top 32 seeding")
            seeding = seeding32

        participant_data = standing["entrant"]["participants"][0]

        try:
            twitterHandle = participant_data \
                    ["player"] \
                    ["user"] \
                    ["authorizations"] \
                    [0] \
                    ["externalUsername"]
        except:
            twitterHandle = None

        if "use_smashgg_prefixes" in import_options:
            prefix = participant_data["prefix"]
        else:
            prefix = ""

        player = smashgg.Player(
                id = standing["entrant"]["id"],
                prefix = prefix,
                gamerTag = participant_data["gamerTag"],
                placement = standing["placement"],
                seeding = seeding,
                twitterHandle = twitterHandle,
                )

        top_players[player.id] = player

    # -------------------------------------------------------------------------
    # Now, we need to find which characters those top players chose
    data = None

    data = smashgg.run_query(
            query_name = "getCharsByTournamentIdAndEntrantIds",
            variables = {
                "tournamentId" : int(tournament.id),
                "entrantIds": [ id for id in top_players.keys() ],
                },
            query_dir = ROOTDIR / "queries",
            token = token,
            proxy = proxy,
            log = log,
            )

    try:
        tournament_data = data["tournament"]
    except:
        log.error("Failed to load Tournament")
        return None,None

    if tournament_data is None:
        log.error("Failed to load Tournament")
        return None,None

    event = None
    if event_slug is None:
        event = selectBiggestEvent(tournament_data, log)
    else:
        event = selectEventBySlug(tournament_data, event_slug, log)

    if event is None :
        return None,None

    # TODO check that sets number is < to hardcoded 100 max value (cf query)
    sets = event["sets"]["nodes"]

    for s in sets:
        try:
            for g in s["games"]:

                winnerId = g["winnerId"]

                for slct in g["selections"]:

                    if slct["selectionType"] == "CHARACTER":
                        eid = slct["entrant"]["id"]
                        try:
                            top_players[eid].add_character_selection(
                                    game = tournament.game,
                                    character = slct["selectionValue"],
                                    win = (winnerId == eid),
                                    )
                        except KeyError:
                            pass
        except TypeError:
            # If some games or selections are null, this can happen
            continue

    # Sort top_players by rank instead of id:
    top_players_sorted = sorted(
                top_players.values(),
                key = lambda p: p.placement,
                )

    # Return the data
    return tournament, top_players_sorted

# =============================================================================
if __name__ == '__main__':
    rv = main()
    sys.exit(rv)

