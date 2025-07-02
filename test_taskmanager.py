# Import knihoven
import pytest  # framework pro testování
import mysql.connector  # knihovna pro připojení k MySQL
import os  # pro práci s proměnnými prostředí
from taskmanagerdb import vytvoreni_db_a_tabulky  # funkce pro vytvoření DB a tabulky

# ================================
# KONFIGURACE DB
# ================================

# Možnost volby databáze pomocí proměnné prostředí TEST_DB:
# - pokud TEST_DB je nastavena na '1', použije se testovací DB
# - jinak se použije hlavní DB

USE_TEST_DB = os.getenv("TEST_DB") == "1"

# Název DB dle volby
DB_NAME = "task_manager_test" if USE_TEST_DB else "task_manager"

# ================================
# FIXTURES – společné pro více testů
# ================================

@pytest.fixture(scope="module")
def db_conn():
    """
    Fixture pro připojení k DB.
    Spustí se jednou pro celý soubor (scope="module").
    """
    # Vytvoření připojení k databázi (hlavní nebo testovací)
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",  # Změň dle svého hesla
        database=DB_NAME
    )
    # Vytvoření DB a tabulky, pokud ještě neexistují
    vytvoreni_db_a_tabulky(conn)
    yield conn  # vrací připojení testům
    conn.close()  # po skončení všech testů zavře připojení

@pytest.fixture
def cursor(db_conn):
    """
    Fixture pro kurzor – vytvoří nový kurzor před testem a smaže testovací data po testu.
    """
    cursor = db_conn.cursor()  # vytvoření kurzoru
    yield cursor  # vrácení kurzoru testu

    # Čištění testovacích dat po testu – smaže úkoly začínající TEST_
    cursor.execute("DELETE FROM ukoly WHERE nazev LIKE 'TEST_%'")
    db_conn.commit()
    cursor.close()  # uzavření kurzoru

# ================================
# TESTY PRO pridat_ukol()
# ================================

def test_pridat_ukol_pozitivni(cursor, db_conn):
    """
    Pozitivní test: přidání platného úkolu.
    Ověří, že úkol se správně uloží do DB.
    """
    nazev = "TEST_ADD_OK"
    popis = "Testovací popis"

    # Vložení úkolu do DB
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s,%s)", (nazev, popis))
    db_conn.commit()

    # Ověření, že úkol existuje v DB
    cursor.execute("SELECT * FROM ukoly WHERE nazev=%s", (nazev,))
    result = cursor.fetchone()
    assert result is not None, "Úkol by měl být přidán."

def test_pridat_ukol_negativni(cursor, db_conn):
    """
    Negativní test: přidání úkolu bez názvu (NULL).
    Ověří, že DB vyhodí chybu.
    """
    popis = "Testovací popis"

    # Očekává chybu při pokusu vložit NULL do sloupce nazev
    with pytest.raises(mysql.connector.Error):
        cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s,%s)", (None, popis))
        db_conn.commit()

# ================================
# TESTY PRO aktualizovat_ukol()
# ================================

def test_aktualizovat_ukol_pozitivni(cursor, db_conn):
    """
    Pozitivní test: změna stavu existujícího úkolu na 'Hotovo'.
    """
    nazev = "TEST_UPDATE_OK"
    popis = "Test"

    # Vložení testovacího úkolu
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s,%s)", (nazev, popis))
    db_conn.commit()

    # Získání ID vloženého úkolu
    cursor.execute("SELECT id FROM ukoly WHERE nazev=%s", (nazev,))
    id_ukol = cursor.fetchone()[0]

    # Aktualizace stavu úkolu na 'Hotovo'
    cursor.execute("UPDATE ukoly SET stav=%s WHERE id=%s", ("Hotovo", id_ukol))
    db_conn.commit()

    # Ověření změny
    cursor.execute("SELECT stav FROM ukoly WHERE id=%s", (id_ukol,))
    stav = cursor.fetchone()[0]
    assert stav == "Hotovo", "Stav úkolu by měl být aktualizován na Hotovo."

def test_aktualizovat_ukol_negativni(cursor, db_conn):
    """
    Negativní test: pokus o aktualizaci neexistujícího úkolu.
    Ověří, že žádný řádek nebyl upraven.
    """
    id_neexistuje = -1  # ID, které neexistuje v DB

    cursor.execute("UPDATE ukoly SET stav=%s WHERE id=%s", ("Hotovo", id_neexistuje))
    db_conn.commit()
    assert cursor.rowcount == 0, "Nemělo by být aktualizováno žádné ID."

# ================================
# TESTY PRO odstranit_ukol()
# ================================

def test_odstranit_ukol_pozitivni(cursor, db_conn):
    """
    Pozitivní test: odstranění existujícího úkolu.
    Ověří, že úkol byl odstraněn z DB.
    """
    nazev = "TEST_DELETE_OK"
    popis = "Test"

    # Vložení testovacího úkolu
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s,%s)", (nazev, popis))
    db_conn.commit()

    # Získání ID vloženého úkolu
    cursor.execute("SELECT id FROM ukoly WHERE nazev=%s", (nazev,))
    id_ukol = cursor.fetchone()[0]

    # Odstranění úkolu
    cursor.execute("DELETE FROM ukoly WHERE id=%s", (id_ukol,))
    db_conn.commit()

    # Ověření, že úkol již neexistuje
    cursor.execute("SELECT * FROM ukoly WHERE id=%s", (id_ukol,))
    result = cursor.fetchone()
    assert result is None, "Úkol by měl být odstraněn."

def test_odstranit_ukol_negativni(cursor, db_conn):
    """
    Negativní test: pokus o odstranění neexistujícího úkolu.
    Ověří, že žádný řádek nebyl smazán.
    """
    id_neexistuje = -1  # ID, které v DB není

    cursor.execute("DELETE FROM ukoly WHERE id=%s", (id_neexistuje,))
    db_conn.commit()
    assert cursor.rowcount == 0, "Nemělo by být odstraněno žádné ID."
