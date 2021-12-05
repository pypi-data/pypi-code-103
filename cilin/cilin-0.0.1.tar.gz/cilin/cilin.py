import json
from pathlib import Path


class Cilin:

    def __init__(self, trad=True) -> None:
        self._load()
        self._get_tree_levels()
        self.trad = False
        if trad: 
            self.trad = True
            from opencc import OpenCC
            self.cc = OpenCC('s2t.json')


    def category_split(self, level=1):
        keys = self.keys.get(level, [])
        return {
            ''.join(k): self.get_members(k) for k in keys
        }


    def get_members(self, k):
        k = self._parse_key(k)
        tree = self.data[k[0]]
        for key in k[1:]:
            tree = tree['sub'][key]
        if isinstance(tree, list):
            return self.s2t(set(tree))
        return self.s2t(set(self._get_leaves(tree)))


    def get_tag(self, k):
        k = self._parse_key(k)
        tree = self.data[k[0]]
        for key in k[1:]:
            tree = tree['sub'][key]
        if 'tag' in tree:
            return self.s2t(tree['tag'])
        return self.s2t(' '.join(tree))


    def _get_leaves(self, tree):
        leaves = []
        for branch in tree['sub'].values():
            if isinstance(branch, list):
                leaves += branch
            else:
                leaves += self._get_leaves(branch)
        return leaves


    def _parse_key(self, k):
        if isinstance(k, tuple): return k
        if len(k) == 1: return (k, )
        if len(k) == 2: return k[0], k[1]
        if len(k) == 4: return k[0], k[1], k[2:]
        if len(k) == 5: return k[0], k[1], k[2:4], k[4:]
        if len(k) == 8: return k[0], k[1], k[2:4], k[4:5], k[5:]
        raise Exception(f'Invalid key format {k}')


    def _get_tree_levels(self):
        keys = []
        for k, v in self.data.items():
            keys.append( (k, ) )
            keys += get_keys(v, prefix=[k])
        key_lev = {}
        for k in keys:
            key_lev.setdefault(len(k), []).append(k)
        self.keys = key_lev


    def s2t(self, text):
        if not self.trad: return text
        if isinstance(text, set):
            return { self.cc.convert(x) for x in text }
        if isinstance(text, tuple):
            return tuple(self.cc.convert(x) for x in text)
        if isinstance(text, list):
            return [ self.cc.convert(x) for x in text ]
        if isinstance(text, str):
            return self.cc.convert(text)
        raise Exception('Unexpected input format')


    def _load(self):
        fp = Path(__file__).parent / "../data/cilin_tree.json"
        with open(fp, encoding="utf-8") as f:
            self.data = json.load(f)
        

def get_keys(tree, prefix=(None,)):
    keys = []
    if 'sub' not in tree: return []
    for key, subtree in tree['sub'].items():
        p = (*prefix, key )
        keys.append(p)
        if isinstance(subtree, dict):
            keys += get_keys(subtree, p)
    return keys

