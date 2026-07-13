"""ابزارهای بصری‌سازی HTML/SVG برای وظایف و نتایج زمان‌بندی.

این توابع کمکی برای قراردادن یک داشبورد ساده در اسلایدهای HTML یا نوت‌بوک‌ها
بسیار مفید هستند. استفاده از آن‌ها در خروجی کنسول (CLI) اختیاری است اما
برای تولید مطالب ارائه (Presentation) کاربرد زیادی دارند.
"""

from __future__ import annotations

from collections import defaultdict
from html import escape
from typing import List

from models.task import Task
from scheduler.task_scheduler import ScheduleEvent, ScheduleResult


def _priority_color(priority: int) -> str:
    """نگاشت اولویت وظیفه به یک رشته رنگ هگز (Hex).

    Args:
        priority (int): اولویت عددی (۰ فوری‌ترین است).

    Returns:
        str: رشته رنگ هگز که برای تاکید بصری استفاده می‌شود.
    """

    if priority == 0:
        return "#ef4444"  # قرمز
    if priority == 1:
        return "#f59e0b"  # نارنجی
    if priority == 2:
        return "#3b82f6"  # آبی
    return "#64748b"      # خاکستری


def render_task_cards_html(tasks: List[Task]) -> str:
    """رسم وظایف به شکل کارت‌های ساده HTML.

    Args:
        tasks (List[Task]): لیست اشیاء Task برای رسم.

    Returns:
        str: قطعه کد HTML شامل ساختار کارت‌ها برای هر وظیفه.
    """

    cards = []
    for task in sorted(tasks, key=lambda item: (item.priority, item.task_id)):
        deps = "بدون وابستگی" if not task.dependencies else "نیاز به: " + ", ".join(task.dependencies)
        deadline = "بدون مهلت" if task.deadline is None else f"مهلت: {task.deadline}"
        color = _priority_color(task.priority)

        cards.append(
            f"""
            <div style="border:1px solid #d6dee8;border-left:8px solid {color};border-radius:8px;padding:12px 14px;background:#ffffff;box-shadow:0 2px 8px rgba(15,23,42,.08);direction:rtl;text-align:right;">
                <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
                    <strong style="font-size:22px;color:#0f172a;">{escape(task.task_id)}</strong>
                    <span style="background:{color};color:white;border-radius:999px;padding:3px 9px;font-size:12px;font-weight:700;">P{task.priority}</span>
                </div>
                <div style="margin-top:8px;color:#334155;font-size:13px;line-height:1.8;">
                    <div>مدت اجرا: <strong>{task.duration}</strong></div>
                    <div>{escape(deps)}</div>
                    <div>{escape(deadline)}</div>
                    <div>سود: <strong>{task.profit}</strong></div>
                </div>
            </div>
            """
        )

    return f"""
    <div style="font-family:Tahoma,Arial,sans-serif;">
        <h2 style="margin:0 0 10px;color:#0f172a;text-align:right;">کارت‌های وظایف</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;">{''.join(cards)}</div>
    </div>
    """


