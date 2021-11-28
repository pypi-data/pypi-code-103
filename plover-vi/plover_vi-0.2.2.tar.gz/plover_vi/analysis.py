#!/bin/python
from plover_vi.decompose import decompose
import sys
import re
from collections import Counter

filename="data/typeracer-quotes"
#filename="data/de-men-phieu-luu-ky"
#filename="data/kieu"


# some books found online

# https://informatik.uni-leipzig.de/~duc/sach/ (html, hard to process)
# libgen (didn't try, might need OCR)

with open(filename) as f:
	words=re.findall(r"\w+", f.read())

words=[word.lower() for word in words]
print("Weird words:")
print( {word for word in words if word not in decompose })
print("======")
words=[word for word in words if word in decompose]

key=lambda d: (d.coda, d.tone)

lookup={word: key(decompose[word.lower()]) for word in words}
reverse=dict(zip(lookup.values(), lookup.keys()))
for x in Counter(lookup.values()).most_common():
	print(x, reverse.get(x[0]))


sys.exit()


# random dictionary found online...
# file downloaded from http://www.informatik.uni-leipzig.de/~duc/Dict/install.html
with open('vietanh.index') as f:
	d=[l.split('\t')[0] for l in f.readlines() if not l.startswith("00-")]

for onset in onsets:
	for nucleus in nucleuses:
		for coda in codas:
			for tone in tones:
				word=construct(onset, nucleus, coda, tone, new_tone_placement)
				if word is not None:
					decompose[word]=SyllableParts(onset, nucleus, coda, tone, new_tone_placement)

sys.exit()

for word in decompose.keys():
	print(word)

sys.exit()

for word in d:
	syllables=word.split()
	if len(syllables)==3:
		print(word)
		for syllable in syllables:
			syllable=syllable.lower()
			if syllable not in decompose:
				print(syllable)

