from core.bot import DiscordBot
import asyncio


async def main() -> None:
    async with DiscordBot() as bot:
        try:
            await bot.async_run()
        except (KeyboardInterrupt, RuntimeError) as e:
            print(e)
            exit(0)

if __name__ == '__main__':
    asyncio.run(main())