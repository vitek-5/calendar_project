import os
import sys
import subprocess
import secrets
import psycopg2

# Путь к .env
dotenv_path = '.env'

def generate_env_file(db_name, db_user, db_password):
    """Создаёт .env файл с данными пользователя"""
    secret_key = secrets.token_urlsafe(50)

    with open(dotenv_path, 'w', encoding='utf-8') as f:
        f.write(f"DJANGO_SECRET_KEY={secret_key}\n")
        f.write("DJANGO_DEBUG=True\n")
        f.write(f"DB_NAME={db_name}\n")
        f.write(f"DB_USER={db_user}\n")
        f.write(f"DB_PASSWORD={db_password}\n")
        f.write("DB_HOST=localhost\n")
        f.write("DB_PORT=5432\n")

    print("📄 Файл .env создан с указанными параметрами.")

def setup_database(db_name, db_user, db_password):
    """Создаёт базу данных в PostgreSQL"""
    print(f"🗄️ Проверяем или создаём базу данных '{db_name}'...")

    conn = None
    try:
        dsn = (
            f"dbname=postgres "
            f"user={db_user} "
            f"password='{db_password}' "
            f"host=localhost"
        )

        os.environ['PGCLIENTENCODING'] = 'UTF8'
        conn = psycopg2.connect(dsn)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}';")
        exists = cur.fetchone()
        if exists:
            print(f"⚠️ База данных '{db_name}' уже существует.")
        else:
            cur.execute(f"CREATE DATABASE {db_name};")
            print(f"✅ База данных '{db_name}' успешно создана.")

        cur.close()
    except Exception as e:
        print(f"❌ Ошибка при подключении или создании БД: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def install_dependencies():
    """Устанавливает зависимости из requirements.txt"""
    print("📦 Установка зависимостей...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def run_migrations():
    """Выполняет миграции через Django API напрямую"""
    print("🔄 Запуск миграций...")

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_project.settings')
    try:
        import django
        from django.core.management import call_command

        # Явная загрузка настроек
        django.setup()

        # Шаг 1: Создание миграций (makemigrations)
        print("⚙️ Создание миграций...")
        call_command('makemigrations')

        # Шаг 2: Применение миграций (migrate)
        print("⚙️ Применение миграций...")
        call_command('migrate')
        print("✅ Все миграции применены.")
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграций: {e}")
        sys.exit(1)

def collect_static():
    """Собираем статические файлы"""
    print("📎 Собираем статику...")

    # Автоматически создаём папку calendar_app/static, если её нет
    static_dir = os.path.join('calendar_app', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"📁 Папка {static_dir} создана.")

    try:
        import django
        from django.core.management import call_command

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_project.settings')
        django.setup()

        # Создаём static_root, если его нет
        static_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'staticfiles')
        if not os.path.exists(static_root):
            os.makedirs(static_root)
            print(f"📁 Папка {static_root} создана для сбора статики.")

        call_command('collectstatic', '--noinput')
        print("✅ Статика успешно собрана.")
    except Exception as e:
        print(f"❌ Ошибка при сборке статики: {e}")
        sys.exit(1)
        
def check_tables_in_db(db_name, db_user, db_password):
    """Проверяет, существуют ли таблицы в БД"""
    print("🔍 Проверяем наличие таблиц в базе данных...")

    try:
        dsn = (
            f"dbname={db_name} "
            f"user={db_user} "
            f"password='{db_password}' "
            f"host=localhost"
        )
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()

        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        tables = cur.fetchall()
        if tables:
            print("✅ Найденные таблицы:")
            for table in tables:
                print(f" - {table[0]}")
        else:
            print("❌ Таблицы в БД не найдены!")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Ошибка при проверке таблиц: {e}")

if __name__ == "__main__":
    # Переключаем Windows терминал на UTF-8
    if os.name == 'nt':
        os.system('chcp 65001 >nul')

    # Установим текущую директорию как рабочую
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    print("🛠️ Мастер установки проекта «Онлайн-календарь»\n")

    # Шаг 1: Ввод данных пользователем
    db_name = input("Введите имя новой базы данных: ")
    db_user = input("Введите имя пользователя PostgreSQL: ")
    db_password = input("Введите пароль для пользователя PostgreSQL: ")

    # Шаг 2: Генерация .env
    generate_env_file(db_name, db_user, db_password)

    # Шаг 3: Установка зависимостей
    install_dependencies()

    # Шаг 4: Настройка БД
    setup_database(db_name, db_user, db_password)

    # Шаг 5: Миграции
    run_migrations()

    # Шаг 6: Проверка наличия таблиц
    check_tables_in_db(db_name, db_user, db_password)

    # Шаг 7: Сборка статики
    collect_static()

    print("\n🎉 Установка завершена успешно!")
    print("🚀 Теперь вы можете запустить сервер:")
    print("   python manage.py runserver")