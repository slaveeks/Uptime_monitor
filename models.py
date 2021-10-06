from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client.sites

class Site:
    def __init__(self, domain):
        self.domain = domain

    def get_count_in_db(self):
        return db.stat.find({"site":self.domain}).count()

    def get_avg_of_time(self):
        cursor = db.stat.find({"site": self.domain, "is_normal": True})
        i = 0
        sum = 0
        for document in cursor:
            i+=1
            sum += document["time"]
        return sum/i

    def get_avg_of_size(self):
        cursor = db.stat.find({"site": self.domain, "is_normal": True})
        i = 0
        sum = 0
        for document in cursor:
            i += 1
            sum += document["size"]
        return sum / i

    def insert_stat(self, time, size, code, is_normal):
        db.sites.insert_one({"site":self.domain, "time": time, "size":size, "code":code, "is_normal" : is_normal})

    def check_data(self, time, size, code):
        if code != 200:
            print(123)
            return False
        elif size > self.get_avg_of_size()*1.1 or size < self.get_avg_of_size()*0.9:
            print(321)
            return False
        elif time > self.get_avg_of_time()*1.4 or time < self.get_avg_of_time()*0.6:
            print(121)
            return False
        return True