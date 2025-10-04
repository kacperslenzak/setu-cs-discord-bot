from cogs.jobs.timetable_job import TimeTableJob


class BaseJobManager(TimeTableJob):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot


async def setup(bot) -> None:
    await bot.add_cog(BaseJobManager(bot))
