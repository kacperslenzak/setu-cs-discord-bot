from discord.ext import commands
from discord import File
from discord import app_commands
import discord
import io
from utils.timetable import generate_timetable
from core.scheduler import ScheduledJob


class TimeTableJob(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.jobs.append(
            ScheduledJob(self.friday_timetable_job, day_of_week="fri", hour=14, minute=10)  # Schedule every friday, 10 mins after 2 to allow for timetable update
        )

    @app_commands.command(name="timetable", description="Generate a timetable for this week")
    @app_commands.describe(group="Pick which group you want to generate a timetable for")
    @app_commands.choices(group=[
        app_commands.Choice(name="Group W3", value="W3"),
        app_commands.Choice(name="Group W4", value="W4")
    ])
    async def _timetable(self, i: discord.Interaction, group: app_commands.Choice[str]):
        """Send the current week timetable for Comp Sci Year 1 W3/W4"""
        message = await i.response.send_message("Generating timetable. Please wait a few moments.", delete_after=3)  # we cant edit the message to include file, so let's delete this later
        try:
            image_bytes = generate_timetable(group.value)
            file = File(io.BytesIO(image_bytes), filename='timetable.png')
            await i.channel.send(f'📅 Timetable for this week! {group.name}', file=file)
        except Exception as e:
            await i.channel.send(f'Error fetching timetable\n```{str(e)}```')

    async def friday_timetable_job(self):
        channel_id = 1424080247191634023
        channel = self.bot.get_channel(channel_id)
        if channel:
            try:
                for g in ['W3', 'W4']:
                    image_bytes = generate_timetable(g)
                    file = File(io.BytesIO(image_bytes), filename='timetable.png')
                    await channel.send(f"📅 Timetable for this week! Group {g}", file=file)
            except Exception as e:
                self.bot.log.error(f"Error with timetable job: {str(e)}")
