import psycopg2 as ps
import loguru
from PyQt5.QtWidgets import QMessageBox


class DBManager:
    def __init__(self, dbname, user, password, host, port):
        self.conn = ps.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()
        self.tables_names = ["names", "surnames", "patronymics", "streets", "entries"]

    def fetch_data(self):
        query = """select 
                    entries.entry_id,
                    names.name, 
                    surnames.surname,
                    patronymics.patronymic, 
                    streets.street,
                    entries.building,
                    entries.apartment,
                    entries.phone
                from entries
                join names on entries.name_id = names.id
                join surnames on entries.surname_id = surnames.id
                join patronymics on entries.patronymic_id = patronymics.id
                join streets on entries.street_id = streets.id"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        col_names = [desc[0] for desc in self.cursor.description]
        return rows, col_names

    def id_check(self, parent_table, col_name, value):
        query = f"SELECT id FROM {parent_table} WHERE {col_name} = %s"
        print(query)
        self.cursor.execute(query, (value,))
        id = self.cursor.fetchone()
        if not id:
            self.cursor.execute(
                f"INSERT INTO {parent_table} ({col_name}) VALUES (%s) RETURNING id",
                (value,))
            id = self.cursor.fetchone()[0]
        else:
            id = id[0]
        return id
    def insert_data(self, data):
        col_names = list(data.keys())
        values = list(data.values())
        id_list = []
        for i in range(1, len(col_names[:5])):
            id_list += [self.id_check(self.tables_names[i - 1], col_names[i - 1], values[i - 1])]

        self.cursor.execute("""
                            INSERT INTO entries (name_id, surname_id, patronymic_id, street_id, building, apartment, phone)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (id_list[0], id_list[1], id_list[2], id_list[3], values[4], values[5], values[6]))
        self.conn.commit()


    def update_data(self, data):
        col_names = list(data.keys())
        values = list(data.values())
        id_list = []
        for i in range(1, len(col_names[:5])):
            id_list += [self.id_check(self.tables_names[i - 1], col_names[i - 1], values[i - 1])]

        self.cursor.execute("""
            UPDATE entries
            SET name_id = %s, surname_id = %s, patronymic_id = %s, street_id = %s, 
            building = %s, apartment = %s, phone = %s
            WHERE entry_id = %s""",
            (id_list[0], id_list[1], id_list[2], id_list[3], values[4], values[5], values[6], values[7]))

        for i in range(1, len(col_names[:5])):
            print(col_names[i-1], values[i-1])

        for i in range(1, len(col_names[:5])):
            print(i)
            print(f"DELETE FROM {self.tables_names[i - 1]} WHERE {col_names[i - 1]} = %s AND id NOT IN (SELECT {col_names[i - 1]}_id FROM entries)")
            query = f"DELETE FROM {self.tables_names[i - 1]} WHERE {col_names[i - 1]} = %s AND id NOT IN (SELECT {col_names[i - 1]}_id FROM entries)"
            self.cursor.execute(query, (values[i-1],))
            print(values[i-1])

        self.conn.commit()

    def delete_data(self, data):
        col_names = list(data.keys())
        print(col_names)
        values = list(data.values())
        query = f"DELETE FROM entries WHERE entry_id = %s"
        self.cursor.execute(query, (values[-1],))
        for i in range(0, len(self.tables_names)-1):
            query = f"DELETE FROM {self.tables_names[i]} WHERE {col_names[i]} = %s AND id NOT IN (SELECT {col_names[i]}_id FROM entries)"
            print(query)
            print(values[i])
            self.cursor.execute(query, (values[i],))
        self.conn.commit()

    def clear_data(self):
        self.cursor.execute(
            "DELETE FROM entries;"
            "DELETE FROM names;"
            "DELETE FROM surnames;"
            "DELETE FROM patronymics;"
            "DELETE FROM streets;"
            
            "ALTER SEQUENCE names_id_seq RESTART WITH 1;"
            "ALTER SEQUENCE surnames_id_seq RESTART WITH 1;"
            "ALTER SEQUENCE patronymics_id_seq RESTART WITH 1;"
            "ALTER SEQUENCE streets_id_seq RESTART WITH 1;"
            "ALTER SEQUENCE entries_id_seq RESTART WITH 1;"
        )
        self.conn.commit()
