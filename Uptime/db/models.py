from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client.sites


class Site:
    def __init__(self, domain):
        self.domain = domain
        self.size = None
        self.time = None
        self.code = None
        self.is_normal = None

    def get_count_in_db(self):
        count = db.sites.find({"site": self.domain}).count()
        return count

    def get_avg_of_time(self):
        cursor = db.sites.find({"site": self.domain, "is_normal": True})
        i = 0
        all_time = 0
        for document in cursor:
            i += 1
            all_time += document["time"]
        return all_time / i

    def get_avg_of_size(self):
        cursor = db.sites.find({"site": self.domain, "is_normal": True})
        i = 0
        all_size = 0
        for document in cursor:
            i += 1
            all_size += int(document["size"])
        return all_size / i

    def insert_stat(self):
        db.sites.insert_one(
            {"site": self.domain, "time": self.time, "size": self.size, "code": self.code, "is_normal": self.is_normal})

    def check_data(self):
        if self.code != 200:
            text = "On " + self.domain + " error code:" + self.code
            data = {
                'message': text,
                'parse_mode': 'HTML'
            }
            self.is_normal = False
            return data
        elif self.size > self.get_avg_of_size() * 1.1 or self.size < self.get_avg_of_size() * 0.9:
            text = "On " + self.domain + " troubles with size, avg: " + str(
                round(self.get_avg_of_size())) + ", but now:" + str(round(self.size))
            data = {
                'message': text,
                'parse_mode': 'HTML'
            }
            self.is_normal = False
            return data
        elif self.time > self.get_avg_of_time() * 3:
            text = "On " + self.domain + " troubles with time, avg: " + str(
                round(self.get_avg_of_time())) + ", but now:" + str(round(self.time))
            data = {
                'message': text,
                'parse_mode': 'HTML'
            }
            self.is_normal = False
            return data
        self.is_normal = True
        return None
