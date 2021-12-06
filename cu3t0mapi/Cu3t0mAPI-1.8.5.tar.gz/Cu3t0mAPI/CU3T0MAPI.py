import random
import requests



def jokes():
  response = requests.get('https://api.cu3t0m.repl.co/gimme/jokes')
  return response.text

def letters():
  response = requests.get('https://api.cu3t0m.repl.co/gimme/letters')
  return response.text

def numbers():
  response = requests.get('https://api.cu3t0m.repl.co/gimme/numbers')
  return response.text

def words():
  response = requests.get('https://api.cu3t0m.repl.co/gimme/words')
  return response.text

def memes(topic="memes", amount="1"):
  response = requests.get(f'https://api.cu3t0m.repl.co/gimme/memes/{topic}/{amount}')
  return response.text

def ai_response(question, prev_question=None):
  response = requests.get(f'https://api.cu3t0m.repl.co/ai/response/{question}/{prev_question}/')
  return response.text