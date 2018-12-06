import re
import pandas as pd
import ConfigKA, ConfigHS
import classes


class Parser:
    """ Generic parser.
    Client specific parser must supply name of appropriate config file,
    Maps 'Config.JOB_PAGE_DATA' to Job class attributes"""

    def __init__(self, job, job_page_data, config=None):
        """job_page_data mirrors Config.JOB_PAGE_DATA"""
        assert config
        self.client = config.CLIENT
        self.regexp = config.REGEXP
        self.job_page_data = job_page_data
        self.job = job
        self.__make_job__()

    # Generic methods
    @staticmethod
    def __parse__(regexp, string):
        """@:return substring of string matching 'regexp' or single space."""
        try:
            return re.search(regexp, string).group(1)
        except (IndexError, AttributeError):
            return " "

    @staticmethod
    def __set_floorplan__(floorplan_string):
        """ Return boolean True if floor plan needed else return False"""
        return floorplan_string.upper().strip().startswith("YES")

    @staticmethod
    def __set_appointment__(time_string, address_string):
        """
        @:param time_string : date and time in format ddd-dd mmm yy HHMM
        @praam address_string : full address including postcode
        @:return: Appointment object:
         """

        # parse street address and postcode from address
        try:
            # get valid postcode or set ="" if  none found [0] is first occurrence
            postcode = (re.findall(classes.Address.postcode_regexp, address_string))[0].strip()
        except IndexError:
            postcode = ""
        # strip out found postcode and any N/A. Remove trailing  spaces and commas to make street address:
        street = address_string.replace(postcode, "").replace("N/A", "").strip().strip(",")
        # make Address object
        address = classes.Address(street, postcode)
        # make Appointment object
        appt = classes.Appointment(address, time_string)
        return appt

    @staticmethod
    def __get_month_num__(date):
        """ convert three letter month name into month number ( jan=1).
        @:param date : first 3 letters of month
        @:return month number int or None if unable to convert"""
        month_nums = {
                "jan": "01",
                "feb": "02",
                "mar": "03",
                "apr": "04",
                "may": "05",
                "jun": "06",
                "jul": "07",
                "aug": "08",
                "sep": "09",
                "oct": "10",
                "nov": "11",
                "dec": "12"
        }
        try:
            return month_nums[date.lower()]
        except KeyError:
            return None

    # Polymorphic methods

    @staticmethod
    def __set_beds__(beds):
        return beds

    @staticmethod
    def __set_property_type__(p_type):
        return p_type

    @staticmethod
    def __set_id__(id_string):
        """Parse unique ID for job"""
        return NotImplementedError

    @staticmethod
    def __set_notes__(notes_string):
        """Return a list of notes """
        return NotImplementedError

    def __make_job__(self):
        """ Map each data field from the job page to an attribute of self.job"""
        return NotImplementedError

    def __set_agent__(self, agent_string):
        return NotImplementedError

    def __set_vendor__(self, vendor_string):
        """Parse vendor_string for name and first two telephone numbers if present.
        @:return Vendor object"""
        return NotImplementedError

    def __reformat_date__(self, date):
        """ convert 'date' from ddd-dd mmm yy HHMM' format to 'dd-mm-yyyy HH:MM'
        @:param: date : 'ddd-mmm yy HHMM'
        @:return  'dd-mm-yyyy HH:MM' or None if unable to convert"""
        return NotImplementedError

    def __set_photos__(self, photo_string):
        """ return the integer number of photos required for the job"""
        return NotImplementedError


