from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timedelta

from django.db import transaction

from .models import ScheduleRule, TaskOccurrence


def _as_date(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        return date.fromisoformat(value)
    return value


def _normalise_weekdays(rule: ScheduleRule) -> list[int]:
    weekdays = rule.weekdays or [6, 7]
    return sorted({int(day) for day in weekdays})


def _weekly_dates(rule: ScheduleRule, start_date: date, end_date: date) -> list[date]:
    weekdays = _normalise_weekdays(rule)
    if not weekdays:
        return []

    rule_starts_on = _as_date(rule.starts_on)
    rule_ends_on = _as_date(rule.ends_on)

    week_start = start_date - timedelta(days=start_date.isoweekday() - 1)
    cursor = max(week_start, rule_starts_on)
    result: list[date] = []

    while cursor <= end_date:
        for weekday in weekdays:
            candidate = cursor + timedelta(days=weekday - 1)
            if start_date <= candidate <= end_date:
                if candidate < rule_starts_on:
                    continue
                if rule_ends_on and candidate > rule_ends_on:
                    continue
                result.append(candidate)
        cursor += timedelta(days=7)

    return sorted(set(result))


def _biweekly_dates(rule: ScheduleRule, start_date: date, end_date: date) -> list[date]:
    anchor_date = _as_date(rule.anchor_date) or _as_date(rule.starts_on)
    weekdays = _normalise_weekdays(rule)
    if not weekdays:
        return []

    rule_starts_on = _as_date(rule.starts_on)
    rule_ends_on = _as_date(rule.ends_on)

    result: list[date] = []
    cycle_index = 0
    while True:
        base = anchor_date + timedelta(days=cycle_index * 14)
        for weekday in weekdays:
            delta = (weekday - anchor_date.isoweekday()) % 7
            candidate = base + timedelta(days=delta)
            if candidate < start_date:
                continue
            if candidate > end_date:
                return sorted(set(result))
            if candidate < rule_starts_on:
                continue
            if rule_ends_on and candidate > rule_ends_on:
                continue
            result.append(candidate)
        cycle_index += 1


def _monthly_dates(rule: ScheduleRule, start_date: date, end_date: date) -> list[date]:
    weekdays = _normalise_weekdays(rule)
    if not weekdays:
        return []

    rule_starts_on = _as_date(rule.starts_on)
    rule_ends_on = _as_date(rule.ends_on)

    result: list[date] = []
    current = date(start_date.year, start_date.month, 1)
    final_month = date(end_date.year, end_date.month, 1)

    while current <= final_month:
        month_days = monthrange(current.year, current.month)[1]
        for day_number in range(1, month_days + 1):
            candidate = date(current.year, current.month, day_number)
            if candidate.isoweekday() not in weekdays:
                continue
            if candidate < start_date or candidate > end_date:
                continue
            if candidate < rule_starts_on:
                continue
            if rule_ends_on and candidate > rule_ends_on:
                continue
            result.append(candidate)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    return sorted(set(result))


def generate_occurrences(rule: ScheduleRule, start_date: date, end_date: date) -> dict[str, int]:
    if not rule.is_active:
        return {"created": 0, "existing": 0, "ignored": 0}

    if start_date > end_date:
        return {"created": 0, "existing": 0, "ignored": 0}

    if rule.frequency == ScheduleRule.Frequency.WEEKLY:
        candidates = _weekly_dates(rule, start_date, end_date)
    elif rule.frequency == ScheduleRule.Frequency.BIWEEKLY:
        candidates = _biweekly_dates(rule, start_date, end_date)
    elif rule.frequency == ScheduleRule.Frequency.MONTHLY:
        candidates = _monthly_dates(rule, start_date, end_date)
    else:
        return {"created": 0, "existing": 0, "ignored": 0}

    created = 0
    existing = 0
    ignored = 0

    with transaction.atomic():
        for candidate in candidates:
            occurrence, was_created = TaskOccurrence.objects.get_or_create(
                task=rule.task,
                scheduled_date=candidate,
                defaults={
                    "schedule_rule": rule,
                    "status": TaskOccurrence.Status.OPEN,
                },
            )
            if was_created:
                created += 1
            else:
                existing += 1

            if occurrence.schedule_rule_id is None:
                occurrence.schedule_rule = rule
                occurrence.save(update_fields=["schedule_rule"])

    return {
        "created": created,
        "existing": existing,
        "ignored": ignored,
    }


__all__ = ["generate_occurrences"]
