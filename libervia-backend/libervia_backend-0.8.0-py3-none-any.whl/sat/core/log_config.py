#!/usr/bin/env python3


# Libervia: an XMPP client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""High level logging functions"""
# XXX: this module use standard logging module when possible, but as SàT can work in different cases where logging is not the best choice (twisted, pyjamas, etc), it is necessary to have a dedicated module. Additional feature like environment variables and colors are also managed.

from sat.core.constants import Const as C
from sat.core import log


class TwistedLogger(log.Logger):
    colors = True
    force_colors = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from twisted.logger import Logger
        self.twisted_log = Logger()

    def out(self, message, level=None, **kwargs):
        """Actually log the message

        @param message: formatted message
        """
        if kwargs.pop('exc_info', False):
            message = self.addTraceback(message)
        self.twisted_log.emit(
            level=self.level_map[level],
            format=message,
            sat_logged=True,
            **kwargs,
        )


class ConfigureBasic(log.ConfigureBase):
    def configureColors(self, colors, force_colors, levels_taints_dict):
        super(ConfigureBasic, self).configureColors(
            colors, force_colors, levels_taints_dict
        )
        if colors:
            import sys

            try:
                isatty = sys.stdout.isatty()
            except AttributeError:
                isatty = False
            # FIXME: isatty should be tested on each handler, not globaly
            if (force_colors or isatty):
                # we need colors
                log.Logger.post_treat = lambda logger, level, message: self.ansiColors(
                    level, message
                )
        elif force_colors:
            raise ValueError("force_colors can't be used if colors is False")

    @staticmethod
    def getProfile():
        """Try to find profile value using introspection"""
        import inspect

        stack = inspect.stack()
        current_path = stack[0][1]
        for frame_data in stack[:-1]:
            if frame_data[1] != current_path:
                if (
                    log.backend == C.LOG_BACKEND_STANDARD
                    and "/logging/__init__.py" in frame_data[1]
                ):
                    continue
                break

        frame = frame_data[0]
        args = inspect.getargvalues(frame)
        try:
            profile = args.locals.get("profile") or args.locals["profile_key"]
        except (TypeError, KeyError):
            try:
                try:
                    profile = args.locals["self"].profile
                except AttributeError:
                    try:
                        profile = args.locals["self"].parent.profile
                    except AttributeError:
                        profile = args.locals[
                            "self"
                        ].host.profile  # used in quick_frontend for single profile configuration
            except Exception:
                # we can't find profile, we return an empty value
                profile = ""
        return profile


class ConfigureTwisted(ConfigureBasic):
    LOGGER_CLASS = TwistedLogger

    def preTreatment(self):
        from twisted import logger
        global logger
        self.level_map = {
            C.LOG_LVL_DEBUG: logger.LogLevel.debug,
            C.LOG_LVL_INFO: logger.LogLevel.info,
            C.LOG_LVL_WARNING: logger.LogLevel.warn,
            C.LOG_LVL_ERROR: logger.LogLevel.error,
            C.LOG_LVL_CRITICAL: logger.LogLevel.critical,
        }
        self.LOGGER_CLASS.level_map = self.level_map

    def configureLevel(self, level):
        self.level = self.level_map[level]

    def configureOutput(self, output):
        import sys
        from twisted.python import logfile
        self.log_publisher = logger.LogPublisher()

        if output is None:
            output = C.LOG_OPT_OUTPUT_SEP + C.LOG_OPT_OUTPUT_DEFAULT
        self.manageOutputs(output)

        if C.LOG_OPT_OUTPUT_DEFAULT in log.handlers:
            if self.backend_data is None:
                raise ValueError(
                    "You must pass options as backend_data with Twisted backend"
                )
            options = self.backend_data
            log_file = logfile.LogFile.fromFullPath(options['logfile'])
            self.log_publisher.addObserver(
                logger.FileLogObserver(log_file, self.textFormatter))
            # we also want output to stdout if we are in debug or nodaemon mode
            if options.get("nodaemon", False) or options.get("debug", False):
                self.log_publisher.addObserver(
                    logger.FileLogObserver(sys.stdout, self.textFormatter))

        if C.LOG_OPT_OUTPUT_FILE in log.handlers:

            for path in log.handlers[C.LOG_OPT_OUTPUT_FILE]:
                log_file = (
                    sys.stdout if path == "-" else logfile.LogFile.fromFullPath(path)
                )
                self.log_publisher.addObserver(
                    logger.FileLogObserver(log_file, self.textFormatter))

        if C.LOG_OPT_OUTPUT_MEMORY in log.handlers:
            raise NotImplementedError(
                "Memory observer is not implemented in Twisted backend"
            )

    def configureColors(self, colors, force_colors, levels_taints_dict):
        super(ConfigureTwisted, self).configureColors(
            colors, force_colors, levels_taints_dict
        )
        self.LOGGER_CLASS.colors = colors
        self.LOGGER_CLASS.force_colors = force_colors
        if force_colors and not colors:
            raise ValueError("colors must be True if force_colors is True")

    def postTreatment(self):
        """Install twistedObserver which manage non SàT logs"""
        # from twisted import logger
        import sys
        filtering_obs = logger.FilteringLogObserver(
            observer=self.log_publisher,
            predicates=[
                logger.LogLevelFilterPredicate(self.level),
                ]
        )
        logger.globalLogBeginner.beginLoggingTo([filtering_obs])

    def textFormatter(self, event):
        if event.get('sat_logged', False):
            timestamp = ''.join([logger.formatTime(event.get("log_time", None)), " "])
            return f"{timestamp}{event.get('log_format', '')}\n"
        else:
            eventText = logger.eventAsText(
                event, includeSystem=True)
            if not eventText:
                return None
            return eventText.replace("\n", "\n\t") + "\n"


