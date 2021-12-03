import logging
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, TypeVar, TypedDict
from itertools import groupby, chain

from django.db.models import (
    Q, QuerySet, Subquery, OuterRef, JSONField, Func, F, Model
)
from django.db import transaction

from .seeker import CodeSeeker
from .registry import CodeSeekerRegistry
from .models import CODES_RELATED_NAME


__all__ = (
    'CodeSeek',
    'CodeSeekSeq',
    'CodesFilter',

    'EMPTY_Q',
    'cmp_AND',
    'cmp_OR',

    'seek_codes_Q',

    'CodeSeekerQuerySet',
)

logger = logging.getLogger(__name__)

QT = TypeVar('QT', bound='CodeSeekerQuerySet')
CodeSeek = Tuple[str, Any]
CodeSeekSeq = Sequence[CodeSeek]

# IMPORT_SQL = '''
# insert into {codes_table}(code, value, entity_id)
# select
#     e.json_code_code as code,
#     e.codes ->> e.json_code_code as value,
#     e.id as entity_id
# from (
# select
#     jsonb_object_keys(t.codes) as json_code_code, t.*
# from {main_table} t
# ) e;
# '''
# FIXME:
# EXPORT_SQL = '''
# update {main_table}
# set codes = e.codes
# from (
#     select jsonb_object_agg(t.code, t.value) as codes, t.entity_id as id
#     from {codes_table} t group by t.entity_id order by t.entity_id
# ) as e
# where {main_table}.id = e.id;
# '''


class CodesFilter(TypedDict):
    codes: CodeSeekSeq
    registry: CodeSeekerRegistry
    cmp: Optional[Callable]
    warning_context: Optional[str]


EMPTY_Q = Q()


def cmp_AND(a: Q, b: Q):
    return a & b


def cmp_OR(a: Q, b: Q):
    return a | b


def code_key(item):
    return item[0]


def get_code_seeker(
    registry: CodeSeekerRegistry,
    code: str,
    warning_context: Optional[str] = None
) -> Optional[CodeSeeker]:
    if code not in registry:
        logger.warning(
            f'[CODE-SEEKING-FILTER] No such code "{code}"'
            +
            (
                f'in {warning_context}.'
                if warning_context is not None
                else
                '.'
            )
        )
        return None

    return registry[code]


def seek_codes_Q_set(
    registry: CodeSeekerRegistry,
    codes: CodeSeekSeq,
    cmp: Callable = cmp_OR,
    warning_context: Optional[str] = None
) -> Q:
    q = EMPTY_Q
    grouped = groupby(sorted(codes, key=code_key), key=code_key)

    for code, values in grouped:
        seeker = get_code_seeker(registry, code, warning_context=warning_context)

        if seeker is None:
            continue

        q = cmp(q, seeker.Q_set({seeker.to_value(v) for c, v in values}, lookup='in'))

    return q


def seek_codes_Q_json(
    registry: CodeSeekerRegistry,
    codes: CodeSeekSeq,
    cmp: Callable = cmp_OR,
    warning_context: Optional[str] = None
) -> Q:
    q = EMPTY_Q

    for code, value in codes:
        seeker = get_code_seeker(registry, code, warning_context=warning_context)

        if seeker is None:
            continue

        q = cmp(q, seeker.Q_json(seeker.to_value(value)))

    return q


class CodeSeekerQuerySet(QuerySet):
    def seek_codes(
        self,
        registry: CodeSeekerRegistry,
        codes: CodeSeekSeq,
        cmp: Callable = cmp_OR,
        warning_context: str = None
    ) -> QuerySet:
        """Seek for codes in a related table as this is more performant,
        than seeking over the json field.
        """
        q = seek_codes_Q_set(
            registry, codes, cmp=cmp, warning_context=warning_context
        )

        return self.filter(q) if q is not EMPTY_Q else self

    def seek_codes_json(
        self,
        registry: CodeSeekerRegistry,
        codes: CodeSeekSeq,
        cmp: Callable = cmp_OR,
        warning_context: str = None
    ) -> QuerySet:
        """This is used when lookup is performed over data in jsonb field.
        As it is a source of thruth for codes and separate table is for
        performance improvements.
        """
        q = seek_codes_Q_json(
            registry, codes, cmp=cmp, warning_context=warning_context
        )

        return self.filter(q) if q is not EMPTY_Q else self

    def general_filter(
        self: QT,
        codes_filter: Optional[CodesFilter] = None,
        codes_filter_json: Optional[CodesFilter] = None,
        **kw
    ) -> QT:
        q = super().general_filter(**kw)

        if codes_filter is not None and codes_filter.get('codes') is not None:
            q = q.seek_codes(**codes_filter)

        if codes_filter_json is not None and codes_filter_json.get('codes') is not None:
            q = q.seek_codes_json(**codes_filter_json)

        return q

    def update_json_from_relations(
        self,
        related_name: str = CODES_RELATED_NAME
    ) -> None:
        CodesModel = self.model._meta.get_field(related_name).related_model

        # FIXME:
        # SQL version could be much more sufficient than default django's update.
        #
        # return self.model.objects.raw(
        #     EXPORT_SQL.format(
        #         main_table=MainModel._meta.db_table,
        #         codes_table=f'{self.query}'
        #     )
        # )

        return self.update(
            codes=Subquery(
                (
                    CodesModel.objects
                    .filter(entity_id=OuterRef('pk'))
                    .values('entity_id')
                    .annotate(
                        values=Subquery(
                            CodesModel.objects.filter(
                                entity_id=OuterRef('entity_id'),
                                code=OuterRef('code')
                            )
                            .values('entity_id')
                            .annotate(_val=Func(
                                F('value'),
                                output_field=JSONField(),
                                function='array_agg'
                            ))
                            .values('_val')
                            .order_by()
                            [:1]
                        )
                    )
                    .annotate(_value=Func(
                        F('code'), F('values'),
                        output_field=JSONField(),
                        function='jsonb_object_agg'
                    ))
                    .values('_value')
                    .order_by()
                    [:1]
                ),
                output_field=JSONField()
            )
        )

    def update_relations_from_json(
        self,
        related_name: str = CODES_RELATED_NAME,
        batch_size: Optional[int] = None,
    ) -> None:
        # FIXME:
        # SQL version could be much more sufficient than default django's update.
        # IMPORT_SQL

        # FIXME:
        # Behaviour to delete all and recreate again is not fast and
        # good in terms of maintenance.
        # So this should need a rework.
        CodesModel: Model = self.model._meta.get_field(related_name).related_model

        generated = [
            CodesModel(entity_id=pk, code=code, value=value)
            for pk, codes in self.values_list('pk', 'codes')
            for code, values in codes.items()
            for value in values
        ]

        if len(generated) == 0:
            return

        with transaction.atomic():
            CodesModel.objects.filter(entity_id__in=self.values('id')).delete()
            CodesModel.objects.bulk_create(generated, batch_size=batch_size)
