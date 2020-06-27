class BaseEnumerate:
    """
    Базовый класс перечислений.

    Предоставляет более удобный интерфейс для
    взаимодействия с джанговскими моделями и
    формами.
    """
    values = {}

    @classmethod
    def get_choices(cls):
        """
        Используется для ограничения полей ORM и
        в качестве источника данных в ChoiceField
        """
        return tuple(cls.values.items())
