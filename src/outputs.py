import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT, FILE, PRETTY

FILE_PATH = 'Файл с результатами был сохранён: {file_path}'
RESULTS_DIR = BASE_DIR / 'results'


def control_output(results, cli_args):
    OUTPUT_HANDLERS = {
        PRETTY: pretty_output,
        FILE: file_output,
        None: default_output,
    }
    handler = OUTPUT_HANDLERS.get(cli_args.output, default_output)
    handler(results, cli_args)


def default_output(results, cli_args):
    for row in results:
        print(*row)


def pretty_output(results, cli_arg):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parsers_mode = cli_args.mode
    now_formatted = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_name = f'{parsers_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(FILE_PATH.format(file_path=file_path))