class KaParser(Parser):
    """ Key Agent specific parser."""

    def __init__(self, job, job_page_data):
        super().__init__(job, job_page_data, config=ConfigKA)

    # Polymorphic methods

    def __make_job__(self):
        """ Map each data field from the job page to an attribute of self.job"""
        self.job.client = self.client
        self.job.id = self.__set_id__(self.job_page_data["JOB_DATA_ID"])
        self.job.agent = self.__set_agent__(self.job_page_data["JOB_DATA_AGENT"])
        self.job.vendor = self.__set_vendor__(self.job_page_data["JOB_DATA_VENDOR"])
        time = self.__reformat_date__(self.job_page_data["JOB_DATA_APPOINTMENT"])
        self.job.appointment = self.__set_appointment__(time, self.job_page_data["JOB_DATA_APPOINTMENT_ADDRESS"])
        self.job.property_type = self.__set_property_type__(self.job_page_data["JOB_DATA_PROPERTY_TYPE"])
        self.job.beds = self.__set_beds__(self.job_page_data["JOB_DATA_BEDS"])
        self.job.notes = self.__set_notes__(self.job_page_data["JOB_DATA_NOTES"])
        self.job.floorplan = self.__set_floorplan__(self.job_page_data["JOB_DATA_FLOORPLAN"])
        self.job.photos = self.__set_photos__(self.job_page_data["JOB_DATA_PHOTOS"])
        self.job.specific_reqs = self.__set_specific_reqs__(self.job_page_data["JOB_DATA_SPECIFIC_REQS_TABLE"])
        self.job.system_notes = self.__set_system_notes__(self.job_page_data["JOB_DATA_HISTORY_TABLE"])
        self.job.status = classes.Job.ACTIVE

    @staticmethod
    def __set_id__(id_string):
        """Parse unique ID for job"""
        try:
            assert id_string.isdigit()
        except AssertionError:
            return None
        return id_string

    def __set_agent__(self, agent_string):
        agent_name = self.__parse__(self.regexp["agent"], agent_string).replace('H Brown of', "").strip()
        tel = self.__parse__(self.regexp["phone1"], agent_string).strip()
        mob = self.__parse__(self.regexp["agent_mob"], agent_string).strip()
        # todo use agent tel number to identify branch will need a new entry in ConfigKA AGENT_BRANCH
        return classes.Agent(name=agent_name, phone1=tel, phone2=mob)

    def __set_vendor__(self, vendor_string):
        """Parse vendor_string for name and first two telephone numbers if present.
        @:return Vendor object"""
        vendor_name = self.__parse__(self.regexp["vendor"], vendor_string).strip()
        tel = self.__parse__(self.regexp["day"], vendor_string).strip()
        mob = self.__parse__(self.regexp["vendor_mob"], vendor_string).strip()
        eve = self.__parse__(self.regexp["eve"], vendor_string).strip()
        return classes.Vendor(name=vendor_name, phone1=tel, phone2=mob or eve)

    def __reformat_date__(self, date):
        """ convert 'date' from ddd-dd mmm yy HHMM' format to 'dd-mm-yyyy HH:MM'
        @:param: date : 'ddd-mmm yy HHMM'
        @:return  'dd-mm-yyyy HH:MM' or None if unable to convert"""
        try:  # todo move these regexp into Config
            # extract day
            dd = self.__parse__(r'(?:\D{4})(\d{2})', date)
            # convert month name to number
            mm = self.__get_month_num__(self.__parse__(r'(?: )([JFMAMASOND]\w{2})', date))
            # convert 2 digit year to 4 digit
            yyyy = 2000 + int(self.__parse__(r'(?: )(\d{2})(?: )', date))
            # extract time
            hh = self.__parse__(r'(?:\d{2} )(\d{2})', date)
            mn = self.__parse__(r'(?:\d{2} \d{2})(\d{2})', date)
            # return concatenated date and time as string
            return dd + "-" + mm + "-" + str(yyyy) + " " + hh + ":" + mn
        # return None if errors occur
        except (TypeError, ValueError):
            return None

    @staticmethod
    def __set_notes__(notes_string):
        """Return a list of notes with unwanted lines removed"""
        # strip out any backslashes to deal with NA and N/A and split the note into a set of lines
        notes = set(notes_string.replace("/", "").split("\n"))
        # loop through each line of notes and add to deletion set those lines containing an unwanted note
        unwanted_notes = {note for note in notes for unwanted in ConfigKA.UNWANTED_NOTES if unwanted in note}
        # delete lines in common between both sets leaving only the lines not marked for deletion
        # and convert to a list
        notes = sorted(list(notes.difference(unwanted_notes)))
        # remove all blank entries
        try:
            while True:
                notes.remove("")
        except ValueError:
            pass
        return notes

    def __set_photos__(self, photo_string):
        """ return the integer number of photos required for the job"""
        try:
            return int(self.__parse__(self.regexp["photo_count"], photo_string).strip())
        except ValueError:
            return 0

    # Client specific methods
    @staticmethod
    def __set_specific_reqs__(table):
        """ Extract specific_reqs from beautiful soup table.
       @:return dict of requirement : quantity"""
        #
        # make pandas dataframe from table
        try:
            df = pd.read_html(str(table), header=0)[0]  # pandas dataframe
        except ValueError:
            pass
        else:
            #
            # read the table into a dict and return it
            return {row['Specific Requirement']: row['Files required'] for _, row in df.iterrows()}

    @staticmethod
    def __set_system_notes__(table):
        """ Extract system notes from 'table' a beautifully souped Site Visit table.
        Shorten commonly found words in the table using Config.JOB_PAGE_SITE_VISIT_ABBRS
       @:return list of system requirements : [Date, Author, Note]"""

        def trim(string):
            """Shorten commonly found words in the table using Config.JOB_PAGE_SITE_VISIT_ABBRS"""
            for k, v in ConfigKA.JOB_PAGE_SITE_VISIT_ABBRS.items():
                string = string.replace(k, v)
            return string

        #
        # make pandas dataframe from table
        try:
            df = pd.read_html(str(table), header=0)[0]  # pandas dataframe
        except ValueError:
            pass
        else:
            #
            # read the table into a list and clean it up by shortening common words
            return [[trim(row['Date Created']), trim(row['Created By']), trim(row['Note'])] for _, row in df.iterrows()]


