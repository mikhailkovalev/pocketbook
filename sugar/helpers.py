import calendar
from bisect import (
    bisect_right,
)
from datetime import (
    date,
    datetime,
    timedelta,
)
from decimal import (
    Decimal,
)
from functools import (
    partial,
)
from itertools import (
    chain,
    groupby,
    islice,
    product,
    repeat,
)
from operator import (
    attrgetter,
    itemgetter,
)
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    Union,
)

import numpy
import scipy.integrate
from django.conf import (
    settings,
)
from django.db.models import (
    DateTimeField,
    Model,
    QuerySet,
)
from django.db.models.functions import (
    Trunc,
)
from pytz import (
    timezone,
)
from sugar.enums import (
    DateAggregateEnum,
)

from .models import (
    SugarMetering,
)

ONE_SECOND = timedelta(seconds=1)
ONE_DAY = timedelta(days=1)
ONE_WEEK = timedelta(days=7)


def _get_first_day_of_next_month(date_: date) -> date:
    _, days_in_this_month = calendar.monthrange(
        date_.year,
        date_.month,
    )
    return date_.replace(day=days_in_this_month)+ONE_DAY


TRUNC_TYPES: Dict[str, str] = {
    DateAggregateEnum.NONE: 'second',
    DateAggregateEnum.DAY: 'day',
    DateAggregateEnum.WEEK: 'week',
    DateAggregateEnum.MONTH: 'month',
    DateAggregateEnum.YEAR: 'year',
}


TIME_LABEL_FORMAT: Dict[str, Callable[[datetime], str]] = {
    DateAggregateEnum.NONE: partial(datetime.strftime, format='%Y-%m-%d %H:%M'),  # noqa
    DateAggregateEnum.DAY: partial(datetime.strftime, format='%Y-%m-%d'),

    # fixme: по номеру недели не понятно, о каких датах идёт речь
    DateAggregateEnum.WEEK: lambda when: '{0}; week {1}'.format(*when.isocalendar()[:2]),  # noqa
    DateAggregateEnum.MONTH: partial(datetime.strftime, format='%Y-%m'),
    DateAggregateEnum.YEAR: partial(datetime.strftime, format='%Y'),
}


TIME_LABEL_ENDS: Dict[str, Callable[[datetime], datetime]] = {
    DateAggregateEnum.NONE: lambda when: when+ONE_SECOND,
    DateAggregateEnum.DAY: lambda when: when+ONE_DAY,
    DateAggregateEnum.WEEK: lambda when: when+ONE_WEEK,
    DateAggregateEnum.MONTH: _get_first_day_of_next_month,
    DateAggregateEnum.YEAR: lambda when: when.replace(day=1, month=1, year=when.year+1),  # noqa
}


# FIXME: don't use NamedTuples?
class SliceParams(NamedTuple):
    records: QuerySet
    slice_filter: Optional[Dict[str, Any]]
    total_rows_count: int
    total_pages_count: int
    page_number: int
    first_shown: int
    last_shown: int


