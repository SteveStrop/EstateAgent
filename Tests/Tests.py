import pickle
import unittest
from Classes import *
from Parsers import *

# import test data
with open('obj/' + "job_dict_hs" + '.pkl', 'rb') as f:
    JOB_DICT_HS = pickle.load(f)
    # print(JOB_DICT_HS)

with open('obj/' + "job_dict_ka" + '.pkl', 'rb') as f:
    JOB_DICT_KA = pickle.load(f)
    # print(JOB_DICT_KA)


class TestAddress(unittest.TestCase):
    def test__validate_postcodes__(self):
        test_pc = Address()
        self.assertEqual("MK4 4FY", test_pc.__validate_postcode__("MK4 4FY"))
        self.assertEqual("MK44 9QT", test_pc.__validate_postcode__("MK44 9QT"))
        self.assertEqual("MK5 1FZ", test_pc.__validate_postcode__("mk5 1Fz"))
        self.assertEqual(None, test_pc.__validate_postcode__("mk44FY"))


class TestAppointment(unittest.TestCase):
    def test__validate_time__(self):
        self.assertEqual("TBA", Appointment(None, None).__str__())


class TestClient(unittest.TestCase):
    def test__validate_tel__(self):
        test_client = Client()
        tels = [
                ('016977 12345', '016977 12345'),
                ('016977 1234', '016977 1234'),
                ('07891465363', '07891 465 363'),
                ('02077607600', '020 7760 7600'),
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
                ('0207 760 7600', '020 7760 7600')
                ]
        for tel in tels:
            self.assertEqual(tel[1], test_client.validate_tel(tel[0]))


class TestKaParser(unittest.TestCase):
    test_parser = KaParser(Job(), JOB_DICT_KA)
    test_parser.map_job()

    def test_set_id(self):
        i = TestKaParser.test_parser.__set_id__()
        self.assertEqual("1000623765", i)

    def test_set_agent(self):
        a = TestKaParser.test_parser.__set_agent__()
        self.assertEqual("Connells - Stony Stratford", a.branch)
        self.assertEqual("01908 222 343", a.phone_1)
        self.assertEqual("01908 111 999", a.phone_2)

    def test_set_vendor(self):
        v = TestKaParser.test_parser.__set_vendor__()
        self.assertEqual("Mrs Sue Blogs", v.name_1)
        self.assertEqual("07891 123 211", v.phone_1)
        self.assertEqual(None, v.phone_2)
        self.assertEqual("07991 332 456", v.phone_3)

    def test_set_property_type(self):
        p = TestKaParser.test_parser.__set_property_type__()
        self.assertEqual("House", p)

    def test_set_beds(self):
        b = TestKaParser.test_parser.__set_beds__()
        self.assertEqual("3", b)

    def test_set_floorplan(self):
        f = TestKaParser.test_parser.__set_floorplan__()
        self.assertEqual(True, f)

    def test_set_photos(self):
        p = TestKaParser.test_parser.__set_photos__()
        self.assertEqual(p, 20)

    def test_set_notes(self):
        n = TestKaParser.test_parser.__set_notes__()
        self.assertIn("Agency Preferences: Nice photos only please", n[0])
        self.assertIn("General Notes: Take every angle.", n[1])
        self.assertIn("Please get shots of the approach", n[2])

    def test_set_specific_reqs(self):
        s = TestKaParser.test_parser.__set_specific_reqs__()
        self.assertIn("StreetScape", s.keys())

    def test_set_system_notes(self):
        s = TestKaParser.test_parser.__set_system_notes__()
        self.assertIn("SC", s[0][1])
        self.assertIn("Changed  ", s[0][2])

    def test_set_appointment(self):
        a = TestKaParser.test_parser.set_appointment()
        self.assertEqual("29, Test Street Testville, Milton Keynes", a.address.street)
        self.assertEqual("MK4 4FY", a.address.postcode)
        self.assertEqual("Fri 08 Feb @ 00:00", a.__str__())


class TestHsParser(unittest.TestCase):
    test_parser = HsParser(Job(), JOB_DICT_HS)
    test_parser.map_job()  # run this first to make the pandas dataframe table used to store all scraped data

    def test_set_id(self):
        i = TestHsParser.test_parser.__set_id__()
        self.assertEqual("HSS103120", i)

    def test_set_vendor(self):
        v = TestHsParser.test_parser.__set_vendor__()
        self.assertEqual("joe blogs", v.name_1)
        self.assertEqual(None, v.phone_1)

    def test_set_property_type(self):
        p = TestHsParser.test_parser.__set_property_type__()
        self.assertEqual("Semi-detached House", p)

    def test_set_appointment(self):
        a = TestHsParser.test_parser.set_appointment()
        self.assertEqual("37 Testy Road, Testtown, Bedfordshire", a.address.street)
        self.assertEqual("MK41 5DA", a.address.postcode)
        self.assertEqual("Sat 08 Dec @ 15:00", a.__str__())
