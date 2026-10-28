from datetime import date, datetime

from src.course_usage_meter import CourseUsageMeter, LessonDelivery


def test_late_delivery_is_counted_separately_for_customer_reporting() -> None:
    meter = CourseUsageMeter()
    meter.record_delivery(LessonDelivery("school-1", "course-1", "learner-1", "lesson-1", date(2026, 10, 20), datetime(2026, 10, 20, 12, 0)))
    meter.record_delivery(LessonDelivery("school-1", "course-1", "learner-1", "lesson-2", date(2026, 10, 20), datetime(2026, 10, 21, 12, 0)))

    assert meter.report("school-1") == type(meter.report("school-1"))("school-1", 2, 1, 1)
