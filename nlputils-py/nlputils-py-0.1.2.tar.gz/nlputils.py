#!/usr/bin/env python
# encoding: utf-8
'''
@author: codingma
@file: nlputils.py
@time: 2019/9/9 21:52
@desc: utils for natural language
'''
import re
import sys

import six
import unicodedata
from openccpy.opencc import *

class NlpUtils(object):
    SENTENCE_SPLITER = re.compile(r"[\?？？。。\!！！,，，]")
    SIMPLE_PUNCTUATION = re.compile(r"[\s+\.\!\/<>“”,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+")
    STOP_WORDS = re.compile(r'[呀啊哈呵]')

    @staticmethod
    def tokenize_chinese_chars(ustring):
        """Adds whitespace around any CJK character."""
        """copy from google/dl"""
        output = []
        for uchar in ustring:
            if NlpUtils.is_chinese_char(uchar):
                output.append(" ")
                output.append(uchar)
                output.append(" ")
            else:
                output.append(uchar)
        return "".join(output)

    @staticmethod
    def delete_chinese(ustring):
        """删除汉字"""
        outputs = []
        for uchar in ustring:
            if NlpUtils.is_chinese_char(uchar):
                outputs.append(uchar)

        return "".join(outputs)

    @staticmethod
    def is_chinese_char(uchar):
        """判断一个unicode是否是汉字"""
        """Checks whether CP is the codepoint of a CJK character."""
        # This defines a "chinese character" as anything in the CJK Unicode block:
        #   https://en.wikipedia.org/wiki/CJK_Unified_Ideographs_(Unicode_block)
        #
        # Note that the CJK Unicode block is NOT all Japanese and Korean characters,
        # despite its name. The modern Korean Hangul alphabet is a different block,
        # as is Japanese Hiragana and Katakana. Those alphabets are used to write
        # space-separated words, so they are not treated specially and handled
        # like the all of the other languages.
        cp = ord(uchar)
        if ((cp >= 0x4E00 and cp <= 0x9FFF) or  #
                (cp >= 0x3400 and cp <= 0x4DBF) or  #
                (cp >= 0x20000 and cp <= 0x2A6DF) or  #
                (cp >= 0x2A700 and cp <= 0x2B73F) or  #
                (cp >= 0x2B740 and cp <= 0x2B81F) or  #
                (cp >= 0x2B820 and cp <= 0x2CEAF) or
                (cp >= 0xF900 and cp <= 0xFAFF) or  #
                (cp >= 0x2F800 and cp <= 0x2FA1F)):  #
            return True
        return False

    @staticmethod
    def is_chinese_string(ustring):
        """判断是否全为汉字"""
        for c in ustring:
            if not NlpUtils.is_chinese_char(c):
                return False
        return True

    @staticmethod
    def has_chinese(ustring):
        """判断是否有汉字"""
        for c in ustring:
            if NlpUtils.is_chinese_char(c):
                return True
        return False

    @staticmethod
    def has_not_chinese(ustring):
        return not NlpUtils.has_chinese(ustring)

    @staticmethod
    def is_number(uchar):
        """判断一个unicode是否是数字"""
        if u'\u0030' <= uchar <= u'\u0039':
            return True
        else:
            return False

    @staticmethod
    def is_alphabet(uchar):
        """判断一个unicode是否是英文字母"""
        if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
            return True
        else:
            return False

    @staticmethod
    def is_alphabet_string(ustring):
        """判断是否全部为英文字母"""
        for ch in ustring:
            if not NlpUtils.is_alphabet(ch):
                return False
        return True

    @staticmethod
    def is_number_str(ustring):
        for ch in ustring:
            if not NlpUtils.is_number(ch):
                return False
        return True

    @staticmethod
    def is_other_ch(uchar):
        """判断是否非汉字，数字和英文字符"""
        if not (NlpUtils.is_chinese_char(uchar) or NlpUtils.is_number(uchar) or NlpUtils.is_alphabet(uchar)):
            return True
        else:
            return False

    @staticmethod
    def is_other_str(ustring):
        """
        判断字符串是否都是异常字符
        :param ustring:
        :return:
        """
        for ch in ustring:
            # 只要有一个是正常字符，就是正常字符
            if not NlpUtils.is_other_ch(ch):
                return False
        return True

    @staticmethod
    def b2q(uchar):
        """字符 半角转全角"""
        inside_code = ord(uchar)
        if inside_code < 0x0020 or inside_code > 0x7e:
            # 不是半角字符就返回原来的字符
            return uchar
        if inside_code == 0x0020:
            # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
            inside_code = 0x3000
        else:
            inside_code += 0xfee0
        return chr(inside_code)

    @staticmethod
    def q2b(uchar):
        """字符 全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e:
            # 转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)

    @staticmethod
    def string_q2b(ustring):
        """字符串 全角转半角"""
        return "".join([NlpUtils.q2b(uchar) for uchar in ustring])

    @staticmethod
    def strip(usting):
        """删除字符串两侧的空白字符"""
        return usting.strip().strip("\n").strip("\t")

    @staticmethod
    def delete_emoji(ustring):
        """将句子中的emoji全部进行删除"""
        return NlpUtils.EMOJI_PATTERN.sub("", ustring)

    @staticmethod
    def delete_all_punct(ustring):
        outputs = []
        for uchar in ustring:
            if not NlpUtils.is_punctuation(uchar):
                outputs.append(uchar)
        return "".join(outputs)

    @staticmethod
    def delete_simple_punctuation(ustring):
        """
        去除普通的标点符号
        :param ustring:
        :return:
        """
        return NlpUtils.SIMPLE_PUNCTUATION.sub("", ustring)

    @staticmethod
    def lower(ustring):
        """
        转小写
        :param strs:
        :return:
        """
        return ustring.lower()

    @staticmethod
    def upper(ustring):
        """
        转大写
        :param ustring:
        :return:
        """
        return ustring.upper()

    @staticmethod
    def convert_to_unicode(text):
        """
        Converts text to unicode
        :param text:
        :return:
        """
        if six.PY3:
            if isinstance(text, str):
                return text
            elif isinstance(text, bytes):
                return text.decode("utf-8", "ignore")
            else:
                raise ValueError("Unsupported string type: %s" % (type(text)))
        elif six.PY2:
            if isinstance(text, str):
                return text.decode("utf-8", "ignore")
            elif isinstance(text, unicode):
                return text
            else:
                raise ValueError("Unsupported string type: %s" % (type(text)))
        else:
            raise ValueError("Not running on Python2 or Python 3?")

    @staticmethod
    def convert_to_utf8(text):
        """
        Converts text to utf-8
        :param text:
        :return:
        """
        if six.PY3:
            if isinstance(text, str):
                return text.encode("utf-8", "ignore")
            elif isinstance(text, bytes):
                return text
            else:
                raise ValueError("Unsupported string type: %s" % (type(text)))
        elif six.PY2:
            if isinstance(text, str):
                return text
            elif isinstance(text, unicode):
                return text.encode("utf-8", "ignore")
            else:
                raise ValueError("Unsupported string type: %s" % (type(text)))
        else:
            raise ValueError("Not running on Python2 or Python3")

    @staticmethod
    def printable_text(text):
        """Returns text encoded in a way suitable for print or `tf.logging`."""

        # These functions want `str` for both Python2 and Python3, but in one case
        # it's a Unicode string and in the other it's a byte string.
        if six.PY3:
            if isinstance(text, str):
                return text
            elif isinstance(text, bytes):
                return text.decode("utf-8", "ignore")
            else:
                raise ValueError("Unsupported string type: %s" % (type(text)))
        elif six.PY2:
            if isinstance(text, str):
                return text
            elif isinstance(text, unicode):
                return text.encode("utf-8")
            else:
                raise ValueError("Unsupported string type: %s" % (type(text)))
        else:
            raise ValueError("Not running on Python2 or Python 3?")

    @staticmethod
    def convert_to_unicode_obj(obj):
        if six.PY3 and (isinstance(obj, str) or isinstance(obj, bytes)) or \
                six.PY2 and (isinstance(obj, str) or isinstance(obj, unicode)):
            obj = NlpUtils.convert_to_unicode(obj)
        if isinstance(obj, list):
            obj = [NlpUtils.convert_to_unicode_obj(w) for w in obj]
        elif isinstance(obj, dict):
            for key in obj.keys():
                obj[key] = NlpUtils.convert_to_unicode_obj(obj[key])
        return obj

    @staticmethod
    def split_sentence(ustring):
        raw_sub_sentences = NlpUtils.SENTENCE_SPLITER.split(ustring)
        raw_sub_sentences = [raw_sub_sentence for raw_sub_sentence in raw_sub_sentences if len(raw_sub_sentence) > 0]
        merged_sentences = []
        length = len(raw_sub_sentences)
        i = 0
        while i < length:
            if (i + 1) < length:
                merged_sentences.append(raw_sub_sentences[i] + raw_sub_sentences[i + 1])
            else:
                merged_sentences.append(raw_sub_sentences[i])
            i += 2
        return merged_sentences

    @staticmethod
    def is_whitespace(uchar):
        """Checks whether `chars` is a whitespace character."""
        # \t, \n, and \r are technically contorl characters but we treat them
        # as whitespace since they are generally considered as such.
        if uchar == " " or uchar == "\t" or uchar == "\n" or uchar == "\r":
            return True
        cat = unicodedata.category(uchar)
        if cat == "Zs":
            return True
        return False

    @staticmethod
    def is_control(uchar):
        """Checks whether `chars` is a control character."""
        # These are technically control characters but we count them as whitespace
        # characters.
        if uchar == "\t" or uchar == "\n" or uchar == "\r":
            return False
        cat = unicodedata.category(uchar)
        if cat in ("Cc", "Cf"):
            return True
        return False

    @staticmethod
    def is_punctuation(uchar):
        """Checks whether `chars` is a punctuation character."""
        cp = ord(uchar)
        # We treat all non-letter/number ASCII as punctuation.
        # Characters such as "^", "$", and "`" are not in the Unicode
        # Punctuation class but we treat them as punctuation anyways, for
        # consistency.
        if ((cp >= 33 and cp <= 47) or (cp >= 58 and cp <= 64) or
                (cp >= 91 and cp <= 96) or (cp >= 123 and cp <= 126)):
            return True
        cat = unicodedata.category(uchar)
        if cat.startswith("P"):
            return True
        return False

    @staticmethod
    def whitespace_tokenize(ustring):
        """Runs basic whitespace cleaning and splitting on a piece of text."""
        ustring = ustring.strip()
        if not ustring:
            return []
        tokens = ustring.split()
        return tokens

    @staticmethod
    def delete_stop_word(ustring):
        """删除停用词"""
        return NlpUtils.STOP_WORDS.sub("", ustring)

    @staticmethod
    def delete_punc_on_side(ustring):
        """
        删除两侧的所有标点符号
        :param ustring:
        :return:
        """
        if ustring and len(ustring) == 0:
            return ustring

        head_output = ""
        for index, uchar in enumerate(ustring):
            if NlpUtils.is_punctuation(uchar):
                continue
            else:
                head_output = ustring[index:]
                break

        tail_output = ""
        for index in reversed(range(len(head_output))):
            if NlpUtils.is_punctuation(head_output[index]):
                continue
            else:
                tail_output = head_output[0:index + 1]
                break

        return tail_output

    @staticmethod
    def is_garbage(ustring):
        """
        是否重复的废话
        :param ustring:
        :return:
        """
        char_set = set(ustring)
        if len(char_set) == 1:
            return True
        return False

    @staticmethod
    def tra2sim(ustring):
        return Opencc.to_simple(ustring)

    @staticmethod
    def sim2tra(ustring):
        return Opencc.to_traditional(ustring)

    # 全角转半角
    # 删除两侧空格
    # 繁体转简体
    # 小写
    @staticmethod
    def clean(ustring):
        return re.sub(u"[^\u4e00-\u9fa5_.a-zA-Z0-9]", "", NlpUtils.lower(NlpUtils.tra2sim(NlpUtils.string_q2b(NlpUtils.strip(ustring)))))


if __name__ == "__main__":
    print(NlpUtils.split_sentence("我要回老家。123."))
    print(NlpUtils.delete_stop_word("你好呀"))
    print(NlpUtils.delete_punc_on_side("u.."))
    print(NlpUtils.is_punctuation("u"))
    print(NlpUtils.clean("ABC123/*-中国 是abc"))
    print(sys.maxsize)
