import csv  #For dictreader and dictwriter
from datetime import date, datetime #Converting string date values into actual dates

#--------- Opening and storing the Accounts csv file ------------
accounts_list = []
def load_accounts(filename):    #Reusable function to open any account file
    with open(filename , "r", newline= "") as accounts:
        account_reader = csv.DictReader(accounts)   #Storing file values as dictionaries
        for row in account_reader:
            accounts_list.append({
                "Account ID" : row["Account ID"],
                "Account Name" : row["Account Name"]
            })

load_accounts("accounts.csv")

budgets_list = []
#--------- Opening and storing the Budget csv file -------------
def load_budget(filename):
    with open(filename , "r", newline= "") as budget:
        budget_reader = csv.DictReader(budget)
    #Storing and Editing values to their appropriate data types
        for row in budget_reader:
            budgets_list.append({
                "Account ID" : row["Account ID"],
                "Category" : row["Category"],
                "Budget Amount" : float(row["Budget Amount"])
            })
#Loading the budgets.csv file
load_budget("budgets.csv")

transactions_list = []
#--------- Opening and storing the transactions csv file --------------
def load_transactions(filename):
    #Opening
    with open(filename , "r", newline= "") as transactions:
        transaction_reader = csv.DictReader(transactions)
    #Storing and Editing values to their appropriate data types
        for row in transaction_reader:  #Iterating the values in the reader
            transactions_list.append({ #Storing the values into the empty list created outside
                "Account ID" : row["Account ID"],
                "Date" : datetime.strptime( #Formatting date into YYYY-MM-DD
                row["Date"],
                "%Y-%m-%d"
                ).date(),
                "Company Name" : row["Company Name"],
                "Amount" : float(row["Amount"]),    #Formatting date into floats
                "Category" : row["Category"],
                "Description" : row["Description"]
            })
load_transactions("transactions.csv")
print(transactions_list[0])
print


