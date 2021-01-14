from collections import namedtuple
from datetime import date
from enum import IntFlag
from itertools import chain

from PIL.Image import new, Image
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
from dateutil.relativedelta import relativedelta
from more_itertools import chunked

REFERENCE_DATE = date(2020, 2, 29)  # day zero
SizedFont = namedtuple("SizedFont", ("regular", "bold"))


def reference(day: date) -> int:
    """ Converts a day to a dom (day-of-march). """
    return (day - REFERENCE_DATE).days


class MonthCalendar:
    def __init__(self, month: date, *circled_days: date):
        self.first_day = first_day = date(month.year, month.month, 1)
        self.first_week_indent = (first_day.weekday() + 1) % 7
        first_dom = reference(first_day)
        last_dom = reference(first_day + relativedelta(months=1))
        self.range = range(first_dom, last_dom)
        self.circled_doms = frozenset(reference(d) for d in circled_days)

    def __repr__(self):
        return f"<MonthCalendar: {str(self.first_day)}, {self.range.start}-{self.range.stop}>"

    def __iter__(self):
        """ Yields rows of cells of tuples(text,format). """
        week_fmt = (CellFmt.color, CellFmt.none, CellFmt.none, CellFmt.none, CellFmt.none, CellFmt.none, CellFmt.color)
        names = "Sun Mon Tue Wed Thu Fri Sat".split()
        yield [(n, f | CellFmt.bold) for n, f in zip(names, week_fmt)]
        days = chain(["" for _ in range(self.first_week_indent)], self.range)
        for week_text in chunked(days, 7):
            row = [
                (t, f | (CellFmt.circled if t in self.circled_doms else CellFmt.none))
                for t, f in zip(week_text, week_fmt)
            ]
            yield row


class Font:
    _regular = "roboto/roboto4regular.ttf"
    _bold = "roboto/roboto7bold.ttf"
    _small = 20
    _large = 50
    small = SizedFont(truetype(_regular, _small), truetype(_bold, _small))
    large = SizedFont(truetype(_regular, _large), truetype(_bold, _large))


class Color:
    background = (128, 255, 128)
    title = (128, 0, 128)
    workday = (0, 0, 0)
    holiday = (128, 0, 0)
    circle = (64, 64, 255)


def draw_calendars(day: date) -> Image:
    image = new("RGB", (1200, 675), color=Color.background)
    draw = Draw(image)
    draw_calendar(draw, "March 2020", MonthCalendar(day, day), Font.large, 21.0, 70.0, 140.0)
    last_month = MonthCalendar(day + relativedelta(months=-1))
    draw_calendar(draw, "Previous March 2020", last_month, Font.small, 10.5, 830.0, 75.0)
    next_month = MonthCalendar(day + relativedelta(months=1))
    draw_calendar(draw, "Next March 2020", next_month, Font.small, 10.5, 830.0, 410.0)
    return image


def draw_calendar(draw: Draw, title: str, calendar: MonthCalendar, font: SizedFont, f: float, ox: float, oy: float):
    """
    :param draw: pillow's drawing object
    :param title: calendar title
    :param calendar: iterable objects that returns 7-wide rows of (text,format) pairs
    :param font: tuple with regular and bold font
    :param f: factor to multiply all positions
    :param ox: horizontal offset
    :param oy: vertical offset
    """
    dx, dy = 5.0 * f, 4.0 * f
    draw.text((3 * dx + ox, oy - dy), title, font=font.bold, fill=Color.title, anchor="ms")
    for y, row in enumerate(calendar):
        for x, (text, fmt) in enumerate(row):
            if CellFmt.circled in fmt:
                ex, ey = (x * dx + ox, y * dy + oy)
                draw.ellipse(
                    (ex - f * 3, ey - f * 2.5, ex + f * 3, ey + f),
                    outline=Color.circle,
                    width=int(round(f * 0.3)),
                )
            draw.text(
                (x * dx + ox, y * dy + oy),
                str(text),
                font=font.bold if CellFmt.bold in fmt else font.regular,
                fill=Color.holiday if CellFmt.color in fmt else Color.workday,
                anchor="ms",
            )


class CellFmt(IntFlag):
    none = 0
    bold = 1
    color = 2
    circled = 4
