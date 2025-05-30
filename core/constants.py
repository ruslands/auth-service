VISIBILITY_GROUP_ENTITY_SETTINGS = {
    "admin": "admin",
    "owner": "owner",
    "user": "user",
    "parent": "parent",
    "child": "child",
    "orphan": "orphan",
}
AMOUNT_OF_SESSIONS_PER_USER = 4
NO_IMAGE_STUB = "no_photo.png"
ALLOWED_METHODS = ["get", "post", "patch", "delete"]
DEFAULT_COLOR = "#AAAAAA"
DA_NET_ABSENT = {True: "Да", False: "Нет", None: "Значение отсутствует"}


class EmptyValue(str):
    def __bool__(self):
        return False


EMPTY_VALUE = EmptyValue("---")
