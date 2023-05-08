import pytz
from time import mktime

tz = pytz.timezone('Europe/Madrid')

def to_local(datetime, is_dst):
    #assertNaive(datetime)
    return tz.localize(datetime, is_dst=is_dst)

def as_naive(datetime):
    return datetime.replace(tzinfo=None)

def utc_timestamp_ms(datetime):
    #assertNotNaive(datetime)
    return mktime(datetime.timetuple()) * 1000

