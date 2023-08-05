from collections import namedtuple

from gpstime import gpstime, GPSTimeException

from . import const


def gpstime_parse(time):
    if time is None:
        return None
    try:
        return gpstime.parse(time)
    except GPSTimeException:
        return None
    except ValueError:
        return None


def gpstime_str_gps(gt):
    if gt:
        return str(gt.gps())


def gpstime_str_greg(gt, fmt=const.DATETIME_FMT_OFFLINE):
    if gt is None:
        return
    return gt.astimezone(const.DATETIME_TZ).strftime(fmt)



TDUnits = namedtuple('TUnits', [t[0] for t in const.TD_UNIT_MAP])


class TDStr:
    """class for formatting seconds into a natural language time delta string

    """
    def __init__(self, seconds):
        self.total_seconds = seconds
        if seconds < 0:
            self.prefix = '-'
        else:
            self.prefix = ''
        seconds, subsec = divmod(abs(seconds), 1)
        seconds = int(seconds)
        nsecs = int(subsec * 1e9)
        usecs, nsecs = divmod(nsecs, 1000)
        msecs, usecs = divmod(usecs, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        years, days = divmod(days, 365)
        weeks, days = divmod(days, 7)
        self.td = TDUnits(
            years,
            weeks,
            days,
            hours,
            minutes,
            seconds,
            msecs,
            usecs,
            nsecs,
        )

    def __getitem__(self, item):
        return getattr(self.td, item)

    def __repr__(self):
        """format object string"""
        ofl = []
        for u in self.td._fields:
            ofl.append('{}={}'.format(u, self[u]))
        return '{}({}{})'.format(
            self.__class__.__name__,
            self.prefix,
            ', '.join(ofl),
        )

    def _fmt_list(self, fl):
        fmt = ' '.join(fl)
        return self.prefix + fmt.format(td=self.td)

    def __str__(self):
        """format duration into simplest string representation"""
        if self.total_seconds == 0:
            return '0'
        ofl = [f for u,s,f in const.TD_UNIT_MAP if self[u] != 0]
        return self._fmt_list(ofl)


def cells_to_tabspec(cells):
    """for a set of occupied cells, return a tabspec dict

    tabspec is keyed by [row, col, rowspan, colspan]

    """
    rows = [x[0] for x in cells]
    cols = [x[1] for x in cells]
    row = min(rows)
    col = min(cols)
    rowspan = len(set(rows))
    colspan = len(set(cols))
    return dict(
        row=row, col=col,
        rowspan=rowspan, colspan=colspan,
    )
