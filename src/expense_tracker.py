import sqlite3
import os
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook

conn=None
c=None
username=""

def get_user_database():
    global conn,c,username
    username=input("Enter your username: ").strip()
    db_name=f"{username}_expenses.db"
    if os.path.exists(db_name):
        print(f"Welcome back,{username}!")
    else:
        print(f"New User Detected. Creating a new database for {username}...")
        create_new_database(db_name)
    conn=sqlite3.connect(db_name)
    c=conn.cursor()
    print(f"Database created/connected for user4: {username}")

def create_new_database(db_name):
    conn=sqlite3.connect(db_name)
    c=conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS Transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,
            category TEXT,
            description TEXT,
            amount REAL
            )""")
    conn.commit()
    conn.close()
    print(f"Database '{db_name}' created successfully!\n")
    
def add_transaction():
    date=input("Enter Date(YYYY-MM-DD): ")
    type_=input("Enter Type(Income/Expense): ").capitalize()
    if type_ not in['Income','Expense']:
        print("Invalid type. Must be 'Income' or 'Expense'.")
        return
    category=input("Enter Category: ")
    description=input("Enter description: ")
    amount=float(input("Enter Amount: "))
    c.execute("INSERT INTO Transactions(date,type,category,description,amount) VALUES(?,?,?,?,?)",
                    (date,type_,category,description,amount))
    conn.commit()
    print(f"{type_} added.")

def view_transaction():
    c.execute("SELECT * FROM Transactions ORDER BY date")
    rows=c.fetchall()
    print("\n All Transactions: ")
    for row in rows:
        print(row)

def delete_transaction():
    view_transactions()
    try:
        trans_id=int(input("Enter ID of transaction to delete: "))
        c.execute("SELECT * FROM Transactions WHERE id= ?",(trans_id,))
        row=c.fetchone()
        if row:
            confirm=input("Are you sure you want to delete this transaction: {row}? (y/n): ").lower()
            if confirm=='y':
                c.execute("DELETE FROM Transactions WHERE id=?",(trans_id,))
                conn.commit()
                print("Transaction deleted successfully")
            else:
                print("Deletion Cancelled")
        else:
            print("Transaction Id not found")
    except ValueError:
        print("Invalid input.Please enter a valid transaction ID")
                    
def monthly_summary():
    month=input("Enter month(YYYY-MM): ")
    c.execute("SELECT type,category,SUM(amount) From Transactions WHERE date LIKE ? GROUP BY type,category",(f'{month}%',))
    rows=c.fetchall()
    print(f"\n Monthly Summary for {month}: ")
    for row in rows:
        print(f"{row[0]} - {row[1]}: ₹{row[2]:.2f}")

def export_to_excel():
    export_file = f"{username}_transactions.xlsx"
    df = pd.read_sql_query("SELECT * FROM Transactions", conn)
    if os.path.exists(export_file):
        existing_df=pd.read_excel(export_file)
        existing_ids=existing_df['id'].tolist()
        new_df=df[~df['id'].isin(existing_ids)]
        if new_df.empty:
            print("No new transactions to export")
            return
        with pd.ExcelWriter(export_file,engine='openpyxl',mode='a',if_sheet_exists='overlay') as writer:
            new_df.to_excel(writer, index=False, header=False, startrow=existing_df.shape[0]+1)
        print(f"{len(new_df)} new transaction exported to {export_file}") 
    else:
        df.to_excel(export_file, index=False)
        print(f"Data exported to {export_file}")

def show_balance():
    c.execute("SELECT type, SUM(amount) FROM Transactions GROUP BY type")
    rows = c.fetchall()
    income = 0
    expense = 0
    for row in rows:
        if row[0] == 'Income':
            income = row[1]
        elif row[0] == 'Expense':
            expense = row[1]
    balance = income - expense
    print(f"\n Total Income: ₹{income:.2f}")
    print(f"Total Expense: ₹{expense:.2f}")
    print(f"Balance: ₹{balance:.2f}")

get_user_database()

while True:
    print("\n==== Expense Tracker Menu =====")
    print("1. Add Transactions")
    print("2. View All Transactions")
    print("3. Delete Transaction")
    print("4. Monthly Summary")
    print("5. Export to Excel")
    print("6. Show Balance")
    print("7. Exit")
    choice=input("Choose an option(1-7): ")
    if choice=='1':
        add_transactions()
    elif choice=='2':
        view_transactions()
    elif choice=='3':
        delete_transaction()    
    elif choice=='4':
        monthly_summary()
    elif choice=='5':
        export_to_excel()
    elif choice=='6':
        show_balance()
    elif choice=='7':
        print("Exiting..")
        break
    else:
        print("Invalid choice.Please try again.")
        
conn.close()
