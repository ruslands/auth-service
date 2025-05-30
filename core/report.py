import datetime
import io
import uuid
from decimal import Decimal
from typing import Any, List

import xlsxwriter
from pydantic import parse_obj_as

from core.base.crud import ModelType
from core.sdui import ColumnAnnotation
from core.settings import settings


class Report:
    EXCLUDE_FIELD = {
        "product": [],
        "card": [],
    }
    content_disposition = 'attachment; filename="{file_name}"'
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    start_write_data = 0
    formats = {}

    def __init__(
        self,
        data: List[ModelType],
        table_mapping: List[ColumnAnnotation],
        type_report: str,
        s3_client=None,
        schema=None,
        scope=None,
        title=True,
    ):
        self.scope = scope
        self.data = parse_obj_as(List[schema], data)
        if scope is None:
            self.table_mapping = {x.key_name: x.column_name for x in table_mapping if x.show_in_table}
        else:
            self.table_mapping = {
                x.key_name: x.column_name for x in table_mapping if x.show_in_table and x.key_name in self.scope
            }
        self.s3_client = s3_client
        self.type_report = type_report
        self.title = title

    async def generate_report(self, save_to_s3=False) -> dict | str:
        """Generate report and depending on the save_to_s3 parameter,
        either return the report or save it to S3.

        Args:
            save_to_s3 (bool): Save to s3
        Returns:
            dict | str: Report if save_to_s3 is False else S3 key
        """

        output = io.BytesIO()
        self.workbook = xlsxwriter.Workbook(output, {"remove_timezone": True, "in_memory": True})
        self.worksheet_main = self.workbook.add_worksheet(self.type_report)
        if self.title:
            self._set_worksheet_title(worksheet=self.worksheet_main, type_report=self.type_report)
        await self._write_header()
        await self._write_data()
        self.workbook.close()

        if save_to_s3:
            key = await self.__putfile(output.getvalue())
            return key

        output.name = self._get_report_name()
        return {
            "content": output.getvalue(),
            "headers": {"Content-Disposition": self.content_disposition.format(file_name=output.name)},
            "media_type": self.media_type,
        }

    async def __putfile(self, file) -> str:
        filename = self._get_report_name()
        key = f"reports/{filename}"

        await self.s3_client.put_file(
            bucket=settings.BUCKET,
            file=file,
            filename=filename,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=key,
        )
        return key

    async def _write_header(self):
        style = {
            "bold": True,
            "font_size": 12,
        }
        for idx_col, col in enumerate(self.table_mapping):
            await self.write_value(
                self.start_write_data, idx_col, self.table_mapping[col], self.workbook, self.worksheet_main, style=style
            )
            self.worksheet_main.set_column(idx_col, idx_col, len(self.table_mapping[col]) + 7)
        self.worksheet_main.set_row(self.start_write_data, 35)
        self.start_write_data += 1

    async def _write_data(self):
        for idx_row, row in enumerate(self.data):
            for idx_col, col in enumerate(self.table_mapping):
                value = getattr(row, col)
                if isinstance(value, dict):
                    value = value.get("value")
                await self.write_value(
                    idx_row + self.start_write_data, idx_col, value, self.workbook, self.worksheet_main
                )
                if value is not None:
                    self.worksheet_main.set_column(
                        idx_col,
                        idx_col,
                        len(str(getattr(row, col))) + 7,
                        # magic number вычесленно империчиским путем
                        # На сколько нужно увеличить ширину столбца в зависимости от содержимого
                        # Размер шрифта влияет тоже.
                        # Метод для подгона ширины столбца под содержимое, отсутсвует
                    )

    @classmethod
    async def write_value(cls, row: int, offset: int, value: Any, workbook, worksheet, style=None):
        """Запись значения в ячейку."""
        row_style = style or {}

        cell_value = value
        if isinstance(value, list):
            if len(value) > 1:
                cell_value = "– " + ("\n– ".join(cls._joinable(value)))
            else:
                cell_value = value[0] if value else ""
        elif isinstance(value, uuid.UUID):
            cell_value = str(value)

        if isinstance(cell_value, datetime.datetime):
            row_style["num_format"] = "dd.mm.yyyy hh:mm"
        elif isinstance(cell_value, datetime.date):
            row_style["num_format"] = "dd.mm.yyyy"
        elif isinstance(cell_value, datetime.time):
            row_style["num_format"] = "hh:mm"
        elif isinstance(cell_value, int) or (isinstance(cell_value, str) and cell_value.isdigit()):
            if len(str(cell_value)) >= 11:
                # Large numbers, treat as text to avoid scientific notation
                cell_value = str(cell_value)
                row_style["num_format"] = "@"
            else:
                # Smaller numbers, treat as integers
                cell_value = int(cell_value)
                row_style["num_format"] = "0"
        elif isinstance(cell_value, Decimal):
            row_style["num_format"] = "#,##0.00"
            if float(cell_value) == int(cell_value):
                row_style["num_format"] = "0"
                cell_value = int(cell_value)
        elif cell_value is None:
            cell_value = ""
        else:
            row_style["num_format"] = "0"
        if cell_value and isinstance(cell_value, str):
            row_style["num_format"] = "@"
            cell_value = cell_value[1:] if cell_value[0] == "=" else cell_value

        worksheet.write(row, offset, cell_value, cls._get_or_create_style(workbook, row_style))

    @classmethod
    def _joinable(cls, arr):
        result = []
        for item in arr:
            val = item
            if isinstance(item, Decimal):
                val = round(item, 2)
            val = str(val)
            result.append(val)
        return result

    @classmethod
    def _get_or_create_style(cls, workbook, attributes=None):
        attributes = attributes or {}
        """Работа со стилями для отчета."""
        default_format = {
            "num_format": "@",
            "align": "center",
            "valign": "vcenter",
            "border": 4,
            "text_wrap": True,
        }
        format_attibutes = {**default_format, **attributes}
        if "background" in format_attibutes:
            background_colors = {
                "@answer_odd": "#f2f4ff",
                "@answer_even": "#f7fff7",
                "@unit": "#fffde1",
                "@default_even": "#efefee",
            }
            if format_attibutes["background"] in background_colors:
                format_attibutes["bg_color"] = background_colors[format_attibutes["background"]]
            del format_attibutes["background"]

        return workbook.add_format(format_attibutes)

    def _set_worksheet_title(self, worksheet, type_report):
        self.start_write_data = 2
        worksheet.merge_range(
            "A1:BA2",
            "            %s" % type_report.capitalize(),
            self._get_or_create_style(
                self.workbook,
                attributes={
                    "bold": True,
                    "align": "left",
                    "valign": "vcenter",
                    "font_size": 16,
                },
            ),
        )

    def _get_report_name(self):
        """Генерация имени."""
        datetime_now = datetime.datetime.now().date()
        file_name = f"{self.type_report}_{datetime_now}.xlsx"

        return file_name
