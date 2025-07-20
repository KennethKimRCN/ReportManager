def compare_project_updates(current_report):
    from app.models import ProjectUpdate, Report
    from app.utils.date_utils import get_previous_week_range
    diffs = {}

    prev_start, _ = get_previous_week_range(current_report.week_start)
    prev_report = Report.query.filter_by(user_id=current_report.user_id, week_start=prev_start).first()

    if not prev_report:
        return diffs

    for update in current_report.project_updates:
        prev_update = next((u for u in prev_report.project_updates if u.project_id == update.project_id), None)
        if not prev_update:
            continue

        changes = {}
        for field in ['progress', 'issue', 'sales_support', 'other_note']:
            curr_val = getattr(update, field) or ""
            prev_val = getattr(prev_update, field) or ""
            if curr_val.strip() != prev_val.strip():
                changes[field] = {
                    'before': prev_val.strip(),
                    'after': curr_val.strip()
                }

        if changes:
            diffs[update.project_id] = changes

    return diffs
