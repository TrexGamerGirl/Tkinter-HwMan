import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import csv

CSV_FILE = "inventory.csv"

# Refresh treeview display
def refresh_tree(tree, items):
    for i in tree.get_children():
        tree.delete(i)

    for item in items:
        tree.insert("", tk.END, values=(
            item["id"],
            item["category"],
            item["desc"],
            item["price"],
            item["qty"]
        ))


# Clear input form
def clear_form(id_var, category_var, desc_var, price_var, qty_var):
    id_var.set("")
    category_var.set("Shoes")
    desc_var.set("")
    price_var.set("")
    qty_var.set("")

# Save full list to CSV
def save_all_to_csv(filename, items):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        for item in items:
            writer.writerow([
                item["id"],
                item["category"],
                item["desc"],
                item["price"],
                item["qty"]
            ])

# Load items from CSV
def load_from_csv(filename):
    items = []
    try:
        with open(filename, mode="r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 5:
                    items.append({
                        "id": row[0],
                        "category": row[1],
                        "desc": row[2],
                        "price": row[3],
                        "qty": row[4]
                    })
    except FileNotFoundError:
        pass
    return items
# Main UI
def main():

    items = load_from_csv(CSV_FILE)

    root = tk.Tk()
    root.title("Clothing Inventory System")
    root.geometry("900x500")

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    # Tkinter variables
    id_var = tk.StringVar()
    category_var = tk.StringVar(value="Shoes")
    desc_var = tk.StringVar()
    price_var = tk.StringVar()
    qty_var = tk.StringVar()

    # Labels
    ttk.Label(frame, text="ID").grid(row=0, column=0, sticky="w")
    ttk.Label(frame, text="Category").grid(row=1, column=0, sticky="w")
    ttk.Label(frame, text="Description").grid(row=2, column=0, sticky="w")
    ttk.Label(frame, text="Price").grid(row=3, column=0, sticky="w")
    ttk.Label(frame, text="Quantity").grid(row=4, column=0, sticky="w")

    # Entry Fields
    ttk.Entry(frame, textvariable=id_var).grid(row=0, column=1, sticky="ew")
    
    ttk.Combobox(
        frame,
        textvariable=category_var,
        values=["Shoes", "Tops", "Pants"],
        state="readonly"
    ).grid(row=1, column=1, sticky="ew")

    ttk.Entry(frame, textvariable=desc_var).grid(row=2, column=1, sticky="ew")
    ttk.Entry(frame, textvariable=price_var).grid(row=3, column=1, sticky="ew")
    ttk.Entry(frame, textvariable=qty_var).grid(row=4, column=1, sticky="ew")

    # Treeview
    tree = ttk.Treeview(
        frame,
        columns=("ID", "Category", "Description", "Price", "Quantity"),
        show="headings",
        height=12
    )

    for col in ("ID", "Category", "Description", "Price", "Quantity"):
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.grid(row=0, column=2, rowspan=6, padx=20)

    # Add Item
    def add_item():
        id_ = id_var.get().strip()
        category = category_var.get().strip()
        desc = desc_var.get().strip()
        price = price_var.get().strip()
        qty = qty_var.get().strip()

        # Validation
        if not id_ or not desc or not price or not qty:
            messagebox.showerror("Error", "All fields must have an input")
            return

        if not id_.isdigit():
            messagebox.showerror("Error", "ID must be a number")
            return

        try:
            float(price)
            int(qty)
        except ValueError:
            messagebox.showerror("Error", "Price must be decimal and Quantity must be a whole number")
            return

        items.append({
            "id": id_,
            "category": category,
            "desc": desc,
            "price": price,
            "qty": qty
        })

        save_all_to_csv(CSV_FILE, items)
        refresh_tree(tree, items)
        clear_form(id_var, category_var, desc_var, price_var, qty_var)

    # Delete Item
    def delete_item():
        selected = tree.selection()
        if not selected:
            return

        index = tree.index(selected[0])
        items.pop(index)

        save_all_to_csv(CSV_FILE, items)
        refresh_tree(tree, items)

    # Edit Item
    def edit_item():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an item to edit")
            return

        index = tree.index(selected[0])

        items[index] = {
            "id": id_var.get(),
            "category": category_var.get(),
            "desc": desc_var.get(),
            "price": price_var.get(),
            "qty": qty_var.get()
        }

        save_all_to_csv(CSV_FILE, items)
        refresh_tree(tree, items)

    # When clicking a row, populate form
    def select_item(event):
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0], "values")
            id_var.set(values[0])
            category_var.set(values[1])
            desc_var.set(values[2])
            price_var.set(values[3])
            qty_var.set(values[4])

    tree.bind("<<TreeviewSelect>>", select_item)

    # Buttons
    ttk.Button(frame, text="Add", command=add_item).grid(row=5, column=0, sticky="ew")
    ttk.Button(frame, text="Edit", command=edit_item).grid(row=5, column=1, sticky="ew")
    ttk.Button(frame, text="Delete", command=delete_item).grid(row=6, column=0, columnspan=2, sticky="ew")

    refresh_tree(tree, items)

    root.mainloop()


if __name__ == "__main__":
    main()