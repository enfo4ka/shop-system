import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = "shop_orders.db"

    sql_create_products_table = """CREATE TABLE IF NOT EXISTS products (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    price real NOT NULL
                                );"""

    sql_create_orders_table = """CREATE TABLE IF NOT EXISTS orders (
                                    id integer PRIMARY KEY,
                                    order_date text NOT NULL,
                                    delivery_address text NOT NULL,
                                    customer_name text NOT NULL
                                );"""

    sql_create_order_items_table = """CREATE TABLE IF NOT EXISTS order_items (
                                        id integer PRIMARY KEY,
                                        order_id integer NOT NULL,
                                        product_id integer NOT NULL,
                                        quantity integer NOT NULL,
                                        FOREIGN KEY (order_id) REFERENCES orders (id),
                                        FOREIGN KEY (product_id) REFERENCES products (id)
                                    );"""

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_products_table)
        create_table(conn, sql_create_orders_table)
        create_table(conn, sql_create_order_items_table)
        conn.close()
        print("База данных успешно создана.")
    else:
        print("Ошибка! Не удалось создать соединение с базой данных.")

if __name__ == '__main__':
    main()
