"""ابزارهای گزارش‌گیری برای نمایش در کنسول.

این ماژول یک گزارش سیستمی متنی و یک قالب‌بند جدول کوچک برای وظایف بارگذاری شده
ارائه می‌دهد. این توابع کمکی عمداً ساده طراحی شده‌اند تا به راحتی در خروجی
دموی اصلی (Main Demo) گنجانده شوند.
"""

from __future__ import annotations

from models.task import Task
from scheduler.task_scheduler import ScheduleResult


def build_system_report(tasks: list[Task], result: ScheduleResult) -> str:
    """ساخت یک خلاصه قابل فهم از نتایج زمان‌بندی.

    Args:
        tasks (list[Task]): لیست اصلی وظایف ارائه شده به زمان‌بند.
        result (ScheduleResult): شیء خروجی بازگردانده شده توسط TaskScheduler.

    Returns:
        str: رشته‌ای چندخطی شامل آمار کل، سودها، ترتیب اجرا و جزئیات موارد حذف شده.
    """

    total_declared_duration = sum(task.duration for task in tasks)
    completed_duration = sum(event.task.duration for event in result.events)
    urgent_count = sum(1 for task in tasks if task.is_urgent)
    deadline_count = sum(1 for task in tasks if task.has_deadline)
    completed_profit = sum(event.task.profit for event in result.events)
    skipped_profit = sum(task.profit for task in tasks if task.task_id in result.skipped)

    lines = [
        "گزارش سیستم:",
        f"- تعداد کل وظایف: {len(tasks)}",
        f"- وظایف تکمیل شده: {len(result.events)}",
        f"- وظایف نادیده گرفته شده: {len(result.skipped)}",
        f"- وظایف فوری (اولیت ۰): {urgent_count}",
        f"- وظایف دارای مهلت زمانی (Deadline): {deadline_count}",
        f"- کل زمان برآورد شده: {total_declared_duration}",
        f"- زمان واقعی زمان‌بندی شده: {result.total_time}",
        f"- سود کسب شده: {completed_profit}",
        f"- سود از دست رفته (وظایف حذف شده): {skipped_profit}",
    ]

    # اگر دوری (Cycle) در گراف وجود داشته باشد، آن را نمایش می‌دهد
    if result.cycle_report.has_cycle:
        lines.append("- دور شناسایی شده: " + " -> ".join(result.cycle_report.cycle))

    # نمایش ترتیب اجرای وظایف
    if result.order:
        lines.append("- ترتیب اجرا: " + " -> ".join(result.order))
    else:
        lines.append("- ترتیب اجرا: هیچ وظیفه‌ی قابل اجرایی یافت نشد")

    # نمایش جزئیات و علت حذف شدن وظایف
    if result.skipped:
        lines.append("- جزئیات موارد نادیده گرفته شده:")
        for task_id, reason in sorted(result.skipped.items()):
            lines.append(f"  * {task_id}: {reason}")

    return "\n".join(lines)


def build_task_table(tasks: list[Task]) -> str:
    """ارائه یک جدول قالب‌بندی شده از وظایف برای نمایش در کنسول.

    Args:
        tasks (list[Task]): لیستی از اشیاء Task برای نمایش.

    Returns:
        str: رشته‌ای با ستون‌های تراز شده و مناسب برای چاپ در خروجی.
    """

    if not tasks:
        return "هیچ وظیفه‌ای بارگذاری نشده است."

    # تعریف عناوین ستون‌ها و خط جداکننده
    rows = [
        ("شناسه", "اولویت", "مدت زمان", "وابستگی‌ها", "مهلت", "سود"),
        ("----", "-------", "---------", "----------", "----", "---"),
    ]

    # اضافه کردن داده‌های هر تسک به سطرها
    for task in sorted(tasks, key=lambda item: item.task_id):
        rows.append((
            task.task_id,
            str(task.priority),
            str(task.duration),
            "-" if not task.dependencies else "|".join(task.dependencies),
            "-" if task.deadline is None else str(task.deadline),
            str(task.profit),
        ))

    # محاسبه بیشترین عرض برای هر ستون جهت تراز کردن (Padding)
    widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]

    formatted_rows: list[str] = []
    for row in rows:
        # تراز کردن هر ستون با استفاده از ljust بر اساس بیشترین عرض آن ستون
        formatted_rows.append("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))

    return "\n".join(formatted_rows)
