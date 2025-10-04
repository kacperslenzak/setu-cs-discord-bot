class BotConfig:
    __conf = {
        "TOKEN": "",
        "timetable_job_channel_id": 0,  # ID for timetable job, will send timetable here every friday
    }

    @staticmethod
    def get(name):
        return BotConfig.__conf[name]