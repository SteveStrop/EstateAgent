import re
import datetime as dt


class Address:
    """
    Store a UK address split into postcode and street parts
    """
    POSTCODE_REGEXP = r'[A-Z]{1,2}[\dR][\dA-Z]? [\d][A-Z]{2}'

    def __init__(self, address=None, postcode=""):
        """
        :param address:  string
        :param postcode: string
        """

        self.street = address
        self.postcode = self.__validate_postcode__(postcode)

    @staticmethod
    def __validate_postcode__(postcode):
        """
        Convert input to upper case then check if it is a valid mainland UK postcode
        :param postcode: string
        :return string : valid uppercase postcode or None
        """
        try:
            postcode = postcode.upper()
            return re.fullmatch(Address.POSTCODE_REGEXP, postcode)[0]
        except AttributeError:
            return None
        except TypeError:
            return None

    def __str__(self):
        """
        String representation of Address object.
        :return: string
        """
        return f"{self.street if self.street else ''}, {self.postcode if self.postcode else ''}"


class Appointment:
    """
    Store appointment date and time in 24h format
    """

    TIME_FORMAT = "%a %d %b @ %H:%M"

    def __init__(self, address=Address(None), dtime=None):
        """
        :param address: Address object
        :param dtime:   Datetime object
        """

        self.address = address
        self.date = dtime

    def __str__(self):
        """
        String representation of Appointment object.
        :return: string
        """
        try:
            return self.date.strftime(Appointment.TIME_FORMAT)  # Day dd Mmm @ hh:mm
        except (TypeError, AttributeError):
            return "TBA"


class Client:
    """
    Stores contact details for a client.
    Clients may have websites where they list details of jobs.
    If they do, then each client has a Scraper, Parser, and ConfigXX file (XX denotes the client).
    These allow parsing of the jobs into Job objects (defined below) for saving to the database.
    """

    def __init__(self, name=None, phone1=None, secondary_contact=None, phone2=None, notes=None):
        """
        :param name:              string
        :param phone1:            string
        :param secondary_contact: string
        :param phone2:            string
        :param notes              string
        """

        self.name = name
        self.phone1 = self.validate_tel(phone1)
        self.secondary_contact = secondary_contact
        self.phone2 = self.validate_tel(phone2)
        self.notes = notes

    def validate_tel(self, tel):
        """ Check tel is a valid UK phone number and return correctly formatted version or None
        :param tel : string
        :return string or None"""
        try:
            return self.__format_tel__(*self.__get_tel_format__(tel))
        except TypeError:
            return None

    @staticmethod
    def __get_tel_format__(tel):

        """
        Get the correct space-delimited format a UK phone number.
        Return the digit only version of tel and it's valid UK phone number format
        :param tel: string
        :return: string , string
        """
        tel_formats = [
                ("01### ##### ", "01\d{8}"),
                ("01### ### ###", "01\d{9}"),
                ("011# ### ####", "011\d{8}"),
                ("01#1 ### ####", "01\d1\d{7}"),
                ("013397 #####", "013397\d{5}"),
                ("013398 #####", "013398\d{5}"),
                ("013873 #####", "013873\d{5}"),
                ("015242 #####", "015242\d{5}"),
                ("015394 #####", "015394\d{5}"),
                ("015395 #####", "015395\d{5}"),
                ("015396 #####", "015396\d{5}"),
                ("016973 #####", "016973\d{5}"),
                ("016974 #####", "016974\d{5}"),
                ("016977 #### ", "016977\d{4}"),
                ("016977 #####", "016977\d{5}"),
                ("017683 #####", "017683\d{5}"),
                ("017684 #####", "017684\d{5}"),
                ("017687 #####", "017687\d{5}"),
                ("019467 #####", "019467\d{5}"),
                ("019755 #####", "019755\d{5}"),
                ("019756 #####", "019756\d{5}"),
                ("02# #### ####", "02\d{9}"),
                ("03## ### ####", "03\d{9}"),
                ("05### ### ###", "05\d{9}"),
                ("07### ### ###", "07\d{9}")
        ]

        try:
            assert isinstance(tel, str)
        except AssertionError:
            return None
        # strip non digits
        tel = "".join([n for n in tel if n.isdigit()])
        tel_format = None
        # compare regexp in tel_formats with tel
        for fmt, regexp in tel_formats:  # search them all because the last match is the one we want
            try:
                tel = re.fullmatch(regexp, tel)[0]
                tel_format = fmt
                # print(f"found a match for {tel} as {tel_format}")
                # input("Continue?")
            except (TypeError, AttributeError):
                pass  # loop if no match
        # print(f"returning {tel_format} as a match")
        # input("Continue?")
        return tel, tel_format

    @staticmethod
    def __format_tel__(phone, template):
        """
        Format the digit only string to match template by adding spaces.
        Return correctly formatted UK phone number
        :param phone: string
        :param template: string
        :return: string
        """
        try:
            assert isinstance(phone, str) and isinstance(template, str)
        except AssertionError:
            return None  # not a valid UK phone number
        # cast phone to a list
        phone = list(phone)
        # build correctly formatted phone by popping first element if matching template character is non blank and strip any whitespace
        return "".join([phone.pop(0) if c != " " else " " for c in template]).strip()

    def __str__(self):
        return f"{self.name if self.name else ''} ({self.phone1 if self.phone1 else ''})" \
            f" ({self.phone2 if self.phone2 else ''})"


