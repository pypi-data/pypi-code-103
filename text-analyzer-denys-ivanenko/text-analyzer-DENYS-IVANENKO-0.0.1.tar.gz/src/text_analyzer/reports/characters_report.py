from collections import Counter


class CharactersReport:
    def __init__(self, text: str):
        self.text = text
        self._characters_freq = None
        self._characters_distribution = None
        self._generate_report()

    def compute_characters_freq(self):
        self._characters_freq = dict(Counter(self.text))

    def compute_characters_distribution(self):
        characters_frequency = self.characters_freq.items()
        self._characters_distribution = list(map(lambda item: (item[0],
                                                               " ".join([str(item[1] / len(self.text) * 100), "%"])),
                                                 characters_frequency))
        self._characters_distribution = dict(self._characters_distribution)

    @property
    def characters_freq(self):
        if self._characters_freq is None:
            self.compute_characters_freq()
        return self._characters_freq

    @property
    def characters_distribution(self):
        if self._characters_distribution is None:
            self.compute_characters_distribution()
        return self._characters_distribution

    def _generate_report(self):
        self.characters_number = len(self.text)
        self.reversed_text = self.text[::-1]
        self.compute_characters_freq()
        self.compute_characters_distribution()
