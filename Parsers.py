import re
import pandas as pd
import datetime as dt
import ConfigKA, ConfigHS
import Classes


class Parser:
    """
    Generic parser.
    Client specific parser must supply name of appropriate config file.
    Parser maps 'ConfigXx.JOB_PAGE_DATA(and/or JOB_PAGE_TABLES)' to Job class attributes
    """

    def __init__(self, job, scraper_data, config=None):
        """
        :param job          : Job object where parsed data will be stored
        :param scraper_data : dict mirroring ConfigXx.JOB_PAGE_DATA.
                               It contains a complete description of a job scraped from a config's website
        :param config       : Master configuration file detailing how the parser should read the scraped data.
                               Edit this if the config website structure changes.
        """
        self.config = config
        self.client = config.CLIENT
        self.scraper_data = scraper_data
        self.time = None
        self.address = None
        self.job = job

    def map_job(self):
        """
        Map each data field from the job page to the corresponding attribute of self.job
        :return None
        """
        return NotImplementedError

    def __set_id__(self):
        """
        Parse unique ID for job
        :return string
        """
        return NotImplementedError

    def __set_agent__(self):
        """
        Parse agent name and branch.
        :return string
        """
        return NotImplementedError

    def __set_vendor__(self):
        """
        Parse vendor name and three telephone numbers if present.
        :return Client object
        """
        return NotImplementedError

    def __set_property_type__(self):
        """
        Parse property type.
        :return string
        """
        return NotImplementedError

    def __set_beds__(self):
        """
        Parse number of bedrooms.
        :return string
        """
        return NotImplementedError

    def __set_floorplan__(self):
        """
        Parse floorplan requirements.
        :return boolean True if floorplan needed else False
        """
        return NotImplementedError

    def __set_photos__(self):
        """
        Parse photos quantity required.
        :return int
        """
        return NotImplementedError

    def __set_notes__(self):
        """
        Parse and summarise notes.
        :return list
        """
        return NotImplementedError

    def set_appointment(self):
        """
        Parse date and time using set_time and set_date methods.
        :return: Appointment object:
         """
        appt = Classes.Appointment(self.address, self.time)
        return appt

    @staticmethod
    def set_time(time, time_format):
        """
        Helper method for set_appointment.
        :param time        : string
        :param time_format : string defines format of time string using Datetime conventions (%m %D %y etc)
        :return Datetime object or None
        """
        try:
            return dt.datetime.strptime(time, time_format)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def set_address(address):
        """
        Helper method for set_appointment.
        Parse full UK address and partition into street address and postcode parts.
        :param address : string
        :return : Address object
        """
        try:
            # get valid postcode  ([0] is first occurrence)
            postcode = (re.findall(Classes.Address.POSTCODE_REGEXP, address))[0]
        except IndexError:
            # no match
            postcode = ""
        # strip out postcode and any trailing  spaces
        street = address.replace(postcode, "").strip()
        while street[-1] == ",":
            street = street.strip(",")  # poorly entered addresses can have extra commas
        # make Address object
        return Classes.Address(street, postcode)

    @staticmethod
    def parse(regexp, string):
        """
        Find regexp in string.
        This is the main method for extracting cleaned data from a config's web page.
        :return string or None
        """
        try:
            return re.search(regexp, string).group(1)
        except (IndexError, AttributeError):
            return None