def slice_records(
        records: QuerySet,
        target_page_number: int,
        page_size: int,
) -> SliceParams:
    # при значении -1 вернём последнюю страницу
    assert target_page_number == -1 or target_page_number >= 1

    time_labels_iterator = records.values(
        'when',
        'time_label',
    ).iterator(
        chunk_size=100,
    )

    groupped_iterator = groupby(
        iterable=time_labels_iterator,
        key=itemgetter('time_label'),
    )

    max_when: Optional[datetime] = None
    min_when: Optional[datetime] = None
    current_page_max_when = None
    current_page_min_when = None
    group_idx = -1

    current_page_number = 0
    # страницы нумеруем с 1

    for group_idx, (_, group) in enumerate(groupped_iterator):
        group_time_labels = map(itemgetter('when'), group)
        
        if group_idx % page_size == 0:
            if current_page_number == target_page_number:
                # предыдущая страница была той, которую запросили
                max_when = current_page_max_when
                min_when = current_page_min_when
            current_page_number += 1
            current_page_max_when = next(group_time_labels)
            current_page_min_when = current_page_max_when

        try:
            current_page_min_when = min(group_time_labels)
        except ValueError:
            # на случай, если итератор пустой, например, если
            # в группе была всего одна запись и её мы уже
            # извлекли в блоке if через next
            pass

    if max_when is None:
        # если так и не достигли запрошенной страницы -- отдадим последнюю
        max_when = current_page_max_when
        min_when = current_page_min_when
        target_page_number = current_page_number

    total_rows_count = group_idx + 1
    # Переменная `group_idx` по завершению цикла как раз
    # будет хранить индекс последней строки,
    # соответственно их общее количество на единицу
    # больше.

    slice_stop = target_page_number * page_size
    slice_start = slice_stop - page_size

    slice_filter: Optional[Dict[str, Any]] = None
    if max_when is not None and min_when is not None:
        slice_filter = dict(
            when__range=(min_when, max_when),
        )
        records = records.filter(
            **slice_filter,
        )

    return SliceParams(
        records=records,
        slice_filter=slice_filter,
        total_rows_count=total_rows_count,
        total_pages_count=current_page_number,
        page_number=target_page_number,
        first_shown=1+slice_start,
        last_shown=min(total_rows_count, slice_stop),
    )


# FIXME: don't use NamedTuples?
class AttachmentMeta(NamedTuple):
    model: Type[Model]
    # Класс модели атачмента

    set_name: str
    # Имя ключа, по которому надо положить к
    # словарю-записи список её атачментов этого типа.

    fk_name: str
    # Имя внешнего ключа, через который этот атачмент
    # ссылается на модель записи.

    filter_: Optional[Dict[str, Any]]
    # Фильтр записей

    export_values: Iterable[str]
    # Какие атрибуты атачмента следует извлечь


def export_attachments(
        records: QuerySet,
        *args: Tuple[AttachmentMeta, ...],
) -> None:
    records_by_ids: Dict[int, Dict[str, Any]] = {
        record['id']: record
        for record in records
    }

    for record in records_by_ids.values():
        record.update(
            **{
                meta.set_name: []
                for meta in args
            },
        )

    meta: AttachmentMeta
    for meta in args:
        attachments = meta.model.objects.filter(
            **{
                f'{meta.fk_name}__{k}': v
                for k, v in meta.filter_.items()
            }
        ).values(
            meta.fk_name,
            *meta.export_values,
        )
        for attachment in attachments:
            record_pk = attachment[meta.fk_name]
            current_record = records_by_ids[record_pk]
            current_record[meta.set_name].append(
                attachment,
            )


def get_meal_verbose_data(
        records: Iterable[Dict[str, Any]],
        columns: List[Dict[str, str]],
        response_rows: List[Dict[str, Any]],
        key_func: Callable[[Dict[str, Any]], Any],
) -> None:
    columns.append(dict(
        data_index='meal',
        header='Съедено (ХЕ)',
    ))
    records_groups_iterator = map(
        itemgetter(1),
        groupby(records, key_func)
    )

    zipped = zip(
        response_rows,
        records_groups_iterator,
    )

    for row, records_group in zipped:
        row['meal'] = Decimal()
        for record in records_group:
            for meal_info in record['meals']:  # fixme: pass attachment_set_name
                row['meal'] += meal_info['food_quantity']

    for row in response_rows:
        value = row['meal']
        row['meal'] = str(value) if value else None


