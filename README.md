# ynab-merge-networth
Combine two budgets into one to get a more accurate picture of total net worth

## What is this for
If you're using multiple budgets (maybe you're using YNAB with a partner and you're keeping separate budgets, or you have two budgets in two currencies), it can be tedious to keep adding balances together whenever you want to see your total net worth. This script lets you automate the whole process.

## How to Use
1. Get your API token from YNAB at https://api.youneedabudget.com/#personal-access-tokens
2. Create a new destination budget in https://app.youneedabudget.com/
3. Download this repo
4. Run merge_budgets.py
5. Initialize settings by inputting your API token, then select your source budgets and destination budget (info will be stored in your local files, so you don't have to keep inputting these in the future)
6. Source budgets will be merged in destination budget, and you'll now be able to preview your total net worth in that budget's report
7. Run merge_budgets.py anytime you want to update your destination budget
