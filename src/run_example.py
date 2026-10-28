from __future__ import annotations

import argparse
from datetime import date, datetime

from course_usage_meter import CourseUsageMeter, LessonDelivery
from infrai_account_client import InfraiAccountClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Report course delivery units by customer")
    parser.add_argument("--fetch-account-usage", action="store_true")
    args = parser.parse_args()

    meter = CourseUsageMeter()
    meter.record_delivery(LessonDelivery("acme-academy", "rag-101", "learner-7", "lesson-1", date(2026, 10, 20), datetime(2026, 10, 20, 9, 0)))
    meter.record_delivery(LessonDelivery("acme-academy", "rag-101", "learner-7", "lesson-2", date(2026, 10, 21), datetime(2026, 10, 22, 9, 0)))
    report = meter.report("acme-academy")
    print(f"customer={report.customer_id} delivered_units={report.delivered_units} on_time_units={report.on_time_units} late_units={report.late_units}")

    if args.fetch_account_usage:
        envelope = InfraiAccountClient().usage_timeseries()
        print(f"account_usage_ok={envelope.ok} data={envelope.data}")


if __name__ == "__main__":
    main()