def get_injections_verbose_data(
        records: Iterable[Dict[str, Any]],
        columns: List[Dict[str, str]],
        response_rows: List[Dict[str, Any]],
        key_func: Callable[[Dict[str, Any]], Any],
) -> None:
    records_groups_iterator = map(
        itemgetter(1),
        groupby(records, key_func)
    )
    zipped = zip(
        response_rows,
        records_groups_iterator,
    )

    data_indices: Dict[int, str] = dict()
    insulin_columns: List[Dict[str, str]] = []

    for row, records_group in zipped:
        for record in records_group:
            for injection_info in record['injections']:  # fixme: pass attachment_set_name
                mark_id = injection_info['insulin_syringe__insulin_mark']
                data_index = data_indices.get(
                    mark_id,
                )
                if data_index is None:
                    data_index = 'insulin_{}'.format(
                        mark_id,
                    )
                    insulin_columns.append(dict(
                        header=injection_info['insulin_syringe__insulin_mark__name'],
                        data_index=data_index,
                    ))
                    data_indices[mark_id] = data_index
                    for row_ in response_rows:
                        row_.setdefault(data_index, 0)
                row[data_index] += injection_info['insulin_quantity']

    for row in response_rows:
        for idx in data_indices.values():
            if row[idx] == 0:
                row[idx] = None

    insulin_columns.sort(key=itemgetter('header'))
    columns.extend(insulin_columns)


def get_sugar_verbose_data(
        records: List[Dict[str, Any]],  # на самом деле не list, а values-QuerySet
        columns: List[Dict[str, str]],
        response_rows: List[Dict[str, Any]],
        key_func: Callable[[Dict[str, Any]], Any],
        groupping: str,
) -> None:
    if groupping == DateAggregateEnum.NONE:
        _get_single_sugar_verbose_data(
            records,
            columns,
            response_rows,
        )
    else:
        _get_groupped_sugar_verbose_data(
            records,
            columns,
            response_rows,
            key_func,
            groupping,
        )


def _get_single_sugar_verbose_data(
        records: Collection[Dict[str, Any]],
        columns: List[Dict[str, str]],
        response_rows: List[Dict[str, Any]],
) -> None:
    columns.append(dict(
        data_index='sugar_level',
        header='Сахар крови'
    ))

    # Если нет группировки, то у нас каждой записи из
    # БД соответствует одна строка таблицы
    for row, record in zip(response_rows, records):
        try:
            sugar_value = next(
                iter(record['sugar_meterings']),
            )
            row['sugar_level'] = str(sugar_value['sugar_level'])
        except StopIteration:
            row['sugar_level'] = None


def _extend_stored_meterings(
        stored_time_moments_iterator: Iterator[int],  # fixme: rename to `timestamps`
        stored_values_iterator: Iterator[float],
        first_moment: datetime,
        last_moment: datetime,
) -> Tuple[Iterator[float], Iterator[float]]:
    # done: достать из базы измерение сахара,
    #  предшествующее самому раннему из
    #  присутствующих, чтобы более точно
    #  интерполировать.
    queryset = SugarMetering.objects.annotate(
        localized_when=Trunc(
            expression='record__when',
            kind='second',
            output_field=DateTimeField(),
            tzinfo=timezone(settings.TIME_ZONE),
        ),
    ).values(
        'localized_when',
        'sugar_level',
    )

    before_first = queryset.filter(
        record__when__lt=first_moment,
    ).last()

    after_last = queryset.filter(
        record__when__gt=last_moment,
    ).first()

    if before_first is not None and after_last is not None:
        stored_time_moments_iterator = chain(
            (
                round(before_first['localized_when'].timestamp()),
            ),
            stored_time_moments_iterator,
            (
                round(after_last['localized_when'].timestamp()),
            ),
        )
        stored_values_iterator = chain(
            (
                float(before_first['sugar_level']),
            ),
            stored_values_iterator,
            (
                float(after_last['sugar_level']),
            ),
        )

    elif before_first is not None:
        stored_time_moments_iterator = chain(
            (
                round(before_first['localized_when'].timestamp()),
            ),
            stored_time_moments_iterator,
        )
        stored_values_iterator = chain(
            (
                float(before_first['sugar_level']),
            ),
            stored_values_iterator,
        )

    elif after_last is not None:
        stored_time_moments_iterator = chain(
            stored_time_moments_iterator,
            (
                round(after_last['localized_when'].timestamp()),
            ),
        )
        stored_values_iterator = chain(
            stored_values_iterator,
            (
                float(after_last['sugar_level']),
            ),
        )

    return (
        stored_time_moments_iterator,
        stored_values_iterator,
    )


