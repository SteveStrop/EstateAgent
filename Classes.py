import re
import datetime


class Address:
    postcode_regexp = r'[A-Z]{1,2}[\dR][\dA-Z]? [\d][A-Z]{2}'

    def __init__(self, address=None, postcode=""):
        self.street = address
        self.postcode = self.__validate_postcode__(postcode)

    @staticmethod
    def __validate_postcode__(postcode):
        """ Convert input to upper case then check if it is a valid mainland UK postcode
        @:param postcode string to test
        :return validated uppercase postcode or None"""
        try:
            postcode = postcode.upper()
            return re.fullmatch(Address.postcode_regexp, postcode)[0]
        except AttributeError:
            return None
        except TypeError:
            return None

    def __str__(self):
        return f"{self.street if self.street else ''}, {self.postcode if self.postcode else ''}"


class Appointment:
    def __init__(self, address=Address(None), dtime=None):
        """@param address: Address object
        @:param dtime: date and time in format 'dd*mm*yyyy*HH*MM' """
        self.address = address
        self.date = self.__validate_time__(dtime)

    def __validate_time__(self, time):
        """ check input is in the format
        'dd*mm*yyyy*HH*MM' and convert it to a datetime object if it is. Note * is any (combination of)separator(s)
        @:return a valid datetime object or None
        """
        try:  # convert time to list of the digits
            time = [c for c in time if c.isdigit()]
            dd = int(self.__multi_pop__(time, 2))
            mm = int(self.__multi_pop__(time, 2))
            yyyy = int(self.__multi_pop__(time, 4))
            hh = int(self.__multi_pop__(time, 2))
            mn = int(self.__multi_pop__(time, 2))
            date = datetime.datetime(yyyy, mm, dd, hh, mn)
            return date
        except (TypeError, IndexError):
            return None

    @staticmethod
    def __multi_pop__(l, n):
        """ pop n items from beginning of list l
        @:return string of n items"""
        string = ""
        for i in range(n):
            string += l.pop(0)
        return string

    def __str__(self):
        try:
            return self.date.strftime("%a %d %b @ %H:%M")  # Day dd Mmm @ hh:mm
        except (TypeError, AttributeError):
            return "TBA"


class Client:
    """ contains all client details:
    @:param name: string
    @:param primary_contact: string
    @:param primary_tel: string
    @:param secondary_contact: string
    @:param secondary_tel: string
    @:param notes string
    """
    VALID_TEL= r'^\(?\d{4,5}\)?[ -]?\d{3}[ -]?\d{3,4}$'
    def __init__(self, name=None, phone1=None, secondary_contact=None, phone2=None, notes=None):
        self.name = name
        self.phone1 = self.__validate_tel__(phone1)
        self.secondary_contact = secondary_contact
        self.phone2 = self.__validate_tel__(phone2)
        self.notes = notes

    @staticmethod
    def __validate_tel__(tel):
        """ Check phone1 is valid uk phone number
        @:return number formatted as ##### ### ###"""  # todo consider adding uk city formatting support
        try:  # strip non digits from phone1
            tel = [n for n in tel if n.isdigit()]
            tel = "".join(tel)
        except TypeError:
            return None
        try:
            tel = re.fullmatch(Client.VALID_TEL, tel)[0]
        except AttributeError:
            return None
        except TypeError:
            return None
        else:
            return tel[:5] + " " + tel[5:8] + " " + tel[8:]

    def __str__(self):
        return f"{self.name if self.name else ''} ({self.phone1 if self.phone1 else ''})" \
            f" ({self.phone2 if self.phone2 else ''})"


class Vendor:
    def __init__(self, name=None, phone1=None, phone2=None):  # todo use Client validate phone method here possibly by
        # todo making vendor a subclass of client
        self.name = name
        self.phone1 = phone1
        self.phone2 = phone2

    def __str__(self):
        return f"{self.name if self.name else 'N/A'} ({self.phone1 if self.phone1 else 'N/A'}) " \
            f"({self.phone2 if self.phone2 else 'N/A'})"


class Agent(Client):

    def __init__(self, name=None, phone1=None, secondary_contact=None, phone2=None,
                 notes=None, address=None, postcode=None):
        super().__init__(name, phone1, secondary_contact, phone2, notes)
        self.address = Address(address=address, postcode=postcode)


class Job:  # todo make KAJob, HSJob, TMJob etc sub classes or keep this one generic (opt 2 better!)
    """A generic class to hold all data that completely describes a job from any client.
    Note not all clients require all attributes to contain valid data"""
    ACTIVE = 1
    ARCHIVED = 0
    """ A Job contains all information needed to successfully carry out a photoshoot of a house for sale.
    It references:
    Job iD (primary key in database later (?)
    the commissioning client (Client object)
    the agent selling the house (Agent object)
    the appointment details (Appointment object)
    the photo folder where taken photos are stored  (os.path object)
    status (active / archived)
    """

    def __init__(self, id_=None, client=Client(None), agent=Agent(None), vendor=None, beds=None, property_type=None,
                 appointment=Appointment(address=Address(None)), folder=None, notes=None, floorplan=True, photos=0,
                 specific_reqs=None, system_notes=None):
        """
        @:param id_: string
        @:param client: Client object
        @:param agent: Agent
        @:param appointment: (Appointment object consisting of Address object and time)
        @:param folder: (os.path object)
        @:param: floorplan: boolean
        @:param: photos: int
        @:param: specific_reqs: dict

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

    def set_appointment_date(self, time):
        """" Set job appointment date and time by calling __validate_time__ method of class Appointment
        @:return True if successful False otherwise"""
        self.appointment.date, self.appointment.time = Appointment.__validate_time__(Appointment(), time)
        return self.appointment.date and self.appointment.time

    def set_appointment_address(self, address, postcode):
        """" Set job appointment address by creating Address object and setting it's values
        @:return True if successful False otherwise"""
        add = Address(address=address, postcode=postcode)
        self.appointment.address.street = add.street
        self.appointment.address.postcode = add.postcode
        return self.appointment.address.street and self.appointment.address.postcode

    def __str__(self):
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
