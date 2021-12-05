from firstpackage.helloworld import say_hello

def test_helloworld_no_param():
  assert say_hello() == "Hello, world!"

def test_helloworld_with_param():
  assert say_hello("Jim") == f"Hello, Jim!"
