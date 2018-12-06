import pickle
import unittest
from classes import *
import datetime
from Parsers import *

# import test data
with open('obj/' + "job_dict" + '.pkl', 'rb') as f:
    JOB_DICT = pickle.load(f)

with open('obj/' + "demo_job" + '.pkl', 'rb') as f:
    DEMO_JOB = pickle.load(f)

with open('obj/' + "table_ss" + '.pkl', 'rb') as f:
    TABLE_SS = pickle.load(f)

with open('obj/' + "table_sv" + '.pkl', 'rb') as f:
    TABLE_SV = pickle.load(f)

with open('obj/' + "notes_string" + '.pkl', 'rb') as f:
    NOTES_STRING = pickle.load(f)


class TestAddress(unittest.TestCase):
    def test__validate_postcodes__(self):
        test_pc = Address()
        self.assertEqual("MK4 4FY", test_pc.__validate_postcode__("MK4 4FY"))
        self.assertEqual("MK44 9QT", test_pc.__validate_postcode__("MK44 9QT"))
        self.assertEqual("MK5 1FZ", test_pc.__validate_postcode__("mk5 1Fz"))
        self.assertEqual(None, test_pc.__validate_postcode__("mk44FY"))


class TestAppointment(unittest.TestCase):
    def test__validate_time__(self):
        test_app = Appointment()
        dates = [["050220180810", ("05-02-2018", "08:10")],
                 ["05/02 201808:10", ("05-02-2018", "08:10")],
                 ["67", (None, None)],
                 [" ", (None, None)],
                 ["", (None, None)]]
        for date in dates:
            if date[1][0]:
                self.assertIsInstance(test_app.__validate_time__(date[0]), datetime.datetime)
            else:
                self.assertEqual(test_app.__validate_time__(date[0]), None)


class TestClient(unittest.TestCase):
    def test__validate_tel__(self):
        test_client = Client()
        tels = [('07891465363', '07891 465 363'),
                ('02077607600', '02077 607 600'),
                ('07891 465 363', '07891 465 363'),
                ('(07891)465363', '07891 465 363'),
                ('(07891) 465 363', '07891 465 363'),
                ('07891465363', '07891 465 363'),
                ('07891-465-363', '07891 465 363'),
                ('(07891)465363', '07891 465 363'),
                ('(07891)-465-363', '07891 465 363'),
                ('01908501401', '01908 501 401'),
                ('(01908)501401', '01908 501 401'),
                ('(01908)501 401', '01908 501 401'),
                ('(01908) 501 401', '01908 501 401'),
                ('01908 501401', '01908 501 401'),
                ('01908 501 401', '01908 501 401'),
                ('(01908)501-401', '01908 501 401'),
                ('(01908)-501-401', '01908 501 401'),
                ('01908-501401', '01908 501 401'),
                ('01908-501-401', '01908 501 401'),
                ('0207 760 7600', '02077 607 600')
                ]
         # todo this is NOT correct for London (similar issue for other cities as well!!)
        for tel in tels:
            self.assertEqual(tel[1], test_client.__validate_tel__(tel[0]))


class TestKaParser(unittest.TestCase):
    test_parser = KaParser(Job(), {**ConfigKA.JOB_PAGE_DATA, **ConfigKA.JOB_PAGE_TABLES})

    def test__set_vendor__(self):
        v = TestKaParser.test_parser.__set_vendor__(
                "Other Vendor:Mr Sue Blogs DAY:07895456410 MOB:07121456789 EVE:N/A Email:N/A")
        self.assertEqual(v.name, "Mr Sue Blogs")
        self.assertEqual(v.phone1, "07895456410")
        self.assertEqual(v.phone2, "07121456789")
        v = TestKaParser.test_parser.__set_vendor__(
                "Other Vendor:Mr Sue Blogs DAY:07895456410 MOB:N/A EVE:07121456789 Email:N/A")
        self.assertEqual(v.name, "Mr Sue Blogs")
        self.assertEqual(v.phone1, "07895456410")
        self.assertEqual(v.phone2, "07121456789")

    def test__set_agent__(self):
        a = TestKaParser.test_parser.__set_agent__(
                "	H Brown of Connells MOB:01908 563 993 TEL:01908 563 993 EVE:N/A")
        self.assertEqual(a.name, "Connells")
        self.assertEqual(a.phone1, "01908 563 993")
        self.assertEqual(a.phone2, "01908 563 993")

    def test__set_floorplan__(self):
        f = TestKaParser.test_parser.__set_floorplan__(" Yes")
        self.assertEqual(True, f)
        f = TestKaParser.test_parser.__set_floorplan__("Yes")
        self.assertEqual(True, f)
        f = TestKaParser.test_parser.__set_floorplan__(" No")
        self.assertEqual(False, f)

    def test__set_photos__(self):
        p = TestKaParser.test_parser.__set_photos__("	Yes - 20 photos (0) Allocated")
        self.assertEqual(20, p)
        p = TestKaParser.test_parser.__set_photos__("	Yes - 9 photos (0) Allocated")
        self.assertEqual(9, p)
        p = TestKaParser.test_parser.__set_photos__("	Yes - 09 photos (0) Allocated")
        self.assertEqual(9, p)

    def test__set__notes__(self):

        n = TestKaParser.test_parser.__set_notes__(NOTES_STRING)
        self.assertIn("prefs", n[0])
        self.assertIn("Beautiful Cottage", n[1])

    def test__set_streetscape__(self):

        s = TestKaParser.test_parser.__set_specific_reqs__(TABLE_SS)
        self.assertIn("StreetScape", s.keys())

    def test__set_system_notes__(self):
        s = TestKaParser.test_parser.__set_system_notes__(TABLE_SV)
        self.assertIn("SC", s[0][1])
        self.assertIn("Changed  ", s[0][2])

    def test__set_appointment__(self):
        test_strings = [
                ("30, Lower Weald Calverton, Milton Keynes", "MK19 6EQ", "03 12 2018 14:30")
        ]
        for street_string, postcode_string, time_string in test_strings:
            address_string = street_string + postcode_string
            a = TestKaParser.test_parser.__set_appointment__(time_string, address_string)
            self.assertEqual(street_string, a.address.street)
            self.assertEqual(datetime.datetime(2018, 12, 3, 14, 30), a.date)


class TestHsParser(unittest.TestCase):
    test_parser = HsParser(Job(), JOB_DICT)

    def test__reformat_date__(self):
        test_string = [("25/12/2018 @ 12:00", "25-12-2018 12:00")]  # ,("25/12/18 @ 12:00",None),(None,None)]
        for s in test_string:
            r = TestHsParser.test_parser.__reformat_date__(s[0])
            self.assertEqual(s[1], r)
