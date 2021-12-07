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

import base64
import codecs
import json
import os

import grpc

from .generated import lightning_pb2 as ln
from .generated import lightning_pb2_grpc as lnrpc
from .tlv_keys import TLVKeys


def load_custom_records(
    tls_cert_path, macaroon_path, rpc_host, tlv_keys, index_offset, max_invoices
):
    os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

    with open(tls_cert_path, 'rb') as f:
        cert = f.read()
        creds = grpc.ssl_channel_credentials(cert)

    with open(macaroon_path, 'rb') as f:
        macaroon_bytes = f.read()
        macaroon = codecs.encode(macaroon_bytes, 'hex')

    with grpc.secure_channel(rpc_host, creds) as channel:
        stub = lnrpc.LightningStub(channel)

        request = ln.ListInvoiceRequest(
            pending_only=False,
            index_offset=index_offset,
            num_max_invoices=max_invoices,
            reversed=False
        )

        response = stub.ListInvoices(request, metadata=[('macaroon', macaroon)])
        invoices = response.invoices

        first_index = lastindex = None
        if len(invoices) > 0:
            first_index = invoices[0].add_index
            lastindex = invoices[-1].add_index

        custom_records = [
            _decode_tlv(key, value)
            for invoice in invoices
            for htlc in invoice.htlcs if invoice.is_keysend
            for key, value in htlc.custom_records.items() if key in tlv_keys
        ]

        return {
            'custom_records': custom_records,
            'queried_invoices': {
                'first_index': first_index,
                'last_index': lastindex
            }
        }

def _decode_tlv(key, value):
    decoders = {
        TLVKeys.PODCAST_METADATA.value:
        lambda v: json.loads(v.decode(encoding="UTF-8")),
    }

    try:
        return {'key': key, 'value': decoders[key](value)}
    except KeyError:
        # default to base64 for unknown TLV keys
        return {'key': key, 'value': base64.b64encode(value).decode("UTF-8")}
