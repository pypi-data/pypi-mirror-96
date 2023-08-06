from hestia_earth.schema import CycleFunctionalUnitMeasure, SiteSiteType

from hestia_earth.validation.utils import _list_has_props, _is_in_days, _diff_in_days, _get_dict_key, _flatten
from .shared import validate_dates, validate_list_dates, validate_list_duplicates, validate_list_min_max, \
    validate_list_term_percent
from .practice import validate_cropResidueManagement
from .product import validate_economicValueShare
from .data_completeness import validate_dataCompleteness


SITE_TYPES_1ha = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.PERMANENT_PASTURE.value
]


def validate_cycle_dates(cycle: dict):
    return validate_dates(cycle) or {
        'level': 'error',
        'dataPath': '.endDate',
        'message': 'must be greater than startDate'
    }


def _should_validate_cycleDuration(cycle: dict):
    return 'cycleDuration' in cycle and _is_in_days(cycle.get('startDate')) and _is_in_days(cycle.get('endDate'))


def validate_cycleDuration(cycle: dict):
    duration = _diff_in_days(cycle.get('startDate'), cycle.get('endDate'))
    return duration == round(cycle.get('cycleDuration'), 1) or {
        'level': 'error',
        'dataPath': '.cycleDuration',
        'message': f"must equal to endDate - startDate in days (~{duration})"
    }


def validate_functionalUnitMeasure(cycle: dict):
    site_type = _get_dict_key(cycle, 'site.siteType')
    value = cycle.get('functionalUnitMeasure')
    expected = CycleFunctionalUnitMeasure._1_HA.value
    return site_type not in SITE_TYPES_1ha or value == expected or {
        'level': 'error',
        'dataPath': '.functionalUnitMeasure',
        'message': f"must equal to {expected}"
    }


def validate_relDays(cycle: dict, prop: str):
    def validate(values):
        value = values[1]
        index = values[0]
        expected = len(value.get('value'))
        return len(value.get('relDays')) == expected or {
            'level': 'error',
            'dataPath': f".{prop}[{index}].relDays",
            'message': 'must contain ' + str(expected) + (' values' if expected > 1 else ' value')
        }

    results = list(map(validate, enumerate(_list_has_props(cycle.get(prop), ['relDays', 'value']))))
    return next((x for x in results if x is not True), True)


def validate_altStartDate(cycle: dict):
    return len(cycle.get('altStartDateDefinition', '')) > 0 or {
        'level': 'error',
        'dataPath': '.altStartDateDefinition',
        'message': 'is required when using altStartDate'
    }


def validate_startDate(cycle: dict):
    return len(cycle.get('altStartDate', '')) == 0 or {
        'level': 'error',
        'dataPath': '.altStartDate',
        'message': 'cannot be used with startDate'
    }


def validate_cycle(cycle: dict):
    """
    Validates a single `Cycle`.

    Parameters
    ----------
    cycle : dict
        The `Cycle` to validate.

    Returns
    -------
    List
        The list of errors for the `Cycle`, which can be empty if no errors detected.
    """
    return [
        validate_cycle_dates(cycle),
        validate_cycleDuration(cycle) if _should_validate_cycleDuration(cycle) else True,
        validate_altStartDate(cycle) if 'altStartDate' in cycle else True,
        validate_startDate(cycle) if 'startDate' in cycle else True,
        validate_dataCompleteness(cycle.get('dataCompleteness'))
    ] + _flatten([
        validate_list_dates(cycle, 'emissions'),
        validate_list_min_max(cycle, 'emissions'),
        validate_list_term_percent(cycle, 'emissions'),
        validate_relDays(cycle, 'emissions'),
        validate_list_duplicates(cycle, 'emissions', [
            'term.@id',
            'method.@id',
            'inputs.@id',
            'source.id',
            'methodDescription',
            'startDate',
            'endDate',
            'relDays'
        ])
    ] if 'emissions' in cycle else []) + _flatten([
        validate_relDays(cycle, 'inputs'),
        validate_list_min_max(cycle, 'inputs'),
        validate_list_term_percent(cycle, 'inputs'),
        validate_list_duplicates(cycle, 'inputs', [
            'term.@id',
            'destination.@id',
            'source.id',
            'methodDescription',
            'startDate',
            'endDate',
            'relDays'
        ])
    ] if 'inputs' in cycle else []) + _flatten([
        validate_relDays(cycle, 'products'),
        validate_list_min_max(cycle, 'products'),
        validate_list_term_percent(cycle, 'products'),
        validate_economicValueShare(cycle.get('products'))
    ] if 'products' in cycle else []) + _flatten([
        validate_list_dates(cycle, 'practices'),
        validate_list_min_max(cycle, 'practices'),
        validate_list_term_percent(cycle, 'practices'),
        validate_cropResidueManagement(cycle.get('practices'))
    ] if 'practices' in cycle else []) + _flatten([
        validate_functionalUnitMeasure(cycle)
    ] if 'functionalUnitMeasure' in cycle else [])
