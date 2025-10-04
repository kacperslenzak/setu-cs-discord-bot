from datetime import datetime, timedelta
from typing import Callable, List, Optional
import asyncio


class ScheduledJob:
    """Represents a single scheduled job"""
    def __init__(self, func: Callable[[], asyncio.coroutines], day_of_week: str, hour: int, minute: int):
        self.func = func
        self.day_of_week = day_of_week.lower()  # e.g., 'fri', 'mon'
        self.hour = hour
        self.minute = minute
        self.weekday_map = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}

    def get_next_run_time(self, from_datetime: datetime) -> Optional[datetime]:
        """Calculate the next time this job should run after from_datetime."""
        weekday_num = self.weekday_map.get(self.day_of_week, -1)
        if weekday_num == -1:
            raise ValueError(f"Invalid day_of_week: {self.day_of_week}")

        now = from_datetime
        days_ahead = weekday_num - now.weekday()
        if days_ahead < 0:  # Changed from <= 0 to < 0
            days_ahead += 7  # Next week only for past days

        next_run = now + timedelta(days=days_ahead)
        target_time = next_run.replace(  # Use next_run for consistency
            hour=self.hour, minute=self.minute, second=0, microsecond=0
        )

        # If target_time is in the past, add 7 days
        if target_time <= now:
            target_time += timedelta(days=7)

        return target_time


async def custom_scheduler_loop(jobs: List[ScheduledJob]):
    """Main scheduler loop: Sleeps to next job time, runs due jobs."""
    if not jobs:
        print("No jobs registered; scheduler idle.")
        return

    print(f"Starting scheduler with {len(jobs)} jobs.")
    while True:
        now = datetime.now()

        # Find the soonest next run time across all jobs
        next_times = []
        for job in jobs:
            next_time = job.get_next_run_time(now)
            if next_time:
                next_times.append((next_time, job))

        if not next_times:
            print("No valid next times; sleeping indefinitely.")
            await asyncio.sleep(3600)  # Wait 1 hour, then retry
            continue

        # Sort by earliest time
        next_times.sort(key=lambda x: x[0])
        soonest_time, soonest_job = next_times[0]
        sleep_duration = max((soonest_time - now).total_seconds(), 0)

        print(f"Sleeping for {sleep_duration / 3600:.1f} hours until {soonest_time.strftime('%Y-%m-%d %H:%M')}...")
        await asyncio.sleep(sleep_duration)

        # Run all jobs due at or around this time (within 1 minute tolerance)
        now_after_sleep = datetime.now()
        due_jobs = [job for run_time, job in next_times if abs((run_time - now_after_sleep).total_seconds()) <= 60]

        for job in due_jobs:
            try:
                await job.func()
                print(f"Job '{job.func.__name__}' executed successfully.")
            except Exception as e:
                print(f"Error running job '{job.func.__name__}': {e}")