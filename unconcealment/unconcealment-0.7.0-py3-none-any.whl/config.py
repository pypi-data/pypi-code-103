import logging


def load_file(path: str) -> str:
    """ Load data from file """
    with open(path, 'r', encoding="utf-8") as file:
        try:
            return file.read()
        except UnicodeDecodeError:
            return ""


class Config:
    """ Config class """
    instance = {'initialized': False}

    @staticmethod
    def init(parser=None):
        """ Get singleton instance of Config """
        if Config.instance['initialized']:
            return Config.instance
        args = parser.parse_args()
        config = {
            'logLevel': args.log_level if "log_level" in args and args.log_level is not None else 'INFO',
            'file': args.file if "file" in args and args.file is not None else None,
            'directory': args.directory if "directory" in args and args.directory is not None else None,
            'data': ' '.join(args.remainder) if "remainder" in args is not None
                                                and args.remainder is not None
                                                and len(args.remainder) > 0 else None,
            'initialized': True
        }
        if config['file'] is not None:
            config['data'] = load_file(config['file'])
        logging.basicConfig(level=config['logLevel'],
                            format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
        Config.instance = config
        return Config.instance

    @staticmethod
    def file():
        """ Getter """
        return Config.instance['file']

    @staticmethod
    def log_level():
        """ Getter """
        # pylint: disable=E1136
        return Config.instance['logLevel']

    @staticmethod
    def data():
        """ Getter """
        # pylint: disable=E1136
        return Config.instance['data']

    @staticmethod
    def directory():
        """ Getter """
        # pylint: disable=E1136
        return Config.instance['directory']
