import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import csv

FILENAME = "list.csv"

def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def refresh_tree(tree, tasks):
    for i in tree.get_children():
        tree.delete(i)
    for t in tasks:
        tree.insert("", tk.END, values = (
            t["task_id"],
            t["subject"],
            t["due_date"],
            t["status"],

        ))

def clear_form( task_id_var, subject_var, desc_var, due_date_var, status_var):
    pass

def save_to_csv(filename, list_to_save):
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(list_to_save)


def load_from_csv(filename):
    fieldnames = ["task_id", "subject", "desc", "due_date", "status"]

    with open(filename, mode="r", newline="") as file:
        reader = csv.DictReader(file, fieldnames=fieldnames)
        rows = list(reader)

    return rows


def main():
    tasks = load_from_csv(FILENAME)

    root = tk.Tk()
    root.title("Homework Tracker (Lesson 1)")
    root.geometry("100000x1000")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    frame = ttk.Frame(root, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")


    frame.columnconfigure(1, weight=1)
    frame.columnconfigure(3, weight=2)
    frame.rowconfigure(5, weight=1)

    # add vars

    task_id_var = tk.StringVar()
    subject_var = tk.StringVar()
    desc_var = tk.StringVar()
    due_date_var = tk.StringVar()
    status_var = tk.StringVar(value = "Pending")

    ttk.Label(frame, text="Task ID").grid(row=0, column=0, sticky="w", pady=6)
    ttk.Label(frame, text="Subject").grid(row=1, column=0, sticky="w", pady=6)
    ttk.Label(frame, text="Description").grid(row=2, column=0, sticky="w", pady=6)
    ttk.Label(frame, text="Due date (YYYY-MM-DD)").grid(row=3, column=0, sticky="w", pady=6)
    ttk.Label(frame, text="Status").grid(row=4, column=0, sticky="w", pady=6)

    entry_task_id = ttk.Entry(frame, textvariable=task_id_var)
    entry_task_id.grid(row=0, column=1, sticky="ew", pady=6)

    entry_subject = ttk.Entry(frame, textvariable=subject_var)
    entry_subject.grid(row=1, column=1, sticky="ew", pady=6)

    entry_desc = ttk.Entry(frame, textvariable=desc_var)
    entry_desc.grid(row=2, column=1, sticky="ew", pady=6)

    entry_due = ttk.Entry(frame, textvariable=due_date_var)
    entry_due.grid(row=3, column=1, sticky="ew", pady=6)

    combo_status = ttk.Combobox(frame, textvariable=status_var, values=["Pending", "Done"], state="readonly")
    combo_status.grid(row=4, column=1, sticky="ew", pady=6)

    tree = ttk.Treeview(frame, columns=("id", "subject", "due", "status"), show="headings", height=12)
    tree.heading("id", text="Task ID")
    tree.heading("subject", text="Subject")
    tree.heading("due", text="Due Date")
    tree.heading("status", text="Status")
    tree.grid(row=0, column=3, rowspan=6, sticky="nsew", padx=(12, 0))

    def add_task(_=None):
        #validate data
        task_id = task_id_var.get().strip()
        subject = subject_var.get().strip()
        desc = desc_var.get().strip()
        due_date = due_date_var.get().strip()
        status = status_var.get().strip()

        if not task_id or not subject or not desc or not due_date:
            messagebox.showerror("Error", "Please insert a response into the required feilds")
            return
        if not task_id.isdigit():
            messagebox.showerror("Error", "Task IDs need to be in integers")
            return

        if int(task_id) < 0 or int(task_id) > 999999:
            messagebox.showerror("Error", "You Task ID excedes the integer limit")
            return
        
        if not is_valid_date(due_date):
            messagebox.showerror(
                "Invalid Date" , 
                f"The date you have inputted is not accurate"
            )
            return
        
        #add to list

        tasks.append({
            "task_id":task_id,
            "subject":subject,
            "desc":desc,
            "due_date":due_date,
            "status":status

        })

        refresh_tree(tree, tasks)
        #clear_form(task_id_var, subject_var, desc_var, due_date_var, status_var)
        save_to_csv(FILENAME, [task_id, subject, desc, due_date, status])
        
        entry_task_id.focus_set()


    btn_add = ttk.Button(frame, text="Add task", command=add_task)
    btn_add.grid(row=5, column=1, sticky="ew", pady=(10, 0))

    root.bind ("<Return>", add_task)

    refresh_tree(tree, tasks)
    entry_task_id.focus_set()

    root.mainloop()


if __name__ == "__main__":
    main()
