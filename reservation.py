from config import (
    TWO_PERSON_TABLES,
    FOUR_PERSON_TABLES,
)

from database import is_table_reserved


def get_available_tables(session_number, guests):
    if guests <= 2:
        tables = TWO_PERSON_TABLES
    elif guests <= 4:
        tables = FOUR_PERSON_TABLES
    else:
        return []

    available = []

    for table_number in tables:
        if not is_table_reserved(
            session_number,
            table_number
        ):
            available.append(table_number)

    return available
