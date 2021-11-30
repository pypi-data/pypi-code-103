try:
    from mlpractice_solutions.mlpractice_solutions\
        .rnn_torch_solution import make_tokens
except ImportError:
    make_tokens = None


def test_all(make_tokens=make_tokens):
    test_simple(make_tokens)
    print('All tests passed!')


def test_simple(make_tokens=make_tokens):
    input_text = "Make ML practice great!"
    expected = set(input_text)

    assert set(make_tokens(input_text)) == expected, \
        "Have you heard of the set datatype in Python?"
