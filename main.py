import asyncio
import aiohttp
import time
import models

sites = ["https://habr.com", "https://vk.com", "https://codex.so"]


async def send_to_chat(data):
    print(data)
    async with aiohttp.ClientSession() as session:
        async with session.post('https://notify.bot.codex.so/u/TOKEN', data=data) as resp: # [1]
            response = await resp.text()
            print(response)


async def check(domain):
    site = models.Site(domain)
    start = time.time()*1000
    async with aiohttp.request('GET', site.domain) as response:
        print(1)
        end = time.time()*1000 - start
        size = response.content.total_bytes/1024
        status = response.status
    response.close()
    if site.get_count_in_db() >=25:
        data = site.check_data(end, size, status)
        if data == None:
            is_normal = True
        else:
            await send_to_chat(data)
            is_normal = False

    else:
        is_normal = True
    site.insert_stat(end, size, status, is_normal)

async def schedul():
    while True:
        await main()

async def main():
    tasks = [check(site) for site in sites]
    await asyncio.sleep(4)
    await asyncio.wait(tasks)

ioloop = asyncio.get_event_loop()
ioloop.run_until_complete(schedul())
ioloop.close()
