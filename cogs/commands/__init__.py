from cogs.commands.help_command import MyHelpCommand
from cogs.commands.ping import PingCommand


class BaseCommandsManager(PingCommand, name="Basic Commands"):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self


async def setup(bot) -> None:
    await bot.add_cog(BaseCommandsManager(bot))