def render_summary_dashboard_html(tasks: List[Task], result: ScheduleResult) -> str:
    """رسم یک داشبورد HTML کوچک برای خلاصه نتایج زمان‌بندی.

    Args:
        tasks (List[Task]): لیست اصلی وظایف.
        result (ScheduleResult): نتیجه زمان‌بندی برای محاسبه شاخص‌ها.

    Returns:
        str: قطعه کد HTML شامل کارت‌های شاخص و جزئیات اجرا.
    """

    completed_profit = sum(event.task.profit for event in result.events)
    lost_profit = sum(task.profit for task in tasks if task.task_id in result.skipped)
    urgent_count = sum(1 for task in tasks if task.priority == 0)
    deadline_count = sum(1 for task in tasks if task.deadline is not None)

    metrics = [
        ("کل وظایف", len(tasks), "#0f172a"),
        ("تکمیل شده", len(result.events), "#16a34a"),
        ("حذف شده", len(result.skipped), "#dc2626"),
        ("فوری (P0)", urgent_count, "#ef4444"),
        ("دارای مهلت", deadline_count, "#7c3aed"),
        ("زمان کل", result.total_time, "#2563eb"),
        ("سود کسب شده", completed_profit, "#059669"),
        ("سود از دست رفته", lost_profit, "#ea580c"),
    ]

    cards = [f"""
        <div style="background:#fff;border:1px solid #d8e0ea;border-radius:8px;padding:14px;box-shadow:0 2px 8px rgba(15,23,42,.07);text-align:center;">
            <div style="font-size:12px;color:#64748b;text-transform:uppercase;font-weight:700;">{escape(title)}</div>
            <div style="font-size:30px;color:{color};font-weight:800;margin-top:4px;">{value}</div>
        </div>
    """ for title, value, color in metrics]

    order = " -> ".join(result.order) if result.order else "هیچ وظیفه‌ای اجرا نشد"
    skipped = "".join(f"<li><strong>{escape(task_id)}</strong>: {escape(reason)}</li>" for task_id, reason in sorted(result.skipped.items()))
    skipped_block = f"<ul style='margin:8px 0 0;color:#7f1d1d;direction:rtl;text-align:right;'>{skipped}</ul>" if skipped else "<div style='color:#166534;font-weight:700;text-align:right;'>هیچ موردی حذف نشد</div>"

    return f"""
    <div style="font-family:Tahoma,Arial,sans-serif;background:#f8fafc;border:1px solid #d8e0ea;border-radius:10px;padding:16px;direction:rtl;">
        <h2 style="margin:0 0 12px;color:#0f172a;text-align:right;">داشبورد سیستم</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;">{''.join(cards)}</div>
        <div style="margin-top:14px;background:white;border:1px solid #d8e0ea;border-radius:8px;padding:12px;text-align:right;">
            <div style="font-weight:800;color:#0f172a;">ترتیب اجرا</div>
            <div style="margin-top:6px;font-size:16px;color:#1e293b;direction:ltr;text-align:right;">{escape(order)}</div>
        </div>
        <div style="margin-top:12px;background:white;border:1px solid #d8e0ea;border-radius:8px;padding:12px;text-align:right;">
            <div style="font-weight:800;color:#0f172a;">وظایف نادیده گرفته شده</div>
            {skipped_block}
        </div>
    </div>
    """


def render_gantt_svg(events: List[ScheduleEvent], width: int = 980) -> str:
    """رسم نمودار گانت به صورت SVG برای رویدادهای زمان‌بندی شده.

    Args:
        events (List[ScheduleEvent]): لیست رویدادهای اجرا شده.
        width (int): عرض مورد نظر برای SVG به پیکسل.

    Returns:
        str: رشته‌ای شامل کدهای SVG برای نمایش نمودار گانت بصری.
    """

    if not events:
        return "<svg width='980' height='90'><text x='20' y='45'>هیچ وظیفه‌ای زمان‌بندی نشده است</text></svg>"

    left = 110
    right = 30
    row_height = 44
    top = 45
    total_time = max(event.finish for event in events)
    scale = (width - left - right) / max(total_time, 1)
    height = top + len(events) * row_height + 35

    rows = ["<text x='20' y='25' font-family='Tahoma,Arial' font-size='20' font-weight='800' fill='#0f172a'>محور زمانی گانت (Visual Gantt)</text>"]

    for index, event in enumerate(events):
        y = top + index * row_height
        x = left + event.start * scale
        bar_width = max(12, (event.finish - event.start) * scale)
        color = _priority_color(event.task.priority)

        rows.append(f"<text x='20' y='{y + 24}' font-family='Arial' font-size='14' font-weight='700' fill='#0f172a'>{escape(event.task.task_id)}</text>")
        rows.append(f"<rect x='{left}' y='{y + 3}' width='{width - left - right}' height='28' rx='6' fill='#eef2f7'/>")
        rows.append(f"<rect x='{x:.1f}' y='{y + 3}' width='{bar_width:.1f}' height='28' rx='6' fill='{color}'/>")
        rows.append(f"<text x='{x + 8:.1f}' y='{y + 23}' font-family='Arial' font-size='12' font-weight='700' fill='white'>{event.start} -> {event.finish}</text>")

    # رسم خطوط عمودی برای هر واحد زمان (Grid lines)
    for time in range(total_time + 1):
        x = left + time * scale
        rows.append(f"<line x1='{x:.1f}' y1='{top - 10}' x2='{x:.1f}' y2='{height - 25}' stroke='#cbd5e1' stroke-width='1' opacity='.55'/>")
        rows.append(f"<text x='{x - 3:.1f}' y='{height - 8}' font-family='Arial' font-size='10' fill='#475569'>{time}</text>")

    return f"<svg viewBox='0 0 {width} {height}' width='100%' height='{height}' direction='ltr'>{''.join(rows)}</svg>"
