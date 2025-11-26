# Парсер для Python и PEPs документации

CLI-утилита для парсинга документации Python и анализа статистики PEP.  
Позволяет получать списки версий, сравнивать статусы, скачивать файлы и выводить результаты в различных форматах.

---

## Автор

**Email:** [deddotu@yandex.ru](mailto:deddotu@yandex.ru) 

**GitHub:** [eqsx000111](https://github.com/eqsx000111)  

**Иван Ильницкий**  

---

## Технологический стек

- Python 3.9+
- BeautifulSoup4 — парсинг HTML
- requests — HTTP-клиент
- requests-cache — кеширование запросов
- tqdm — прогресс-бар

---

## Развертывание проекта

```bash
git clone https://github.com/eqsx000111/bs4_parser_pep-master
cd bs4_parser_pep-master
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

---

## Команды запуска
- Сравнение статусов документов PEP в списке со статусом на странице самого PEP
```bash
python main.py pep
```
- Получение ссылок на страницу с описанием обновлений в каждой новой версии Python
```bash
python main.py whats-new
```
- Получение ссылок на документацию заданной версии Python, ее версию и статус
```bash
python main.py latest-versions
```
- Загрузка документии для определенной версии Python
 ```bash
python main.py download
```

---

## Форматы вывода
- Красивый вывод в терминал
```bash
python main.py pep --output pretty
```
- Сохранение результата в файл
```bash
python main.py pep --output file
```
- Вывод по умолчанию в консоль
```bash
python main.py pep
```
- Вызов справки с доступными параметрами
```bash
python main.py -h
python main.py --help
```

---

### Содержимое справки
```bash
usage: main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}

Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

options:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```