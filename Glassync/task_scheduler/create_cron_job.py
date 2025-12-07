from crontab import CronTab


def create_cron_job(command: str | list[str], schedule: str) -> bool:
    """
    Создаёт cron-задачу, которая выполняется по расписанию.

    :param command: комманда
    :param schedule: cron-выражение
    """
    user_cron = CronTab(user=True)

    # Собираем все задания с таким же командным текстом
    jobs_to_remove = [job for job in user_cron if job.command == command_str]

    for job in jobs_to_remove:
        user_cron.remove(job)

    # Создаём новую задачу
    job = user_cron.new(command=command_str)
    job.setall(schedule)

    user_cron.write()
    return True