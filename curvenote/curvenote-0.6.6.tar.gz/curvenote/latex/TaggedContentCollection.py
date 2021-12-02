from typing import Dict


class TaggedContentCollection(dict):
    """
    A Container for tagged content that supports the appending we need
    """
    def __init__(self):
        super(TaggedContentCollection, self).__init__({})
        self.plain = {}

    def add(self, tag: str, content: str, plain: bool = False):
        """
        Add content to the collection
        """
        if tag not in self:
            self.plain[tag] = plain
            if plain:
                self[tag] = content.replace('\n','')
            else:
                self[tag] = f"{content}\n"
            return
        self.plain[tag] = plain or self.plain[tag]
        if plain:
            self[tag] += (" " + content.replace('\n',''))
        else:
            self[tag] += f"\n{content}\n"

    def merge(self, other: "TaggedContentCollection"):
        """
        Merge this collection with another
        """
        for tag, content in other.items():
            is_plain = (tag in self.plain and self.plain[tag]) or (tag in other.plain and other.plain[tag])
            if tag not in self:
                self[tag] = content.replace('\n','') if is_plain else content
            else:
                if is_plain:
                    self[tag] = self[tag].replace('\n','') + (" " + content.replace('\n',''))
                else:
                    self[tag] += f"\n{content}"
