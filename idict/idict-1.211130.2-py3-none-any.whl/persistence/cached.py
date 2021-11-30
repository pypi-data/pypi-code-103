#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the idict project.
#  Please respect the license - more about this in the section (*) below.
#
#  idict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  idict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with idict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and unethical regarding the effort and
#  time spent here.
import json

from idict.core.identification import key2id
from idict.persistence.cache import Cache
from ldict.core.base import AbstractLazyDict
from ldict.lazyval import LazyVal


def storevalue(id, value, cache):
    cache[id] = value


def storeblob(id, blob, cache):
    cache.setblob(id, blob)


def cached(d, cache) -> AbstractLazyDict:
    """
    Store each value (fid: value) and an extra value containing the fids (did: {"_id": did, "_ids": fids}).
    When the dict is a singleton, we have to use id² as dict id to workaround the ambiguity did=fid.
    """
    # TODO: gravar hashes como aliases no cache pros hoshes. tb recuperar. [serve p/ poupar espaço. e tráfego se usar duplo cache local-remoto]
    #  mas hash não é antecipável! 'cached' teria de fazer o ponteiro: ho -> {"_id": ". . ."}.  aproveitar pack() para guardar todo valor assim.
    from idict.core.idict_ import Idict
    from idict.core.frozenidentifieddict import FrozenIdentifiedDict

    store = storeblob if isinstance(cache, Cache) else storevalue
    front_id = handle_singleton_id(d)

    def closure(outputf, fid, fids, data, output_fields, id):
        def func(**kwargs):
            # Try loading.
            if fid in cache:
                return get_following_pointers(fid, cache)

            # Process and save (all fields, to avoid a parcial ldict being stored).
            k = None
            for k, v in fids.items():
                # TODO (minor): all lazies are evaluated, but show() still shows deps as lazy.
                #    Fortunately the dep is evaluated only once.
                if isinstance(data[k], LazyVal):
                    data[k] = data[k](**kwargs)
                if isinstance(data[k], (FrozenIdentifiedDict, Idict)):
                    store(v, {"_id": handle_singleton_id(data[k])}, cache)
                    data[k] = cached(data[k], cache)
                else:
                    store(v, data[k], cache)
            if (result := data[outputf]) is None:  # pragma: no cover
                if k is None:
                    raise Exception(f"No ids")
                raise Exception(f"Key {k} not in output fields: {output_fields}. ids: {fids.items()}")
            # if did not in cache:
            store(front_id, {"_id": id, "_ids": fids}, cache)
            return result

        return func

    data = d.data.copy()
    lazies = False
    output_fields = []
    for field, v in list(data.items()):
        if isinstance(v, LazyVal):
            if field.startswith("_"):  # pragma: no cover
                raise Exception("Cannot have a lazy value in a metafield.", field)
            output_fields.append(field)
            lazies = True
            id = d.hashes[field].id if field in d.hashes else d.hoshes[field].id
            deps = {"↑": None}
            deps.update(v.deps)
            lazy = LazyVal(field, closure(field, id, d.ids, d.data, output_fields, d.id), deps, data, None)
            data[field] = lazy

    # Eager saving when there are no lazies.
    if not lazies:
        for k, fid in d.ids.items():
            if fid not in cache:
                if isinstance(data[k], (FrozenIdentifiedDict, Idict)):
                    store(fid, {"_id": handle_singleton_id(data[k])}, cache)
                    data[k] = cached(data[k], cache)
                else:
                    store(fid, data[k], cache)
        if front_id not in cache:
            store(front_id, {"_id": d.id, "_ids": d.ids}, cache)

    return d.clone(data)


