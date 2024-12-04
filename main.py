import sqlite3
from sqlite3 import Error
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def add_product(conn, name, price):
    sql = ''' INSERT INTO products(name,price)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (name, price))
    conn.commit()
    return cur.lastrowid

def create_order(conn, date, address, customer_name):
    sql = ''' INSERT INTO orders(order_date,delivery_address,customer_name)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (date, address, customer_name))
    conn.commit()
    return cur.lastrowid

def add_order_item(conn, order_id, product_id, quantity):
    sql = ''' INSERT INTO order_items(order_id,product_id,quantity)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (order_id, product_id, quantity))
    conn.commit()
    return cur.lastrowid

def get_all_products(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    return cur.fetchall()

def get_all_orders(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT o.id, o.order_date, o.delivery_address, o.customer_name,
               p.name, oi.quantity, p.price
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        ORDER BY o.id
    """)
    return cur.fetchall()

class ShopApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Магазин")
        self.geometry("800x600")  # Увеличенный размер окна

        self.conn = create_connection("shop_orders.db")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.add_product_frame = ttk.Frame(self.notebook)
        self.create_order_frame = ttk.Frame(self.notebook)
        self.view_orders_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.add_product_frame, text="Добавить товар")
        self.notebook.add(self.create_order_frame, text="Создать заказ")
        self.notebook.add(self.view_orders_frame, text="Просмотр заказов")

        # Настройка весов для create_order_frame
        self.create_order_frame.columnconfigure(0, weight=1)
        self.create_order_frame.columnconfigure(1, weight=1)
        self.create_order_frame.rowconfigure(0, weight=1)
        self.create_order_frame.rowconfigure(1, weight=1)

        self.setup_add_product_frame()
        self.setup_create_order_frame()
        self.setup_view_orders_frame()

    def setup_add_product_frame(self):
        ttk.Label(self.add_product_frame, text="Название товара:").grid(row=0, column=0, padx=5, pady=5)
        self.product_name = ttk.Entry(self.add_product_frame)
        self.product_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.add_product_frame, text="Стоимость товара:").grid(row=1, column=0, padx=5, pady=5)
        self.product_price = ttk.Entry(self.add_product_frame)
        self.product_price.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.add_product_frame, text="Добавить товар", command=self.add_product_gui).grid(row=2, column=0, columnspan=2, pady=10)

    def setup_create_order_frame(self):
        # Левая колонка для информации о заказе
        left_frame = ttk.Frame(self.create_order_frame)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(left_frame, text="Адрес доставки:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.delivery_address = ttk.Entry(left_frame, width=30)
        self.delivery_address.grid(row=1, column=0, padx=5, pady=5)

        ttk.Label(left_frame, text="ФИО клиента:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.customer_name = ttk.Entry(left_frame, width=30)
        self.customer_name.grid(row=3, column=0, padx=5, pady=5)

        # Правая колонка для выбора товаров
        right_frame = ttk.Frame(self.create_order_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Label(right_frame, text="Доступные товары:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.products_listbox = tk.Listbox(right_frame, width=40, height=10)
        self.products_listbox.grid(row=1, column=0, padx=5, pady=5)
        self.update_products_listbox()

        ttk.Label(right_frame, text="Количество:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.quantity = ttk.Entry(right_frame, width=10)
        self.quantity.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        ttk.Button(right_frame, text="Добавить в заказ", command=self.add_to_order).grid(row=4, column=0, padx=5, pady=10)

        # Нижняя часть для сводки заказа и кнопки создания
        bottom_frame = ttk.Frame(self.create_order_frame)
        bottom_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        ttk.Label(bottom_frame, text="Текущий заказ:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.order_summary = tk.Text(bottom_frame, height=5, width=70)
        self.order_summary.grid(row=1, column=0, padx=5, pady=5)
        self.order_summary.config(state=tk.DISABLED)

        # Кнопка "Создать заказ" теперь более заметна
        ttk.Button(bottom_frame, text="Создать заказ", command=self.create_order_gui, style='Accent.TButton').grid(row=2, column=0, padx=5, pady=10)

        self.order_items = []

        # Настройка стиля для кнопки
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 12, 'bold'))

    def setup_view_orders_frame(self):
        self.orders_tree = ttk.Treeview(self.view_orders_frame, columns=("ID", "Дата", "Адрес", "Клиент", "Товар", "Количество", "Цена"), show="headings")
        self.orders_tree.heading("ID", text="ID")
        self.orders_tree.heading("Дата", text="Дата")
        self.orders_tree.heading("Адрес", text="Адрес")
        self.orders_tree.heading("Клиент", text="Клиент")
        self.orders_tree.heading("Товар", text="Товар")
        self.orders_tree.heading("Количество", text="Количество")
        self.orders_tree.heading("Цена", text="Цена")
        self.orders_tree.pack(expand=True, fill="both")

        ttk.Button(self.view_orders_frame, text="Обновить", command=self.update_orders_tree).pack(pady=10)

    def add_product_gui(self):
        name = self.product_name.get()
        price = self.product_price.get()
        if name and price:
            try:
                price = float(price)
                add_product(self.conn, name, price)
                messagebox.showinfo("Успех", "Товар успешно добавлен")
                self.product_name.delete(0, tk.END)
                self.product_price.delete(0, tk.END)
                self.update_products_listbox()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат цены")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля")

    def update_products_listbox(self):
        self.products_listbox.delete(0, tk.END)
        products = get_all_products(self.conn)
        for product in products:
            self.products_listbox.insert(tk.END, f"{product[0]}. {product[1]} - {product[2]} руб.")

    def add_to_order(self):
        selection = self.products_listbox.curselection()
        if selection:
            product_info = self.products_listbox.get(selection[0]).split('.')
            product_id = int(product_info[0])
            product_name = product_info[1].split('-')[0].strip()
            quantity = self.quantity.get()
            if quantity:
                try:
                    quantity = int(quantity)
                    self.order_items.append((product_id, quantity, product_name))
                    messagebox.showinfo("Успех", "Товар добавлен в заказ")
                    self.quantity.delete(0, tk.END)
                    self.update_order_summary()
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверный формат количества")
            else:
                messagebox.showerror("Ошибка", "Введите количество")
        else:
            messagebox.showerror("Ошибка", "Выберите товар")

    def update_order_summary(self):
        self.order_summary.config(state=tk.NORMAL)
        self.order_summary.delete(1.0, tk.END)
        for item in self.order_items:
            self.order_summary.insert(tk.END, f"{item[2]} - {item[1]} шт.\n")
        self.order_summary.config(state=tk.DISABLED)

    def create_order_gui(self):
        address = self.delivery_address.get()
        customer_name = self.customer_name.get()
        if address and customer_name and self.order_items:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order_id = create_order(self.conn, date, address, customer_name)
            for product_id, quantity, _ in self.order_items:
                add_order_item(self.conn, order_id, product_id, quantity)
            messagebox.showinfo("Успех", "Заказ успешно создан")
            self.delivery_address.delete(0, tk.END)
            self.customer_name.delete(0, tk.END)
            self.order_items.clear()
            self.update_order_summary()
            self.update_orders_tree()
        else:
            messagebox.showerror("Ошибка", "Заполните все поля и добавьте товары в заказ")

    def update_orders_tree(self):
        for i in self.orders_tree.get_children():
            self.orders_tree.delete(i)
        orders = get_all_orders(self.conn)
        for order in orders:
            self.orders_tree.insert("", "end", values=order)

if __name__ == '__main__':
    app = ShopApp()
    app.mainloop()