from .bert import BertTokenizer


class GPTTokenizer(BertTokenizer):
    """GPT2 tokenizer from GPT2-ML, it uses same tokenizer with BERT, same vocab, same pattern"""


class HuaweiGPTTokenizer(BertTokenizer):
    """Huawei GPT tokenizer, it uses same vocal file"""
