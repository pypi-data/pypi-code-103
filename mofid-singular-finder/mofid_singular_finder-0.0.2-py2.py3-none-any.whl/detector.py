import os
import json
from .data_helper import DataHelper


class SingularDetector:
    """Find Stem ,prefix and postfix of Combined words"""

    def __init__(self):
        """

        Parameters
        ----------
        config_file : config file that contains affix lists.
        double_postfix_joint : some words like کتابهایتان have 2 postfixes we can decide how to struggle with these words.
        """

        self.dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        self.noun_lex_path = self.dir_path + "resource/stemmer/stem_lex.pckl"
        self.mini_noun_lex_path = self.dir_path + "resource/stemmer/original_parsivar_stem_lex.pckl"
        self.verb_lex_path = self.dir_path + "resource/stemmer/verbStemDict.pckl"
        self.verb_tense_map_path = self.dir_path + "resource/stemmer/stem_verbMap.pckl"
        self.irregular_nouns_path = self.dir_path + "resource/stemmer/stem_irregularNounDict.pckl"
        self.prefix_list_path = self.dir_path + "resource/stemmer/pishvand.txt"
        self.postfix_list_path = self.dir_path + "resource/stemmer/pasvand.txt"
        self.verb_tense_file_path = self.dir_path + "resource/stemmer/verb_tense.txt"
        with open(self.dir_path + "resource/stemmer/verb_tenses.json") as f:
            self.verb_list_tenses = json.load(f)
        self.mokasar_noun_path = self.dir_path + "resource/stemmer/mokasar.txt"
        self.data_helper = DataHelper()
        if (os.path.isfile(self.noun_lex_path) and os.path.isfile(self.verb_lex_path)
                and os.path.isfile(self.verb_tense_map_path) and os.path.isfile(self.irregular_nouns_path)):
            self.noun_lexicon = self.data_helper.load_var(self.noun_lex_path)
            self.mini_lexicon = self.data_helper.load_var(self.mini_noun_lex_path)
            self.verb_lexicon = self.data_helper.load_var(self.verb_lex_path)
            self.verb_tense_map = self.data_helper.load_var(self.verb_tense_map_path)
            self.irregular_nouns = self.data_helper.load_var(self.irregular_nouns_path)

            self.verb_p2f_map, self.verb_f2p_map = self.verb_tense_map[0], self.verb_tense_map[1]

        with open(self.dir_path + "resource/affix.json") as f:
            self.affix_list = json.load(f)
        self.noun_lexicon.update(self.mini_lexicon)

    def select_candidate(self, candidate_list, lexicon_set=None):
        """
        check if candidate stem is there in vocabulary or not?

        Parameters
        ----------
        candidate_list : list of candidate
        lexicon_set: vocabulary of nouns or verbs

        Returns
        -------
        selected word: str
        """
        length = 1000
        selected = ""
        for tmp_candidate in candidate_list:
            if lexicon_set is None and len(tmp_candidate) < length:
                selected = tmp_candidate
                length = len(tmp_candidate)
            elif lexicon_set is not None and (tmp_candidate in lexicon_set):
                if length == 1000:
                    selected = tmp_candidate
                    length = len(tmp_candidate)
                else:
                    if len(tmp_candidate) > length:
                        selected = tmp_candidate
                        length = len(tmp_candidate)
        return selected

    def is_prefix(self, word, prefix):
        """
        check verb has prefix or not, then return true or false

        Parameters
        ----------
        word: str,input verb
        prefix: str, candidate postfix we should check

        Returns
        -------
        Boolean
        """
        word = word.strip("\u200c")
        return word.startswith(prefix)

    def is_postfix(self, word, post):
        """
        check verb has postfix or not, then return true or false

        Parameters
        ----------
        word: str,input verb
        post: str, candidate postfix we should check

        Returns
        -------
        Boolean
        """
        word = word.strip("\u200c")
        return word.endswith(post)

    def remove_prefixes(self, word, prefix):
        """
        detect prefix of words based on prefix list pass to the function

        Parameters
        ----------
        word: str
        prefix: list of prefix

        Returns
        -------
        prefix, list of candidate stem
        """
        word = word.strip("\u200c")
        candidateStem = set({})
        last_el = ''
        for el in prefix:
            if word.startswith(el):
                if len(el) > 0:
                    if len(el) > len(last_el):
                        last_el = el
                        tmp = word[len(el):].strip().strip('\u200c')
                else:
                    tmp = word
                candidateStem.add(tmp)
        return last_el, candidateStem

    def remove_postfixes(self, word, postfix):
        """
        detect postfix of words based on postfix list pass to the function.

        Parameters
        ----------
        word: str
        postfix: list of prefix

        Returns
        -------
        postfix, list of candidate stem
        """
        word = word.strip("\u200c")
        candidateStem = set({})
        last_el = ''
        for el in postfix:

            if word.endswith(el):
                if len(el) > 0:
                    if len(el) > len(last_el):
                        last_el = el
                        tmp = word[:-len(el)].strip().strip('\u200c')
                        candidateStem = set({})
                        candidateStem.add(tmp)
                else:
                    tmp = word

        return last_el, candidateStem

    def postfix_g(self, word):
        """
        find postfix "گ", like: ستارگان
        Parameters
        ----------
        word: str

        Returns
        -------

        """
        postfix, candidate_list = self.remove_postfixes(word, ["گ"])
        if len(candidate_list) > 0 and postfix != '' and len(list(candidate_list)[0]) > 1:
            new_word = self.select_candidate(candidate_list)
            new_word = new_word + "ه"

            if new_word in self.noun_lexicon:
                return new_word, "گ"

        return [word]

    def eltezami_stem_converter(self, new_word):
        """
        For Eltezami, verbs should check some extra rules.

        Parameters
        ----------
        new_word:str , stem of verb

        Returns
        -------
        change_status: boolean, if the input verb is changed this will change to True.
        new_word: str, converted format of verb.
        """

        if self.is_prefix(new_word, "یا") and new_word not in self.verb_lexicon:
            prefix_word, candidate_list = self.remove_prefixes(new_word, ["یا"])
            new_word = self.select_candidate(candidate_list)
            new_word = "آ" + new_word

        if self.is_postfix(new_word, "آی") or self.is_postfix(new_word, "ای") and new_word not in self.verb_lexicon:
            postfix_word, candidate_list = self.remove_postfixes(new_word, ["ی"])
            new_word = self.select_candidate(candidate_list)

        if self.is_prefix(new_word, "ی"):
            prefix_word, candidate_list = self.remove_prefixes(new_word, ["ی"])
            tmp_word = self.select_candidate(candidate_list)
            if tmp_word and ("ا" + tmp_word) in self.verb_lexicon:
                new_word = "ا" + tmp_word

        return new_word

    def verb_rule_checker(self, input_word):
        """
        check rules for all tenses of verbs and detect singular verbs.

        Parameters
        ----------
        input_word: str

        Returns
        -------
        boolean, True if word is a singular verb otherwise None.

        """
        for key, value in self.verb_list_tenses.items():
            prefix_tmp = []
            postfix_tmp = []
            word = input_word
            # See if the word has a specific prefix.
            for key1, value1 in value.items():
                if key1.startswith("postfix"):
                    postfix_word, candidate_list = self.remove_postfixes(word, value1)
                    postfix_tmp.append(postfix_word)

                if key1.startswith("prefix"):
                    prefix_word, candidate_list = self.remove_prefixes(word, value1)
                    prefix_tmp.append(prefix_word)

                if len(candidate_list) > 0:
                    word = self.select_candidate(candidate_list)

            stem = self.select_candidate(candidate_list, self.verb_lexicon)

            if key == "مضارع التزامی و امر":
                result = self.eltezami_stem_converter(word)
                if result != word:
                    stem = result

            if stem in eval("self." + value["root_vocab"]) and stem is not None:

                for i in prefix_tmp:
                    if i in ["داشتی", "داری", "ی"]:
                        return True

                for i in postfix_tmp:
                    if i in ["ی", "ای"]:
                        return True
        return None

    def noun_rule_checker_pre(self, input_word, affix_list):
        """
        lookup for prefixes in the input word.

        Parameters
        ----------
        input_word: str, input word that we should check its prefix.
        affix_list: list, potential prefixes that should lookup for them.

        Returns
        -------
        prefix: str, stem candidate: str,(if conditions satisfied and there is a prefix in the word)
        input_word: list, if can't find the prefix, will return input
        """
        # lookup for prefix of the noun
        prefix, candidate_list = self.remove_prefixes(input_word, affix_list)

        # check if there is a candidate and length of that candidate should be greater than 1
        if len(candidate_list) > 0 and prefix != '' and len(list(candidate_list)[0]) > 1:
            stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
            # check if the stem that finds it is in vocabulary or not?
            if stem_candidate:
                return prefix, stem_candidate
            else:
                # Maybe Word has a two-prefix, so we can continue on it.
                stem_candidate = self.select_candidate(candidate_list)
                return prefix, stem_candidate
        else:
            return [input_word]

    def noun_rule_checker_pos(self, input_word, affix_list):
        """
        lookup for postfixes in the input word.

        Parameters
        ----------
        input_word: str, input word that we should check its postfix.
        affix_list: list, potential postfixes that should lookup for them.

        Returns
        -------
        postfix: str, stem candidate: str,(if conditions satisfied and there is a postfix in the word)
        input_word: list, if can't find the postfix, will return input
        """

        # lookup for postfix of the noun

        postfix, candidate_list = self.remove_postfixes(input_word, affix_list)

        # check if there is a candidate and length of that candidate should be greater than 1

        if len(candidate_list) > 0 and postfix != '' and len(list(candidate_list)[0]) > 1:
            stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
            if stem_candidate:
                return postfix, stem_candidate
            else:
                # Maybe Word has a two-postfix, so we can continue on it.
                stem_candidate = self.select_candidate(candidate_list)
                return postfix, stem_candidate
        else:

            return [input_word]

    def noun_decomposer(self, word):
        """
        Consider the prefix and postfix of the noun, then divide it according to the condition.

        Parameters
        ----------
        word
        str, input word that should be normalized

        Returns
        -------
        boolean, True if word is singular noun, otherwise None.
        """

        # list of suffixes that we look up for them
        suffix = {"pron": "", "plural": "", "prefix": "", "pos_irreqular": "", "pos_ge": "", "zame": "",
                  "he_chasban": ""}

        # START chain analyze of word
        # check for, "و" at the end of the word, e.x: کتابو
        try:
            suffix["zame"], new_word = self.noun_rule_checker_pos(word, self.affix_list["zame"])
        except:
            new_word = word

        # check for, "ه" at the end of the word, e.x: ماشینه
        try:
            suffix["he_chasban"], new_word = self.noun_rule_checker_pos(new_word, self.affix_list["he_chasban"])
        except:
            new_word = new_word

        # check for, pronoun of the word, e.x: ماشینم
        try:
            suffix["pron"], new_word = self.noun_rule_checker_pos(new_word, self.affix_list["prop_postfix_all"])
        except Exception as e:
            new_word = new_word

        # check for, plural form of the word, e.x: ماشینها
        try:
            suffix["plural"], new_word = self.noun_rule_checker_pos(new_word, self.affix_list["plural_postfix_all"])
        except:

            new_word = new_word
        # check for, prefix of the word, e.x: پیشبینی
        try:
            suffix["prefix"], new_word = self.noun_rule_checker_pre(new_word, self.affix_list["prefix_all"])
        except:
            new_word = new_word
        # check for, irregular postfix of the word, e.x: کتابسرا
        try:
            suffix["pos_irreqular"], new_word = self.noun_rule_checker_pos(new_word,
                                                                           self.affix_list["irregular_postfix_all"])
        except:
            new_word = new_word

        # check for postfix with "گ" like: ستارگان
        try:
            new_word, suffix["pos_ge"] = self.postfix_g(new_word)
        except:
            new_word = new_word
        print(suffix)
        if new_word in self.noun_lexicon and word != new_word:
            if suffix["pron"] in ["ت", "یت"]:
                return True

        return None

    def singular_checker(self, word, word_pos=None):
        """
        find stem,postfix and prefix of words.

        Parameters
        ----------
        word: str, input words
        word_pos: Part of speech tag of word

        Returns
        -------
        stem of word with prefix and postfix of it
        """

        # If the word already exists in vocabulary(mini_lexicon), then it isn't combined
        if word in self.mini_lexicon:
            if word_pos is None or word_pos == 'N':
                return False

        # If the word already exists in verb vocabulary(verb_f2p_map), then it isn't combined
        elif word in self.verb_lexicon:
            if word_pos is None or word_pos == 'V':
                return False

        # find stem, postfix, and prefix of words.
        # we have 2 groups of words: 1. verbs 2. nouns,
        # each of them has separate rules.

        # ***************** VERB-Block *****************
        # detect singular verbs

        if word_pos is None or word_pos == "V":
            decomposedـverb = self.verb_rule_checker(word)
            if decomposedـverb is True:
                return decomposedـverb
        print(word)
        # ***************** NOUN-Block *****************
        # detect singular nouns

        if word_pos is None or word_pos == "N":
            decomposedـnoun = self.noun_decomposer(word)
            if decomposedـnoun is True:
                return decomposedـnoun

        return False


test = SingularDetector()
test = test.singular_checker("حسابت")
print(test)
