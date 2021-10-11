from pymongo import MongoClient
import config

client = MongoClient(config.DATABASE, 27017)
db = client.sites


class Site:
    def __init__(self, domain):
        """
        Initialize class
        :param domain: Domain of site, which is checking
        """
        self.domain = domain
        self.size = None
        self.time = None
        self.code = None
        self.time_of_check = None
        self.is_normal = True

    def get_count_in_db(self):
        """
        Counting the number of checking site in db
        :return: int
        """
        count = db.sites.find({"site": self.domain}).count()
        return count

    def get_avg_of_time(self):
        """
        Calculates the average request time from db for this site
        :return: float
        """
        cursor = db.sites.find({"site": self.domain, "is_normal": True})
        i = 0
        all_time = 0
        for document in cursor:
            i += 1
            all_time += document["time"]
        return all_time / i

    def get_avg_of_size(self):
        """
        Calculates the average request size from db for this site
        :return: float
        """
        cursor = db.sites.find({"site": self.domain, "is_normal": True})
        i = 0
        all_size = 0
        for document in cursor:
            i += 1
            all_size += int(document["size"])
        return all_size / i

    def insert_stat(self):
        """
        Inserts data to DataBase
        """
        db.sites.insert_one(
            {"site": self.domain, "time": self.time, "size": self.size,
             "code": self.code, "is_normal": self.is_normal, "time_of_check": self.time_of_check})

    @staticmethod
    def data_for_webhook(text):
        """
        Make data, which you can use for webhook
        :param text: text, which will be send to chat
        :return: dict
        """
        data = {
            'message': text,
            'parse_mode': 'HTML'
        }
        return data

    def check_data(self):
        """
        Checks is request answer from site right
        :return: data (If there is no problems data = None)
        """
        if self.code != 200:
            text = "On " + self.domain + " error code:" + self.code
            data = self.data_for_webhook(text)
            self.is_normal = False
            return data
        elif self.size > self.get_avg_of_size() * 1.1 or self.size < self.get_avg_of_size() * 0.9:
            text = "On " + self.domain + " troubles with size, avg: " + str(
                self.get_avg_of_size()) + " bytes, but now:" + str(self.size)
            data = self.data_for_webhook(text)
            self.is_normal = False
            return data
        elif self.time > self.get_avg_of_time() * 3:
            text = "On " + self.domain + " troubles with time, avg: " + str(
                round(self.get_avg_of_time())) + ", ms but now:" + str(round(self.time))
            data = self.data_for_webhook(text)
            self.is_normal = False
            return data
        self.is_normal = True
        return None
