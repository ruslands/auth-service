# server driven user interface
from typing import Optional


class ColumnAnnotation:
    def __init__(
        self,
        column_name: str,
        key_name: str,
        column_type: str = "text",
        default_visibility: bool = True,  # видимость в таблице по умолчанию
        is_editable: bool = False,  # редактирование текста
        is_filterable: bool = False,  # числовая фильтрация (больше, меньше, равно)
        is_sortable: bool = False,  # сортировка
        is_searchable: bool = False,  # поиск
        is_multiselect: bool = False,  # множественный выбор при фильтрации и редактировании
        show_in_table: bool = True,
        show_in_page: bool = True,
        order: int = 0,
        group: str = None,
        available_values: dict = None,  # показывает доступные значения для фильтрации и редактирования
        filter_by: Optional[str] = None,
        update_by: Optional[str] = None,
        group_url: Optional[dict] = None,
    ):
        """ColumnAnnotation is class to generate frontend table mapping

        Attributes:
            key_name: Name of model field
            column_name: Human-readable field name in russian
            column_type: The data format of the field used can have four values: 'text', 'image', 'datetime', 'url'.
            default_visibility: The field that configures whether it is available in the standard table form
            is_filterable:  Is the field available for filtering
            is_editable:  Is the field available for editing in table
            is_multiselect: Can the field have multiple values
            show_in_table: ...
            show_in_page: ...
            order: The order of fields in the table
            available_values: All available values for select field
            filter_by: The field by which the filter is applied
            update_by: The field by which the update is applied
        """
        self.column_name = column_name
        self.key_name = key_name
        self.column_type = column_type
        self.default_visibility = default_visibility
        self.is_editable = is_editable
        self.is_filterable = is_filterable
        self.is_sortable = is_sortable
        self.is_multiselect = is_multiselect
        self.is_searchable = is_searchable
        self.show_in_table = show_in_table
        self.show_in_page = show_in_page
        self.order = order
        self.group = group
        self.filter_by = filter_by or key_name
        self.update_by = update_by or key_name
        self.group_url = group_url
        if available_values is not None:
            self.available_values = available_values
        if self.column_type not in [
            "text",
            "image",
            "datetime",
            "url",
            "integer",
            "chart",
            "qr_code",
            "enum",
            "boolean",
            "tag",
            "array",
        ]:
            raise Exception("wrong column_type")
        if not isinstance(self.default_visibility, bool):
            raise Exception("default_visibility must be a boolean")
        if not isinstance(self.is_editable, bool):
            raise Exception("is_editable must be a boolean")

    def __str__(self):
        return self.key_name

    def __repr__(self):
        return self.key_name

    @classmethod
    def get_key_for_value(cls, value):  # todo не используется?
        for x in cls:
            if x.value == value:
                return x.name
        else:
            return value
