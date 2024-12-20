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
        self.parents_table = ["names", "surnames", "patronymics", "streets"]

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
            self.id_check()
            query = f"SELECT id FROM {self.parents_table[i-1]} WHERE {col_names[i-1]} = %s"
            print(query)
            self.cursor.execute(query, (values[i-1],))
            id = self.cursor.fetchone()
            if not id:
                self.cursor.execute(f"INSERT INTO {self.parents_table[i-1]} ({col_names[i-1]}) VALUES (%s) RETURNING id", (values[i-1],))
                id = self.cursor.fetchone()[0]
            else:
                id = id[0]
            id_list += [id]

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
            query = f"SELECT id FROM {self.parents_table[i-1]} WHERE {col_names[i-1]} = %s"
            print(query)
            self.cursor.execute(query, (values[i-1],))
            id = self.cursor.fetchone()
            if not id:
                self.cursor.execute(f"INSERT INTO {self.parents_table[i-1]} ({col_names[i-1]}) VALUES (%s) RETURNING id", (values[i-1],))
                id = self.cursor.fetchone()[0]
            else:
                id = id[0]
            id_list += [id]

        self.conn.commit()

    def delete_data(self, item_id):
        """Удалить строку из таблицы."""
        query = "DELETE FROM entries WHERE id = %s"
        self.cursor.execute(query, (item_id,))
        self.conn.commit()


"""self.cursor.close()
        self.conn.close()"""