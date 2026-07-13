from __future__ import annotations

"""
نقطه ورود اصلی برای شبیه‌ساز زمان‌بندی وظایف (Task Scheduler).

این ماژول رابط خط فرمان (CLI) را برای بارگذاری وظایف از فایل یا به صورت تعاملی
از کنسول فراهم می‌کند، موتور زمان‌بندی را اجرا کرده و گزارش‌ها و یک نمودار
گانت (Gantt) ساده را چاپ می‌کند.

توابع عمومی:
- `main()` : اجراکننده رابط خط فرمان
"""

import argparse
from pathlib import Path

from models.task import Task
from scheduler.task_scheduler import TaskScheduler
from utils.gantt import render_gantt_chart
from utils.logger import log
from utils.report import build_system_report, build_task_table


# مسیر ریشه پروژه (برای ساختن مسیرهای مطلق به صورت مطمئن)
PROJECT_ROOT = Path(__file__).resolve().parent

# فایل ورودی پیش‌فرض در صورتی که کاربر فایل دیگری ارائه ندهد
DEFAULT_INPUT_FILE = PROJECT_ROOT / "data" / "input.txt"


def parse_dependencies(text: str) -> list[str]:
    """تجزیه یک رشته وابستگی به لیستی از شناسه‌های وظایف.

    جداکننده‌های پشتیبانی شده شامل کاما (,)، خط عمودی (|) و فضای خالی (whitespace) هستند.
    مقدار ویژه `-` یا ورودی خالی به معنای "بدون وابستگی" است.

    Args:
        text: رشته خام وابستگی‌ها که توسط کاربر ارائه شده است.

    Returns:
        لیستی از رشته‌های تمیز شده شناسه‌ی وظایف.
    """

    if not text or text.strip() == "-":
        return []

    cleaned = text.replace(",", " ").replace("|", " ")
    parts = cleaned.split()
    return [p.strip() for p in parts if p.strip()]


def load_tasks_from_file(path: Path) -> list[Task]:
    """خواندن وظایف از یک فایل مشابه CSV و برگرداندن اشیاء Task.

    فرمت مورد انتظار برای هر خط: ``id, priority, duration, dependencies, deadline, profit``.
    خطوطی که با ``#`` شروع می‌شوند یا خالی هستند، نادیده گرفته می‌شوند.

    Args:
        path: مسیر فایل ورودی.

    Returns:
        لیستی از نمونه‌های :class:`models.task.Task`.

    Raises:
        ValueError: هنگامی که یک خط نتواند به یک Task معتبر تجزیه شود. 
            استثنای صادر شده شامل مسیر فایل و شماره خط است.
    """

    tasks: list[Task] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            tasks.append(Task.from_csv_line(line))
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc

    return tasks


def read_tasks_from_console() -> list[Task]:
    """درخواست از کاربر برای وارد کردن وظایف به صورت تعاملی از طریق کنسول.

    این تابع تعداد وظایف را می‌پرسد و سپس فیلدهای هر وظیفه را دریافت می‌کند.
    از `-` برای نشان دادن نبود وابستگی یا مقادیر تنظیم نشده استفاده کنید.

    Returns:
        لیستی از اشیاء :class:`models.task.Task` ایجاد شده.
    """

    count = int(input("تعداد وظایفی که می‌خواهید وارد کنید؟ ").strip())
    tasks: list[Task] = []

    print("وابستگی‌ها را با |، فاصله یا کاما وارد کنید. برای هیچ‌کدام از - استفاده کنید.")
    print("ددلاین (Deadline) و سود (Profit) ویژگی‌های اختیاری هستند.")

    for index in range(1, count + 1):
        print(f"\nوظیفه {index}")
        task_id = input("شناسه (id): ").strip()
        priority = int(input("اولویت (0 فوری است): ").strip())
        duration = int(input("مدت زمان (duration): ").strip())

        dependency_text = input("وابستگی‌ها: ").strip()
        dependencies = parse_dependencies(dependency_text)

        deadline_text = input("ددلاین (- برای بدون ددلاین): ").strip()
        deadline = None if deadline_text in {"", "-"} else int(deadline_text)

        profit_text = input("سود (- برای 0): ").strip()
        profit = 0 if profit_text in {"", "-"} else int(profit_text)

        tasks.append(Task(task_id=task_id, priority=priority, duration=duration,
                          dependencies=dependencies, deadline=deadline, profit=profit))

    return tasks


def run_simulation(tasks: list[Task]) -> None:
    """اجرای کامل خط لوله (Pipeline) زمان‌بندی و چاپ نتایج.

    مراحل انجام شده شامل اعتبارسنجی، زمان‌بندی، تولید گزارش و 
    رسم یک نمودار گانت ساده در کنسول است.

    Args:
        tasks: لیست وظایف برای زمان‌بندی.

    Raises:
        ValueError: اگر لیست وظایف ارائه شده خالی باشد.
    """

    if not tasks:
        raise ValueError("وظیفه‌ای یافت نشد. وظایف را به data/input.txt اضافه کنید یا از --interactive استفاده کنید.")

    print("\nوظایف بارگذاری شده:")
    print(build_task_table(tasks))

    scheduler = TaskScheduler(tasks)
    result = scheduler.schedule()

    print()
    print(build_system_report(tasks, result))
    print()
    print(render_gantt_chart(result.events))


def parse_args() -> argparse.Namespace:
    """تجزیه آرگومان‌های خط فرمان.

    Returns:
        یک argparse.Namespace با دو صفت:
        - ``file``: مسیر فایل ورودی (پیش‌فرض: ``data/input.txt``)
        - ``interactive``: پرچم بولی برای فعال‌سازی ورودی تعاملی.
    """

    parser = argparse.ArgumentParser(description="شبیه‌ساز زمان‌بندی وظایف برای پروژه برنامه سازی پیشرفته ۲.")

    parser.add_argument("-f", "--file", type=Path, default=DEFAULT_INPUT_FILE,
                        help="مسیر فایل ورودی. پیش‌فرض: data/input.txt")

    parser.add_argument("-i", "--interactive", action="store_true",
                        help="خواندن وظایف از کنسول به جای فایل.")

    return parser.parse_args()


def main() -> None:
    """نقطه ورود برنامه که هنگام اجرای ماژول به عنوان اسکریپت فراخوانی می‌شود.

    این تابع آرگومان‌های CLI را تجزیه می‌کند، وظایف را از منبع درخواست شده بارگذاری کرده
    و خط لوله شبیه‌سازی را اجرا می‌کند. خطاها کپچر شده و در کنسول چاپ می‌شوند.
    """

    args = parse_args()
    try:
        if args.interactive:
            log("در حال خواندن وظایف از کنسول.")
            tasks = read_tasks_from_console()
        else:
            log(f"در حال خواندن وظایف از {args.file}.")
            tasks = load_tasks_from_file(args.file)

        run_simulation(tasks)
    except Exception as exc:
        print(f"خطا: {exc}")


if __name__ == "__main__":
    main()
