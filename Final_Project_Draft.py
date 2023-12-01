import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from datetime import datetime

class Book:
    def __init__(self, book_id, title, author, genre, price, description):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.price = price
        self.description = description

class User:
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.shopping_cart = []

class ShoppingCartItem:
    def __init__(self, book, quantity):
        self.book = book
        self.quantity = quantity

class BookstoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bookstore App")

        # Database connection
        self.conn = sqlite3.connect("bookstore.db")
        self.create_tables()

        # Current user
        self.current_user = None

        # Search bar
        self.search_entry = tk.Entry(root, width=30)
        self.search_entry.grid(row=0, column=0, padx=10, pady=10)

        # Search button
        search_button = tk.Button(root, text="Search", command=self.search_books)
        search_button.grid(row=0, column=1, padx=10, pady=10)

        # Book list
        self.book_listbox = tk.Listbox(root, width=50, height=10)
        self.book_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        self.populate_books()

        # Login button
        login_button = tk.Button(root, text="Login", command=self.login)
        login_button.grid(row=2, column=0, padx=10, pady=10)

        # Register button
        register_button = tk.Button(root, text="Register", command=self.register)
        register_button.grid(row=2, column=1, padx=10, pady=10)

        # Add to cart button
        add_to_cart_button = tk.Button(root, text="Add to Cart", command=self.add_to_cart)
        add_to_cart_button.grid(row=3, column=0, padx=10, pady=10)

        # Shopping cart button
        cart_button = tk.Button(root, text="Shopping Cart", command=self.view_cart)
        cart_button.grid(row=3, column=1, padx=10, pady=10)

        # Checkout button
        checkout_button = tk.Button(root, text="Checkout", command=self.checkout)
        checkout_button.grid(row=4, column=0, columnspan=2, pady=10)

    def create_tables(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    genre TEXT,
                    price REAL,
                    description TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    password TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    total REAL,
                    order_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY,
                    order_id INTEGER,
                    book_id INTEGER,
                    quantity INTEGER,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (book_id) REFERENCES books (id)
                )
            ''')

    def populate_books(self):
        # For simplicity, we're using hardcoded data here. In a real application, you'd load this data from a database.
        books_data = [
            ("Book 1", "Author 1", "Fiction", 20.0, "A captivating story."),
            ("Book 2", "Author 2", "Non-Fiction", 15.0, "An informative read."),
            # Add more books as needed
        ]

        with self.conn:
            cursor = self.conn.cursor()
            cursor.executemany('INSERT INTO books (title, author, genre, price, description) VALUES (?, ?, ?, ?, ?)', books_data)

    def search_books(self):
        query = self.search_entry.get().lower()
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM books WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ?', ('%' + query + '%', '%' + query + '%'))
            results = cursor.fetchall()
            self.display_books(results)

    def display_books(self, book_list):
        self.book_listbox.delete(0, tk.END)
        for book in book_list:
            self.book_listbox.insert(tk.END, f"{book[1]} by {book[2]} - ${book[4]}")

    def login(self):
        username = simpledialog.askstring("Login", "Enter your username:")
        password = simpledialog.askstring("Login", "Enter your password:", show='*')
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user_data = cursor.fetchone()
            if user_data:
                self.current_user = User(*user_data)
                messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            else:
                messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")

    def register(self):
        username = simpledialog.askstring("Register", "Choose a username:")
        password = simpledialog.askstring("Register", "Choose a password:", show='*')
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            self.conn.commit()
            messagebox.showinfo("Registration Successful", f"Account created for {username}!")

    def add_to_cart(self):
        selected_book_index = self.book_listbox.curselection()
        if selected_book_index:
            book_id = selected_book_index[0] + 1  # Adjust for SQLite indexing starting from 1
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
                book_data = cursor.fetchone()
                if book_data:
                    book = Book(*book_data)
                    quantity = simpledialog.askinteger("Quantity", f"How many copies of {book.title} would you like to add to the cart?", minvalue=1)
                    if quantity is not None:
                        self.current_user.shopping_cart.append(ShoppingCartItem(book, quantity))
                        messagebox.showinfo("Added to Cart", f"{quantity} copies of {book.title} added to your shopping cart!")
        else:
            messagebox.showwarning("No Book Selected", "Please select a book before adding to the cart.")

    def view_cart(self):
        if not self.current_user:
            messagebox.showwarning("Not Logged In", "Please log in to view your shopping cart.")
            return

        cart_window = tk.Toplevel(self.root)
        cart_window.title("Shopping Cart")

        if not self.current_user.shopping_cart:
            message_label = tk.Label(cart_window, text="Your shopping cart is empty. Add books to start shopping!")
            message_label.pack(pady=10)
        else:
            for item in self.current_user.shopping_cart:
                item_label = tk.Label(cart_window, text=f"{item.book.title} - Quantity: {item.quantity} - Total: ${item.quantity * item.book.price}")
                item_label.pack(pady=5)

            total_label = tk.Label(cart_window, text=f"Total: ${self.calculate_total()}")
            total_label.pack(pady=10)

            clear_button = tk.Button(cart_window, text="Clear Cart", command=self.clear_cart)
            clear_button.pack(pady=10)

            checkout_button = tk.Button(cart_window, text="Proceed to Checkout", command=self.checkout)
            checkout_button.pack(pady=10)

    def clear_cart(self):
        self.current_user.shopping_cart.clear()
        messagebox.showinfo("Cart Cleared", "Your shopping cart has been cleared.")

    def checkout(self):
        if not self.current_user:
            messagebox.showwarning("Not Logged In", "Please log in to proceed to checkout.")
            return

        if not self.current_user.shopping_cart:
            messagebox.showwarning("Empty Cart", "Your shopping cart is empty. Add books before proceeding to checkout.")
            return

        total_price = self.calculate_total()
        order_confirmation = f"Order Confirmation\n\nUsername: {self.current_user.username}\nTotal: ${total_price}\n\nItems:\n"

        with self.conn:
            cursor = self.conn.cursor()

            # Create a new order
            cursor.execute('INSERT INTO orders (user_id, total, order_date) VALUES (?, ?, ?)',
                           (self.current_user.user_id, total_price, datetime.now()))
            order_id = cursor.lastrowid

            # Add items to the order
            for item in self.current_user.shopping_cart:
                cursor.execute('INSERT INTO order_items (order_id, book_id, quantity) VALUES (?, ?, ?)',
                               (order_id, item.book.book_id, item.quantity))

                order_confirmation += f"{item.book.title} - Quantity: {item.quantity} - Total: ${item.quantity * item.book.price}\n"

            self.conn.commit()

        messagebox.showinfo("Checkout Successful", "Thank you for shopping with us!\n\n" + order_confirmation)
        self.current_user.shopping_cart.clear()

    def calculate_total(self):
        return sum(item.quantity * item.book.price for item in self.current_user.shopping_cart)

if __name__ == "__main__":
    root = tk.Tk()
    app = BookstoreApp(root)
    root.mainloop()
