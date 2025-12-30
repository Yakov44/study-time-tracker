import os.path
import time
from datetime import datetime, timedelta
from sqlite3 import connect


GOALS = {
    'week': 12,
    'month': 50,
    'year': 500
}


def init_db():
    """Создает базу данных и таблицу, если их нет."""
    conn = connect('my_study_time.db')
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS
    sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                duration_minutes REAL
            )
    ''')
    conn.commit()
    conn.close()


def save_sessions(minutes):
    """Сохраняет результат сессии в базу данных"""
    conn = connect('my_study_time.db')
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('INSERT INTO sessions (date, duration_minutes) VALUES (?, ?)',
                    (today, minutes))
    conn.commit()
    conn.close()


def get_stats(period_key):
    """Считает прогресс за выбранный период"""
    conn = connect('my_study_time.db')
    cursor = conn.cursor()

    today = datetime.now()
    if period_key == 'week':
        start_date = today - timedelta(days=7)
        label = 'НЕДЕЛЯ'
    elif period_key == 'month':
        start_date = today - timedelta(days=30)
        label = 'MEСЯЦ'
    else:
        start_date = today - timedelta(days=365)
        label = 'ГОД'

    start_date_str = start_date.strftime('%Y-%m-%d')
    cursor.execute('SELECT SUM(duration_minutes) FROM sessions WHERE date >= ?',
                   (start_date_str,))
    total_minutes = cursor.fetchone()[0] or 0
    conn.close()

    total_hours = total_minutes / 60
    goal = GOALS[period_key]

    percent = min((total_hours / goal) * 100, 100)
    bar_length = 20
    filled = int(bar_length * percent // 100)
    bar = ' ' * filled + '-' * (bar_length - filled)

    print(f'\n[{label}] {total_hours:.2f} / {goal} ч.')
    print(f'Прогресс: [ {bar} ] {percent:.1f}%')


def write_to_txt_log(text):
    """Записывает короткий отчет в текстовый файл"""
    today = datetime.now().strftime('%d.%m.%Y')
    with open('study_journal.txt', 'a', encoding='utf-8') as f:
        f.write(f'{today}  |  {text}\n')


def read_txt_log():
    """Читает текстовый файл"""
    if not os.path.exists('study_journal.txt'):
        print('Журнал пуст. Проведите учебную сессию!')
        return

    print('--- Учебный журнал ---')
    with open('study_journal.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            print(line.strip())


def start_timer():
    """Запускает счетчик времени с возможностью паузы"""
    print('\n' + '=' * 30)
    print('Таймер запущен!')
    print('\nКоманды: [p] - пауза, [r] - продолжить, [s] - стоп')

    total_seconds = 0
    is_running = True
    start_time = time.time()

    while True:
        if is_running:
            cmd = input('Идет запись.. \nКоманда: ').lower().strip()

            if cmd == 'p':
                total_seconds += time.time() - start_time
                is_running = False

            elif cmd == 's' or cmd == '':
                total_seconds += time.time() - start_time

        else:
            cmd = input(
                f"|| НА ПАУЗЕ (всего {total_seconds / 60:.2f} мин). Введите 'r' для продолжения или 's' для стопа: ").lower().strip()
            if cmd == 'r':
                start_time = time.time()
                is_running = True
                print(">> ТАЙМЕР ВОЗОБНОВЛЕН")
            elif cmd == 's':
                break

    report = input('Что сегодня кодил? Что выучил?\n'
                   '')
    duration_minutes = total_seconds / 60

    save_sessions(duration_minutes)
    write_to_txt_log(report)

    print(f'\nСессия завершена! Чистое время: {duration_minutes:.2f} мин.')


def main():
    init_db()
    while True:
        print('--- ТРЕКЕР УЧЕБЫ --- ')
        print('1. Начать учится')
        print('2. Статистика за неделю')
        print('3. Статистика за месяц')
        print('4. Статистика за год')
        print('5. Прочитать журнал')
        print('0. Выход')

        choice = input('\nВыбери действие: ')

        if choice == '1':
            start_timer()
        elif choice == '2':
            get_stats('week')
        elif choice == '3':
            get_stats('month')
        elif choice == '4':
            get_stats('year')
        elif choice == '5':
            read_txt_log()
        elif choice == '0':
            print('Надеюсь это было продуктивно. ПОКА!')
            break


if __name__ == '__main__':
    main()