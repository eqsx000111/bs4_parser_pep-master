import csv
import datetime as dt
import logging

from prettytable import PrettyTable

import constants

FILE_PATH = 'Файл с результатами был сохранён: {file_path}'
FILE_NAME = '{parsers_mode}_{now_formatted}.csv'
BASE_DIR = constants.BASE_DIR


def get_results_dir():
    return BASE_DIR / constants.RESULTS_DIR_NAME


def control_output(results, cli_args):
    OUTPUT_HANDLERS[cli_args.output](results, cli_args)


def default_output(results, cli_args):
    for row in results:
        print(*row)


def pretty_output(results, cli_arg):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args, encoding='utf-8'):
    results_dir = get_results_dir()
    results_dir.mkdir(exist_ok=True)
    file_path = results_dir / FILE_NAME.format(
        parsers_mode=cli_args.mode,
        now_formatted=dt.datetime.now().strftime(constants.DATETIME_FORMAT)
    )
    with open(file_path, 'w', encoding=encoding) as f:
        csv.writer(f, dialect=csv.unix_dialect).writerows(results)
    logging.info(FILE_PATH.format(file_path=file_path))


OUTPUT_HANDLERS = {
    constants.PRETTY: pretty_output,
    constants.FILE: file_output,
    None: default_output,
}
