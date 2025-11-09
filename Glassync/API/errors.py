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
        "invalid_first_name": {
            "code": "invalid_first_name",
            "message_en": "First name must only contain letters, hyphens, apostrophes, or spaces, and be 1-50 characters.",
            "message_ru": "Имя может содержать только буквы, дефисы, апострофы или пробелы, длина от 1 до 50 символов."
        },
        "invalid_last_name": {
            "code": "invalid_last_name",
            "message_en": "Last name must only contain letters, hyphens, apostrophes, or spaces, and be 1-50 characters.",
            "message_ru": "Фамилия может содержать только буквы, дефисы, апострофы или пробелы, длина от 1 до 50 символов."
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
    }
}