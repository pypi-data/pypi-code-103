# Copyright (C) 2021  https://seetee.io

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os
import sys

import click

from . import load_custom_records
from .tlv_keys import TLVKeys


@click.command(
    short_help=
    "Extract custom metadata records that may have been attached to lightning payments you received."
)
@click.option(
    '--tlscertpath',
    default='~/.lnd/tls.cert',
    show_default=True,
    metavar='<value>',
    help="\b\nPath to the TLS certificate for lnd's RPC service"
)
@click.option(
    '--macaroonpath',
    default='~/.lnd/data/chain/bitcoin/mainnet/readonly.macaroon',
    show_default=True,
    metavar='<value>',
    help="\b\nPath to the (read-only) macaroon for lnd's RPC service"
)
@click.option(
    '--rpchost',
    default='127.0.0.1:10009',
    show_default=True,
    metavar='<value>',
    help="\b\nThe address and port where lnd's RPC service is listening"
)
@click.option(
    '--tlvkey',
    multiple=True,
    default=[TLVKeys.PODCAST_METADATA.value],
    show_default=True,
    metavar='<value>',
    help="\b\nA TLV key to extract - can be specified multiple times"
)
@click.option(
    '--indexoffset',
    default=0,
    show_default=True,
    metavar='<value>',
    help="\b\nQuery for invoices starting at (not including) this offset"
)
@click.option(
    '--maxinvoices',
    default=1000,
    show_default=True,
    metavar='<value>',
    help="\b\nThe maximum number of invoices to query"
)
def main(tlscertpath, macaroonpath, rpchost, tlvkey, indexoffset, maxinvoices):
    """\b
    Extract custom metadata records that may have been attached to lightning payments you received.
    """

    tlvkeys = [*tlvkey]

    custom_records = load_custom_records(
        tls_cert_path=os.path.expanduser(tlscertpath),
        macaroon_path=os.path.expanduser(macaroonpath),
        rpc_host=rpchost,
        tlv_keys=tlvkeys,
        index_offset=indexoffset,
        max_invoices=maxinvoices
    )

    click.echo(json.dumps(custom_records, indent=4))
