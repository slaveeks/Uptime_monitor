from pymongo import MongoClient
import aiohttp

client = MongoClient('127.0.0.1', 27017)
db = client.sites

class Site:
    def __init__(self, domain):
        self.domain = domain

    def get_count_in_db(self):
        count = db.sites.find({"site":self.domain}).count()
        return count

    def get_avg_of_time(self):
        cursor = db.sites.find({"site": self.domain, "is_normal": True})
        i = 0
        sum = 0
        for document in cursor:
            i+=1
            sum += document["time"]
        return sum/i

    def get_avg_of_size(self):
        cursor = db.sites.find({"site": self.domain, "is_normal": True})
        i = 0
        sum = 0
        for document in cursor:
            i += 1
            sum += int(document["size"])
        return sum / i

    def insert_stat(self, time, size, code, is_normal):
        db.sites.insert_one({"site":self.domain, "time": time, "size":size, "code":code, "is_normal" : is_normal})

    def check_data(self, time, size, code):
        if code != 200:
            text = "On "+self.domain+" error code:"+code
            data = {
                'message': text,
                'parse_mode': 'HTML'
            }
            return data
        elif size > self.get_avg_of_size()*1.1 or size < self.get_avg_of_size()*0.9:
            text = "On "+self.domain+" troubles with size, avg: "+str(round(self.get_avg_of_size()))+", but now:"+str(round(size))
            data = {
                'message': text,
                'parse_mode': 'HTML'
            }
            return data
        elif time > self.get_avg_of_time()*3:
            text = "On "+self.domain+" troubles with time, avg: "+str(round(self.get_avg_of_time()))+", but now:"+str(round(time))
            data = {
                'message': text,
                'parse_mode': 'HTML'
            }
            return data
        return None