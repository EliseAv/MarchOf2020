from datetime import date
import tempfile
import calendarer

WEEKDAY = tuple("Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split())
ORDINALS = {u + d % 100: s for u, s in ((1, "st"), (2, "nd"), (3, "rd")) for d in range(20, 110, 10)}


def build_tweet(today: date):
    days = calendarer.reference(today)
    ordinal = str(days) + ORDINALS.get(abs(days) % 100, "th")
    weekday = WEEKDAY[today.weekday()]
    message = f"Today is {weekday} the {ordinal} of March, 2020."
    with calendarer.draw_calendars(today) as image:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as file:
            image.save(file, "PNG")
    print(message)


# Shift+F10 to execute. Ctrl+F8 to toggle the breakpoint.
if __name__ == "__main__":
    build_tweet(date.today())
    build_tweet(date(2021, 2, 28))
    build_tweet(date(2020, 12, 1))
