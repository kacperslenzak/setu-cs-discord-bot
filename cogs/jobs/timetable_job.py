from discord.ext import commands
from discord import File
import io
from utils.timetable import fetch_timetable_image
from core.scheduler import ScheduledJob


class TimeTableJob(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.jobs.append(
            ScheduledJob(self.friday_timetable_job, day_of_week="fri", hour=14, minute=10)  # Schedule every friday, 10 mins after 2 to allow for timetable update
        )

    @commands.command(name='timetable')
    async def _timetable(self, ctx):
        """Send the current week timetable for Comp Sci Year 1 W3/W4"""
        message = await ctx.send("Generating timetable. Please wait a few moments.", delete_after=3)  # we cant edit the message to include file, so let's delete this later
        try:
            image_bytes = fetch_timetable_image()
            file = File(io.BytesIO(image_bytes), filename='timetable.png')
            await ctx.send('📅 Timetable for this week!', file=file)
        except Exception as e:
            await ctx.send(f'Error fetching timetable\n```{str(e)}```')

    async def friday_timetable_job(self):
        channel_id = 1424080247191634023
        channel = self.bot.get_channel(channel_id)
        if channel:
            try:
                image_bytes = fetch_timetable_image()
                file = File(io.BytesIO(image_bytes), filename='timetable.png')
                await channel.send(f"📅 Timetable for this week!", file=file)
            except Exception as e:
                self.bot.log.error(f"Error with timetable job: {str(e)}")
