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
    test_parser = KaParser(Job(), JOB_DICT_KA)
    def test_set_vendor(self):
        v = TestKaParser.test_parser.__set_vendor__()
        self.assertEqual("Mrs Sue Blogs", v.name)
        self.assertEqual("07891123211", v.phone1)
        self.assertEqual(None, v.phone2)
        self.assertEqual("07991332456", v.phone3)

    def test_set_agent(self):
        a = TestKaParser.test_parser.__set_agent__()
        self.assertEqual("Connells - Stony Stratford", a.name)
        self.assertEqual("01908 222 343", a.phone1)
        self.assertEqual("01908 111 999", a.phone2)

    def tests_et_floorplan(self):
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

    def test_set_streetscape(self):
        s = TestKaParser.test_parser.__set_specific_reqs__()
        self.assertIn("StreetScape", s.keys())

    def test_set_system_notes(self):
        s = TestKaParser.test_parser.__set_system_notes__()
        self.assertIn("SC", s[0][1])
        self.assertIn("Changed  ", s[0][2])

    def test_set_appointment(self):
        a= TestKaParser.test_parser.__set_appointment__()
        self.assertEqual("29, Test Street Testville, Milton Keynes", a.address.street)
        self.assertEqual("MK4 4FY", a.address.postcode)
        self.assertEqual("Fri 08 Feb @ 00:00", a.__str__())


class TestHsParser(unittest.TestCase):
    test_parser = HsParser(Job(), JOB_DICT_HS)
