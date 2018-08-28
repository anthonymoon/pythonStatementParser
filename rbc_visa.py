import logging
import parser_utils
from datetime import datetime
from decimal import *
from typing import List
from rbc_statement import Statement


class RbcVisaStatement(Statement):
    def __parse_date(self, line: str):
        date_arr: List[str] = line.replace("STATEMENT FROM ", '').split(" TO ")
        self.end_date = datetime.strptime(date_arr[1][:12], '%b %d, %Y')
        try:
            self.start_date = datetime.strptime(date_arr[0], '%b %d, %Y')
        except ValueError:
            self.start_date = datetime.strptime(date_arr[0], '%b %d')
            self.start_date = self.start_date.replace(year=self.end_date.year)
        logging.debug("Parsing statement date: " + str(self.start_date) + " - " + str(self.end_date))

    def __parse_transaction(self, line: str) -> None:
        if "$" not in line:
            return
        line = line.strip()
        row = {}
        try:
            # Getting rid of transaction date
            row['trans_date']: datetime = datetime.strptime(line[:6], '%b %d')
            line = line[6:]
            line = line.strip()

            # Getting rid of posting date
            row['post_date']: datetime = datetime.strptime(line[:6], '%b %d')
            line = line[6:]
            line = line.strip()

            row['trans_date'] = parser_utils.deduce_date(row['trans_date'], self.start_date, self.end_date)
            row['post_date'] = parser_utils.deduce_date(row['post_date'], self.start_date, self.end_date)

        except ValueError:
            return

        row['desc'] = line.split('     ')[0].strip()
        amount = parser_utils.money_reg.findall(line)
        row['amount'] = parser_utils.str_to_money(amount[0])
        self.transaction_table = self.transaction_table.append(row, ignore_index=True)
        pass

    def parse(self, str_data: str):
        str_data = str_data.splitlines()

        opening_balance = None
        closing_balance = None

        # Parses the statement date and transactions
        for line in str_data:
            # Possible bug later: if we parse a transaction before getting the date (statement layout change)
            if "STATEMENT FROM " in line:
                self.__parse_date(line)
            if "NEW BALANCE" in line:
                money_arr = parser_utils.money_reg.findall(line)
                if len(money_arr) > 0:
                    closing_balance: Decimal = Decimal(parser_utils.strip_currency(money_arr[0]))
            if "PREVIOUS STATEMENT BALANCE" in line:
                money_arr = parser_utils.money_reg.findall(line)
                if len(money_arr) > 0:
                    opening_balance: Decimal = Decimal(parser_utils.strip_currency(money_arr[0]))

            self.__parse_transaction(line)

        if self.end_date is None or self.start_date is None:
            raise ValueError("Could not parse start or end date")

        if opening_balance is None or closing_balance is None:
            raise ValueError("opening_balance or closing_balance is None")

        transactions = round(Decimal(self.transaction_table['amount'].sum()), 2)
        if transactions + opening_balance != closing_balance:
            raise ValueError("The (closing balance) != (opening balance) + (transactions)")