class HsParser(Parser):
    """ House Simple specific parser"""

    def __init__(self, job, job_page_data):
        super().__init__(job, job_page_data, config=ConfigHS)
        self.__make_job__()

    def __make_job__(self):
        """ Map each data field from the job page to an attribute of self.job"""
        df = pd.read_html(str(self.job_page_data["JOB_DATA_TABLE"]), index_col=0)
        table = pd.concat([pd.DataFrame(df[i]) for i in range(len(df))]).T  # Transpose the table
        self.job.client = self.client
        self.job.id = self.__set_id__(table)
        self.job.vendor = self.__set_vendor__(table)
        self.job.appointment = self.__do_set_appointment__(table)
        self.job.property_type = self.__set_property_type__(table)
        self.job.beds = self.__set_beds__(table)
        self.job.notes = None
        self.job.floorplan = True
        self.job.photos = 20
        self.job.specific_reqs = None
        self.job.system_notes = None
        self.job.status = classes.Job.ACTIVE

    @staticmethod
    def __set_id__(table):
        """Parse unique job ID
        @:param table DataFrame object
        @:return string"""
        try:
            # extract the series corresponding to the ID key in the Config file
            id_ = table.T[ConfigHS.JOB_PAGE_DATA["ID"]].values[0]  # return the first item in the series
        except KeyError:
            id_ = None
        return id_

    def __set_vendor__(self, table):
        """Parse vendor name only. No phone numbers on House Simple job page.
        @:param table DataFrame object
        @:return Vendor object"""
        try:
            vendor = table[ConfigHS.JOB_PAGE_DATA["Vendor"]].values[0]
        except KeyError:
            vendor = None
        return classes.Vendor(name=vendor)

    def __do_set_appointment__(self, table):
        """Read time and address from the table and convert into Parser format"""

        # extract the series corresponding to the Address and Appointment keys in the Config file
        try:
            address = table[ConfigHS.JOB_PAGE_DATA["Address"]].values[0]
        except KeyError:
            address = None

        try:
            time = table[ConfigHS.JOB_PAGE_DATA["Appointment"]].values[0]
            # convert time to ddd-dd mmm yy HHMM format
            time = self.__reformat_date__(time)
        except KeyError:
            time = None

        return self.__set_appointment__(address_string=address, time_string=time)

    def __reformat_date__(self, time):
        """ convert 'time' from dd*mm*yyyy*@*HH:MM' format to 'dd-mm-yyyy HH:MM'
        @:param: time : 'dd/mm/yyyy @ HH:MM'
        @:return  'dd-mm-yyyy HH:MM' or None if unable to convert"""
        try:
            assert isinstance(time,str)
        except AssertionError:
            return None
        # extract day
        dd = self.__parse__(ConfigHS.REGEXP["day"], time)
        # extract month
        mm = self.__parse__(ConfigHS.REGEXP["month"], time)
        # extract year
        yyyy = self.__parse__(ConfigHS.REGEXP["year"], time)
        # extract time
        hh = self.__parse__(ConfigHS.REGEXP["hour"], time)
        mn = self.__parse__(ConfigHS.REGEXP["min"], time)
        # concatenate and check for errors
        time = dd + "-" + mm + "-" + yyyy + " " + hh + ":" + mn
        if len(time) == len("dd-mm-yyyy HH:MM"):
            return time
        else:
            return None

    @staticmethod
    def __set_property_type__(table):
        try:
            # extract the series corresponding to the ID key in the Config file
            property_type = table[ConfigHS.JOB_PAGE_DATA["Property"]].values[0]  # return the first item in the series
        except KeyError:
            property_type = None
        return property_type

    @staticmethod
    def __set_beds__(table):
        try:
            # extract the series corresponding to the ID key in the Config file
            beds = table[ConfigHS.JOB_PAGE_DATA["Beds"]].values[0]  # return the first item in the series
        except KeyError:
            beds = None
        return beds
