from crontab import CronTab


def create_cron_job(command: str | list[str], schedule: str) -> bool:
    """
    Создаёт cron-задачу, которая выполняется по расписанию.

    :param command: комманда
    :param schedule: cron-выражение
    """
    user_cron = CronTab(user=True)

    # Поиск и удаление всех задач с такой командой
    jobs = list(user_cron.find_command(command))
    for job in jobs:
        user_cron.remove(job)

    # Создание новой задачи с заданным расписанием
    job = user_cron.new(command=command)
    job.setall(schedule)

    user_cron.write()
    return True
