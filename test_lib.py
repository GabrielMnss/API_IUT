import pandas as pd

from SQL_connect import connection, cursor


def get_test_lib():
    try:
        if connection.is_connected():
            columns = []

            cursor.execute("SELECT * FROM geii_quizz_information")
            for column in cursor.description:
                columns.append(column[0])

            result = pd.DataFrame(cursor.fetchall(), columns=columns)
            return result.to_json(orient="records")
        return None
    except ValueError:
        return None
