import json
from forex_python.converter import CurrencyRates
import requests
from datetime import date

def init_server(key):
	# YNAB API server details
	global serviceurl
	serviceurl = "https://api.youneedabudget.com/v1/budgets"

	global headers
	headers = {
		'accept': 'application/json',
		'Authorization': f'Bearer {key}',
		'Content-Type': 'application/json',
	}


# Get list of all budgets in account, and save JSON copy to local files
def retrieve_budget_list():
	print("Retrieving", serviceurl)
	response = requests.get(serviceurl, headers=headers)

	# Copy data to local files
	try:
		js = response.json()

		with open(budgets_file, 'w') as outfile:
			json.dump(js, outfile, indent=2)

	except:
		print("Couldn't retrieve budgets from YNAB")
		quit()

# Display all budgets
def print_budgets():
	try:
		fh = open(budgets_file)
	except:
		print("Can't open", budgets_file)
		quit()

	data = fh.read()
	js_budgets = json.loads(data)

	global budgets
	budgets = []
	for budget in js_budgets['data']['budgets']:
		budgets.append({'id': budget['id'], 'name': budget['name'], 'iso_code': budget['currency_format']['iso_code']})

	print("Available budgets:")
	counter = 1
	for budget in budgets:
		print('\t' + str(counter) + '. ' + budget['name'])
		counter += 1

	fh.close()

# Get list of all budgets in account, and save JSON copy to local files
def retrieve_budget_accounts(budget_id, category):
	url = serviceurl + '/' + budget_id + '/accounts'
	print("Retrieving", url)
	response = requests.get(url, headers=headers)

	js_budget = response.json()

	js_budgets = json.load(open(budgets_file))
	for budget in js_budgets['data']['budgets']:
		if budget['id'] == budget_id:
			js_budget['data']['info'] = {'id': budget['id'], 'name': budget['name'], 'iso_code': budget['currency_format']['iso_code']}
			break

	return js_budget

def copy_budgets(source_budget_json, final_budget_json):
	# Create or update accounts from source budget in destination budget
	for source_account in source_budget_json['data']['accounts']:
		# Check if source budget account is already in destination budget
		in_dest = False
		final_name = source_budget_json['data']['info']['name'] + ' - ' + source_account['name']
		for dest_account in final_budget_json['data']['accounts']:
			if final_name == dest_account['name']:
				in_dest = True
				break

		#Check if source budget has a different currency than destination budget, and if yes, convert balance to destination currency
		source_budget_currency = source_budget_json['data']['info']['iso_code']
		final_budget_currency = final_budget_json['data']['info']['iso_code']
		if  source_budget_currency != final_budget_currency:
			c = CurrencyRates()
			final_balance = int(c.convert(source_budget_currency, final_budget_currency, source_account['balance']/100) * 100)
		else:
			final_balance = int(source_account['balance'])

		# If source account is already in destination budget, just update the balance
		# Otherwise, create a new account in destination budget
		if in_dest == True:
			print('Updating', final_name)

			# Find the difference between old and new account balances
			old_balance = dest_account['balance']
			difference = final_balance - old_balance
			if difference == 0:
				print('No difference')
				continue

			# Post transaction to make source and destination balances equal
			url = serviceurl + '/' + final_budget_json['data']['info']['id'] + '/transactions'

			data = {
				"transaction": {
					"account_id": dest_account['id'],
					"date": str(date.today()),
					"amount": difference,
					"payee_id": None,
					"payee_name": None,
					"category_id": None,
					"memo": None,
					"cleared": "cleared",
					"approved": True,
					"flag_color": None,
					"import_id": None,
					"subtransactions": [
					{
						"amount": difference,
						"payee_id": None,
						"payee_name": None,
						"category_id": None,
						"memo": None
				}]}}

			response = requests.post(url, headers=headers, json=data)
			print('Difference:', difference)

		else:
			print('Creating', final_name)

			#Create account in destination budget
			url = serviceurl + '/' + final_budget_json['data']['info']['id'] + '/accounts'

			data = {
				"account": {
					"name": final_name,
					"type": source_account['type'],
					"balance": final_balance
				}}

			response = requests.post(url, headers=headers, json=data)

init_exists = True

# Storage files for budget list json
budgets_file = 'budgets.json'
init_file = 'init.json'

try:
	fh = open(init_file)
except:
	init_exists = False

if not init_exists:
	key = input("Token: ")
	init_server(key)
	retrieve_budget_list()
	print_budgets()
	first_num = input("Select 1st budget to merge: ")
	first_budget_id = budgets[int(first_num) - 1]['id']
	second_num = input("Select 2nd budget to merge: ")
	second_budget_id = budgets[int(second_num) - 1]['id']
	final_num = input("Select destination budget: ")
	final_budget_id = budgets[int(final_num) - 1]['id']
	data = {
		'key': key,
		'dest_budget': final_budget_id,
		'first_source': first_budget_id,
		'second_source': second_budget_id
	}
	with open(init_file, 'w') as outfile:
		json.dump(data, outfile, indent=2)
else:
	init_data = json.loads(fh.read())
	key = init_data['key']
	first_budget_id = init_data['first_source']
	second_budget_id = init_data['second_source']
	final_budget_id = init_data['dest_budget']
	fh.close()
	init_server(key)

first_budget_json = retrieve_budget_accounts(first_budget_id, 'first')
second_budget_json = retrieve_budget_accounts(second_budget_id, 'second')
final_budget_json = retrieve_budget_accounts(final_budget_id, 'second')

copy_budgets(first_budget_json, final_budget_json)
copy_budgets(second_budget_json, final_budget_json)