def _interpolate_meterings(
        records: List[Dict[str, Any]],  # на самом деле не list, а values-QuerySet
        stored_moments: Tuple[int, ...],
        stored_values: Tuple[float, ...],
        key_func: Callable[[Dict[str, Any]], Any],
        end_group_func: Callable[[datetime], datetime],

) -> Tuple[
    List[int],
    Collection[float],
]:
    ext_moments: List[int]
    ext_moments = sorted(set(chain(
        stored_moments,
        chain.from_iterable((
            map(
                round,
                (
                    moment.timestamp(),
                    end_group_func(moment).timestamp(),
                ),
            )
            for moment in (
                key_func(record)
                for record in records
            )
        )),
    )))[:-1]

    ext_values = numpy.interp(
        ext_moments,
        stored_moments,
        stored_values,
    )
    if settings.DEBUG:
        ext_values = tuple(ext_values)

    return ext_moments, ext_values


def _extend_and_interpolate(
        records: List[Dict[str, Any]],  # на самом деле не list, а values-QuerySet
        key_func: Callable[[Dict[str, Any]], Any],
        end_group_func: Callable[[datetime], datetime],
) -> Tuple[List[float], Collection[float]]:
    stored_time_moments_iterator: Iterator[int]
    stored_time_moments_iterator = (
        round(record['localized_when'].timestamp())
        for record in reversed(records)
        if record['sugar_meterings']
    )
    stored_values_iterator = (
        float(metering['sugar_level'])
        for record in reversed(records)
        for metering in record['sugar_meterings']
    )

    stored_time_moments_iterator, stored_values_iterator = _extend_stored_meterings(  # noqa
        stored_time_moments_iterator,
        stored_values_iterator,
        records[len(records) - 1]['when'],
        records[0]['when'],
    )

    stored_moments: Tuple[int, ...]
    stored_moments = tuple(stored_time_moments_iterator)

    stored_values: Tuple[float, ...]
    stored_values = tuple(stored_values_iterator)

    return _interpolate_meterings(
        records,
        stored_moments,
        stored_values,
        key_func,
        end_group_func,
    )


