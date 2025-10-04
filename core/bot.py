import discord
from discord import app_commands
from discord.ext.commands import Bot
from discord.http import Route
from discord import Intents
from config import BotConfig
from core.scheduler import custom_scheduler_loop
from utils import logging
import time

description = """
Discord bot created for SETU COMP SCI.
"""


class DiscordBot(Bot):
    def __init__(self):
        super().__init__(
            command_prefix='?',
            description=description,
            strip_after_prefix=True,
            owner_ids=(1369058479771357277,),
            intents=Intents.all()
        )
        self.config: BotConfig = BotConfig()
        self.jobs = []
        self.log = logging.setup()

    async def on_ready(self) -> None:
        await self.change_presence(
            status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="over the comp sci freaks 😇")
        )
        print(f"Logged in as {self.user}")

    async def ping(self):
        start = time.perf_counter()
        ws = self.latency
        await self.http.request(Route("GET", "/users/@me"))
        end = time.perf_counter()

        return ws, end - start

    async def setup_hook(self):
        extensions = [
            'cogs.jobs',
            'cogs.commands'
        ]
        await self.load_extensions(*extensions)

        if self.jobs:
            self.scheduler_task = self.loop.create_task(custom_scheduler_loop(self.jobs))
            self.log.info(f"Jobs Registered -> {len(self.jobs)}")

        await self.sync_command_tree()

    async def sync_command_tree(self):
        try:
            synced = await self.tree.sync()
            if not synced:
                self.log.error("No commands synced. Check applications.commands scope!")
            else:
                self.log.info(f"Synced {len(synced)} commands")
        except discord.HTTPException as e:
            if "Missing Access" in str(e) or "403" in str(e):
                self.log.error('❌ Missing applications.commands scope! Re-invite the bot.')
            else:
                self.log.error(f'❌ Sync error: {e}')

    async def load_extensions(self, *extensions):
        for extension in extensions:
            await self.load_extension(extension)

    async def async_run(self) -> None:
        await self.login(BotConfig.get('TOKEN'))
        await self.connect()
