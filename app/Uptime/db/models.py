from sqlalchemy import create_engine, MetaData, Column, Integer, Date, String, Float, Table, Boolean, func, select
from sqlalchemy_utils import database_exists, create_database
import config

engine = create_engine("postgresql+psycopg2://" + config.DATABASE)
if not database_exists(engine.url):
    create_database(engine.url)
con = engine.connect()


class Site:
    def __init__(self, domain):
        """
        Initialize class
        :param domain: Domain of site, which is checking
        """
        self.metadata = None
        self.domain = domain
        self.size = None
        self.time = None
        self.code = None
        self.time_of_check = None
        self.is_normal = True
        self.check_create_table("sites")
        self.table = Table('sites', self.metadata, autoload = True)

    def get_count_in_db(self):
        """
        Counting the number of checking site in db
        :return: int
        """
        cur = select([func.count(self.table.columns.id)]).where(self.table.columns.site == self.domain)
        res = con.execute(cur)
        for row in res:
            count = row.count
        return count

    def get_avg_of_time(self):
        """
        Calculates the average request time from db for this site
        :return: float
        """
        s = self.table.select().where(self.table.columns.site == self.domain, self.table.columns.is_normal)
        results = con.execute(s)
        i = 0
        all_time = 0
        for result in results:
            i += 1
            all_time += result["time"]
        return all_time / i

    def get_avg_of_size(self):
        """
        Calculates the average request size from db for this site
        :return: float
        """
        s = self.table.select().where(self.table.columns.site == self.domain, self.table.columns.is_normal)
        results = con.execute(s)
        i = 0
        all_size = 0
        for result in results:
            i += 1
            all_size += int(result["size"])
        return all_size / i

    def insert_stat(self):
        """
        Inserts data to DataBase
        """
        ins = self.table.insert().values(site=self.domain, time=self.time, size=self.size,
                                       code=self.code, is_normal=self.is_normal, time_of_check=self.time_of_check)
        con.execute(ins)

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

    def check_create_table(self, table_name):
        self.metadata = MetaData(engine)
        if not engine.dialect.has_table(con, table_name):
            Table("sites", self.metadata,
                  Column('id', Integer, primary_key=True, nullable=False),
                  Column('site', String), Column('time', Float),
                  Column('size', Float), Column('code', Integer), Column('is_normal', Boolean),
                  Column('time_of_check', Date))
            self.metadata.create_all()

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
