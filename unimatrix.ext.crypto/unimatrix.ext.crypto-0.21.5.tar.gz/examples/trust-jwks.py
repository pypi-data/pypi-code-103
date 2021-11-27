#!/usr/bin/env python3
import unimatrix.runtime
from unimatrix.ext import crypto
from unimatrix.ext.crypto import policy


async def main():
    keys = await crypto.trust.jwks("https://molano.webidentity.id", ["foo"], {
        'greeting': 'Hello world!',
        'mynamespace/key': 'namespaced'
    })
    key = keys[0]
    assert key in crypto.trust
    assert key.is_tagged('foo')
    assert key.is_annotated('greeting')
    assert key.is_annotated('key', 'mynamespace')
    assert key.get_annotation('key', 'mynamespace') == 'namespaced'

    # Define policies for the key.
    assert policy.IsTagged('foo') & key
    assert not policy.IsTagged('foo') ^ key

    # The policy must not match key
    assert policy.IsTagged('bar') ^ key
    assert not policy.IsTagged('bar') & key

    # Policies can be AND-ed
    assert policy.IsTagged('foo') & policy.HasAnnotation('greeting') & key

    # Policies can be OR-ed
    assert policy.IsTagged('foo') | policy.IsTagged('bar') & key

    # Policies can be negated
    assert ~policy.IsTagged('bar') & key

    # Policies can be conditionally applied
    assert ~policy.IsTagged('bar', tags=['foo']) & key

    # Shorthand for multiple policies
    assert policy.combine(policy.IsTagged('foo'), ~policy.IsTagged('bar')) & key

    # And more combinations
    assert ~policy.IsTagged('bar') & policy.IsTagged('foo') & key


if __name__ == '__main__':
    unimatrix.runtime.execute(main)
