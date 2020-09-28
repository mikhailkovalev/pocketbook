from collections import (
    defaultdict,
)
from itertools import (
    chain,
)
from operator import (
    itemgetter,
)
from typing import (
    Dict,
    Iterable,
    List,
    Set,
    Tuple,
)

from django.db.models import (
    QuerySet,
)
from django.db.transaction import (
    atomic,
)


class HierarchicalQuerySet(QuerySet):

    def delete(self):
        items: Iterable[Tuple[str, str]] = self.values_list(
            'id',
            'parent_id',
        )

        keys = chain(
            (None,),
            map(
                itemgetter(0),
                items,
            ),
        )
        children_by_parent: Dict[str, Set[str]] = {
            item_id: set()
            for item_id in keys
        }
        for item_id, parent_id in items:
            children_by_parent[parent_id].add(item_id)

        layers_queue: List[Set[str]] = []

        while True:
            current_layer: Set[str] = {
                item_id
                for item_id, children in children_by_parent.items()
                if not children and item_id
            }
            if not current_layer:
                break

            for item_id in current_layer:
                del children_by_parent[item_id]

            for parent_id, children_ids in children_by_parent.items():
                children_ids.difference_update(current_layer)

            layers_queue.append(current_layer)

        survived = tuple(filter(None, children_by_parent))

        if survived:
            raise ValueError(
                'Cannot resolve deleting order of elements!',
                survived,
            )
        report = defaultdict(int)
        with atomic():
            for layer in layers_queue:
                layer_queryset = self.filter(id__in=layer)
                _, sub_report = super(HierarchicalQuerySet, layer_queryset).delete()
                for model_label, deleted in sub_report.items():
                    report[model_label] += deleted

        return sum(report.values()), report
