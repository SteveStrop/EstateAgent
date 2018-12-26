# import sys  # only used when running pickle dumps
import pickle
import re
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import ConfigKA
import ConfigHS
import Classes
import Parsers


class Scraper:
    """
    Navigate to logon page as specified in ConfigXX file.
    Navigate to landing page.
    Crawl through jobs matching Config.REGEXP['job_page_link'] and create a Job object for each one.
    Store a list of all Jobs in self.jobs"""

    def __init__(self, config, parser):
        """
        :param config : ConfigXX file tailored to each config
        :param parser : Parser object specific to each config to convert scraped data into Job attributes
        :return: None
        """
        self.parser = parser
        self.config = config
        self.driver = None  # Selenium webdriver

    def scrape_site(self):
        """
        Use Selenium to log on and scrape data from the website specified in ConfigfXX.
        :return: None
        """
        # logon and get a driver instance
        self.driver = self._logon()
        # get list of links to jobs
        links = self._extract_job_links()
        # parse the linked pages into Job instances
        jobs = self._extract_jobs(links)
        self._process_jobs(jobs)
        self.driver.quit()

    def _logon(self, landing_pg=None):
        """
        Logon to a web site using credentials and web addresses from ConfigXX
        :return Selenium webdriver
        """
        # create a selenium browser driver
        driver = webdriver.Chrome(self.config.CHROME_DRIVER)
        driver.implicitly_wait(10)  # wait for up to 10 secs

        # read credential and addresses
        username = self.config.USERNAME
        password = self.config.PASSWORD
        login_pg = self.config.LOGIN_PAGE
        username_field = self.config.USERNAME_FIELD
        password_field = self.config.PASSWORD_FIELD
        login_btn = self.config.LOGIN_BUTTON

        # set landing page
        if landing_pg is None:
            landing_pg = self.config.LANDING_PAGE

        # Navigate to the config home page
        driver.get(login_pg)

        # find input fields and log on
        username_field = driver.find_element_by_name(username_field)
        password_field = driver.find_element_by_name(password_field)
        username_field.send_keys(username)
        password_field.send_keys(password)
        driver.find_element_by_name(login_btn).click()

        # navigate to the landing page with the list of all jobs
        driver.get(landing_pg)

        # return the selenium browser driver
        return driver

    def _extract_job_links(self, html=None):
        """
        Crawl a list of pages matching Config.REGEXP[job_page_link].
        Create a Job class object for each page visited
        :return list [<a> tags containing href to job pages]"""

        # get html to read if none passed
        if html is None:
            html = BeautifulSoup(self.driver.page_source, 'lxml')
        # find all links pointing to job pages from the landing page
        return html.find_all('a', href=re.compile(self.config.REGEXP["JOB_PAGE_LINK"]))

    def _extract_jobs(self, links):
        """

        :param links: list of html <a> tags containing href to page with details of a job
        :return list : Job objects, one for each link
        """
        return [self._scrape_job(link) for link in links]

    def _scrape_job(self, link):
        """
        Scrape the web page specified by 'link' and parse it into a Job object.
        :param link : BeautifulSoup.Tag pointing to job page
        :return job : Job object containing all scraped and cleaned data from the visited page

        """
        # crawl to Job page
        python_button = self.driver.find_element_by_xpath('//a[@href="' + link['href'] + '"]')
        python_button.click()
        # create a dict of scraped page data matching ConfigXX specifications
        job_dict = self._extract_page_fields()
        # create a new Job instance to store the scraped and cleaned data
        job = Classes.Job()
        # instantiate a Parser and map the scraped page data stored in job_dict onto Job attributes
        p = self.parser(job, job_dict)  # todo make this parser a variable imported from Config
        p.map_job()
        # click the back button
        self.driver.execute_script("window.history.go(-1)")
        return job

    def _extract_page_fields(self, html=None):
        """
        Read required data from ConfigXX.JOB_PAGE_DATA and ConfigXX.JOB_PAGE_TABLES.
        Scrape that data into a dict.
        :param html the html page containing data to be scraped.
        If None then Beautiful soup will parse the current Selenium webdriver.page source
        :return dict {ConfigXX.JOB_PAGE|DATA|TABLES[key] : scraped value}
        """
        job_dict = {}
        if html is None:
            html = BeautifulSoup(self.driver.page_source, 'lxml')
        data = self.config.JOB_PAGE_DATA
        # scrape the text fields
        for key in data.keys():
            try:
                value = html.find(id=data[key]).get_text()
                job_dict[key] = value
            except(IndexError, AttributeError):
                job_dict[key] = None
        # scrape the tables
        data = self.config.JOB_PAGE_TABLES
        for key in data.keys():
            try:
                table = html.find(id=data[key])
                job_dict[key] = table
            except (IndexError, AttributeError):
                job_dict[key] = None
        return job_dict

    @staticmethod
    def _process_jobs(jobs):
        """
        Placeholder for further processing.
        Will eventually store the jobs in a DB via Django.
        :return None
        """
        for job in jobs:
            print(job, sep="\n")

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # these two methods allow saving sample data for use in unit tests
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _save_obj_to_file(obj, name):
        """
        Use pickle to save objects to file for use in unit testing.
        :param obj: object to be saved
        :param name: filename for object
        :return None
        """
        with open('G:/EstateAgent/Tests/obj/' + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

        # no need to scrape_site every page once valid data saved
        input("dict saved. Abort?")
        #
        # --------------------------TO USE THESE METHODS UN-COMMENT AND INSERT WHERE NEEDED-----------------------------
        # # create sample data RUN ONCE!!
        # sys.setrecursionlimit(10000) # pickle can get deep!
        # self._save_obj_to_file(obj, "filename")
        # --------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _load_obj(name):
        """
        Load pickled data.
        :param name: file to load
        :return: None
        """

        with open('G:/EstateAgent/Tests/obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)


class KaScraper(Scraper):
    """
    KeyAgent Scraper
    """

    def __init__(self):
        super().__init__(config=ConfigKA, parser=Parsers.KaParser)


class HsScraper(Scraper):
    """
    House Simple Scraper
    """

    def __init__(self):
        super().__init__(config=ConfigHS, parser=Parsers.HsParser)

    def _extract_job_links(self, html=None):
        """
        Crawl a list of pages matching Config.REGEXP[job_page_link] that are in the CONFIRMED_HOME_VISIT_TABLE and have
        a status indicating the job is live. i.e all jobs with a status of confirmed.
        Create a Job object for each page visited.
        @param: html : beautiful soup object
        :return jobs : list [Job objects]
        """
        # get html to read if none passed
        if html is None:
            html = BeautifulSoup(self.driver.page_source, 'lxml')
        # get table - any live jobs found will be in the first table
        table = html.find_all(ConfigHS.CONFIRMED_HOME_VISIT_TABLE)[0]
        # convert to a pandas dataframe - we're only interested in the first select_drop
        # this is a table of addresses and job statuses etc.
        df = pd.read_html(str(table), encoding='utf-8', header=0)[0]
        # pandas will strip out the href data so we add it back in:
        df["href"] = [tag for tag in table.find_all('a')]
        # all live jobs have a status of "confirmed" so make a list of those [] = table headings
        return [row["href"] for _, row in df.iterrows() if row[ConfigHS.JOB_STATUS] == ConfigHS.JOB_OPEN]

    def _extract_page_fields(self, html=None):
        """
        Read required data from ConfigHS.JOB_PAGE_TABLES.
        Scrape that data into a dict.
        :return dict {ConfigHS.JOB_PAGE_TABLES[key] : scraped value}
        """
        job_dict = {}
        # read html page data
        if html is None:
            html = BeautifulSoup(self.driver.page_source, 'lxml')
        # scrape the tables
        data = self.config.JOB_PAGE_TABLES
        for key in data.keys():
            try:
                table = html.findAll(data[key])
                job_dict[key] = table
            except (IndexError, AttributeError):
                job_dict[key] = None
        return job_dict  # just a copy of the job page table. All data extracted in the parser.


if __name__ == '__main__':
    k = KaScraper()
    h = HsScraper()
    k.scrape_site()
    h.scrape_site()
