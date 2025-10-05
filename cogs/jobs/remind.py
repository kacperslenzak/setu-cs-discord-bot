from discord.ext import commands
from discord import app_commands
from datetime import datetime
from db.models import Reminder
import asyncio
from config import BotConfig
from sqlalchemy import select, delete


class RemindJob(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="remind", description="Set a reminder at a given date")
    @app_commands.describe(date="Please enter the date in format Day-Month. e.g. 05-10", time="Please enter the time in 24h format. e.g. 14:20", message="Please enter the message for the reminder.")
    async def _remind(self, ctx, date: str, time: str, *, message: str):
        """
        Save a reminder
        Example: ?remind 05-10-2025 14:30
        :param ctx:
        :param date:
        :param message:
        :return:
        """
        now = datetime.now()
        remind_at = None

        try:
            remind_at = datetime.strptime(f"{date}-{now.year} {time}", "%d-%m-%Y %H:%M")
        except ValueError:
            return await ctx.send("❌ Invalid date format! Correct Example (DAY-MONTH HOUR-MINUTE): 15-09 14:10")

        async with self.bot.session() as session:
            reminder = Reminder(user_id=ctx.author.id, message=message, remind_at=remind_at)
            session.add(reminder)
            await session.commit()

        await self.schedule_reminder(reminder)
        await ctx.send(f"✅ Reminder saved for {remind_at.strftime('%d-%m-%Y %H:%M')}")

    async def schedule_reminder(self, reminder: Reminder):
        """
        This is a scheduler for reminders. We need a different scheduler than the one in the project
        as we need to schedule single tasks rather than recurring tasks
        :return:
        """
        async def run_reminder():
            sleep_seconds = max((reminder.remind_at - datetime.now()).total_seconds(), 0)
            if sleep_seconds > 0:
                await asyncio.sleep(sleep_seconds)

            try:
                user = await self.bot.fetch_user(reminder.user_id)
                channel = self.bot.get_channel(BotConfig.get("REMINDER_CHANNEL_ID"))
                if user and channel:
                    await channel.send(f"⏰ Reminder <@{user.id}>! {reminder.message}")
                else:
                    self.bot.log.error(f"Failed to fetch reminder for user {reminder.user_id}, reminder: {reminder.id}")
            except Exception as e:
                self.bot.log.error(f"Error sending reminder {reminder.id}: {e}")

            async with self.bot.session() as session:
                await session.delete(reminder)
                await session.commit()

        asyncio.create_task(run_reminder())
        self.bot.log.info(f"Scheduled reminder {reminder.id} for {reminder.remind_at}")

    @commands.Cog.listener()
    async def on_ready(self):
        """On ready hook to schedule reminders"""
        self.bot.log.info(f"{self.__class__.__name__} cog loaded and scheduling reminders")

        async with self.bot.session() as session:
            expired = await session.execute(
                delete(Reminder).where(Reminder.remind_at < datetime.now())
            )
            await session.commit()
            if expired.rowcount > 0:
                self.bot.log.info(f"Cleaned up {expired.rowcount} expired reminders")

            query = select(Reminder).where(Reminder.remind_at > datetime.now())
            result = await session.execute(query)
            pending = result.scalars().all()

            for reminder in pending:
                await self.schedule_reminder(reminder)
                self.bot.log.info(f"Rescheduled reminder {reminder.id} for {reminder.remind_at}")

            self.bot.log.info(f"Rescheduled {len(pending)} pending remainders")