def _get_groupped_sugar_verbose_data(
        records: List[Dict[str, Any]],  # на самом деле не list, а values-QuerySet
        columns: List[Dict[str, str]],
        response_rows: List[Dict[str, Any]],
        key_func: Callable[[Dict[str, Any]], Any],
        groupping: str,
) -> None:
    end_group_func: Callable[[datetime], datetime]
    end_group_func = TIME_LABEL_ENDS[groupping]

    extending_columns: Tuple[Dict[str, str], ...]
    extending_columns = (
        dict(
            data_index='sugar_level',
            header='Средний сахар',
        ),
        dict(
            data_index='max_sugar',
            header='Max',
        ),
        dict(
            data_index='min_sugar',
            header='Min',
        ),
        dict(
            data_index='meterings_count',
            header='Измерений',
        )
    )

    columns.extend(extending_columns)

    new_cells_iterator: Iterator[Tuple[
        Dict[str, Any],  # row
        str,  # data_index
    ]]
    new_cells_iterator = product(
        response_rows,
        map(
            itemgetter('data_index'),
            extending_columns,
        ),
    )
    for row, data_index in new_cells_iterator:
        row[data_index] = '-'

    ext_moments, ext_values = _extend_and_interpolate(
        records,
        key_func,
        end_group_func,
    )

    ext_arrays_length = len(ext_moments)
    assert ext_arrays_length == len(ext_values)

    records_groups_iterator = map(
        itemgetter(1),
        groupby(reversed(records), key_func),
    )
    zipped = zip(
        reversed(response_rows),
        records_groups_iterator,
    )
    ext_start = 0
    for row, records_group in zipped:
        records_group_iterator = (
            record
            for record in records_group
            if record['sugar_meterings']
        )
        try:
            first_record = next(records_group_iterator)
            time_label = first_record['time_label']
            records_group_len = sum(
                (1 for _ in records_group_iterator),
                1,
            )
        except StopIteration:
            continue

        start_period = round(time_label.timestamp())
        stop_period = round(end_group_func(time_label).timestamp())

        while (ext_start < ext_arrays_length
                and ext_moments[ext_start] < start_period):
            ext_start += 1

        ext_stop = ext_start + records_group_len

        assert ext_moments[ext_stop] <= stop_period
        while (ext_stop < ext_arrays_length
                and ext_moments[ext_stop] < stop_period):
            ext_stop += 1

        if ext_stop >= ext_arrays_length:
            stop_period = ext_moments[-1]

        ext_moments_slice = ext_moments[ext_start:ext_stop+1]
        ext_values_slice = ext_values[ext_start:ext_stop+1]

        integrated_value = scipy.integrate.trapz(
            ext_values_slice,
            ext_moments_slice,
        )
        averaged_value = integrated_value / (stop_period - start_period)
        row['sugar_level'] = '{:.2f}'.format(averaged_value)

        ext_values_slice_iterator = iter(ext_values_slice)
        max_value = min_value = next(ext_values_slice_iterator)
        for value in ext_values_slice_iterator:
            if value > max_value:
                max_value = value
            elif value < min_value:
                min_value = value

        def make_verbose(value: float) -> str:
            verbose = '{:.2f}'.format(value)
            if verbose[-1] == '0':
                verbose = verbose[:-1]

            return verbose

        verbose_values = map(
            make_verbose,
            (min_value, max_value),
        )
        row['min_sugar'], row['max_sugar'] = verbose_values

        row['meterings_count'] = records_group_len
        ext_start = ext_stop


class SugarMeteringTuple(NamedTuple):
    when: datetime
    value: Decimal


class ISugarAverager:
    def add_metering(self, metering: SugarMeteringTuple) -> None:
        raise NotImplementedError

    def get_value(self, when: Union[datetime, float], chunk_idx: Optional[int] = None, force: bool = False) -> float:
        raise NotImplementedError

    def get_avg(self, begin: datetime, end: datetime) -> float:
        raise NotImplementedError

    def _prepare(self):
        raise NotImplementedError


