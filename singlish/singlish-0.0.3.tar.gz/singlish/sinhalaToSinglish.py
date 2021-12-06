

class SinhalaToSinglish:

    def __init__(self):
        self.sinhalaDictValue = {

            '්': '-',
            'ා': '-aa',
            'ැ': '-ae',
            'ෑ': '-aee',
            'ි': '-i',
            'ී': '-ee',
            'ු': '-u',
            'ූ': '-uu',
            'ෘ': '-ru',
            'ෲ': '-ruu',
            'ෟ': '-aou',
            'ෙ': '-e',
            'ේ': '-ee',
            'ෛ': '-ai',
            'ො': '-o',
            'ෝ': '-oo',
            'ෞ': '-aou',

            'අ': 'a',
            'ආ': 'aa',
            'ඇ': 'A',
            'ඉ': 'i',
            'ඊ': 'ii',
            'උ': 'u',
            'ඌ': 'uu',
            'එ': 'e',
            'ඒ': 'ee',
            'ඓ': 'ai',
            'ඔ': 'o',
            'ඕ': 'oo',
            'ඖ': 'au',
            'ක': 'ka',
            'ඛ': 'Ka',
            'ග': 'ga',
            'ඝ': 'Ga',
            'ච': 'cha',
            'ජ': 'ja',
            'ඣ': 'Ja',
            'ට': 'ta',
            'ඨ': 'Ta',
            'ඩ': 'da',
            'ඪ': 'Da',
            'ණ': 'Na',
            'ත': 'tha',
            'ද': 'dha',
            'ධ': 'Dha',
            'න': 'na',
            'ප': 'pa',
            'ඵ': 'pha',
            'බ': 'ba',
            'භ': 'bha',
            'ම': 'ma',
            'ය': 'ya',
            'ර': 'ra',
            'ල': 'la',
            'ව': 'va',
            'ශ': 'sha',
            'ෂ': 'Sa',
            'ස': 'sa',
            'හ': 'ha',
            'ෆ': 'fa',
            'ළ': 'La',
            'ං': 'x',
            'ඟ': 'zga',
            'ඦ': 'zja',
            'ඵ': 'pha',
            'ථ': 'thha',
            'ඥ': 'zha',
            'ඦ': 'zja',
            'ඡ': 'chha',
            'ඬ': 'zda',
            'ඃ': 'H',
            'ඳ': 'zdha',
            'ඹ': 'Ba',
            'ʠ': 'unk',
            'ඈ': 'AA',
            "'ׂ": 'unk',
            'ඤ': 'zka',
            'ඍ': 'R',
            'ඎ': 'Ru'

        }

        self.badWords = []

    def convert(self,word):
        sinhala_word = ''
        for character in word:
            try:
                if character != '\n' and character != '\u200d':
                    if self.sinhalaDictValue[character][0] == '-':
                        sinhala_word = sinhala_word[:-1] + self.sinhalaDictValue[character][1:]
                    else:
                        sinhala_word += self.sinhalaDictValue[character]
            except:
                self.badWords.append(word)
        return sinhala_word