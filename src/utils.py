import logging

from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException, ParserRequestException

REQUEST_EXCEPTION = (
    'Возникла ошибка при загрузке страницы {url}, ошибка: {errors}'
)
ERROR_MESSAGE = 'Не найден тег {tag} {attrs}'
PAGE_ERROR = 'Не удалось получить страницу: {url}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as errors:
        raise ParserRequestException(
            REQUEST_EXCEPTION.format(url=url, errors=errors)
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(
            ERROR_MESSAGE.format(tag=tag, attrs=attrs)
        )
    return searched_tag


def find_soup(session, url):
    response = get_response(session, url)
    if response is None:
        logging.error(PAGE_ERROR.format(url=url), stack_info=True)
        return None
    return BeautifulSoup(response.text, features='lxml')
