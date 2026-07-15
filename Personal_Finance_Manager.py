import csv  #For dictreader and dictwriter
from datetime import date, datetime #Converting string date values into actual dates

#--------- Opening and storing the Accounts csv file ------------
with open("accounts.csv" , "r", newline= "") as accounts_file:
    account_dict = csv.DictReader(accounts_file)
    for row in account_dict:
        print(row)

#--------- Opening and storing the Budget csv file -------------
with open("budget.csv" , "r", newline= "") as budget_file:
    budget_dict = csv.DictReader(budget_file)

#--------- Opening and storing the transactions csv file --------------
with open("transactions.csv" , "r", newline= "") as transactions_file:
    transaction_dict = csv.DictReader(transactions_file)
    #Converting string dates into actual dates
    for row in transaction_dict:
        d = date.fromisoformat(row["Date"])
        #print(d)

    #Printing only a specific field
        #print(row)