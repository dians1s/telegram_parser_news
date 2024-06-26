import httpx
import asyncio
import feedparser
from send_msg_to_telegram import send_msg
from bs4 import BeautifulSoup
from re import search
from ast import literal_eval

exception_news = []


def init_last_news():
    '''Инициализация если брать не из деки, а из файла (Сделана только инициализацию файла)'''
    with open('news_temp.txt', encoding='windows-1251') as f:
        for line in f:
            exception_news.append(literal_eval(line))


init_last_news()


def summary_fixed(text):
    '''Форматируем и убираем теги из новости и убираем Photo by ..., если такое имеется'''
    temp = ''.join(BeautifulSoup(
        text, features="html.parser").findAll(string=True))
    try:
        temp = temp[:search(r'Photo', temp).start()]
    finally:
        return temp


def write_exception_news():
    '''Запись списка исключений в файл.'''
    with open('news_temp.txt', 'w', encoding='windows-1251') as f:
        for i in exception_news:
            f.write(str(i) + "\n")


async def parser_rss(httpx_client, max_list_items, n_test_chars, send_message_func=None, loop=None):
    '''Парсинг новостной ленты prian & homeoverseas'''

    rss_link_first = 'https://prian.ru/rss/news_ru.xml'
    rss_link_second = 'https://www.homesoverseas.ru/rss/'

    while True:
        try:
            response_first = await httpx_client.get(rss_link_first)
            response_second = await httpx_client.get(rss_link_second)
        except:
            await asyncio.sleep(10)
            continue

        feed_first = feedparser.parse(response_first.text)
        feed_second = feedparser.parse(response_second.text)

        first_skip = 50 - max_list_items
        for entry in feed_first.entries[::-1]:
            if first_skip != 0:
                first_skip -= 1
                continue
            summary = entry['fulltext']
            title = entry['title']
            category = entry['category']
            news_text = f'{title}\n{summary_fixed(summary)}'

            head = news_text[:n_test_chars].strip()

            if head in exception_news[0]:
                continue

            if send_message_func is None:
                print(news_text, '\n')
            else:
                await send_message_func(f'{"From site - Prian"}\n{category}\n{news_text}')
            exception_news[0].append(head)
            if len(exception_news[0]) > max_list_items:
                del exception_news[0][0]
            write_exception_news()
            await asyncio.sleep(10)

        for entry in feed_second.entries[::-1]:
            summary = entry['yandex_full-text']
            title = entry['title']
            news_text = f'{title}\n{summary_fixed(summary)}'

            head = news_text[:n_test_chars].strip()

            if head in exception_news[1]:
                continue

            if send_message_func is None:
                print(news_text, '\n')
            else:
                await send_message_func(f'{"From site - HomeOverSeas"}\n{news_text}')
            exception_news[1].append(head)
            if len(exception_news[1]) > max_list_items:
                del exception_news[1][0]
            write_exception_news()
            await asyncio.sleep(10)
        await asyncio.sleep(5)

if __name__ == "__main__":

    # Сколько будет храниться последних новостей, чтобы не повторялись
    max_list_items = 20

    # 50 первых символов от текста новости - это ключ для проверки повторений
    n_test_chars = 50

    httpx_client = httpx.AsyncClient()

    asyncio.run(parser_rss(httpx_client, max_list_items,
                n_test_chars, send_message_func=send_msg))
