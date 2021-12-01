from kama_sdk.model.input.generic_input import GenericInput


def in_variable(ginput: GenericInput):
  return dict(
    type=ginput.get_kind(),
    options=ginput.serialize_options(),
    extras=ginput.get_extras()
  )
