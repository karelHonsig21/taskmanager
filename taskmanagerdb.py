import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

DB_NAME = "task_manager"

# 1. Připojení k databázi
def pripojeni_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345"  # změň dle svého nastavení
        )
        print("✅ Připojení k MySQL serveru bylo úspěšné.")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Chyba při připojování k DB: {err}")
        exit(1)

# 2. Vytvoření databáze a tabulky
def vytvoreni_db_a_tabulky(conn):
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8mb4'")
        conn.database = DB_NAME
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT NOT NULL,
                stav ENUM('Nezahájeno','Probíhá','Hotovo') DEFAULT 'Nezahájeno',
                datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Databáze a tabulka připraveny.")
    except mysql.connector.Error as err:
        print(f"❌ Chyba při vytváření DB/tabulky: {err}")
        exit(1)
    finally:
        cursor.close()

# 3. Hlavní menu
def hlavni_menu(conn):
    while True:
        print("\n===== TASK MANAGER =====")
        print("1 - Přidat úkol")
        print("2 - Zobrazit úkoly")
        print("3 - Aktualizovat úkol")
        print("4 - Odstranit úkol")
        print("5 - Konec programu")

        volba = input("Zadejte číslo volby: ")

        if volba == "1":
            pridat_ukol(conn)
        elif volba == "2":
            zobrazit_ukoly(conn)
        elif volba == "3":
            aktualizovat_ukol(conn)
        elif volba == "4":
            odstranit_ukol(conn)
        elif volba == "5":
            print(">> Program ukončen.")
            break
        else:
            print("❌ Neplatná volba. Zadejte číslo 1-5.")

# 4. Přidání úkolu
def pridat_ukol(conn):
    cursor = conn.cursor()
    while True:
        nazev = input("Zadejte název úkolu: ").strip()
        if nazev == "":
            print("⚠️ Název úkolu nesmí být prázdný.")
            continue

        popis = input("Zadejte popis úkolu: ").strip()
        if popis == "":
            print("⚠️ Popis úkolu nesmí být prázdný.")
            continue

        try:
            cursor.execute(
                "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
                (nazev, popis)
            )
            conn.commit()
            print(f"✅ Úkol '{nazev}' byl přidán.")
            break
        except mysql.connector.Error as err:
            print(f"❌ Chyba při vkládání úkolu: {err}")
            break
    cursor.close()

# 5. Zobrazení úkolů
def zobrazit_ukoly(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, nazev, popis, stav FROM ukoly
            WHERE stav IN ('Nezahájeno','Probíhá')
        """)
        rows = cursor.fetchall()
        if not rows:
            print("📭 Žádné úkoly nejsou k dispozici.")
        else:
            print("\n📋 SEZNAM ÚKOLŮ:")
            for row in rows:
                print(f"ID: {row[0]}, Název: {row[1]}, Stav: {row[3]}")
                print(f"Popis: {row[2]}")
    except mysql.connector.Error as err:
        print(f"❌ Chyba při načítání úkolů: {err}")
    cursor.close()

# 6. Aktualizace úkolu
def aktualizovat_ukol(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nazev, stav FROM ukoly")
        rows = cursor.fetchall()
        if not rows:
            print("📭 Žádné úkoly nejsou k dispozici.")
            cursor.close()
            return

        print("\n🔄 AKTUALIZACE ÚKOLU:")
        for row in rows:
            print(f"ID: {row[0]}, Název: {row[1]}, Stav: {row[2]}")

        while True:
            try:
                id_update = int(input("Zadejte ID úkolu pro změnu stavu: "))
                cursor.execute("SELECT id FROM ukoly WHERE id=%s", (id_update,))
                if cursor.fetchone() is None:
                    print("❌ Neexistující ID. Zkuste znovu.")
                    continue
                break
            except ValueError:
                print("❌ Neplatný vstup – zadejte číslo.")

        print("Vyberte nový stav:\n1 - Probíhá\n2 - Hotovo")
        stav_volba = input("Zadejte volbu: ")
        if stav_volba == "1":
            novy_stav = "Probíhá"
        elif stav_volba == "2":
            novy_stav = "Hotovo"
        else:
            print("❌ Neplatná volba.")
            cursor.close()
            return

        cursor.execute(
            "UPDATE ukoly SET stav=%s WHERE id=%s",
            (novy_stav, id_update)
        )
        conn.commit()
        print("✅ Stav úkolu aktualizován.")
    except mysql.connector.Error as err:
        print(f"❌ Chyba při aktualizaci: {err}")
    cursor.close()

# 7. Odstranění úkolu
def odstranit_ukol(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nazev FROM ukoly")
        rows = cursor.fetchall()
        if not rows:
            print("📭 Žádné úkoly nejsou k odstranění.")
            cursor.close()
            return

        print("\n🗑️ SEZNAM ÚKOLŮ K ODSTRANĚNÍ:")
        for row in rows:
            print(f"ID: {row[0]}, Název: {row[1]}")

        while True:
            try:
                id_delete = int(input("Zadejte ID úkolu k odstranění: "))
                cursor.execute("SELECT id FROM ukoly WHERE id=%s", (id_delete,))
                if cursor.fetchone() is None:
                    print("❌ Neexistující ID. Zkuste znovu.")
                    continue
                break
            except ValueError:
                print("❌ Neplatný vstup – zadejte číslo.")

        cursor.execute("DELETE FROM ukoly WHERE id=%s", (id_delete,))
        conn.commit()
        print("✅ Úkol byl odstraněn.")
    except mysql.connector.Error as err:
        print(f"❌ Chyba při mazání: {err}")
    cursor.close()

# Spuštění programu
if __name__ == "__main__":
    conn = pripojeni_db()
    vytvoreni_db_a_tabulky(conn)
    hlavni_menu(conn)
    conn.close()
