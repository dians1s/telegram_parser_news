import requests
import httpx


async def send_msg(text):
    # Необходимо вставить токен
    token = "..."
    # Необходимо вставить ссылку на канал
    chat_id = "@..."
    url_req = f"https://api.telegram.org/bot{
        token}/sendMessage?chat_id={chat_id}&text={text}"
    async with httpx.AsyncClient() as client:
        results = requests.get(url_req)
        print(results.json())
