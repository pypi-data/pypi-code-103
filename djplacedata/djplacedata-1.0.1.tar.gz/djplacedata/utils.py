def get_place_field_from_model(model):
    places_meta = getattr(model, 'PlacesMeta', None)
    return getattr(places_meta, 'field')


def get_values_from_model(model):
    places_meta = getattr(model, 'PlacesMeta', None)
    return getattr(places_meta, 'values')
