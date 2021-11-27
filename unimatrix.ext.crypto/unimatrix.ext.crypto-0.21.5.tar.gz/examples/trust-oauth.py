#!/usr/bin/env python3
import unimatrix.runtime
from unimatrix.ext import crypto
from unimatrix.ext.crypto import policy


async def main():
    await crypto.trust.load([
        {
            'loader': 'unimatrix.ext.crypto.loaders.WellKnownOAuthLoader',
            'tags': ['foo'],
            'annotations': {
                'greeting': 'Hello world!',
                'mynamespace/key': 'namespaced'
            },
            'opts': {
                'server': "https://id.realm.digitalcitizen.nl"
            }
        }
    ])


if __name__ == '__main__':
    unimatrix.runtime.execute(main)