class TrapezoidalSugarAverager(ISugarAverager):
    STAMPS_EPSILON = 1e-6

    def __init__(self) -> None:
        self._meterings: List[SugarMeteringTuple] = []
        self._unix_stamps: Optional[Tuple[float, ...]] = None
        self._prepared: bool = True
        self._coeffs: Optional[List[
                Optional[Tuple[
                    float,
                    float,
                ]]
            ]]
        self._coeffs = None

    def add_metering(self, metering: SugarMeteringTuple) -> None:
        self._meterings.append(metering)
        self._prepared = False

    def get_value(self, when: Union[datetime, float], chunk_idx: Optional[int] = None, force: bool = False) -> float:
        self._prepare()

        unix_when: float
        if isinstance(when, datetime):
            unix_when = when.timestamp()
        else:
            unix_when = when

        if chunk_idx is None:
            chunk_idx = self._determine_chunk_idx(unix_when)

        if not force:
            inside_chunk = (
                    0 <= chunk_idx < len(self._coeffs)
                    and self._unix_stamps[chunk_idx]-self.STAMPS_EPSILON <= unix_when <= self._unix_stamps[1+chunk_idx]+self.STAMPS_EPSILON
            ) or (
                chunk_idx == len(self._coeffs)
                and abs(unix_when-self._unix_stamps[-1]) < self.STAMPS_EPSILON
            )
            if not inside_chunk:
                raise ValueError

        chunk_idx = min(chunk_idx, -1+len(self._coeffs))

        offset, factor = self._coeffs[chunk_idx]
        return offset + factor * unix_when

    def get_avg(self, begin: datetime, end: datetime) -> float:
        self._prepare()

        if begin > end:
            begin, end = end, begin
        unix_begin: float = begin.timestamp()
        unix_end: float = end.timestamp()
        begin_chunk = self._determine_chunk_idx(unix_begin)
        end_chunk = self._determine_chunk_idx(unix_end)
        # todo: что если случай вырожден и между begin
        #  и end нет ни одного измерения

        begin_stamp: float = max(
            self._unix_stamps[0],
            unix_begin,
        )

        prev_stamp: float = begin_stamp
        prev_value: float = self.get_value(
            prev_stamp,
            begin_chunk,
        )

        last_stamp: float = min(
            self._unix_stamps[-1],
            unix_end,
        )
        islice_stop = end_chunk
        if end_chunk < len(self._unix_stamps):
            islice_stop += 1
        last_value: float = self.get_value(
            last_stamp,
            end_chunk,
        )

        items_iterator: Iterator[Tuple[float, float]] = (
            (when.timestamp(), float(value))
            for when, value in islice(
                self._meterings,
                1+begin_chunk,
                islice_stop,
            )
        )
        items_iterator = chain(
            items_iterator,
            (
                (last_stamp, last_value),
            ),
        )

        sum_values = 0.0
        for stamp, value in items_iterator:
            sum_values += 0.5 * (stamp-prev_stamp) * (value+prev_value)
            prev_stamp, prev_value = stamp, value

        avg_value = sum_values / (last_stamp-begin_stamp)
        return avg_value

    def _prepare(self) -> None:
        if not self._prepared:
            self._meterings.sort(
                key=attrgetter('when'),
            )
            self._unix_stamps = tuple(
                item.when.timestamp()
                for item in self._meterings
            )
            self._do_prepare()
            self._prepared = True

    def _do_prepare(self) -> None:
        assert not self._prepared
        meterings_pairs_iterator: Iterator[Tuple[
            SugarMeteringTuple,
            SugarMeteringTuple,
        ]]
        meterings_pairs_iterator = zip(
            self._meterings,
            islice(self._meterings, 1, None),
        )
        self._coeffs = list(repeat(
            None,
            times=len(self._meterings) - 1,
        ))
        for idx, (prev_point, curr_point) in enumerate(meterings_pairs_iterator):
            float_curr_point_value: float = float(curr_point.value)
            float_curr_point_when: float = curr_point.when.timestamp()
            factor: float = (float_curr_point_value - float(prev_point.value)) / (float_curr_point_when - prev_point.when.timestamp())
            offset: float = float_curr_point_value - factor*float_curr_point_when
            self._coeffs[idx] = (offset, factor)

    def _determine_chunk_idx(self, unix_when: float) -> int:
        assert self._prepared
        assert self._unix_stamps
        chunk_idx = -1 + bisect_right(
            self._unix_stamps,
            unix_when,
        )
        return chunk_idx


