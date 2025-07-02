import os
import mysql.connector

DB_NAME = os.getenv('TASK_DB_NAME', 'taskmanager')
DB_USER = os.getenv('TASK_DB_USER', 'root')
DB_PASSWORD = os.getenv('TASK_DB_PASSWORD', '')
DB_HOST = os.getenv('TASK_DB_HOST', 'localhost')


def get_connection(test: bool = False):
    """Return a MySQL connection. If ``test`` is True, connect to the test DB."""
    db = f"{DB_NAME}_test" if test else DB_NAME
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=db,
        autocommit=True,
    )


def init_db(test: bool = False) -> None:
    """Create the database and ``ukoly`` table if they do not exist."""
    db = f"{DB_NAME}_test" if test else DB_NAME
    conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
    cur.execute(f"USE {db}")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL,
            popis TEXT NOT NULL,
            stav ENUM('nezahájeno','hotovo','probíhá') DEFAULT 'nezahájeno',
            datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.close()
    conn.close()


def pridat_ukol(conn, nazev: str, popis: str, stav: str = 'nezahájeno') -> int:
    """Insert a new task and return its ID."""
    if not nazev or not popis:
        raise ValueError('Název a popis jsou povinné.')
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s)',
        (nazev, popis, stav)
    )
    task_id = cur.lastrowid
    cur.close()
    return task_id


def aktualizovat_ukol(conn, task_id: int, nazev: str | None = None,
                      popis: str | None = None, stav: str | None = None) -> None:
    """Update task fields given its ID."""
    if nazev is None and popis is None and stav is None:
        raise ValueError('Musí být zadán alespoň jeden parametr k aktualizaci.')
    sets = []
    values = []
    if nazev is not None:
        sets.append('nazev=%s')
        values.append(nazev)
    if popis is not None:
        sets.append('popis=%s')
        values.append(popis)
    if stav is not None:
        sets.append('stav=%s')
        values.append(stav)
    values.append(task_id)
    cur = conn.cursor()
    cur.execute(f"UPDATE ukoly SET {', '.join(sets)} WHERE id=%s", values)
    if cur.rowcount == 0:
        cur.close()
        raise ValueError('Úkol neexistuje.')
    cur.close()


def odstranit_ukol(conn, task_id: int) -> None:
    """Delete task by ID."""
    cur = conn.cursor()
    cur.execute('DELETE FROM ukoly WHERE id=%s', (task_id,))
    if cur.rowcount == 0:
        cur.close()
        raise ValueError('Úkol neexistuje.')
    cur.close()


def get_ukol(conn, task_id: int):
    """Retrieve task by ID."""
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM ukoly WHERE id=%s', (task_id,))
    row = cur.fetchone()
    cur.close()
    return row


if __name__ == '__main__':
    init_db()
    conn = get_connection()
    while True:
        print('\n===== TASK MANAGER =====')
        print('1 - Přidat úkol')
        print('2 - Aktualizovat úkol')
        print('3 - Odstranit úkol')
        print('4 - Konec programu')
        choice = input('Zadejte číslo volby: ').strip()
        try:
            if choice == '1':
                nazev = input('Zadejte název úkolu: ').strip()
                popis = input('Zadejte popis úkolu: ').strip()
                stav = input('Zadejte stav (nezahájeno/hotovo/probíhá) [nezahájeno]: ').strip() or 'nezahájeno'
                pid = pridat_ukol(conn, nazev, popis, stav)
                print(f'✅ Úkol uložen s ID {pid}.')
            elif choice == '2':
                tid = int(input('Zadejte ID úkolu: '))
                nazev = input('Nový název (enter pro ponechání): ').strip() or None
                popis = input('Nový popis (enter pro ponechání): ').strip() or None
                stav = input('Nový stav (enter pro ponechání): ').strip() or None
                aktualizovat_ukol(conn, tid, nazev, popis, stav)
                print('✅ Úkol aktualizován.')
            elif choice == '3':
                tid = int(input('Zadejte ID úkolu: '))
                odstranit_ukol(conn, tid)
                print('✅ Úkol odstraněn.')
            elif choice == '4':
                break
            else:
                print('Neplatná volba.')
        except Exception as e:
            print(f'❌ Chyba: {e}')
    conn.close()
