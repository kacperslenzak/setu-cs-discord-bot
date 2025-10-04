from discord.ext import commands


class PingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Returns the bots ping in ms")
    async def _ping(self, ctx):
        """This command returns the bots ping in ms"""
        ws, rest = await ctx.bot.ping()

        return await ctx.send(f"Pong! Websocket: {ws * 1000: .2f}ms, REST: {rest * 1000: .2f}ms")
