from heman.erpdb_manager import get_timescale_connection


class TimescaleCurveBackend:
    def __init__(self):
        self.db_connection = get_timescale_connection()

    def build_query(
        self,
        start=None,
        end=None,
        cups=None,
        **extra_filter
    ):

        result = []
        with self.db_connection as connection:
            cursor = connection.cursor()
            if cups:
                result += [cursor.mogrify("name ILIKE %s", [cups[:20] + "%"])]
            if start:
                result += [cursor.mogrify("utc_timestamp >= %s", [start])]
            if end:
                result += [cursor.mogrify("utc_timestamp <= %s", [end])]
            for key, value in extra_filter.items():
                result += [cursor.mogrify("{key} = %s".format(key=key), [value])]
        return result

    def get_curve(self, curve_type, start, end, cups=None):
        query = self.build_query(start, end, cups, **curve_type.extra_filter)
        if query:
            where_clause = "WHERE {}".format(" AND ".join(query))
        else:
            where_clause = ""

        with self.db_connection as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * from {model}
                {where_clause}
                ORDER BY utc_timestamp
                ;
            """.format(
                model=curve_type.model,
                where_clause=where_clause,
            ))
            return cursor.fetchall()
