import asyncio
import aiohttp
import time
import models

sites = ["https://vk.com", "https://ok.ru"]

async def check(domain):
    site = models.Site(domain)
    start = time.time()*1000
    async with aiohttp.request('GET', site.domain) as response:
        end = round(time.time()*1000 - start)
        size = response.headers.get('Content-length')
        status = response.status
    response.close()
    if site.get_count_in_db() >=10:
        is_normal = site.check_data(end, size, status)
    else:
        is_normal = True
    site.insert_stat(end, size, status, is_normal)

async def schedul():
    while True:
        await main()

async def main():
    tasks = [check(site) for site in sites]
    await asyncio.wait(tasks)

ioloop = asyncio.get_event_loop()
ioloop.run_until_complete(schedul())
ioloop.close()
