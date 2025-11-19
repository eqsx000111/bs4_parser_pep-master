import logging
import re
from collections import Counter
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_DOC_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return response
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All version' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = table_tag.find('a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = urljoin(downloads_url, pdf_a4_tag['href'])
    filename = pdf_a4_link.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(pdf_a4_link)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEP_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'pep-content'})
    pep_fid = find_tag(main_div, 'section', attrs={'id': 'index-by-category'})
    all_section = pep_fid.find_all('section')
    status_counter = Counter()
    mismatches = []
    for section in tqdm(all_section):
        tbody = find_tag(section, 'tbody')
        if not tbody:
            continue
        for row in tbody.find_all('tr'):
            abbr_tag = find_tag(row, 'abbr')
            status_abbr = abbr_tag.get_text(strip=True) if abbr_tag else ''
            a_tag = row.find('a', class_='pep reference internal')
            if not a_tag:
                continue
            href = a_tag['href']
            pep_number = a_tag.get_text(strip=True).split()[0]
            if pep_number == '0':
                continue
            with_link = urljoin(PEP_DOC_URL, href)
            response = get_response(session, with_link)
            if response is None:
                continue
            soup = BeautifulSoup(response.text, features='lxml')
            status_on_page = None
            for dl in soup.find_all('dl', class_='rfc2822 field-list simple'):
                for dt in dl.find_all('dt'):
                    if dt.get_text(strip=True).startswith('Status'):
                        dd = dt.find_next_sibling('dd')
                        status_on_page = dd.get_text(strip=True)
                        break
                if status_on_page:
                    break
            if not status_on_page:
                continue
            status_counter[status_on_page] += 1
            expected_statuses = EXPECTED_STATUS.get(status_abbr, ())
            if expected_statuses and status_on_page not in expected_statuses:
                mismatches.append({
                    'url': with_link,
                    'status_on_page': status_on_page,
                    'expected': expected_statuses
                })
    if mismatches:
        logging.info('Несовпадающие статусы:')
        for mismatch in mismatches:
            logging.info(f"{mismatch['url']}")
            logging.info(f"Статус в карточке: {mismatch['status_on_page']}")
            logging.info(f"Ожидаемые статусы: {list(mismatch['expected'])}")
    results = [['Статус', 'Количество']]
    results.extend(sorted(status_counter.items()))
    results.append(['Итого', sum(status_counter.values())])
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
