import parser_utils
from datetime import datetime
from decimal import *
from typing import Dict
from rbc_statement import Statement


class RbcBankStatement(Statement):
    def parse(self, str_data: str):
        if "No activity for this period" in str_data:
            return
        str_data = str_data.splitlines()

        # Parses the statement date
        for line in str_data:
            if "Your opening balance on " in line:
                line = line.replace("Your opening balance on ", '')
                line = line.strip()
                self.start_date = datetime.strptime(line.split('    ')[0], '%B %d, %Y')
                continue

            if "Your closing balance on " in line:
                line = line.replace("Your closing balance on ", '')
                line = line.strip()
                self.end_date = datetime.strptime(line.split('    ')[0], '%B %d, %Y')
                continue

            if "From " in line and " to " in line:
                output = line.replace("From ", '').split(" to ")
                if len(output) != 2:
                    raise ValueError()
                self.start_date = datetime.strptime(output[0].strip(), '%B %d, %Y')
                self.end_date = datetime.strptime(output[1].strip(), '%B %d, %Y')

        if self.end_date is None or self.start_date is None:
            raise ValueError("Could not parse start or end date")

        # Start parsing using state from other lines
        pos_header: Dict[str, int] = {'date': -1, 'desc': -1, 'with': -1, 'dep': -1, 'bal': -1}
        process_date: datetime = None
        multiline_desc: str = ''
        opening_balance: str = None
        closing_balance: str = None
        for x in range(len(str_data)):
            line = str_data[x]
            if "Closing Balance" in line:
                closing_balance: str = parser_utils.strip_currency(parser_utils.money_reg.findall(line)[0])
                break
            if "Opening Balance" in line:
                opening_balance: str = parser_utils.strip_currency(parser_utils.money_reg.findall(line)[0])
                continue
            if 'RBPDA' in line and 'HRI' in line:
                continue
            temp_header = {'date': line.find("Date"),
                           'desc': line.find("Description"),
                           'with': line.find("Withdrawals"),
                           'dep': line.find("Deposits"),
                           'bal': line.find("Balance")}
            if -1 not in temp_header.values():
                pos_header = temp_header
                multiline_desc = ''
                continue
            if -1 not in pos_header.values():
                try:
                    process_date = datetime.strptime(line[pos_header['date']:pos_header['desc']].strip(), '%d %b')
                    process_date = parser_utils.deduce_date(process_date, self.start_date, self.end_date)
                except ValueError:
                    if process_date is None:
                        continue
                deposit = parser_utils.money_reg.findall(line[pos_header['dep']:pos_header['bal']])
                withdrawal = parser_utils.money_reg.findall(line[pos_header['with']:pos_header['dep']])
                cur_desc = line[pos_header['desc']:pos_header['with']].strip()
                if len(deposit) == 0 and len(withdrawal) == 0:
                    multiline_desc = cur_desc
                    continue
                if len(deposit) != 0 and len(withdrawal) != 0:
                    raise Exception("Why is there a withdrawal and deposit in the same transaction")
                transaction = {'trans_date': process_date}
                if len(withdrawal) != 0:
                    transaction['amount'] = -1 * parser_utils.str_to_money(withdrawal[0])
                else:
                    transaction['amount'] = parser_utils.str_to_money(deposit[0])
                transaction['desc'] = (multiline_desc + " " + cur_desc).strip()
                multiline_desc = ''
                self.transaction_table = self.transaction_table.append(transaction, ignore_index=True)

        opening_balance_d = Decimal(opening_balance)
        transactions = round(Decimal(self.transaction_table['amount'].sum()), 2)
        estimated_close = opening_balance_d + transactions
        close = Decimal(closing_balance)
        if estimated_close != close:
            raise ValueError("The (closing balance) != (opening balance) + (transactions)")
