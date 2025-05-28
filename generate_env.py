# ./generate_env.py

import os
from django.core.management.utils import get_random_secret_key

dotenv_path = '.env'

if not os.path.exists(dotenv_path):
    with open(dotenv_path, 'w') as f:
        secret_key = get_random_secret_key()
        f.write(f"DJANGO_SECRET_KEY={secret_key}\n")
        f.write("DJANGO_DEBUG=True\n")
        f.write("DB_NAME=НАЗВАНИЕ БАЗЫ ДАННЫХ\n")
        f.write("DB_USER=ИМЯ ПОЛЬЗОВАТЕЛЯ\n")
        f.write("DB_PASSWORD=ВВЕДИТЕ ПАРОЛЬ ПОЛЬЗОВАТЕЛЯ\n")
        f.write("DB_HOST=localhost\n")
        f.write("DB_PORT=5432\n")

    print(f".env создан с новым SECRET_KEY:\n{secret_key}")
else:
    print(".env уже существует.")