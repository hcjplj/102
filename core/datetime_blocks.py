"""날짜/시간 블록 계산: 형식 변환, 더하기/빼기, 영업일(주말+휴일) 계산."""
import calendar
import re
from datetime import date, datetime, timedelta

WEEKDAYS = "월화수목금토일"  # datetime.weekday() 0=월
WEEKDAYS_LONG = [d + "요일" for d in WEEKDAYS]

_TOKEN = re.compile(r"yyyy|yy|MM|M|dd|d|HH|H|hh|h|mm|m|ss|s|EEEE|E|a")


class DateError(Exception):
    pass


def format_dt(dt, fmt):
    """엑셀 방식 형식(yyyy, yy, MM, M, dd, d, HH, H, hh, h, mm, m, ss, s, E, EEEE, a)으로 변환."""
    h12 = dt.hour % 12 or 12

    def sub(m):
        t = m.group(0)
        return {
            "yyyy": f"{dt.year:04d}", "yy": f"{dt.year % 100:02d}",
            "MM": f"{dt.month:02d}", "M": str(dt.month),
            "dd": f"{dt.day:02d}", "d": str(dt.day),
            "HH": f"{dt.hour:02d}", "H": str(dt.hour),
            "hh": f"{h12:02d}", "h": str(h12),
            "mm": f"{dt.minute:02d}", "m": str(dt.minute),
            "ss": f"{dt.second:02d}", "s": str(dt.second),
            "E": WEEKDAYS[dt.weekday()], "EEEE": WEEKDAYS_LONG[dt.weekday()],
            "a": "오전" if dt.hour < 12 else "오후",
        }[t]

    return _TOKEN.sub(sub, fmt)


def add_months(dt, n):
    y, m = divmod(dt.year * 12 + dt.month - 1 + n, 12)
    m += 1
    return dt.replace(year=y, month=m, day=min(dt.day, calendar.monthrange(y, m)[1]))


def add_years(dt, n):
    return add_months(dt, 12 * n)


# ---- 휴일 설정 ----
class Holidays:
    def __init__(self, sat_off=True, sun_off=True, dates=None):
        self.sat_off, self.sun_off, self.dates = sat_off, sun_off, dates or set()

    def is_business(self, d):
        wd = d.weekday()
        if (wd == 5 and self.sat_off) or (wd == 6 and self.sun_off):
            return False
        return d.date() not in self.dates if isinstance(d, datetime) else d not in self.dates


def parse_date(text):
    """2026-01-01, 2026.1.1, 2026/01/01, 20260101, 260101, 26-01-01 등을 date 로."""
    s = text.strip()
    m = re.fullmatch(r"(\d{2}|\d{4})[-./](\d{1,2})[-./](\d{1,2})", s)
    if m:
        y, mo, d = int(m[1]), int(m[2]), int(m[3])
        y += 2000 if len(m[1]) == 2 else 0
    elif re.fullmatch(r"\d{8}", s):
        y, mo, d = int(s[:4]), int(s[4:6]), int(s[6:])
    elif re.fullmatch(r"\d{6}", s):
        y, mo, d = 2000 + int(s[:2]), int(s[2:4]), int(s[4:])
    else:
        raise ValueError(s)
    return date(y, mo, d)  # 없는 날짜면 ValueError


def parse_holidays(text):
    """여러 줄/쉼표로 적은 휴일. 범위는 '시작~끝'. 반환: date 집합."""
    result = set()
    for no, line in enumerate((text or "").splitlines(), 1):
        for item in re.split(r"[,;]", line):
            item = item.strip()
            if not item or item.startswith("#"):
                continue
            try:
                if "~" in item:
                    a, b = (parse_date(p) for p in item.split("~", 1))
                    if b < a or (b - a).days > 3660:
                        raise ValueError(item)
                    result.update(a + timedelta(days=i) for i in range((b - a).days + 1))
                else:
                    result.add(parse_date(item))
            except ValueError:
                raise DateError(f"휴일 설정 {no}번째 줄을 읽을 수 없습니다: '{item}' (예: 2026-01-01 또는 2026-02-16~2026-02-18)")
    return result


def add_business_days(dt, n, hol):
    step = 1 if n > 0 else -1
    left = abs(n)
    while left:
        dt += timedelta(days=step)
        if hol.is_business(dt):
            left -= 1
    return dt


# ---- 블록 계산 ----
def _fmt_of(fields, default):
    fmt = fields.get("CUSTOM") if fields.get("FMT") == "custom" else fields.get("FMT")
    return fmt or default


def _signed(fields):
    """SIGN(+/-)과 OFFSET 으로 부호 있는 정수를 만든다. (SIGN 이 없는 예전 저장 파일은 OFFSET 의 부호를 그대로 사용)"""
    try:
        n = int(float(fields.get("OFFSET", 0)))
    except (TypeError, ValueError):
        n = 0
    return -n if fields.get("SIGN") == "-" else n


def _apply_date(dt, n, unit, hol):
    if unit == "day":
        return dt + timedelta(days=n)
    if unit == "week":
        return dt + timedelta(weeks=n)
    if unit == "month":
        return add_months(dt, n)
    if unit == "year":
        return add_years(dt, n)
    if unit == "bday":
        return add_business_days(dt, n, hol)
    return dt


def _apply_time(dt, n, unit):
    return dt + {"hour": timedelta(hours=n), "minute": timedelta(minutes=n), "second": timedelta(seconds=n)}.get(unit, timedelta())


def eval_date(fields, hol, now=None, chain=()):
    """fields: 날짜 블록 값. chain: 가로로 이어 붙인 조정 블록들의 fields (왼쪽부터 차례로 적용)."""
    dt = now or datetime.now()
    for f in (fields, *chain):
        dt = _apply_date(dt, _signed(f), f.get("UNIT", "day"), hol)
    return format_dt(dt, _fmt_of(fields, "yyyy-MM-dd"))


def eval_time(fields, now=None, chain=()):
    dt = now or datetime.now()
    for f in (fields, *chain):
        dt = _apply_time(dt, _signed(f), f.get("UNIT", "hour"))
    return format_dt(dt, _fmt_of(fields, "HH:mm"))


def is_business_day(fields, hol, now=None, chain=()):
    """오늘(+조정)이 영업일(토/일/휴일이 아님)인지."""
    dt = now or datetime.now()
    for f in (fields, *chain):
        dt = _apply_date(dt, _signed(f), f.get("UNIT", "day"), hol)
    return hol.is_business(dt)
