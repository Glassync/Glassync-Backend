ERRORS = {
    "general": {
        "invalid_json": {
            "code": "invalid_json",
            "message_en": "Invalid JSON body",
            "message_ru": "Некорректное тело запроса (JSON)"
        },
        "unexpected_error": {
            "code": "unexpected_error",
            "message_en": "An unexpected error occurred",
            "message_ru": "Произошла непредвиденная ошибка"
        },
        "invalid_request_method": {
            "code": "invalid_request_method",
            "message_en": "Invalid request method, only POST is allowed",
            "message_ru": "Недопустимый метод запроса, разрешён только POST"
        }
    },
    "fields": {
        "missing_email": {
            "code": "missing_email",
            "message_en": "Email is required",
            "message_ru": "Требуется email"
        },
        "missing_password": {
            "code": "missing_password",
            "message_en": "Password is required",
            "message_ru": "Требуется пароль"
        },
        "missing_first_name": {
            "code": "missing_first_name",
            "message_en": "First name is required",
            "message_ru": "Требуется имя"
        },
        "missing_last_name": {
            "code": "missing_last_name",
            "message_en": "Last name is required",
            "message_ru": "Требуется фамилия"
        },
        "missing_name": {
            "code": "missing_name",
            "message_en": "Event name is required",
            "message_ru": "Требуется название события"
        },
        "missing_date": {
            "code": "missing_date",
            "message_en": "Event date is required",
            "message_ru": "Требуется дата события"
        },
        "missing_event_id": {
            "code": "missing_event_id",
            "message_en": "Event ID is required",
            "message_ru": "Требуется идентификатор события"
        },
        "missing_action": {
            "code": "missing_action",
            "message_en": "Action is required",
            "message_ru": "Требуется действие"
        },
        "missing_user_id": {
            "code": "missing_user_id",
            "message_en": "User ID is required",
            "message_ru": "Требуется идентификатор пользователя"
        },
        "missing_creator": {
            "code": "missing_creator",
            "message_en": "Creator is required for creating a new event",
            "message_ru": "Требуется создатель для создания события"
        },
        "missing_time_start": {
            "code": "missing_time_start",
            "message_en": "Start time is required if end time is provided",
            "message_ru": "Время начала обязательно, если указано время окончания"
        },
        "missing_time_end": {
            "code": "missing_time_end",
            "message_en": "End time is required if start time is provided",
            "message_ru": "Время окончания обязательно, если указано время начала"
        },
        "invalid_action": {
            "code": "invalid_action",
            "message_en": "Invalid action",
            "message_ru": "Недопустимое действие"
        },
        "invalid_first_name": {
            "code": "invalid_first_name",
            "message_en": "First name must only contain letters, hyphens, apostrophes, or spaces, and be 1-50 characters.",
            "message_ru": "Имя может содержать только буквы, дефисы, апострофы или пробелы, длина от 1 до 50 символов."
        },
        "invalid_last_name": {
            "code": "invalid_last_name",
            "message_en": "Last name must only contain letters, hyphens, apostrophes, or spaces, and be 1-50 characters.",
            "message_ru": "Фамилия может содержать только буквы, дефисы, апострофы или пробелы, длина от 1 до 50 символов."
        },
        "invalid_time_order": {
            "code": "invalid_time_order",
            "message_en": "time_start must be earlier than time_end",
            "message_ru": "Время начала должно быть раньше времени окончания"
        },
        "invalid_time_format": {
            "code": "invalid_time_format",
            "message_en": "Invalid time format. Use HH:MM:SS",
            "message_ru": "Неверный формат времени. Используйте HH:MM:SS"
        },
        "invalid_date_format": {
            "code": "invalid_date_format",
            "message_en": "Invalid date format. Use YYYY-MM-DD",
            "message_ru": "Неверный формат даты. Используйте YYYY-MM-DD"
        },
        "invalid_notifications_type": {
            "code": "invalid_notifications_type",
            "message_en": "notifications must be a list",
            "message_ru": "notifications должен быть списком"
        },
        "invalid_notification_entry": {
            "code": "invalid_notification_entry",
            "message_en": 'Each notification must be a dict with "type" and "count"',
            "message_ru": "Каждое уведомление должно быть словарём с ключами 'type' и 'count'"
        },
        "invalid_notification_type": {
            "code": "invalid_notification_type",
            "message_en": 'notification type must be "minutes", "hours", or "days"',
            "message_ru": "Тип уведомления должен быть 'minutes', 'hours' или 'days'"
        },
        "invalid_notification_count": {
            "code": "invalid_notification_count",
            "message_en": "notification count must be a positive integer",
            "message_ru": "Количество уведомлений должно быть положительным числом"
        },
        "invalid_notification_integer": {
            "code": "invalid_notification_integer",
            "message_en": "notification count must be an integer",
            "message_ru": "Количество уведомлений должно быть целым числом"
        },
        "invalid_recurrence_type": {
            "code": "invalid_recurrence_type",
            "message_en": "Invalid recurrence_rule_type. Must be one of daily, weekly, monthly, yearly",
            "message_ru": "Неверный тип повторения. Должен быть 'daily', 'weekly', 'monthly' или 'yearly'"
        },
        "invalid_recurrence_interval": {
            "code": "invalid_recurrence_interval",
            "message_en": "recurrence_rule_interval must be a positive integer and less than or equal to 1000",
            "message_ru": "Интервал повторения должен быть положительным числом не больше 1000"
        },
        "invalid_recurrence_integer": {
            "code": "invalid_recurrence_integer",
            "message_en": "recurrence_rule_interval must be a valid integer",
            "message_ru": "Интервал повторения должен быть целым числом"
        }
    },
    "auth": {
        "user_exists": {
            "code": "user_exists",
            "message_en": "A user with this email already exists",
            "message_ru": "Пользователь с таким email уже существует"
        },
        "invalid_credentials": {
            "code": "invalid_credentials",
            "message_en": "Invalid email or password",
            "message_ru": "Неверный email или пароль"
        },
        "not_logged_in": {
            "code": "not_logged_in",
            "message_en": "User is not logged in",
            "message_ru": "Пользователь не вошёл в систему"
        }
    },
    "event": {
        "event_not_found": {
            "code": "event_not_found",
            "message_en": "Event not found",
            "message_ru": "Событие не найдено"
        },
        "permission_denied": {
            "code": "permission_denied",
            "message_en": "Permission denied. Only the creator can edit/delete this event.",
            "message_ru": "Недостаточно прав. Только создатель может редактировать или удалять событие."
        },
        "invite_not_friends": {
            "code": "invite_not_friends",
            "message_en": "Users are not friends",
            "message_ru": "Пользователи не являются друзьями"
        },
        "already_invited": {
            "code": "already_invited",
            "message_en": "User is already invited",
            "message_ru": "Пользователь уже приглашён"
        },
        "invitation_not_found": {
            "code": "invitation_not_found",
            "message_en": "Invitation not found or already accepted",
            "message_ru": "Приглашение не найдено или уже принято"
        },
        "creator_cannot_leave": {
            "code": "creator_cannot_leave",
            "message_en": "Event creator cannot leave their own event",
            "message_ru": "Создатель события не может покинуть своё событие"
        },
        "user_not_in_event": {
            "code": "user_not_in_event",
            "message_en": "User is not part of the event",
            "message_ru": "Пользователь не является участником события"
        }
    }
}