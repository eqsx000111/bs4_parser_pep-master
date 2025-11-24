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

# Логи
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'

# Результаты
RESULTS_DIR = BASE_DIR / 'results'

# Скачать PDF / HTML / что-то ещё
DOWNLOADS_DIR = BASE_DIR / 'downloads'
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
