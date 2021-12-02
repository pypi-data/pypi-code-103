import datetime

from ..models import (
    ProductType,
    Product,
    ProductFilePath,
    ProductRelation,
    ProductRelationType,
    FieldType,
    GitHubUser,
)

from ..db.sa import sa


##__________________________________________________________________||
def create_product(
    type_id,
    paths=None,
    relations=None,
    attributes=None,
    posting_git_hub_user_id=None,
    **kwargs
):
    """Create a product"""

    with sa.session.no_autoflush:
        return _create_product(
            type_id,
            paths,
            relations,
            attributes,
            posting_git_hub_user_id,
            **kwargs
        )


def update_product(
    product_id,
    paths=None,
    relations=None,
    attributes=None,
    updating_git_hub_user_id=None,
    **kwargs
):
    """Update a product"""

    with sa.session.no_autoflush:
        return _update_product(
            product_id,
            paths,
            relations,
            attributes,
            updating_git_hub_user_id,
            **kwargs
        )


def delete_product(product_id):
    """Delete a product"""

    model = Product.query.filter_by(product_id=product_id).one()
    sa.session.delete(model)
    return


def convert_product_type(product_id, type_id, updating_git_hub_user_id=None):
    with sa.session.no_autoflush:
        return _convert_product_type(product_id, type_id, updating_git_hub_user_id)


##__________________________________________________________________||
def uniq_preserving_order(list_):
    # https://stackoverflow.com/a/17016257/7309855
    return list(dict.fromkeys(list_))


def _normalize_paths(paths):
    # e.g., paths = ["  /d/e ", " ", "/a/b/c", "/f/g", "/d/e"]

    ret = [p.strip() for p in paths]  # strip
    # e.g., ["/d/e", "", "/a/b/c", "/f/g", "/d/e"]

    ret = [p for p in ret if p]  # remove empty
    # e.g., ["/d/e", "/a/b/c", "/f/g", "/d/e"]

    ret = uniq_preserving_order(ret)
    # e.g., ["/d/e", "/a/b/c", "/f/g"]

    return ret


##__________________________________________________________________||
def _create_product(
    type_id, paths, relations, attributes, posting_git_hub_user_id, **kwargs
):
    product_type = ProductType.query.filter_by(type_id=type_id).one()

    model = Product(type_=product_type, **kwargs)

    if paths is not None:
        paths = _normalize_paths(paths)
        model.paths = [ProductFilePath(path=p) for p in paths]

    if relations is not None:
        model.relations = [
            ProductRelation(
                type_=ProductRelationType.query.filter_by(
                    type_id=r["type_id"]
                ).one(),
                other=Product.query.filter_by(
                    product_id=r["product_id"]
                ).one(),
            )
            for r in relations
        ]

    if attributes is None:
        attributes = {}

    for association in product_type.fields:
        field = association.field
        value = attributes.get(field.field_id)
        field.type_.attribute_class(
            type_field_association=association,
            field=field,
            product=model,
            value=value,
        )

    if posting_git_hub_user_id:
        model.posting_git_hub_user = GitHubUser.query.filter_by(
            user_id=posting_git_hub_user_id
        ).one()

    sa.session.add(model)
    return model


def _update_product(
    product_id,
    paths,
    relations,
    attributes,
    updating_git_hub_user_id,
    **kwargs
):

    model = Product.query.filter_by(product_id=product_id).one()

    if not attributes:
        attributes = {}

    # update paths
    if paths is not None:
        model.paths = _update_paths(model.paths, paths)

    # update relations
    if relations is not None:
        model.relations = _update_relations(model.relations, relations)

    # update scalar fields
    for k, v in kwargs.items():
        setattr(model, k, v)

    # update attributes
    for association in model.type_.fields:
        field = association.field
        try:
            value = attributes[field.field_id]
        except KeyError:
            continue
        attribute_class = field.type_.attribute_class
        query = attribute_class.query.filter_by(product=model, field=field)
        attr = query.one_or_none()
        if attr:
            attr.value = value
        else:
            attribute_class(
                type_field_association=association,
                field=field,
                product=model,
                value=value,
            )

    model.time_updated = datetime.datetime.now()
    if updating_git_hub_user_id:
        GitHubUser.query.filter_by(user_id=updating_git_hub_user_id).one()
    model.updating_git_hub_user_id = updating_git_hub_user_id

    return model


def _update_paths(old, input):
    input = _normalize_paths(input)
    path_dict = {p.path: p for p in old}
    return [
        path_dict[p] if p in path_dict else ProductFilePath(path=p)
        for p in input
    ]


def _update_relations(old, input):

    # sets of tuples (type_id, other_product_id) of ProductRelation
    new_ids = {(i["type_id"], i["product_id"]) for i in input}
    old_ids = {(r.type_id, r.other_product_id) for r in old}

    added_ids = new_ids - old_ids

    model_dict = {(r.type_id, r.other_product_id): r for r in old}
    for id_ in added_ids:
        type_id, product_id = id_
        type_ = ProductRelationType.query.filter_by(type_id=type_id).one()
        other = Product.query.filter_by(product_id=product_id).one()
        model_dict[id_] = ProductRelation(type_=type_, other=other)

    return [model_dict[i] for i in new_ids]


##__________________________________________________________________||
def _convert_product_type(product_id, type_id, updating_git_hub_user_id):
    model = Product.query.filter_by(product_id=product_id).one()
    product_type = ProductType.query.filter_by(type_id=type_id).one()
    model.type_ = product_type

    attr_names = [
        a.attribute_class.backref_column
        for a in FieldType.__members__.values()
    ]
    # e.g., 'attributes_unicode_text', 'attributes_boolean'

    attrs = [e for attr in attr_names for e in getattr(model, attr)]
    # e.g., AttributeUnicodeText

    attr_dict = {a.field_id: a for a in attrs}

    for association in model.type_.fields:
        field = association.field
        attr = attr_dict.pop(field.field_id, None)
        if attr:
            attr.type_field_association = association
        else:
            attribute_class = field.type_.attribute_class
            attribute_class(
                type_field_association=association,
                field=field,
                product=model,
                value=None,
            )

    for attr in attr_dict.values():
        attr.product = None

    model.time_updated = datetime.datetime.now()
    if updating_git_hub_user_id:
        GitHubUser.query.filter_by(user_id=updating_git_hub_user_id).one()
    model.updating_git_hub_user_id = updating_git_hub_user_id

    return model


##__________________________________________________________________||
