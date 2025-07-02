# Import potřebných knihoven
import mysql.connector  # knihovna pro připojení k MySQL
from mysql.connector import errorcode  # pro zachytávání specifických chyb
from datetime import datetime  # import pro práci s datumem a časem (zde nepoužit, ale může být při rozšíření)

# Název databáze
DB_NAME = "task_manager"

# Funkce 1: Připojení k databázi
def pripojeni_db():
    try:
        # Navázání připojení k MySQL serveru (zadej své přihlašovací údaje)
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345"  # zde uprav podle svého nastavení
        )
        print("✅ Připojení k MySQL serveru bylo úspěšné.")
        return conn  # funkce vrací objekt připojení pro další práci
    except mysql.connector.Error as err:
        # Pokud připojení selže, vypíše chybovou hlášku a ukončí program
        print(f"❌ Chyba při připojování k DB: {err}")
        exit(1)

# Funkce 2: Vytvoření databáze a tabulky
def vytvoreni_db_a_tabulky(conn):
    cursor = conn.cursor()  # vytvoření kurzoru pro SQL dotazy
    try:
        # Vytvoření databáze, pokud ještě neexistuje
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8mb4'")
        conn.database = DB_NAME  # přepnutí na právě vytvořenou databázi

        # Vytvoření tabulky ukoly, pokud ještě neexistuje
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,  # unikátní ID úkolu
                nazev VARCHAR(255) NOT NULL,        # název úkolu
                popis TEXT NOT NULL,                # popis úkolu
                stav ENUM('Nezahájeno','Probíhá','Hotovo') DEFAULT 'Nezahájeno',  # stav úkolu
                datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP  # datum a čas vytvoření úkolu
            )
        """)
        print("✅ Databáze a tabulka připraveny.")
    except mysql.connector.Error as err:
        # Zachytí chybu při vytváření databáze/tabulky a ukončí program
        print(f"❌ Chyba při vytváření DB/tabulky: {err}")
        exit(1)
    finally:
        cursor.close()  # vždy uzavře kurzor

# Funkce 3: Hlavní menu programu
def hlavni_menu(conn):
    while True:
        # Zobrazení hlavního menu
        print("\n===== TASK MANAGER =====")
        print("1 - Přidat úkol")
        print("2 - Zobrazit úkoly")
        print("3 - Aktualizovat úkol")
        print("4 - Odstranit úkol")
        print("5 - Konec programu")

        volba = input("Zadejte číslo volby: ")

        # Vyhodnocení volby uživatele a volání příslušných funkcí
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
            break  # ukončení cyklu = konec programu
        else:
            print("❌ Neplatná volba. Zadejte číslo 1-5.")

# Funkce 4: Přidání úkolu do databáze
def pridat_ukol(conn):
    cursor = conn.cursor()
    while True:
        # Získání názvu úkolu od uživatele
        nazev = input("Zadejte název úkolu: ").strip()
        if nazev == "":
            print("⚠️ Název úkolu nesmí být prázdný.")
            continue

        # Získání popisu úkolu
        popis = input("Zadejte popis úkolu: ").strip()
        if popis == "":
            print("⚠️ Popis úkolu nesmí být prázdný.")
            continue

        try:
            # Vložení úkolu do tabulky ukoly
            cursor.execute(
                "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
                (nazev, popis)
            )
            conn.commit()  # uložení změn do DB
            print(f"✅ Úkol '{nazev}' byl přidán.")
            break
        except mysql.connector.Error as err:
            # Zachycení chyby při vkládání úkolu
            print(f"❌ Chyba při vkládání úkolu: {err}")
            break
    cursor.close()

# Funkce 5: Zobrazení úkolů (filtr na Nezahájeno a Probíhá)
def zobrazit_ukoly(conn):
    cursor = conn.cursor()
    try:
        # Výběr úkolů se stavem Nezahájeno nebo Probíhá
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
        # Zachycení chyby při načítání úkolů
        print(f"❌ Chyba při načítání úkolů: {err}")
    cursor.close()

# Funkce 6: Aktualizace stavu úkolu
def aktualizovat_ukol(conn):
    cursor = conn.cursor()
    try:
        # Načtení všech úkolů pro zobrazení uživateli
        cursor.execute("SELECT id, nazev, stav FROM ukoly")
        rows = cursor.fetchall()
        if not rows:
            print("📭 Žádné úkoly nejsou k dispozici.")
            cursor.close()
            return

        # Zobrazení úkolů s ID a aktuálním stavem
        print("\n🔄 AKTUALIZACE ÚKOLU:")
        for row in rows:
            print(f"ID: {row[0]}, Název: {row[1]}, Stav: {row[2]}")

        # Výběr úkolu k aktualizaci podle ID
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

        # Výběr nového stavu úkolu
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

        # Aktualizace stavu v databázi
        cursor.execute(
            "UPDATE ukoly SET stav=%s WHERE id=%s",
            (novy_stav, id_update)
        )
        conn.commit()
        print("✅ Stav úkolu aktualizován.")
    except mysql.connector.Error as err:
        print(f"❌ Chyba při aktualizaci: {err}")
    cursor.close()

# Funkce 7: Odstranění úkolu
def odstranit_ukol(conn):
    cursor = conn.cursor()
    try:
        # Načtení všech úkolů pro zobrazení uživateli
        cursor.execute("SELECT id, nazev FROM ukoly")
        rows = cursor.fetchall()
        if not rows:
            print("📭 Žádné úkoly nejsou k odstranění.")
            cursor.close()
            return

        # Zobrazení seznamu úkolů s ID
        print("\n🗑️ SEZNAM ÚKOLŮ K ODSTRANĚNÍ:")
        for row in rows:
            print(f"ID: {row[0]}, Název: {row[1]}")

        # Výběr úkolu k odstranění podle ID
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

        # Odstranění úkolu z databáze
        cursor.execute("DELETE FROM ukoly WHERE id=%s", (id_delete,))
        conn.commit()
        print("✅ Úkol byl odstraněn.")
    except mysql.connector.Error as err:
        print(f"❌ Chyba při mazání: {err}")
    cursor.close()

# Spuštění hlavního programu
if __name__ == "__main__":
    conn = pripojeni_db()  # připojení k DB
    vytvoreni_db_a_tabulky(conn)  # vytvoření DB a tabulky, pokud ještě neexistují
    hlavni_menu(conn)  # spuštění hlavního menu (nekonečný cyklus dokud neukončíš program)
    conn.close()  # uzavření připojení k DB po ukončení programu
