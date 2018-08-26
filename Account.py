import logging
from os import PathLike

import pandas as pd
import parser_utils
from rbc_chequing import RbcBankStatement
from rbc_visa import RbcVisaStatement
from pathlib import Path
from typing import List
from pandas import DataFrame
from rbc_statement import Statement

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S')


class StatementFactory:
    text_source: Path
    pdf_source: Path

    def __init__(self, pdf_source: Path):
        self.pdf_source = pdf_source
        text_dir: Path = self.pdf_source.parent / 'txt'
        if text_dir.is_file():
            text_dir.unlink()
        if not text_dir.is_dir():
            text_dir.mkdir(parents=True, exist_ok=True)

        self.text_source = pdf_source.parents[0] / 'txt' / self.pdf_source.name.replace('pdf', 'txt')

        if not self.text_source.exists():
            parser_utils.pdf_to_text(self.pdf_source, self.text_source)

    @property
    def statement(self) -> Statement:
        with open(self.text_source, mode='r', encoding='utf-8') as statement_file:
            data: str = statement_file.read()
        if "PAYMENTS & INTEREST RATES" in data:
            result = RbcVisaStatement()
        else:
            result = RbcBankStatement()
        result.add_source(str(self.pdf_source))
        result.add_source(str(self.text_source))
        result.parse(data)
        return result


class Account:
    path: Path
    statements: List[Statement]
    transactions: DataFrame

    def __init__(self, path: Path, skip_rename: bool=False, name: str=None):
        self.path = path
        self.statements = []
        self.transactions = pd.DataFrame()

        statements: List[Path] = self.path.glob('*.pdf')
        for statement in statements:
            if not skip_rename:
                rename_target: str = str(statement)
                for x in range(1, 13):
                    rename_target = rename_target.replace(parser_utils.month_cal[x], '-' + str(x).rjust(2, '0') + '-')
                rename_target: Path = Path(rename_target)
                if not rename_target.exists():
                    statement.rename(rename_target)
                    statement = rename_target
            s = StatementFactory(statement).statement
            self.transactions = self.transactions.append(s.transaction_table)
            self.statements.append(s)
        if name is not None:
            self.transactions.insert(1, 'account', name)

    def save_csv(self, path: Path):
        self.transactions.sort_values(by=['trans_date'], inplace=True)
        self.transactions.to_csv(path, index=False)


def merge_accounts(accounts: List[Account], path: PathLike, unique_date=False) -> None:
    output_df = pd.DataFrame()
    for account in accounts:
        output_df = output_df.append(account.transactions, sort=False)
    if unique_date:
        output_df = output_df.groupby(['trans_date'], as_index=False)\
                 .agg(lambda x: x.sum() if x.dtype == 'float64' else ' + '.join(x))
    output_df.sort_values(by=['trans_date'], inplace=True)
    output_df.to_csv(path, index=False)
