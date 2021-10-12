import asyncio
import aiohttp
import time
from Uptime.db import models


class UptimeMonitor:
    def __init__(self, sites, endpoint):
        """
        Initialize class
        :param sites: Array of sites' domains, which need to be checked
        :param endpoint: endpoint for sending to telegram chat
        """
        self.sites = sites
        self.webhook_endpoint = endpoint
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.scheduler())
        loop.close()

    async def send_to_chat(self, data):
        """
        Send request to server, which send webhook to chat
        :param data: Dict with some info for webhook
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_endpoint, data=data, ssl = False) as resp:
                response = await resp.text()
                print(response)

    async def check(self, domain):
        """
        Sending get requests to site and check it's answer
        :param domain: Domain of site, which need to be checked
        """
        site = models.Site(domain)
        start = time.time() * 1000
        site.time_of_check = time.asctime()
        async with aiohttp.ClientSession() as session:
            response = await session.get(site.domain, ssl=False)
            site.time = time.time() * 1000 - start
            site.size = response.content.total_bytes
            site.code = response.status
        response.close()
        if site.get_count_in_db() >= 25:
            data = site.check_data()
            if data is not None:
                await self.send_to_chat(data)
        site.insert_stat()

    async def scheduler(self):
        """
        Make a cycle of checking sites
        """
        while True:
            await self.check_sites()

    async def check_sites(self):
        """
        Make functions check(site) by using array of sites
        """
        tasks = [self.check(site) for site in self.sites]
        tasks.append(asyncio.sleep(60))
        await asyncio.wait(tasks)