class KaParser(Parser):
    """
    Key Agent parser.
    Most Key agent data is stored in HTML tags with ids. Some is in tables.
    ConfigKa keeps track of these in JOB_PAGE_DATA
    Some data is stored in tables tracked in JOB_PAGE_TABLES.
    Job attributes are parsed by cross referencing this table.
    """

    def __init__(self, job, scraper_data):
        super().__init__(job, scraper_data, config=ConfigKA)

    def map_job(self):
        """
        Map each data field from the job page to an attribute of self.job
        :return None
        """
        self.job.client = self.client
        self.job.id = self.__set_id__()
        self.job.agent = self.__set_agent__()
        self.job.vendor = self.__set_vendor__()
        self.time = self.__set_time__()
        self.address = self.__set_address__()
        self.job.appointment = self.set_appointment()
        self.job.property_type = self.__set_property_type__()
        self.job.beds = self.__set_beds__()
        self.job.floorplan = self.__set_floorplan__()
        self.job.photos = self.__set_photos__()
        self.job.notes = self.__set_notes__()
        self.job.specific_reqs = self.__set_specific_reqs__()
        self.job.system_notes = self.__set_system_notes__()
        self.job.status = Classes.Job.ACTIVE

    def __set_id__(self):
        """
        Parse unique ID for job
        :return string
        """
        return self.scraper_data["JOB_DATA_ID"]

    def __set_agent__(self):
        """
        Parse agent name and branch.
        :return string
        """
        # parse agent name from notes as this contains branch name info
        notes = self.scraper_data["JOB_DATA_NOTES"]
        agent_name = self.parse(self.config.REGEXP["AGENT"], notes).strip()

        # parse agent for phone numbers
        agent = self.scraper_data["JOB_DATA_AGENT"]
        tel = self.parse(self.config.REGEXP["PHONE_1"], agent)
        mob = self.parse(self.config.REGEXP["AGENT_MOB"], agent)
        eve = self.parse(self.config.REGEXP["PHONE_EVE"], agent)
        return Classes.Agent(branch=agent_name, phone_1=tel, phone_2=mob, phone_3=eve)

    def __set_vendor__(self):
        """
        Parse vendor name and three telephone numbers if present.
        :return Vendor object
        """
        vendor = self.scraper_data["JOB_DATA_VENDOR"]
        vendor_name = self.parse(self.config.REGEXP["VENDOR"], vendor)
        tel = self.parse(self.config.REGEXP["PHONE_DAY"], vendor)
        mob = self.parse(self.config.REGEXP["VENDOR_MOB"], vendor)
        eve = self.parse(self.config.REGEXP["PHONE_EVE"], vendor)
        return Classes.Vendor(name_1=vendor_name, phone_1=tel, phone_2=mob, phone_3=eve)

    def __set_property_type__(self):
        """
        Parse property type.
        :return string
        """
        return self.scraper_data["JOB_DATA_PROPERTY_TYPE"]

    def __set_beds__(self):
        """
        Parse number of bedrooms.
        :return string
        """
        return self.scraper_data["JOB_DATA_BEDS"]

    def __set_floorplan__(self):
        """
        Parse floorplan requirements.
        :return boolean True if floorplan needed else False
        """
        return self.scraper_data["JOB_DATA_FLOORPLAN"].strip().upper().startswith("YES")

    def __set_photos__(self):
        """
        Parse photos quantity required.
        :return int
        """
        photos = self.scraper_data["JOB_DATA_PHOTOS"]
        try:
            return int(self.parse(self.config.REGEXP["PHOTO_COUNT"], photos).strip())
        except ValueError:
            return 0

    def __set_notes__(self):
        """
        Parse and summarise notes.
        :return list
        """
        notes = self.scraper_data["JOB_DATA_NOTES"]  # strip out any backslashes to deal with NA and N/A and split the
        # note into a set of lines
        notes = set(notes.replace("/", "").split("\n"))
        # loop through each line of notes
        # mark unwanted lines for deletion by adding to a new set
        unwanted_notes = {note for note in notes for unwanted in ConfigKA.UNWANTED_NOTES if unwanted in note}
        # delete them
        notes = sorted(list(notes.difference(unwanted_notes)))  # set.difference() is the lines only in notes.
        # remove all blank entries
        try:
            while True:
                notes.remove("")
        except ValueError:
            pass
        return notes

    def __set_address__(self):
        """
        Extract address field from scraper_data and send it to base Parser.set_address().
        :return Address object
        """
        address = self.scraper_data["JOB_DATA_APPOINTMENT_ADDRESS"]
        return self.set_address(address)

    def __set_time__(self):
        """
        Extract date & time field from scraper_data.
        Define Datetime format for that data and send these to base Parser.set_time().
        :return Datetime object
        """
        time = self.scraper_data["JOB_DATA_APPOINTMENT"]
        time_format = ConfigKA.TIME_FORMAT
        return self.set_time(time, time_format)

    # Client specific methods

    def __set_specific_reqs__(self):
        """
        Parse the specific requirements table.
        Currently this is only used for streetscape but it could be expanded to cover any specific photo requirements.
       :return dict {requirement : quantity}
       """
        # make pandas dataframe from table
        table = self.scraper_data["JOB_DATA_SPECIFIC_REQS_TABLE"]
        try:
            df = pd.read_html(str(table), header=0)[0]  # pandas dataframe
        except ValueError:
            return None
        # read the table into a dict and return it
        return {row['Specific Requirement']: row['Files required'] for _, row in df.iterrows()}

    def __set_system_notes__(self):
        """
        Parse job history.
        Abbreviate jargon using Config.JOB_PAGE_SITE_VISIT_ABBRS
       :return list [Date, Author, Note]
       """

        def abbreviate(string):
            for k, v in ConfigKA.JOB_PAGE_SITE_VISIT_ABBRS.items():
                string = string.replace(k, v)
            return string

        # make pandas dataframe from table
        table = self.scraper_data["JOB_DATA_HISTORY_TABLE"]
        try:
            df = pd.read_html(str(table), header=0)[0]  # pandas dataframe
        except ValueError:
            return None
        # read the table into a list and abbreviate
        return [[abbreviate(row['Date Created']), abbreviate(row['Created By']), abbreviate(row['Note'])] for _, row in
                df.iterrows()]


