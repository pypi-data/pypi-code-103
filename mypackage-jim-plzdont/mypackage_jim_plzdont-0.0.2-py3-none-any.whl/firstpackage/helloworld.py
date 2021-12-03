def say_hello(name: str = None):
  if name:
    return f"Hello, {name}!"
  else:
    return "Hello, world!"
