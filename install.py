import os
import sys
import subprocess
import secrets
import shutil
import webbrowser

# Константы
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(PROJECT_ROOT, 'venv')
DOTENV_PATH = os.path.join(PROJECT_ROOT, '.env')
REQUIREMENTS_PATH = os.path.join(PROJECT_ROOT, 'requirements.txt')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'calendar_app', 'static')
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

def check_venv():
    """Проверяет, запущен ли скрипт внутри виртуального окружения"""
    return sys.prefix != sys.base_prefix

def create_virtualenv():
    """Создаёт venv и перезапускает install.py внутри него"""
    # Создаём venv, если его нет
    if not os.path.exists(VENV_DIR):
        print("📁 Создаём виртуальное окружение...")
        subprocess.check_call([sys.executable, '-m', 'venv', VENV_DIR])
    else:
        print("📁 Виртуальное окружение уже существует.")

    # Перезапуск в venv
    if os.name == 'nt':
        activate_script = os.path.join(VENV_DIR, 'Scripts', 'activate.bat')
        python_executable = os.path.join(VENV_DIR, 'Scripts', 'python.exe')
    else:
        activate_script = os.path.join(VENV_DIR, 'bin', 'activate')
        python_executable = os.path.join(VENV_DIR, 'bin', 'python')

    cmd = f'"{python_executable}" "{os.path.abspath(sys.argv[0])}"'
    if os.name == 'nt':
        os.system(f'call "{activate_script}" && {cmd}')
    else:
        os.system(f'source "{activate_script}" && exec {cmd}')

    sys.exit(0)
    
def generate_env_file(db_name, db_user, db_password):
    """Создаёт .env файл с данными пользователя"""
    secret_key = secrets.token_urlsafe(50)

    with open(DOTENV_PATH, 'w', encoding='utf-8') as f:
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
    try:
        import psycopg2
    except ImportError:
        print("❌ Не удалось импортировать psycopg2 — возможно, нужно запустить скрипт внутри venv")
        sys.exit(1)

    print(f"🗄️ Проверяем или создаём базу данных '{db_name}'...")

    conn = None
    try:
        dsn = (
            f"dbname=postgres "
            f"user={db_user} "
            f"password='{db_password}' "
            f"host=localhost"
        )

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
        print(f"❌ Ошибка при подключении к PostgreSQL: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def install_dependencies():
    """Устанавливает зависимости из requirements.txt в виртуальное окружение"""
    pip_path = os.path.join(VENV_DIR, 'Scripts', 'pip') if os.name == 'nt' else os.path.join(VENV_DIR, 'bin', 'pip')

    print("📦 Установка зависимостей...")
    try:
        subprocess.check_call([pip_path, 'install', '-r', REQUIREMENTS_PATH])
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке зависимостей: {e}")
        sys.exit(1)

def run_migrations():
    """Выполняет миграции через Django API напрямую"""
    print("🔄 Выполняем миграции...")

    try:
        import django
        from django.core.management import call_command

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_project.settings')
        django.setup()

        print("⚙️ Создание миграций...")
        call_command('makemigrations', 'calendar_app')

        print("⚙️ Применение миграций...")
        call_command('migrate') 
        print("✅ Все миграции выполнены.")
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграций: {e}")
        sys.exit(1)

def collect_static():
    """Собираем статические файлы"""
    print("📎 Собираем статику...")

    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)
        print(f"📁 Папка {STATIC_DIR} создана для статики.")

    try:
        import django
        from django.core.management import call_command

        django.setup()
        call_command('collectstatic', '--noinput')
        print("✅ Статика собрана.")
    except Exception as e:
        print(f"⚠️ Не удалось собрать статику: {e}")

def check_tables_in_db(db_name, db_user, db_password):
    """Проверяет, существуют ли нужные таблицы в БД"""
    print("🔍 Проверяем наличие таблиц в БД...")

    try:
        import psycopg2
    except ImportError:
        print("❌ Для проверки БД нужно установить psycopg2 вручную:")
        print("   pip install psycopg2-binary")
        sys.exit(1)

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
            WHERE table_schema = 'public'
        """)
        tables = [t[0] for t in cur.fetchall()]
        target_tables = ['calendar_app_calendar', 'calendar_app_event']

        missing = [t for t in target_tables if t not in tables]
        if missing:
            print(f"❌ Не хватает таблиц: {', '.join(missing)}")
        else:
            print("✅ Все таблицы присутствуют в БД:")
            for table in tables:
                print(f" - {table}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Ошибка при проверке таблиц: {e}")

def main():
    # Переключаем Windows терминал на UTF-8
    if os.name == 'nt':
        os.system('chcp 65001 >nul')

    print("🛠️ Мастер установки проекта «Онлайн-календарь»\n")

    # Шаг 1: Ввод данных пользователем
    db_name = input("Введите имя новой/существующей базы данных: ")
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

    # Шаг 6: Сборка статики
    collect_static()

    # Шаг 7: Проверка таблиц
    check_tables_in_db(db_name, db_user, db_password)

    print("\n🎉 Установка завершена успешно!")
    print("📌 Теперь вы можете запустить сервер.")

    # Новый шаг: предложить запуск сервера
    while True:
        choice = input("\nЗапустить сервер Django? (y/n): ").strip().lower()
        if choice in ('y', 'yes', 'д', 'да'):
            print("\n🚀 Запуск сервера Django...")
            print("📌 Открываем браузер...")
            webbrowser.open("http://127.0.0.1:8000/create/")

            # Передаём управление напрямую subprocess
            os.execv(sys.executable, [sys.executable, 'manage.py', 'runserver'])

        elif choice in ('n', 'no', 'н', 'нет'):
            print("\n📌 Чтобы запустить сервер позже, используйте команду:")
            print("   python manage.py runserver")
            print("🌐 Сервер будет доступен по адресу: http://127.0.0.1:8000/create/")
            break
        else:
            print("⚠️ Введите 'y' или 'n'")

if __name__ == "__main__":
    if not check_venv():
        create_virtualenv()
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n🛑 Операция прервана пользователем.")
            print("📌 Чтобы запустить сервер позже, используйте:")
            print("   python manage.py runserver")
            sys.exit(0)