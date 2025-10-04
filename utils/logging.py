import logging


def setup() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "\033[31m|discordbot.{module:<10}| \033[0m |\033[35m{levelname:<8}\033[0m|  |\033[34m{threadName}\033[37m:\033[30m{process}\033[0m|  |\033[35m{asctime}\033[0m|   {message}",
        "%Y-%m-%d %H:%M:%S",
        style="{",
    )
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
