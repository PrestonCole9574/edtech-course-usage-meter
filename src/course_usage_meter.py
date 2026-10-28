from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class LessonDelivery:
    customer_id: str
    course_id: str
    learner_id: str
    lesson_id: str
    deadline: date
    delivered_at: datetime

    @property
    def on_time(self) -> bool:
        return self.delivered_at.date() <= self.deadline


@dataclass(frozen=True)
class CustomerUsageReport:
    customer_id: str
    delivered_units: int
    on_time_units: int
    late_units: int


class CourseUsageMeter:
    def __init__(self) -> None:
        self._deliveries: list[LessonDelivery] = []

    def record_delivery(self, delivery: LessonDelivery) -> None:
        self._deliveries.append(delivery)

    def report(self, customer_id: str) -> CustomerUsageReport:
        deliveries = [item for item in self._deliveries if item.customer_id == customer_id]
        on_time_units = sum(item.on_time for item in deliveries)
        return CustomerUsageReport(
            customer_id=customer_id,
            delivered_units=len(deliveries),
            on_time_units=on_time_units,
            late_units=len(deliveries) - on_time_units,
        )