class Vendor:
    """
    Stores contact details for a property vendor.
    """

    def __init__(self, name=None, phone1=None, phone2=None, phone3=None):
        """
        :param name:   string
        :param phone1: string
        :param phone2: string
        :param phone3: string
        """
        self.name = name
        self.phone1 = phone1
        self.phone2 = phone2
        self.phone3 = phone3

    def __str__(self):
        return f"{self.name if self.name else 'N/A'}" \
            f"({self.phone1 if self.phone1 else 'N/A'}) " \
            f"({self.phone2 if self.phone2 else 'N/A'})" \
            f"({self.phone3 if self.phone3 else 'N/A'})"


class Agent(Client):
    """
    Stores contact details for an Estate agent at branch level
    """

    def __init__(self, name=None, phone1=None, secondary_contact=None, phone2=None, notes=None, address=None,
                 postcode=None):
        """
        :param name:              string
        :param phone1:            string
        :param secondary_contact: string
        :param phone2:            string
        :param notes:             string
        :param address:           string
        :param postcode:          string
        """
        super().__init__(name, phone1, secondary_contact, phone2, notes)
        self.address = Address(address=address, postcode=postcode)


class Job:
    """
    Holds all data that completely describes a job from any client.
    Note not all clients require all attributes to contain valid data
    A Job contains all information needed to successfully carry out a photoshoot of a house for sale.
    It references:
    Job.id (primary key in database later (?)
    The commissioning Client
    The Agent selling the house on behalf of the Vendor
    The Appointment details: Address and time
    The local folder where taken photos are stored  (os.path object)
    The job status (active / archived)
    """
    ACTIVE = 1
    ARCHIVED = 0

    def __init__(self, id_=None, client=Client(None), agent=Agent(None), vendor=None, beds=None, property_type=None,
                 appointment=Appointment(address=Address(None)), folder=None, notes=None, floorplan=True, photos=0,
                 specific_reqs=None, system_notes=None):
        """
        :param id_:            string
        :param client:         Client object
        :param agent:          Agent object
        :param appointment:    Appointment object consisting of Address object and time
        :param folder:         os.path object
        :param: floorplan:     boolean
        :param: photos:        int
        :param: specific_reqs: dict {req : quantity}

        """
        self.id = id_
        self.client = client
        self.agent = agent
        self.vendor = vendor
        self.appointment = appointment
        self.property_type = property_type
        self.beds = beds
        self.notes = notes
        self.floorplan = floorplan
        self.photos = photos
        self.folder = folder
        self.specific_reqs = specific_reqs
        self.status = Job.ACTIVE
        self.system_notes = system_notes
        # todo possible add references to links on webpage for various bits and pieces

    def set_appointment_date(self, time, time_format):
        """"
        Set job appointment date and time as datetime objects
        :param time :        datetime object
        :param time_format : Datetime format
        :return bool
        """
        # assert isinstance(dt.datetime,time)
        # todo implement this
        # self.appointment.date = dt.datetime.
        # self.appointment.time =
        return self.appointment.date and self.appointment.time

    def set_appointment_address(self, address, postcode):
        """" Set job appointment address by creating Address object and setting it's values
        @:return True if successful False otherwise"""
        add = Address(address=address, postcode=postcode)
        self.appointment.address.street = add.street
        self.appointment.address.postcode = add.postcode
        return self.appointment.address.street and self.appointment.address.postcode

    def __str__(self):
        """ String representation of Job."""
        try:
            specifics = "\n".join(f"{k}: {v}" for k, v in self.specific_reqs.items())
        except (TypeError, AttributeError):
            specifics = ""
        try:
            system_notes = "\n".join(f"{d:11.11} {a:5.5} {n:60.60}" for d, a, n in self.system_notes)
        except (TypeError, AttributeError):
            system_notes = ""
        try:
            notes = "\n".join(f"{n:100}" for n in self.notes)
        except (TypeError, AttributeError):
            notes = ""

        return \
            f"ID:\n{self.id}\n" \
                f"CLIENT:\n{self.client}\n" \
                f"AGENT:\n{self.agent}\n" \
                f"VENDOR:\n{self.vendor}\n" \
                f"APPOINTMENT:\n{self.appointment}\n" \
                f"ADDRESS:\n{self.appointment.address}\n" \
                f"PROPERTY:\n{self.property_type}\n" \
                f"BEDS:\n{self.beds}\n" \
                f"FOLDER:\n{self.folder}\n" \
                f"NOTES:\n{notes}\n" \
                f"FLOORPLAN:\n{'Yes' if self.floorplan else 'No'}\n" \
                f"PHOTOS:\n{self.photos}\n" \
                f"SPECIFICS:\n{specifics}\n" \
                f"SYSTEM NOTES:\n{system_notes}"
