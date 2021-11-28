from transformers import AutoTokenizer

class ClassificationProcessor:
  """
  Processor for Text Classification
  """
  
  def __init__(self, max_input_length):
    
    self.max_input_length = max_input_length
  
  def process(self, examples):

    self.examples = examples
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased", use_fast=True)
    model_inputs = self.tokenizer(examples['sentence'], max_length=self.max_input_length, truncation=True, padding=True)

    return tokenizer, model_inputs


class T5Seq2SeqProcessor:
  """
  Processor for T5 models
  """
  
  def __init__(self, max_input_length, max_target_length, prefix):
    
    self.max_input_length = max_input_length
    self.max_target_length = max_target_length
    self.prefix = prefix
    
  def process(self, examples):

    self.examples = examples

    tokenizer = AutoTokenizer.from_pretrained("t5-small", use_fast=True)
    inputs = [self.prefix + doc for doc in self.examples["source"]]
    model_inputs = self.tokenizer(inputs, max_length=self.max_input_length, truncation=True, padding=True)

    # Setup the tokenizer for targets
    with self.tokenizer.as_target_tokenizer():
        labels = self.tokenizer(self.examples["target"], max_length=self.max_target_length, truncation=True, padding=True)

    model_inputs["labels"] = labels["input_ids"]
    
    return tokenizer, model_inputs 
  
  
class LanguageModelProcessor:
  """
  Processor for T5 models
  """

  def __init__(self, max_input_length):
    
    self.max_input_length = max_input_length
  
  def process(self, examples):

    self.examples = examples
    tokenizer = AutoTokenizer.from_pretrained("gpt-2", use_fast=True)
    model_inputs = self.tokenizer(examples['sentence'], max_length=self.max_input_length, truncation=True, padding=True)

    return tokenizer, model_inputs