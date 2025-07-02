import unittest
import mysql.connector
from taskmanager import init_db, get_connection, pridat_ukol, aktualizovat_ukol, odstranit_ukol, get_ukol

class TaskManagerTestCase(unittest.TestCase):
    def setUp(self):
        init_db(test=True)
        self.conn = get_connection(test=True)
        cur = self.conn.cursor()
        cur.execute('DELETE FROM ukoly')
        self.conn.commit()
        cur.close()

    def tearDown(self):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM ukoly')
        self.conn.commit()
        cur.close()
        self.conn.close()

    def test_pridat_ukol_positive(self):
        tid = pridat_ukol(self.conn, 'Test', 'Popis', 'nezahájeno')
        row = get_ukol(self.conn, tid)
        self.assertIsNotNone(row)
        self.assertEqual(row['nazev'], 'Test')
        self.assertEqual(row['popis'], 'Popis')

    def test_pridat_ukol_negative(self):
        with self.assertRaises(ValueError):
            pridat_ukol(self.conn, '', '')

    def test_aktualizovat_ukol_positive(self):
        tid = pridat_ukol(self.conn, 'T', 'P')
        aktualizovat_ukol(self.conn, tid, nazev='N', stav='hotovo')
        row = get_ukol(self.conn, tid)
        self.assertEqual(row['nazev'], 'N')
        self.assertEqual(row['stav'], 'hotovo')

    def test_aktualizovat_ukol_negative(self):
        with self.assertRaises(ValueError):
            aktualizovat_ukol(self.conn, 9999, nazev='x')

    def test_odstranit_ukol_positive(self):
        tid = pridat_ukol(self.conn, 'T', 'P')
        odstranit_ukol(self.conn, tid)
        row = get_ukol(self.conn, tid)
        self.assertIsNone(row)

    def test_odstranit_ukol_negative(self):
        with self.assertRaises(ValueError):
            odstranit_ukol(self.conn, 9999)

if __name__ == '__main__':
    unittest.main()
