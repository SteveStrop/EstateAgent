import sys
import pickle
import re
from selenium import webdriver
from bs4 import BeautifulSoup
import ConfigKA
import ConfigHS
import Classes
import Parsers


class Scraper:
    """ Crawls through jobs found on a given landing page and creates a Job object for each one.
    The list is stored in self.jobs"""

    def __init__(self, client, parser):
        """@:param client Config file tailored to each client
        @:param Parser object specific to each client"""
        self.parser = parser
        self.client = client
        self.driver = None
        self.jobs = None

    def scrape_site(self):
        """Use Selenium to log on and scrape_site data from the client website as specified in the Config.Xx file"""
        self.driver = self.__logon__()
        self.jobs = self.__get_jobs__()
        self.__process_jobs__()
        self.driver.quit()

    def __logon__(self):
        """
        Logon to a web site using credentials and page addresses from Config file
        @:return Selenium webdriver
        """
        # create a selenium browser driver
        driver = webdriver.Chrome(self.client.CHROME_DRIVER)

        username = self.client.USERNAME
        password = self.client.PASSWORD
        login_pg = self.client.LOGIN_PAGE
        landing_pg = self.client.LANDING_PAGE
        username_field = self.client.USERNAME_FIELD
        password_field = self.client.PASSWORD_FIELD
        login_btn = self.client.LOGIN_BUTTON

        # Navigate to the application home page
        driver.get(login_pg)

        # get input fields
        username_field = driver.find_element_by_name(username_field)
        password_field = driver.find_element_by_name(password_field)

        # enter job_page_data
        username_field.send_keys(username)
        password_field.send_keys(password)

        # get the Login button & click it
        driver.find_element_by_name(login_btn).click()

        # navigate to the home visits list page
        driver.get(landing_pg)

        # return the selenium browser driver
        return driver

    def __get_jobs__(self):
        """ Crawl a list of pages matching Config.REGEXP[job_page_link].
        Create a Job class instance for each page visited
        @:return a list of Job class instances for each page crawled"""

        # find all links pointing to job pages from the landing page
        links = BeautifulSoup(self.driver.page_source, 'lxml').find_all('a', href=re.compile(
                self.client.REGEXP["job_page_link"]))
        # create list of scraped jobs
        jobs = [self.__scrape_job__(link) for link in links]
        return jobs

    def __scrape_job__(self, link):
        """Scrape the web page specified by 'link' and parse it into a Job class instance"""
        # crawl to Job page
        python_button = self.driver.find_element_by_xpath('//a[@href="' + link['href'] + '"]')
        python_button.click()
        # create a dict of page data matching Config specifications (see below)
        job_dict = self.__get_page_fields__()
        # create a new Job instance to store the scraped and formatted data
        job = Classes.Job()
        # map the job_dict data into a Job Class
        # todo make this parser a variable imported from Config
        p = self.parser(job, job_dict)  # sets all fields of job to those from the scraped page
        p.make_job()
        # click the back button
        self.driver.execute_script("window.history.go(-1)")
        return job

    def __get_page_fields__(self):
        """Read required data from Config.JOB_PAGE_DATA and Config.JOB_PAGE_TABLES.
        Scrape that data into a dict.
        @:return dict of scrapped job page data"""

        job_dict = {}
        page_source = BeautifulSoup(self.driver.page_source, 'lxml')
        data = self.client.JOB_PAGE_DATA
        # scrape_site the text fields
        for key in data.keys():
            value = page_source.find(id=data[key]).get_text()
            job_dict[key] = value
        # scrape_site the tables
        data = self.client.JOB_PAGE_TABLES
        for key in data.keys():
            try:
                table = page_source.find(id=data[key])
                job_dict[key] = table
            except (IndexError, AttributeError):

                job_dict[key] = None
        return job_dict

    def __process_jobs__(self):
        """placeholder for further processing. Will eventually store the jobs in a DB via Django
        """
        for job in self.jobs:
            print(job, sep="\n")

    # these two methods allow saving sample data for use in unit tests
    @staticmethod
    def __save_obj_to_file__(obj, name):
        with open('G:/EstateAgent/Tests/obj/' + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        input("dict saved. Abort?")  # no need to scrape_site every page once valid data saved
        # insert this where needed
        # create sample data RUN ONCE!!
        # sys.setrecursionlimit(10000)
        # self.__save_obj_to_file__(job_dict, "job_dict")

    @staticmethod
    def __load_obj__(name):
        with open('G:/EstateAgent/Tests/obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)


class KaScraper(Scraper):
    def __init__(self):
        super().__init__(client=ConfigKA, parser=Parsers.KaParser)


class HsScraper(Scraper):
    def __init__(self):
        super().__init__(client=ConfigHS, parser=Parsers.HsParser)

    def __get_jobs__(self):
        """ Crawl a list of pages matching Config.REGEXP[job_page_link] that are in the CONFIRMED_HOME_VISIT_TABLE
        Create a Job object for each page visited
        @:return list : Job object for each page crawled"""

        # read html page data
        html = BeautifulSoup(self.driver.page_source, 'lxml')
        # find home visits_table
        table = html.find('table', self.client.CONFIRMED_HOME_VISIT_TABLE)
        # find all links pointing to job pages
        links = table.find_all('a', href=re.compile(self.client.REGEXP["job_page_link"]))
        # loop though each job page and scrape_site the job details
        jobs = [self.__scrape_job__(link) for link in links]
        return jobs

    def __get_page_fields__(self):
        """Read required data from Config.JOB_PAGE_DATA and Config.JOB_PAGE_TABLES.
        Scrape that data into a dict.
        @:return dict of scrapped job page data"""

        job_dict = {}
        page_source = BeautifulSoup(self.driver.page_source, 'lxml')

        # scrape_site the tables
        data = self.client.JOB_PAGE_TABLES
        for key in data.keys():
            try:
                table = page_source.findAll(data[key])
                job_dict[key] = table
            except (IndexError, AttributeError):
                job_dict[key] = None
        return job_dict


if __name__ == '__main__':
    k = KaScraper()
    h = HsScraper()
    #k.scrape_site()
    h.scrape_site()
