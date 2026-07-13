"""موتور اصلی زمان‌بندی (Scheduling Engine).

این ماژول یک گراف وابستگی از وظایف ارائه شده می‌سازد، دورها (Cycles) را شناسایی کرده
و یک حلقه زمان‌بندی حریصانه (Greedy) را اجرا می‌کند که به وابستگی‌ها،
زمان‌های نهایی (Deadlines) و اولویت‌ها احترام می‌گذارد.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from math import inf

from models.task import Task
from scheduler.dependency_graph import CycleReport, DependencyGraph


@dataclass(frozen=True)
class ScheduleEvent:
    """نمایانگر اجرای یک وظیفه در جدول زمان‌بندی نهایی.

    Attributes:
        task (Task): وظیفه‌ی اجرا شده.
        start (int): زمان شروع اجرا.
        finish (int): زمان پایان اجرا.
    """

    task: Task
    start: int
    finish: int


@dataclass
class ScheduleResult:
    """محفظه نتایج بازگردانده شده توسط کلاس :class:`TaskScheduler`.

    Attributes:
        events (list[ScheduleEvent]): لیست رویدادهای اجرا شده به ترتیب زمان.
        skipped (dict[str, str]): نگاشت شناسه وظیفه به علت نادیده گرفته شدن (Skip).
        cycle_report (CycleReport): گزارش دور تولید شده در طول فرآیند تشخیص.
    """

    events: list[ScheduleEvent] = field(default_factory=list)
    skipped: dict[str, str] = field(default_factory=dict)
    cycle_report: CycleReport = field(default_factory=lambda: CycleReport(False, []))

    @property
    def is_successful(self) -> bool:
        """بررسی موفقیت‌آمیز بودن زمان‌بندی (بدون دور و بدون وظیفه نادیده گرفته شده)."""
        return not self.cycle_report.has_cycle and not self.skipped

    @property
    def total_time(self) -> int:
        """کل زمان اجرای پوشش داده شده توسط رویدادهای زمان‌بندی شده."""
        if not self.events:
            return 0
        return max(event.finish for event in self.events)

    @property
    def order(self) -> list[str]:
        """بازگرداندن ترتیب اجرا به صورت لیستی از شناسه‌های وظایف."""
        return [event.task.task_id for event in self.events]

    @property
    def completed_ids(self) -> set[str]:
        """مجموعه‌ای از شناسه‌های وظایفی که با موفقیت اجرا شده‌اند."""
        return {event.task.task_id for event in self.events}


class TaskScheduler:
    """زمان‌بندی که به وابستگی‌ها و زمان‌های نهایی احترام می‌گذارد.

    استراتژی انتخاب برای وظایف آماده به اجرا بر اساس اولویت‌های زیر است:
    ۱. Slack کمتر (کارهای فوری در اولویت هستند)
    ۲. اولویت عددی پایین‌تر (عدد ۰ بالاترین اهمیت را دارد)
    ۳. تعداد وابسته‌های بیشتر (کارهایی که پیش‌نیاز وظایف بیشتری هستند)
    ۴. سود (Profit) بالاتر
    ۵. ترتیب حروف الفبای شناسه وظیفه برای تضمین رفتار قطعی (Deterministic)
    """

    def __init__(self, tasks: list[Task]) -> None:
        """مقداردهی اولیه زمان‌بند و ساخت گراف وابستگی.

        Args:
            tasks (list[Task]): لیستی از نمونه‌های Task برای زمان‌بندی.
        """
        self.graph = DependencyGraph(tasks)
        self.tasks = self.graph.tasks

    def schedule(self) -> ScheduleResult:
        """اجرای حلقه زمان‌بندی و بازگرداندن یک ScheduleResult.

        Returns:
            ScheduleResult: نتیجه نهایی شامل رویدادهای موفق و موارد نادیده گرفته شده.
        """

        # ۱. بررسی وجود دور (حلقه) در گراف
        cycle_report = self.graph.detect_cycle()
        if cycle_report.has_cycle:
            skipped = {task_id: "dependency cycle detected" for task_id in self._tasks_in_cycle(cycle_report.cycle)}
            return ScheduleResult(cycle_report=cycle_report, skipped=skipped)

        current_time = 0
        result = ScheduleResult(cycle_report=cycle_report)
        indegree = dict(self.graph.indegree)
        
        # صف اولویت‌دار برای نگهداری تسک‌های آماده (Ready)
        ready_heap: list[tuple[float, int, int, int, str]] = []

        # اضافه کردن وظایفی که هیچ پیش‌نیازی ندارند به صف
        for task_id, degree in indegree.items():
            if degree == 0:
                self._push_ready_task(ready_heap, self.tasks[task_id], current_time)

        while ready_heap:
            # انتخاب بهترین تسک بر اساس استراتژی تعریف شده
            _, _, _, _, task_id = heapq.heappop(ready_heap)
            task = self.tasks[task_id]

            start_time = current_time
            finish_time = start_time + task.duration

            # بررسی اینکه آیا وظیفه قبل از مهلت نهایی (Deadline) تمام می‌شود یا خیر
            if task.deadline is not None and finish_time > task.deadline:
                result.skipped[task_id] = f"expired: finishes at {finish_time}, deadline is {task.deadline}"
                # تمام کارهایی که به این کار وابسته هستند هم باید مسدود شوند
                self._mark_dependents_blocked(task_id, result.skipped)
                continue

            # ثبت رویداد اجرای موفق
            result.events.append(ScheduleEvent(task=task, start=start_time, finish=finish_time))
            current_time = finish_time

            # به‌روزرسانی وابسته‌ها (کاهش درجه ورودی آن‌ها)
            for child_id in self.graph.dependents[task_id]:
                if child_id in result.skipped:
                    continue
                indegree[child_id] -= 1
                if indegree[child_id] == 0:
                    self._push_ready_task(ready_heap, self.tasks[child_id], current_time)

        # مشخص کردن وظایفی که به دلیل اتمام نرسیدن پیش‌نیازها اجرا نشده‌اند
        for task_id in self.tasks:
            if task_id not in result.completed_ids and task_id not in result.skipped:
                result.skipped[task_id] = "blocked by skipped or unfinished dependency"

        return result

    def _push_ready_task(self, heap: list[tuple[float, int, int, int, str]], task: Task, current_time: int) -> None:
        """محاسبه چندگانه (Tuple) اولویت وظیفه و افزودن آن به Heap."""
        
        # محاسبه Slack: مدت زمان باقی‌مانده تا ددلاین پس از انجام کار
        slack = inf if task.deadline is None else task.deadline - current_time - task.duration
        
        # مقادیر منفی برای dependent_count و profit به دلیل ساختار Min-Heap پایتون است (برای تبدیل به Max-Priority)
        heapq.heappush(heap, (
            slack, 
            task.priority, 
            -self.graph.dependent_count(task.task_id), 
            -task.profit, 
            task.task_id
        ))

    def _mark_dependents_blocked(self, task_id: str, skipped: dict[str, str]) -> None:
        """علامت‌گذاری بازگشتی وظایف وابسته به عنوان مسدود شده وقتی پیش‌نیاز نادیده گرفته می‌شود."""
        for child_id in self.graph.dependents[task_id]:
            if child_id not in skipped:
                skipped[child_id] = f"blocked because dependency {task_id} was skipped"
                self._mark_dependents_blocked(child_id, skipped)

    @staticmethod
    def _tasks_in_cycle(cycle: list[str]) -> set[str]:
        """بازگرداندن مجموعه‌ای از وظایف که تحت تأثیر دور شناسایی شده هستند."""
        return set(cycle)
