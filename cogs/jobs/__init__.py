from cogs.jobs.timetable_job import TimeTableJob
from cogs.jobs.remind import RemindJob


class BaseJobManager(TimeTableJob, RemindJob, name="Job Commands (e.g timetable, reminder)"):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot


async def setup(bot) -> None:
    await bot.add_cog(BaseJobManager(bot))
