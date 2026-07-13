"""توابع کمکی برای نمایش نمودار گانت در کنسول.

این ماژول یک نمایش فشرده و متنی از وظایف زمان‌بندی‌شده ارائه می‌دهد
که زمان شروع، زمان پایان و یک نوار نمایانگر مدت اجرای هر وظیفه را نشان می‌دهد.
"""

from __future__ import annotations

from scheduler.task_scheduler import ScheduleEvent


def render_gantt_chart(events: list[ScheduleEvent]) -> str:
    """تولید یک نمودار گانت متنی برای وظایف زمان‌بندی‌شده.

    Args:
        events (list[ScheduleEvent]): لیست رویدادهای زمان‌بندی به ترتیب اجرا.

    Returns:
        str: رشته‌ای چندخطی شامل نمایش ASCII هر وظیفه همراه با
        زمان شروع و پایان آن.
    """

    if not events:
        return "هیچ وظیفه‌ای زمان‌بندی نشد."

    # پیدا کردن طول بلندترین شناسه برای تراز شدن خروجی
    max_id_length = max(len(event.task.task_id) for event in events)

    lines = ["نمودار گانت:"]

    for event in events:
        # هر # نمایانگر یک واحد زمان از مدت اجرای وظیفه است
        bar = "#" * max(1, event.task.duration)

        # هم‌تراز کردن نام وظایف در خروجی
        task_name = event.task.task_id.ljust(max_id_length)

        lines.append(
            f"{task_name} | {bar}  {event.start} -> {event.finish}"
        )

    return "\n".join(lines)
