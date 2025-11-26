import logging
import re
from collections import Counter
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

import constants
from configs import configure_argument_parser, configure_logging
from constants import EXPECTED_STATUS, MAIN_DOC_URL, PEP_DOC_URL
from exceptions import NothingFoundError
from outputs import control_output
from utils import calculate_soup, find_tag

BASE_DIR = constants.BASE_DIR
ARCHIVE_DOWNLOAD_DONE = 'Архив был загружен и сохранён: {archive_path}'
ALL_VERSION_NOT_FOUND = 'Не найден блок "All version"'
RESULTS_LATEST_VER_HEADER = ('Ссылка на документацию', 'Версия', 'Статус')
RESULTS_WHATS_NEW_HEADER = ('Ссылка на статью', 'Заголовок', 'Редактор, автор')
MISMATCH = 'Несовпадающие статусы:'
MISMATCH_INFO = (
    'Адрес: {url} | Статус в карточке: '
    '{status_on_page} | Ожидаемые статусы: {expected}'
)
STATUS_ON_PAGE = 'Статус в карточке: {status_on_page}'
EXPECTED = 'Ожидаемые статусы: {expected}'
PARSER_RUN = 'Парсер запущен!'
ARGS = 'Аргументы командной строки: {args}'
PARSER_DONE = 'Парсер завершил работу.'
LAST_EXCEPTION = 'Произошла непредвиденная ошибка: {error}'
SOUP_ERROR = 'Не удалось получить soup для {link}: {error}'


def get_downloads():
    return BASE_DIR / constants.DOWNLOADS_DIR_NAME


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = calculate_soup(session, whats_new_url)
    versions = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 > a'
    )
    results = [RESULTS_WHATS_NEW_HEADER]
    for version in tqdm(versions):
        version_link = urljoin(whats_new_url, version['href'])
        try:
            soup = calculate_soup(session, version_link)
        except Exception as error:
            raise RuntimeError(
                SOUP_ERROR.format(link=version_link, error=error)
            )
        dl = soup.find('dl')
        dl_text = dl.text.replace('\n', ' ') if dl else ' '
        results.append((version_link, find_tag(soup,  'h1').text, dl_text))
    return results


def latest_versions(session):
    soup = calculate_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All version' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise NothingFoundError(ALL_VERSION_NOT_FOUND)
    results = [RESULTS_LATEST_VER_HEADER]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag['href'], version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = calculate_soup(session, downloads_url)
    pdf_a4_link = urljoin(
        downloads_url,
        soup.select_one(
            'div[role="main"] table.docutils a[href$="pdf-a4.zip"]'
        )['href']
    )
    filename = pdf_a4_link.split('/')[-1]
    downloads_dir = get_downloads()
    archive_path = downloads_dir / filename
    downloads_dir.mkdir(exist_ok=True)
    response = session.get(pdf_a4_link)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(ARCHIVE_DOWNLOAD_DONE.format(archive_path=archive_path))


def pep(session):
    soup = calculate_soup(session, PEP_DOC_URL)
    all_section = soup.select('#index-by-category section tbody tr')
    status_counter = Counter()
    mismatches = []
    for row in tqdm(all_section):
        status_abbr = row.select_one('abbr').text[1:]
        with_link = urljoin(
            PEP_DOC_URL,
            row.select_one('a.pep.reference.internal')['href']
        )
        try:
            soup = calculate_soup(session, with_link)
        except Exception as error:
            raise RuntimeError(SOUP_ERROR.format(link=with_link, error=error))
        status_on_page = None
        status_dd = soup.select_one(
            'dl.rfc2822.field-list.simple dt:-soup-contains("Status") + dd'
        )
        status_on_page = status_dd.get_text(
            strip=True
        ) if status_dd else None
        status_counter[status_on_page] += 1
        expected_statuses = EXPECTED_STATUS.get(status_abbr, ())
        if expected_statuses and status_on_page not in expected_statuses:
            mismatches.append(
                MISMATCH_INFO.format(
                    url=with_link,
                    status_on_page=status_on_page,
                    expected=list(expected_statuses)
                )
            )
    if mismatches:
        logging.info(MISMATCH)
        for mismatch in mismatches:
            logging.info(mismatch)
    return [
        ('Статус', 'Количество'),
        *status_counter.items(),
        ('Всего', sum(status_counter.values()))
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info(PARSER_RUN)
    try:
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(ARGS.format(args=args))
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
        logging.info(PARSER_DONE)
    except Exception as error:
        logging.exception(LAST_EXCEPTION.format(error=error))


if __name__ == '__main__':
    main()