class HsParser(Parser):
    """
    House Simple parser.
    All House simple fields are elements of one of two tables: Home Visit and Owner.
    These two tables are concatenated into the pandas dataframe object self.table.
    Job attributes are parsed from this table.
    """

    def __init__(self, job, scraper_data):
        super().__init__(job, scraper_data, config=ConfigHS)
        self.table = None  # maps to ConfigHS.JOB_PAGE_DATA

    def map_job(self):
        """
        Map each data field from the job page to an attribute of self.job
        :return None
        """

        # get the data and read it into a pandas table
        df = pd.read_html(str(self.scraper_data["JOB_DATA_TABLE"]), index_col=0)
        self.table = pd.concat([pd.DataFrame(df[i]) for i in range(len(df))]).T  # Transpose the table
        self.job.client = self.client
        self.job.id = self.__set_id__()
        self.job.vendor = self.__set_vendor__()
        self.time = self.__set_time__()
        self.address = self.__set_address__()
        self.job.appointment = self.set_appointment()
        self.job.property_type = self.__set_property_type__()
        self.job.beds = self.__set_beds__()
        self.job.floorplan = True
        self.job.photos = 10
        self.job.status = Classes.Job.ACTIVE

    def __set_id__(self):
        """
        Parse unique job ID
        :return string
        """
        try:
            # extract the series corresponding to the ID key in the Config file
            id_ = self.table[ConfigHS.JOB_PAGE_DATA["ID"]].values[0]  # return the first item in the series
        except KeyError:
            id_ = None
        return id_

    def __set_vendor__(self):
        """
        Parse vendor name only.
        No vendor phone numbers on House Simple job page.
        :return Vendor object
        """
        try:
            vendor = self.table[ConfigHS.JOB_PAGE_DATA["VENDOR"]].values[0]
        except KeyError:
            vendor = None
        return Classes.Client(name_1=vendor)

    def __set_property_type__(self):
        """
        Parse property type.
        :return string
        """
        try:
            # extract the series corresponding to the Property key in the Config file
            p_type = self.table[ConfigHS.JOB_PAGE_DATA["PROPERTY"]].values[0]  # return the first item in the series
        except KeyError:
            p_type = None
        return p_type

    def __set_beds__(self):
        """
        Parse number of bedrooms.
        :return string
        """
        try:
            # extract the series corresponding to the Beds key in the Config file
            beds = self.table[ConfigHS.JOB_PAGE_DATA["BEDS"]].values[0]  # return the first item in the series
        except KeyError:
            beds = None
        return beds

    def __set_address__(self):
        """
        Extract address field from scraper_data and send it to base Parser.set_address().
        :return Address object
        """
        address = self.table[ConfigHS.JOB_PAGE_DATA["ADDRESS"]].values[0].strip()
        return self.set_address(address)

    def __set_time__(self):
        """
        Extract date & time field from scraper_data.
        Define Datetime format for that data and send these to base Parser.set_time().
        :return Datetime object
        """
        time = self.table[ConfigHS.JOB_PAGE_DATA["APPOINTMENT"]].values[0]
        time_format = "%d/%m/%Y @ %H:%M"
        return self.set_time(time, time_format)
