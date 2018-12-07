import re
import pandas as pd
import datetime as dt
import ConfigKA, ConfigHS
import Classes


class Parser:
    """ Generic parser.
    Client specific parser must supply name of appropriate config file.
    Parser maps 'ConfigXx.JOB_PAGE_DATA' to Job class attributes"""

    def __init__(self, job, job_page_data, config=None):
        """job_page_data mirrors ConfigXx.JOB_PAGE_DATA and contains a complete description of a job scraped from a
        client's website"""
        self.client = config.CLIENT
        self.regexp = config.REGEXP
        self.job_page_data = job_page_data
        self.time = None  # not added to new class
        self.address = None  # not added to new class
        self.job = job

    def make_job(self):
        """ Map each data field from the job page to an attribute of self.job"""
        return NotImplementedError

    def __set_id__(self):
        """Parse unique ID for job"""
        return NotImplementedError

    def __set_agent__(self):
        return NotImplementedError

    def __set_vendor__(self):
        """Parse vendor_string for name and first two telephone numbers if present.
        @:return Vendor object"""
        return NotImplementedError

    def __set_property_type__(self):
        return NotImplementedError

    def __set_beds__(self):
        return NotImplementedError

    def __set_floorplan__(self):
        """ Return boolean True if floor plan needed else return False"""
        return NotImplementedError

    def __set_photos__(self):
        """ return the integer number of photos required for the job"""
        return NotImplementedError

    def __set_appointment__(self):
        """
        @:return: Appointment object:
         """
        self.time = self.__set_time__()
        self.address = self.__set_address__()
        appt = Classes.Appointment(self.address, self.time)
        return appt

    def __set_notes__(self):
        """Return a list of notes """
        return NotImplementedError

    def __set_time__(self):
        """return a valid datetime object or None"""
        return NotImplementedError

    def __set_address__(self):
        """return a valid Address object or None"""
        return NotImplementedError

    @staticmethod
    def __parse__(regexp, string):
        """@:return substring of string matching 'regexp' or single space."""
        try:
            return re.search(regexp, string).group(1)
        except (IndexError, AttributeError):
            return None


class KaParser(Parser):
    """ Key Agent specific parser."""

    def __init__(self, job, job_page_data):
        """job_page_data mirrors ConfigXx.JOB_PAGE_DATA and contains a complete description of a job scraped from a
        client's website"""
        super().__init__(job, job_page_data, config=ConfigKA)

    # todo make these all GET methods then use set in the super class!!! probably self.job.xxx=self.xxx in the super
    def make_job(self):
        """ Map each data field from the job page to an attribute of self.job"""
        self.job.client = self.client
        self.job.id = self.__set_id__()
        self.job.agent = self.__set_agent__()
        self.job.vendor = self.__set_vendor__()
        self.job.appointment = self.__set_appointment__()
        self.job.property_type = self.__set_property_type__()
        self.job.beds = self.__set_beds__()
        self.job.floorplan = self.__set_floorplan__()
        self.job.photos = self.__set_photos__()
        self.job.notes = self.__set_notes__()
        self.job.specific_reqs = self.__set_specific_reqs__()
        self.job.system_notes = self.__set_system_notes__()
        self.job.status = Classes.Job.ACTIVE

    def __set_id__(self):
        """Parse unique ID for job"""
        id_ = self.job_page_data["JOB_DATA_ID"]
        return id_

    def __set_agent__(self):
        # parse agent name from notes as this contains branch name info
        notes = self.job_page_data["JOB_DATA_NOTES"]
        agent_name = self.__parse__(self.regexp["agent"], notes).strip()
        agent = self.job_page_data["JOB_DATA_AGENT"]  # for phone numbers

        # parse phone numbers from agent id
        tel = self.__parse__(self.regexp["phone1"], agent).strip()
        mob = self.__parse__(self.regexp["agent_mob"], agent).strip()
        return Classes.Agent(name=agent_name, phone1=tel, phone2=mob)

    def __set_vendor__(self):
        """Parse vendor for name and first three telephone numbers if present.
        @:return Vendor object"""
        vendor = self.job_page_data["JOB_DATA_VENDOR"]
        vendor_name = self.__parse__(self.regexp["vendor"], vendor)
        tel = self.__parse__(self.regexp["day"], vendor)
        mob = self.__parse__(self.regexp["vendor_mob"], vendor)
        eve = self.__parse__(self.regexp["eve"], vendor)
        return Classes.Vendor(name=vendor_name, phone1=tel, phone2=mob, phone3=eve)

    def __set_property_type__(self):
        return self.job_page_data["JOB_DATA_PROPERTY_TYPE"]

    def __set_beds__(self):
        return self.job_page_data["JOB_DATA_BEDS"]

    def __set_floorplan__(self):
        return self.job_page_data["JOB_DATA_FLOORPLAN"].strip().upper().startswith("YES")

    def __set_photos__(self):
        """ return the integer number of photos required for the job"""
        photos = self.job_page_data["JOB_DATA_PHOTOS"]
        try:
            return int(self.__parse__(self.regexp["photo_count"], photos).strip())
        except ValueError:
            return 0

    def __set_notes__(self):
        """Return a list of notes with unwanted lines removed"""
        notes = self.job_page_data["JOB_DATA_NOTES"]  # strip out any backslashes to deal with NA and N/A and split the
        # note into a set of lines
        notes = set(notes.replace("/", "").split("\n"))
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

    def __set_address__(self):
        """return a valid Address object"""
        address = self.job_page_data["JOB_DATA_APPOINTMENT_ADDRESS"]
        try:
            # get valid postcode  ([0] is first occurrence)
            postcode = (re.findall(Classes.Address.postcode_regexp, address))[0].strip()
        except IndexError:
            # no match
            postcode = ""
        # strip out postcode and any 'N/A'. Remove trailing  spaces and commas to make street address:
        street = address.replace(postcode, "").replace("N/A", "").strip().strip(",")
        # make Address object
        return Classes.Address(street, postcode)

    def __set_time__(self):
        """return a valid datetime object"""
        time = self.job_page_data["JOB_DATA_APPOINTMENT"]
        try:
            return dt.datetime.strptime(time, "%a-%d %b %y %H%M")
        except (TypeError, ValueError):
            return None

    # Client specific methods
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

    def __set_specific_reqs__(self):
        """ Extract specific_reqs from beautiful soup table.
       @:return dict of requirement : quantity"""
        #
        # make pandas dataframe from table
        table = self.job_page_data["JOB_DATA_SPECIFIC_REQS_TABLE"]
        try:
            df = pd.read_html(str(table), header=0)[0]  # pandas dataframe
        except ValueError:
            return NotImplementedError
        else:
            #
            # read the table into a dict and return it
            return {row['Specific Requirement']: row['Files required'] for _, row in df.iterrows()}

    def __set_system_notes__(self):
        """ Extract system notes from 'table' a beautifully souped Site Visit table.
        Shorten commonly found words in the table using Config.JOB_PAGE_SITE_VISIT_ABBRS
       @:return list of system requirements : [Date, Author, Note]"""
        table = self.job_page_data["JOB_DATA_HISTORY_TABLE"]

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
            return NotImplementedError
        else:
            #
            # read the table into a list and clean it up by shortening common words
            return [[trim(row['Date Created']), trim(row['Created By']), trim(row['Note'])] for _, row in df.iterrows()]