class ConfigureStandard(ConfigureBasic):
    def __init__(
        self,
        level=None,
        fmt=None,
        output=None,
        logger=None,
        colors=False,
        levels_taints_dict=None,
        force_colors=False,
        backend_data=None,
    ):
        if fmt is None:
            fmt = C.LOG_OPT_FORMAT[1]
        if output is None:
            output = C.LOG_OPT_OUTPUT[1]
        super(ConfigureStandard, self).__init__(
            level,
            fmt,
            output,
            logger,
            colors,
            levels_taints_dict,
            force_colors,
            backend_data,
        )

    def preTreatment(self):
        """We use logging methods directly, instead of using Logger"""
        import logging

        log.getLogger = logging.getLogger
        log.debug = logging.debug
        log.info = logging.info
        log.warning = logging.warning
        log.error = logging.error
        log.critical = logging.critical

    def configureLevel(self, level):
        if level is None:
            level = C.LOG_LVL_DEBUG
        self.level = level

    def configureFormat(self, fmt):
        super(ConfigureStandard, self).configureFormat(fmt)
        import logging

        class SatFormatter(logging.Formatter):
            """Formatter which manage SàT specificities"""
            _format = fmt
            _with_profile = "%(profile)s" in fmt

            def __init__(self, can_colors=False):
                super(SatFormatter, self).__init__(self._format)
                self.can_colors = can_colors

            def format(self, record):
                if self._with_profile:
                    record.profile = ConfigureStandard.getProfile()
                do_color = self.with_colors and (self.can_colors or self.force_colors)
                if ConfigureStandard._color_location:
                    # we copy raw formatting strings for color_*
                    # as formatting is handled in ansiColors in this case
                    if do_color:
                        record.color_start = log.COLOR_START
                        record.color_end = log.COLOR_END
                    else:
                        record.color_start = record.color_end = ""
                s = super(SatFormatter, self).format(record)
                if do_color:
                    s = ConfigureStandard.ansiColors(record.levelname, s)
                return s

        self.formatterClass = SatFormatter

    def configureOutput(self, output):
        self.manageOutputs(output)

    def configureLogger(self, logger):
        self.name_filter = log.FilterName(logger) if logger else None

    def configureColors(self, colors, force_colors, levels_taints_dict):
        super(ConfigureStandard, self).configureColors(
            colors, force_colors, levels_taints_dict
        )
        self.formatterClass.with_colors = colors
        self.formatterClass.force_colors = force_colors
        if not colors and force_colors:
            raise ValueError("force_colors can't be used if colors is False")

    def _addHandler(self, root_logger, hdlr, can_colors=False):
        hdlr.setFormatter(self.formatterClass(can_colors))
        root_logger.addHandler(hdlr)
        root_logger.setLevel(self.level)
        if self.name_filter is not None:
            hdlr.addFilter(self.name_filter)

    def postTreatment(self):
        import logging

        root_logger = logging.getLogger()
        if len(root_logger.handlers) == 0:
            for handler, options in list(log.handlers.items()):
                if handler == C.LOG_OPT_OUTPUT_DEFAULT:
                    hdlr = logging.StreamHandler()
                    try:
                        can_colors = hdlr.stream.isatty()
                    except AttributeError:
                        can_colors = False
                    self._addHandler(root_logger, hdlr, can_colors=can_colors)
                elif handler == C.LOG_OPT_OUTPUT_MEMORY:
                    from logging.handlers import BufferingHandler

                    class SatMemoryHandler(BufferingHandler):
                        def emit(self, record):
                            super(SatMemoryHandler, self).emit(self.format(record))

                    hdlr = SatMemoryHandler(options)
                    log.handlers[
                        handler
                    ] = (
                        hdlr
                    )  # we keep a reference to the handler to read the buffer later
                    self._addHandler(root_logger, hdlr, can_colors=False)
                elif handler == C.LOG_OPT_OUTPUT_FILE:
                    import os.path

                    for path in options:
                        hdlr = logging.FileHandler(os.path.expanduser(path))
                        self._addHandler(root_logger, hdlr, can_colors=False)
                else:
                    raise ValueError("Unknown handler type")
        else:
            root_logger.warning("Handlers already set on root logger")

    @staticmethod
    def memoryGet(size=None):
        """Return buffered logs

        @param size: number of logs to return
        """
        mem_handler = log.handlers[C.LOG_OPT_OUTPUT_MEMORY]
        return (
            log_msg for log_msg in mem_handler.buffer[size if size is None else -size :]
        )


