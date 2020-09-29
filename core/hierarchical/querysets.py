from itertools import (
    chain,
)
from operator import (
    itemgetter,
)
from typing import (
    Dict,
    Iterable,
    Iterator,
    Optional,
    Set,
    Tuple,
    TypeVar,
)

from django.db.transaction import (
    atomic,
)
from mptt.querysets import (
    TreeQuerySet,
)


PkType = TypeVar('PkType')


class HierarchicalQuerySet(TreeQuerySet):

    @atomic
    def _delete_by_layers(self) -> Dict[str, int]:
        result: Dict[str, int] = {}

        doomed: Dict[Optional[PkType], Set[PkType]]
        doomed = self._get_doomed_dict()

        while True:
            layer: Set[PkType] = {
                item_id
                for item_id, children in doomed.items()
                if not children and item_id
            }
            if not layer:
                break

            for item_id in layer:
                del doomed[item_id]

            for parent_id, children_ids in doomed.items():
                children_ids.difference_update(layer)

            _, sub_result = super(
                TreeQuerySet,
                self.filter(pk__in=layer),
            ).delete()

            for app_label, deleted_count in sub_result.items():
                try:
                    result[app_label] += deleted_count
                except KeyError:
                    result[app_label] = deleted_count

        if next(filter(None, doomed), None):
            raise ValueError(
                'Cannot resolve deleting order of elements!',
            )

        return result

    def _get_doomed_dict(self) -> Dict[Optional[PkType], Set[PkType]]:
        items: Iterable[Tuple[PkType, Optional[PkType]]] = self.values_list(
            'id',
            'parent_id',
        )

        keys: Iterator[Optional[PkType]] = chain(
            (None,),
            map(
                itemgetter(0),
                items,
            ),
        )
        doomed: Dict[Optional[PkType], Set[PkType]] = {
            item_id: set()
            for item_id in keys
        }
        for item_id, parent_id in items:
            doomed[parent_id].add(item_id)

        return doomed

    def delete(self) -> Tuple[int, Dict[str, int]]:
        result: Dict[str, int] = self._delete_by_layers()
        return sum(result.values()), result
