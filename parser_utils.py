import subprocess
import platform
import logging
import re
import calendar
from datetime import datetime
from pathlib import Path

month_cal = dict((k, v) for v, k in zip(calendar.month_abbr[1:], range(1, 13)))
money_reg = re.compile('-?\$?[\d,]+\.\d{2}')


def sanitize_path(path: Path) -> str:
    path = str(path).replace('\\', '/')
    if "Windows" == platform.system():
        output = subprocess.run(['bash', '-c', 'wslpath -a ' + path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True
                                )
        path = output.stdout
    logging.debug("sanitize_path returning " + str(path))
    return str(path)


def strip_currency(string: str) -> str:
    return string.replace(",", '').replace('$', '')


def str_to_money(string: str) -> float:
    return float(strip_currency(string))


def pdf_to_text(path: Path, output_path: Path) -> bool:
    path = sanitize_path(path)
    output_path = sanitize_path(output_path)
    cmd: str = 'pdftotext -layout ' + str(path) + ' ' + str(output_path)
    cmd = cmd.replace('\n', '')
    result = subprocess.run(['bash', '-c', cmd],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            )
    if result.returncode != 0:
        logging.warning("pdftotext exited with code " + str(result.returncode) + " stderr: " + result.stderr)
    return result.returncode == 0


def deduce_date(current: datetime, start: datetime, end: datetime) -> datetime:
    # On the basis that a transaction or post cannot occur after a statement period
    result = current.replace(year=end.year)
    if result > end:
        result = result.replace(year=start.year)
    return result