class HsParser(Parser):
    """ House Simple specific parser"""

    def __init__(self, job, job_page_data):
        """job_page_data mirrors ConfigXx.JOB_PAGE_DATA and contains a complete description of a job scraped from a
        client's website"""
        super().__init__(job, job_page_data, config=ConfigHS)
        self.table = None # ConfigHs.JOB_PAGE_DATA contains one table with all the page data. We store it here

    def make_job(self):
        """ Map each data field from the job page to an attribute of self.job"""

        # get the data and read it into a pandas table
        df = pd.read_html(str(self.job_page_data["JOB_DATA_TABLE"]), index_col=0)
        self.table = pd.concat([pd.DataFrame(df[i]) for i in range(len(df))]).T  # Transpose the table
        self.job.client = self.client
        self.job.id = self.__set_id__()
        self.job.vendor = self.__set_vendor__()
        self.job.appointment = self.__set_appointment__()
        self.job.property_type = self.__set_property_type__()
        self.job.beds = self.__set_beds__()
        self.job.floorplan = True
        self.job.photos = 10
        self.job.status = Classes.Job.ACTIVE

    def __set_id__(self):
        """Parse unique job ID
        @:param table DataFrame object
        @:return string"""
        try:
            # extract the series corresponding to the ID key in the Config file
            id_ = self.table[ConfigHS.JOB_PAGE_DATA["ID"]].values[0]  # return the first item in the series
        except KeyError:
            id_ = None
        return id_

    def __set_vendor__(self):
        """Parse vendor name only. No phone numbers on House Simple job page.
        @:param table DataFrame object
        @:return Vendor object"""
        try:
            vendor = self.table[ConfigHS.JOB_PAGE_DATA["Vendor"]].values[0]
        except KeyError:
            vendor = None
        return Classes.Vendor(name=vendor)

    def __set_property_type__(self):
        try:
            # extract the series corresponding to the ID key in the Config file
            property_type = self.table[ConfigHS.JOB_PAGE_DATA["Property"]].values[0]  # return the first item in the
            # series
        except KeyError:
            property_type = None
        return property_type

    def __set_beds__(self):
        try:
            # extract the series corresponding to the ID key in the Config file
            beds = self.table[ConfigHS.JOB_PAGE_DATA["Beds"]].values[0]  # return the first item in the series
        except KeyError:
            beds = None
        return beds

    def __set_address__(self):
        """@:return a valid Address object"""
        address = self.table[ConfigHS.JOB_PAGE_DATA["Address"]].values[0].strip()
        try:
            # get valid postcode  ([0] is first occurrence)
            postcode = (re.findall(Classes.Address.postcode_regexp, address))[0]
        except IndexError:
            # no match
            postcode = ""
        # strip out postcode and any trailing  spaces
        street = address.replace(postcode, "").strip()
        # make Address object
        return Classes.Address(street, postcode)

    def __set_time__(self):
        """return a valid datetime object"""
        time = self.table[ConfigHS.JOB_PAGE_DATA["Appointment"]].values[0]
        try:
            return dt.datetime.strptime(time, "%d/%m/%Y @ %H:%M")
        except (TypeError, ValueError):
            return None