def build(id, ids, cache, identity):
    """Build an idict from a given identity

    >>> from idict import idict
    >>> a = idict(x=5,z=9)
    >>> b = idict(y=7)
    >>> b["d"] = a
    >>> b >>= [cache := {}]
    >>> print(json.dumps(cache, indent=2))
    {
      "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065": 7,
      "UX_b6e9bdf8ec93b97f17e2db72cf72a856aaa2c": {
        "_id": "HZ_922bbdb73ad1a6fc17e2329dcf72a8909aa2c"
      },
      "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f": 5,
      "pH_c0fec534e9799b37ee981fbb17f2ea635ec9c": 9,
      "HZ_922bbdb73ad1a6fc17e2329dcf72a8909aa2c": {
        "_id": "HZ_922bbdb73ad1a6fc17e2329dcf72a8909aa2c",
        "_ids": {
          "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f",
          "z": "pH_c0fec534e9799b37ee981fbb17f2ea635ec9c"
        }
      },
      "ug_32623f744b4b879f8b0b91bca8ace13993b81": {
        "_id": "ug_32623f744b4b879f8b0b91bca8ace13993b81",
        "_ids": {
          "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065",
          "d": "UX_b6e9bdf8ec93b97f17e2db72cf72a856aaa2c"
        }
      }
    }
    >>> build(b.id, b.ids, cache, b.hosh.ø).evaluated.show(colored=False)
    {
        "y": 7,
        "d": {
            "x": 5,
            "z": 9,
            "_id": "HZ_922bbdb73ad1a6fc17e2329dcf72a8909aa2c",
            "_ids": {
                "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f",
                "z": "pH_c0fec534e9799b37ee981fbb17f2ea635ec9c"
            }
        },
        "_id": "ug_32623f744b4b879f8b0b91bca8ace13993b81",
        "_ids": {
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065",
            "d": "UX_b6e9bdf8ec93b97f17e2db72cf72a856aaa2c"
        }
    }
    >>> (a.hosh ** key2id("d", 40)).show(colored=False)
    UX_b6e9bdf8ec93b97f17e2db72cf72a856aaa2c
    >>> a = idict(x=5)
    >>> b = idict(y=7)
    >>> b["d"] = a
    >>> b >>= [cache := {}]
    >>> print(json.dumps(cache, indent=2))
    {
      "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065": 7,
      "ug_65906b93071a1e38384abcb6a88fbde25cd8f": {
        "_id": "_i_7d6b4783509390c5384ac2c1b88fbd3d3cd8f"
      },
      "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f": 5,
      "_i_7d6b4783509390c5384ac2c1b88fbd3d3cd8f": {
        "_id": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f",
        "_ids": {
          "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f"
        }
      },
      "4B_8e0bd25f553b6ed5ac6298fb91b9071035ee4": {
        "_id": "4B_8e0bd25f553b6ed5ac6298fb91b9071035ee4",
        "_ids": {
          "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065",
          "d": "ug_65906b93071a1e38384abcb6a88fbde25cd8f"
        }
      }
    }
    >>> d = build(b.id, b.ids, cache, b.hosh.ø)
    >>> d.show(colored=False)
    {
        "y": "→(↑)",
        "d": "→(↑)",
        "_id": "4B_8e0bd25f553b6ed5ac6298fb91b9071035ee4",
        "_ids": {
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065",
            "d": "ug_65906b93071a1e38384abcb6a88fbde25cd8f"
        }
    }
    >>> d.evaluated.show(colored=False)
    {
        "y": 7,
        "d": {
            "x": 5,
            "_id": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f",
            "_ids": {
                "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f"
            }
        },
        "_id": "4B_8e0bd25f553b6ed5ac6298fb91b9071035ee4",
        "_ids": {
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065",
            "d": "ug_65906b93071a1e38384abcb6a88fbde25cd8f"
        }
    }
    >>> (a.hosh ** key2id("d", 40)).show(colored=False)
    ug_65906b93071a1e38384abcb6a88fbde25cd8f
    >>> a = idict(x=5,z=9)
    >>> b = idict(y=7)
    >>> b["d"] = lambda y: a
    >>> b >>= [cache := {}]
    >>> _ = b.d
    >>> print(json.dumps(cache, indent=2))
    {
      "3pPmLR.updFJHo4YwW3OipmZxyzZJVxChr1XgFng": {
        "_id": "HZ_922bbdb73ad1a6fc17e2329dcf72a8909aa2c"
      },
      "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f": 5,
      "pH_c0fec534e9799b37ee981fbb17f2ea635ec9c": 9,
      "HZ_922bbdb73ad1a6fc17e2329dcf72a8909aa2c": {
        "_id": "HZ_922bbdb73ad1a6fc17e2329dcf72a8909aa2c",
        "_ids": {
          "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f",
          "z": "pH_c0fec534e9799b37ee981fbb17f2ea635ec9c"
        }
      },
      "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065": 7,
      "y79Q0oV.uFUWaj0hM4enBgvlTHEZJVxChr1XgFng": {
        "_id": "y79Q0oV.uFUWaj0hM4enBgvlTHEZJVxChr1XgFng",
        "_ids": {
          "d": "3pPmLR.updFJHo4YwW3OipmZxyzZJVxChr1XgFng",
          "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065"
        }
      }
    }
    >>> build(b.id, b.ids, cache, b.hosh.ø).evaluated.show(colored=False)
    {
        "d": {
            "x": 5,
            "z": 9,
            "_id": "HZ_922bbdb73ad1a6fc17e2329dcf72a8909aa2c",
            "_ids": {
                "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f",
                "z": "pH_c0fec534e9799b37ee981fbb17f2ea635ec9c"
            }
        },
        "y": 7,
        "_id": "y79Q0oV.uFUWaj0hM4enBgvlTHEZJVxChr1XgFng",
        "_ids": {
            "d": "3pPmLR.updFJHo4YwW3OipmZxyzZJVxChr1XgFng",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065"
        }
    }
    >>> (a.hosh ** key2id("d", 40)).show(colored=False)
    UX_b6e9bdf8ec93b97f17e2db72cf72a856aaa2c
    >>> a = idict(x=5)
    >>> b = idict(y=7)
    >>> b["d"] = lambda y: a
    >>> b >>= [cache := {}]
    >>> _ = b.d
    >>> print(json.dumps(cache, indent=2))
    {
      "3pPmLR.updFJHo4YwW3OipmZxyzZJVxChr1XgFng": {
        "_id": "_i_7d6b4783509390c5384ac2c1b88fbd3d3cd8f"
      },
      "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f": 5,
      "_i_7d6b4783509390c5384ac2c1b88fbd3d3cd8f": {
        "_id": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f",
        "_ids": {
          "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f"
        }
      },
      "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065": 7,
      "y79Q0oV.uFUWaj0hM4enBgvlTHEZJVxChr1XgFng": {
        "_id": "y79Q0oV.uFUWaj0hM4enBgvlTHEZJVxChr1XgFng",
        "_ids": {
          "d": "3pPmLR.updFJHo4YwW3OipmZxyzZJVxChr1XgFng",
          "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065"
        }
      }
    }
    >>> d = build(b.id, b.ids, cache, b.hosh.ø)
    >>> d.show(colored=False)
    {
        "d": "→(↑)",
        "y": "→(↑)",
        "_id": "y79Q0oV.uFUWaj0hM4enBgvlTHEZJVxChr1XgFng",
        "_ids": {
            "d": "3pPmLR.updFJHo4YwW3OipmZxyzZJVxChr1XgFng",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065"
        }
    }
    >>> d.evaluated.show(colored=False)
    {
        "d": {
            "x": 5,
            "_id": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f",
            "_ids": {
                "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f"
            }
        },
        "y": 7,
        "_id": "y79Q0oV.uFUWaj0hM4enBgvlTHEZJVxChr1XgFng",
        "_ids": {
            "d": "3pPmLR.updFJHo4YwW3OipmZxyzZJVxChr1XgFng",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065"
        }
    }
    >>> (a.hosh ** key2id("d", 40)).show(colored=False)
    ug_65906b93071a1e38384abcb6a88fbde25cd8f
    """
    dic = {}
    for k, fid in ids.items():
        # REMINDER: An item id will never start with '_'. That only happens with singleton-idict id translated to cache.
        if fid in cache:
            value = get_following_pointers(fid, cache)
            # WARN: The closures bellow assume items will not be removed from 'cache' in the meantime.
            if isinstance(value, dict) and list(value.keys()) == ["_id", "_ids"]:
                closure = lambda value_: lambda **kwargs: build(value_["_id"], value_["_ids"], cache, identity)
                dic[k] = LazyVal(k, closure(value), {"↑": None}, {}, None)
            else:
                closure = lambda fid_: lambda **kwargs: cache[fid_]
                dic[k] = LazyVal(k, closure(fid), {"↑": None}, {}, None)
        else:  # pragma: no cover
            raise Exception(f"Missing key={fid} or singleton key=_{fid[1:]}.\n{json.dumps(cache, indent=2)}")
    from idict.core.frozenidentifieddict import FrozenIdentifiedDict

    return FrozenIdentifiedDict(dic, _id=id, _ids=ids, identity=identity)


def get_following_pointers(fid, cache):
    """Fetch item value from cache following pointers"""
    result = cache[fid]
    while isinstance(result, dict) and list(result.keys()) == ["_id"]:
        result = cache[result["_id"]]
    return result


def handle_singleton_id(d):
    return "_" + d.id[1:] if len(d.ids) == 1 else d.id
