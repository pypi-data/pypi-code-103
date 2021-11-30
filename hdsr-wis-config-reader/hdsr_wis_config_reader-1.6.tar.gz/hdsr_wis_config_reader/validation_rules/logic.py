from typing import List
from typing import Tuple

import itertools


class ValidationLogic:

    gt = "<"
    gte = "<="
    HLOC_SLOC_VALIDATIONR_RULES = ["hmin", gte, "smin", gt, "smax", gte, "hmax"]
    # [hmin <= smin < smax <= hmax] combined with [WIN <= OV <= ZOM]
    WLOC_VALIDATIONR_RULES = [
        "hmin",
        gte,
        "smin_win",
        gte,
        "smin_ov",
        gte,
        "smin_zom",
        gt,
        "smax_win",
        gte,
        "smax_ov",
        gte,
        "smax_zom",
        gte,
        "hmax",
    ]

    @classmethod
    def __find_operator(cls, left_part: str, right_part: str, rules: List[str]) -> str:
        """
        Find operators between left_part and right_part.
        If operators hold '<' then return '<' else '<='

        Examples with rules = ['smin_win', '<=', 'smin_ov', '<=', 'smin_zom', '<', 'smax_win', '<=', 'smax_ov']
        Example 1:
            arguments:
                left_part = 'smin_win'
                right_part = 'smin_zom'
            results in:
                '<='  # so this rule applies: smin_win <= smin_zom
        Example 2:
            arguments:
                left_part = 'smin_zom'
                right_part = 'smax_ov'
            results in:
                '<'  # so this rule applies: smin_zom < smax_ov
        """
        idx_left_part = rules.index(left_part)
        idx_right_part = rules.index(right_part)
        assert idx_left_part < idx_right_part
        operators_between = [x for x in rules[idx_left_part:idx_right_part] if x in (cls.gt, cls.gte)]
        operator = cls.gt if cls.gt in operators_between else cls.gte
        return operator

    @classmethod
    def __get_validation_logic(cls, rules: List[str]) -> List[Tuple[str, str, str]]:
        limits_no_operators = [x for x in rules if x not in (cls.gt, cls.gte)]
        pairs = list(itertools.combinations(iterable=limits_no_operators, r=2))
        pairs_with_operator = [
            (x[0], cls.__find_operator(left_part=x[0], right_part=x[1], rules=rules), x[1],) for x in pairs
        ]
        return pairs_with_operator

    @classmethod
    def get_hloc_sloc_validation_logic(cls) -> List[Tuple[str, str, str]]:
        return cls.__get_validation_logic(rules=cls.HLOC_SLOC_VALIDATIONR_RULES)

    @classmethod
    def get_wloc_validation_logic(cls) -> List[Tuple[str, str, str]]:
        return cls.__get_validation_logic(rules=cls.WLOC_VALIDATIONR_RULES)