log.configure_cls[C.LOG_BACKEND_BASIC] = ConfigureBasic
log.configure_cls[C.LOG_BACKEND_TWISTED] = ConfigureTwisted
log.configure_cls[C.LOG_BACKEND_STANDARD] = ConfigureStandard


def configure(backend, **options):
    """Configure logging behaviour
    @param backend: can be:
        C.LOG_BACKEND_STANDARD: use standard logging module
        C.LOG_BACKEND_TWISTED: use twisted logging module (with standard logging observer)
        C.LOG_BACKEND_BASIC: use a basic print based logging
        C.LOG_BACKEND_CUSTOM: use a given Logger subclass
    """
    return log.configure(backend, **options)


def _parseOptions(options):
    """Parse string options as given in conf or environment variable, and return expected python value

    @param options (dict): options with (key: name, value: string value)
    """
    COLORS = C.LOG_OPT_COLORS[0]
    LEVEL = C.LOG_OPT_LEVEL[0]

    if COLORS in options:
        if options[COLORS].lower() in ("1", "true"):
            options[COLORS] = True
        elif options[COLORS] == "force":
            options[COLORS] = True
            options["force_colors"] = True
        else:
            options[COLORS] = False
    if LEVEL in options:
        level = options[LEVEL].upper()
        if level not in C.LOG_LEVELS:
            level = C.LOG_LVL_INFO
        options[LEVEL] = level


def satConfigure(backend=C.LOG_BACKEND_STANDARD, const=None, backend_data=None):
    """Configure logging system for SàT, can be used by frontends

    logs conf is read in SàT conf, then in environment variables. It must be done before Memory init
    @param backend: backend to use, it can be:
        - C.LOG_BACKEND_BASIC: print based backend
        - C.LOG_BACKEND_TWISTED: Twisted logging backend
        - C.LOG_BACKEND_STANDARD: standard logging backend
    @param const: Const class to use instead of sat.core.constants.Const (mainly used to change default values)
    """
    if const is not None:
        global C
        C = const
        log.C = const
    from sat.tools import config
    import os

    log_conf = {}
    sat_conf = config.parseMainConf()
    for opt_name, opt_default in C.LOG_OPTIONS():
        try:
            log_conf[opt_name] = os.environ[
                "".join((C.ENV_PREFIX, C.LOG_OPT_PREFIX.upper(), opt_name.upper()))
            ]
        except KeyError:
            log_conf[opt_name] = config.getConfig(
                sat_conf, C.LOG_OPT_SECTION, C.LOG_OPT_PREFIX + opt_name, opt_default
            )

    _parseOptions(log_conf)
    configure(backend, backend_data=backend_data, **log_conf)
