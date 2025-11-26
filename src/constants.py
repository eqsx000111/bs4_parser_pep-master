from pathlib import Path

# =========================
# БЛОК: URLs
# =========================
MAIN_DOC_URL = 'https://docs.python.org/3.9/'
PEP_DOC_URL = 'https://peps.python.org/'


# =========================
# БЛОК: Форматирование вывода / режимов
# =========================
PRETTY = 'pretty'
FILE = 'file'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'


# =========================
# БЛОК: Файловые пути
# =========================
BASE_DIR = Path(__file__).parent
LOG_DIR_NAME = 'logs'
LOG_FILE_NAME = 'parser.log'
RESULTS_DIR_NAME = 'results'
DOWNLOADS_DIR_NAME = 'downloads'

# Логи
LOG_DIR = BASE_DIR / LOG_DIR_NAME
LOG_FILE = LOG_DIR / LOG_FILE_NAME

# Результаты
RESULTS_DIR = BASE_DIR / RESULTS_DIR_NAME

# Скачать PDF / HTML / что-то ещё
DOWNLOADS_DIR = BASE_DIR / DOWNLOADS_DIR_NAME
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_FORMAT = '%(asctime)s - [%(levelname)s] - %(message)s'


# =========================
# БЛОК: Статусы PEP
# =========================
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
