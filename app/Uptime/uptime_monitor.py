import asyncio
import aiohttp
import time
from Uptime.db import models


class UptimeMonitor:
    def __init__(self, sites, token):
        self.sites = sites
        self.token = token
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.scheduler())
        loop.close()

    async def send_to_chat(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post('https://notify.bot.codex.so/u/' + self.token, data=data) as resp:
                response = await resp.text()
                print(response)

    async def check(self, domain):
        site = models.Site(domain)
        start = time.time() * 1000
        async with aiohttp.request('GET', site.domain) as response:
            site.time = time.time() * 1000 - start
            site.size = response.content.total_bytes / 1024
            site.code = response.status
        response.close()
        if site.get_count_in_db() >= 25:
            data = site.check_data()
            if data is not None:
                await self.send_to_chat(data)
        site.insert_stat()

    async def scheduler(self):
        while True:
            await self.check_sites()

    async def check_sites(self):
        tasks = [self.check(site) for site in self.sites]
        await asyncio.sleep(4)
        await asyncio.wait(tasks)
