import Account
import sys
import json
from pathlib import Path


def main(argv):
    with open('manifest.json', 'r') as settings_file:
        settings = json.load(settings_file)
    accounts = []

    # Example usage
    for path in settings['accounts']:
        path = Path(path)

        # Create an account with a name and a path
        account = Account.Account(path, name=path.parent.name)

        # Save the account as a CSV
        account.save_csv(path / 'all_transactions.csv')

        # Save the account in an array so that we can merge it at the end
        accounts.append(account)

    # Merge all the accounts into one CSV output file
    Account.merge_accounts(accounts, settings['merged_output'])

    # Merge all the accounts into one CSV output file with a unique date
    Account.merge_accounts(accounts, settings['merged_output_ud'], unique_date=True)


if __name__ == "__main__":
    main(sys.argv)
