import datetime
import pandas as pd

from pandas import DataFrame


class Statement:
    source: str = None
    end_date: datetime = None
    start_date: datetime = None
    transaction_table: DataFrame = None

    def __init__(self):
        self.transaction_table = pd.DataFrame()

    def add_source(self, source: str) -> None:
        self.source = source.replace('\\', '/')

    def parse(self, str_data: str):
        raise NotImplementedError
