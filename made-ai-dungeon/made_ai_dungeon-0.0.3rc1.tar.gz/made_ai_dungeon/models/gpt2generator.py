import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, AutoTokenizer, AutoModelWithLMHead

from made_ai_dungeon.process_text import gpt_text_post_processing


class GPTGenerator:
    def __init__(self, model_path: str, max_len: int = 60, max_context_len: int = 1024, old_model: bool = True) -> None:
        self.max_len = max_len
        self.max_context_len = max_context_len
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if old_model is True:
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
            self.model = GPT2LMHeadModel.from_pretrained(model_path).to(self.device)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelWithLMHead.from_pretrained(model_path).to(self.device)
        self.model.eval()

    def get_context_tokens(self, input_text):
        context_tokens = self.tokenizer.encode(input_text, add_special_tokens=False, return_tensors="pt").to(
            self.device)
        context_tokens[0] = context_tokens[0][-self.max_context_len:]
        return context_tokens

    def generate_text(self, input_text: str) -> str:
        context_tokens = self.get_context_tokens(input_text)
        generated_tokens = self.model.generate(context_tokens, max_length=context_tokens.shape[1] + self.max_len,
                                               top_k=50, top_p=0.95, do_sample=True)
        generated_new_tokens = generated_tokens.cpu().tolist()[0][context_tokens.shape[1]:]
        generated_text = self.tokenizer.decode(generated_new_tokens,
                                               clean_up_tokenization_spaces=False,
                                               skip_special_tokens=True)
        generated_text = gpt_text_post_processing(generated_text)
        return generated_text
