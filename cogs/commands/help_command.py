from discord.ext import commands


class MyHelpCommand(commands.MinimalHelpCommand):
    def add_bot_commands_formatting(self, commands, heading, /) -> None:
        if commands:
            joined = ', '.join(c.name for c in commands)
            self.paginator.add_line(f'**{heading}**')
            self.paginator.add_line(joined)
