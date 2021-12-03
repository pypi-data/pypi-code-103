from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum, safe_parse_float, non_empty_list

from ..log import logger


def get_product(impact_assessment: dict) -> dict:
    """
    Get the full `Product` from the `ImpactAssessment.cycle`.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.

    Returns
    -------
    dict
        The `Product` of the `ImpactAssessment`.
    """
    product = impact_assessment.get('product', {})
    products = impact_assessment.get('cycle', {}).get('products', [])
    return find_term_match(products, product.get('@id'))


def get_site(impact_assessment: dict) -> dict:
    return impact_assessment.get('site', impact_assessment.get('cycle', {}).get('site', {}))


def get_region_id(impact_assessment: dict) -> str:
    """
    Get the country or region @id of the ImpactAssessment.
    Note: level 1 GADM region will be returned only, even if the region is of level > 1.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.

    Returns
    -------
    str
        The `@id` of the `region`.
    """
    site = get_site(impact_assessment)
    term_id = site.get('region', site.get('country', impact_assessment.get('country', {}))).get('@id')
    is_allowed = term_id is None or len(term_id) == 8 or not term_id.startswith('GADM')
    term_parts = term_id.split('.') if term_id else []
    return term_id if is_allowed else (
        f"{'.'.join(term_parts[0:2])}{('_' + term_id.split('_')[1]) if len(term_parts) > 2 else ''}"
    )


def _factor_value(nodes: str, term_id: str):
    def get_value(factor: tuple):
        factor_term_id, coefficient = factor
        values = non_empty_list([
            node.get('value') for node in nodes if node.get('term', {}).get('@id') == factor_term_id
        ])
        value = sum(values) if len(values) > 0 else None
        log_func = logger.error if value is None else logger.debug
        log_func('term=%s, node=%s, value=%s, coefficient=%s', term_id, factor_term_id, value, coefficient)
        return value * coefficient if value is not None else None
    return get_value


def _factor_values(lookup, lookup_col: str):
    terms = list(lookup.termid)
    values = [[term, get_table_value(lookup, 'termid', term, column_name(lookup_col))] for term in terms]
    return list(filter(lambda value: value[1] is not None, values))


def impact_value(impact: dict, lookup_col: str, term_id='') -> float:
    lookup = download_lookup('emission.csv')
    factors = _factor_values(lookup, lookup_col)
    blank_nodes = impact.get('emissionsResourceUse', [])
    values = [value for value in list(map(_factor_value(blank_nodes, term_id), factors)) if value is not None]
    return list_sum(values) if len(values) > 0 else None


def emission_value(impact_assessment: dict, term_id: str):
    return safe_parse_float(find_term_match(impact_assessment.get('emissionsResourceUse', []), term_id).get('value'), 0)


def convert_value_from_cycle(product: dict, value: float, default=0):
    pyield = list_sum(product.get('value', [])) if product else 0
    economic_value = product.get('economicValueShare', 0) if product else 0
    return (value / pyield) * economic_value / 100 if pyield > 0 else default
