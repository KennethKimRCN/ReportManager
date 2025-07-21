from datetime import date, timedelta


def get_current_week_range(today=None):
    today = today or date.today()
    start = today - timedelta(days=today.weekday() + 1) if today.weekday() != 6 else today
    end = start + timedelta(days=6)
    return start, end


def get_week_label(week_start):
    year = str(week_start.year)[2:]
    week_num = week_start.isocalendar().week
    return f"Y{year}W{week_num:02d}"


def get_previous_week_range(current_start):
    prev_start = current_start - timedelta(days=7)
    return get_current_week_range(prev_start)

from datetime import date, timedelta

def get_sunday_of_current_week():
    today = date.today()
    return today - timedelta(days=today.weekday() + 1 if today.weekday() < 6 else 0)
