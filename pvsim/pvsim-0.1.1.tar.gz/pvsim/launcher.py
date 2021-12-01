import argparse
import logging
import yaml

from p4p.server import Server
from p4p.server.thread import SharedPV
from p4p.nt import NTScalar


class RWHandler:
    def put(self, pv, op):
        pv.post(op.value())
        op.done()


CLASS_FOR_TYPE = {
    'ao': (NTScalar, 'd', True),
    'ai': (NTScalar, 'd', False),
    'bo': (NTScalar, '?', True),
    'bi': (NTScalar, '?', False),
}

INITIAL_FOR_TYPE = {
    'ao': 0.0,
    'ai': 0.0,
    'bi': False,
    'bo': False
}

logger = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'pvlist',
        help='YAML file with the PVs to be served',
        type=argparse.FileType('r', encoding='UTF-8')
    )
    parser.add_argument('-d', '--debug', action='store_const', const=logging.DEBUG, default=logging.INFO)
    return parser.parse_args()


def main():
    args = get_args()
    logging.basicConfig(level=args.debug)

    pvlist = yaml.safe_load(args.pvlist)

    db = {}

    for pv, meta in pvlist.items():
        logger.debug(f'PV: {pv} with metadata: {meta}')
        pv_type = meta.get('type', 'ao')
        initial = meta.get('initial') or INITIAL_FOR_TYPE.get(pv_type)
        klass, arg, write_access = CLASS_FOR_TYPE.get(pv_type)

        nt = klass(arg) if arg else klass()
        handler = RWHandler() if write_access else None

        db[pv] = SharedPV(nt=nt, initial=initial, handler=handler)

    print("Serving PVs:")
    print("\n".join(pvlist))

    Server.forever(providers=[db])
