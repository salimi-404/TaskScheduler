"""ابزارهای گراف وابستگی مورد استفاده در زمان‌بند.

این ماژول یک گراف جهت‌دار از لیست وابستگی‌های وظایف (Task) می‌سازد،
اطلاعات مربوط به درجه ورود (Indegree) و وظایف وابسته را ارائه می‌دهد و دورها را با DFS شناسایی می‌کند.
"""

from collections import defaultdict, deque
from typing import Dict, List, Optional


class CycleReport:
    """نگه‌دارنده ساده برای گزارش نتایج تشخیص دور (حلقه).

    Attributes:
        has_cycle (bool): مقدار True در صورتی که دور وجود داشته باشد.
        cycle (list): لیستی از شناسه‌های وظایف که مسیر دور را نشان می‌دهد (در صورت وجود).
    """

    def __init__(self, has_cycle: bool, cycle: List[str]):
        self.has_cycle = has_cycle
        self.cycle = cycle


class DependencyGraph:
    """ساخت ساختار گراف بر اساس لیستی از وظایف.

    این شیء ویژگی‌های زیر را در دسترس قرار می‌دهد:
    - `tasks`: نگاشت task_id به شیء Task.
    - `dependents`: نگاشت task_id به لیستی از وظایف فرزند (وابسته به آن).
    - `indegree`: نگاشت task_id به تعداد پیش‌نیازهای آن وظیفه (درجه ورودی).
    """

    def __init__(self, tasks):
        self.tasks: Dict[str, object] = {}

        # بررسی تکراری نبودن شناسه‌ها و ذخیره در دیکشنری
        for task in tasks:
            if task.task_id in self.tasks:
                raise ValueError("Duplicate task id: " + task.task_id)
            self.tasks[task.task_id] = task

        self.dependents: Dict[str, List[str]] = defaultdict(list)
        self.indegree: Dict[str, int] = {task_id: 0 for task_id in self.tasks}
        
        # ساخت اتصالات گراف
        self._build()

    def _build(self) -> None:
        """مقداردهی ساختارهای dependents و indegree بر اساس وابستگی وظایف."""

        for task in self.tasks.values():
            for dep in task.dependencies:
                # اگر پیش‌نیاز تعریف شده در سیستم ثبت نشده باشد، خطا صادر می‌شود
                if dep not in self.tasks:
                    raise ValueError(f"Task {task.task_id} depends on unknown task {dep}")
                self.dependents[dep].append(task.task_id)
                self.indegree[task.task_id] += 1

        # مطمئن شدن از اینکه تمامی وظایف کلیدی در دیکشنری dependents وجود دارند
        for task_id in self.tasks:
            if task_id not in self.dependents:
                self.dependents[task_id] = []

    def dependent_count(self, task_id: str) -> int:
        """محاسبه تعداد وظایف مستقیم وابسته به یک وظیفه خاص.

        Args:
            task_id (str): شناسه وظیفه مورد نظر.

        Returns:
            int: تعداد وظایف وابسته مستقیم.
        """
        return len(self.dependents.get(task_id, []))

    def detect_cycle(self) -> CycleReport:
        """تشخیص دور (حلقه) در گراف وابستگی با استفاده از الگوریتم DFS.

        Returns:
            CycleReport: شیء شامل وضعیت وجود دور و مسیر آن.
        """

        # سفید: پیمایش نشده، خاکستری: در حال پیمایش در شاخه فعلی، مشکی: پیمایش کامل شده
        color: Dict[str, str] = {tid: "white" for tid in self.tasks}
        parent: Dict[str, Optional[str]] = {tid: None for tid in self.tasks}

        def visit(node: str):
            color[node] = "gray"
            for child in self.dependents[node]:
                if color[child] == "white":
                    parent[child] = node
                    cycle_result = visit(child)
                    if cycle_result:
                        return cycle_result
                elif color[child] == "gray":
                    # پیدا شدن یال بازگشتی (Back-edge) نشان‌دهنده وجود دور است
                    return self._reconstruct_cycle(parent, child, node)
            color[node] = "black"
            return None

        # اجرای DFS برای تمام گره‌های پیمایش‌نشده
        for tid in self.tasks:
            if color[tid] == "white":
                cycle_result = visit(tid)
                if cycle_result:
                    return CycleReport(True, cycle_result)

        return CycleReport(False, [])

    @staticmethod
    def _reconstruct_cycle(parent: Dict[str, Optional[str]], start: str, end: str) -> List[str]:
        """بازسازی مسیر دور شناسایی شده در گراف.

        Args:
            parent (dict): نگاشت گره‌ها به والد خود در درخت DFS.
            start (str): گره شروع دور (فرزند).
            end (str): گره پایان دور (والد فعلی).

        Returns:
            list: مسیر گره‌های تشکیل‌دهنده دور به ترتیب اجرا.
        """
        cycle = [start]
        current = end
        while current != start and current is not None:
            cycle.append(current)
            current = parent[current]
        cycle.append(start)
        cycle.reverse()
        return cycle

    def topological_order_without_priority(self) -> List[str]:
        """تولید یک ترتیب توپولوژیک بدون در نظر گرفتن اولویت‌ها با الگوریتم کان (Kahn).

        Returns:
            list: لیستی از شناسه‌های وظایف به ترتیب اولویت وابستگی.
        """
        indegree = self.indegree.copy()
        # صف حاوی وظایفی که هیچ پیش‌نیازی ندارند (درجه ورودی صفر)
        queue = deque([tid for tid, deg in indegree.items() if deg == 0])
        order: List[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for child in self.dependents[node]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)

        return order
