from heman.erpdb_manager import get_timescale_connection

from somutils.dbutils import fetchNs
from somutils.isodates import toLocal, asUtc

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


        def from_naive_localdate_to_naiveutc_datetime(naive_localdate):
            return asUtc(toLocal(naive_localdate)).replace(tzinfo=None)
            #return naive_localdate

        result = []
        with self.db_connection as connection:
            cursor = connection.cursor()
            if cups:
                result += [cursor.mogrify("name ILIKE %s", [cups[:20] + "%"])]
            if start:
                result += [cursor.mogrify("utc_timestamp >= %s", [from_naive_localdate_to_naiveutc_datetime(start)])]
            if end:
                result += [cursor.mogrify("utc_timestamp < %s", [from_naive_localdate_to_naiveutc_datetime(end)])]
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
            return fetchNs(cursor)