class TrapezoidalScipySugarAverager(ISugarAverager):

    def __init__(self) -> None:
        self._meterings: List[SugarMeteringTuple] = []
        self._prepared: bool = True
        self._coeffs: Dict[int, Tuple[float, float]] = {}
        self._unix_stamps: Optional[List[float]] = None

    def add_metering(self, metering: SugarMeteringTuple) -> None:
        self._meterings.append(metering)
        self._prepared = False

    def get_value(self, when: Union[datetime, float], chunk_idx: Optional[int] = None, force: bool = False) -> float:
        self._prepare()

        unix_when: float
        if isinstance(when, datetime):
            unix_when = when.timestamp()
        else:
            unix_when = when

        if chunk_idx is None:
            chunk_idx = self._determine_chunk_idx(unix_when)

        if not force:
            inside_chunk = (
                0 <= chunk_idx < len(self._coeffs)
                and self._unix_stamps[chunk_idx] - self.STAMPS_EPSILON <= unix_when <= self._unix_stamps[1 + chunk_idx] + self.STAMPS_EPSILON
            ) or (
                chunk_idx == len(self._coeffs)
                and abs(unix_when - self._unix_stamps[-1]) < self.STAMPS_EPSILON
            )
            if not inside_chunk:
                raise ValueError

    def _get_value(self, timestamp: float, chunk_idx: int):
        assert self._prepared
        coeffs = self._coeffs.get(chunk_idx)
        if coeffs is None:
            self._calculate_coeffs(chunk_idx)
            coeffs = self._coeffs[chunk_idx]
        scale, offset = coeffs
        return scale*timestamp + offset

    def _calculate_coeffs(self, chunk_idx: int):
        assert self._prepared
        assert 0 <= chunk_idx < len(self._meterings)-1

        float_curr_value = float(self._meterings[chunk_idx].value)
        curr_timestamp = self._unix_stamps[chunk_idx]
        scale = (float_curr_value - float(self._meterings[chunk_idx+1].value)) / (curr_timestamp - self._unix_stamps[chunk_idx+1])
        offset = float_curr_value - scale*curr_timestamp
        self._coeffs[chunk_idx] = (scale, offset)

    def get_avg(self, begin: datetime, end: datetime) -> float:
        self._prepare()

        if begin > end:
            tmp = begin
            begin = end
            end = tmp

        begin_timestamp: float = begin.timestamp()
        end_timestamp: float = end.timestamp()

        begin_chunk_idx: int = 0
        end_chunk_idx: int = len(self._meterings)-1
        first_interpolated: Optional[Tuple[float, float]] = None
        last_interpolated: Optional[Tuple[float, float]] = None

        if begin_timestamp > self._meterings[0].when.timestamp():
            # todo: use bisect
            begin_chunk_idx = self._determine_chunk_idx(
                begin_timestamp,
            )
            first_interpolated = self.get_value(
                begin_timestamp,
                begin_chunk_idx,
            )

            # first_interpolated = (
            #     begin_timestamp,
            #     numpy.interp(
            #         begin_timestamp,
            #         (
            #             self._meterings[begin_chunk_idx-1].when.timestamp(),
            #             self._meterings[begin_chunk_idx].when.timestamp(),
            #         ),
            #         (
            #             float(self._meterings[begin_chunk_idx-1].value),
            #             float(self._meterings[begin_chunk_idx].value),
            #         ),
            #     )
            # )

        if end_timestamp < self._meterings[-1].when.timestamp():
            # todo: use bisect
            end_chunk_idx = next(
                idx
                for idx, (when, value) in enumerate(self._meterings)
                if when.timestamp() >= end_timestamp
            )
            last_interpolated = (
                end_timestamp,
                numpy.interp(
                    end_timestamp,
                    (
                        self._meterings[end_chunk_idx-1].when.timestamp(),
                        self._meterings[end_chunk_idx].when.timestamp(),
                    ),
                    (
                        float(self._meterings[end_chunk_idx-1].value),
                        float(self._meterings[end_chunk_idx].value),
                    ),
                )
            )

        pairs_iterator: Iterator[Tuple[float, float]]
        pairs_iterator = filter(None, chain(
            (
                first_interpolated,
            ),
            (
                (when.timestamp(), float(value))
                for when, value in islice(
                    self._meterings,
                    begin_chunk_idx,
                    1+end_chunk_idx,
                )
            ),
            (
                last_interpolated,
            ),
        ))

        args, values = zip(*pairs_iterator)

        return scipy.integrate.trapz(values, args) / (args[-1] - args[0])

    def _prepare(self) -> None:
        if not self._prepared:
            self._meterings.sort(
                key=attrgetter('when'),
            )
            self._unix_stamps = [
                metering.when.timestamp()
                for metering in self._meterings
            ]
            self._coeffs.clear()
            self._prepared = True

    def _determine_chunk_idx(self, unix_when: float) -> int:
        assert self._prepared
        assert self._unix_stamps
        chunk_idx = -1 + bisect_right(
            self._unix_stamps,
            unix_when,
        )
        return chunk_idx
