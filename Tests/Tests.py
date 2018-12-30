import unittest

from EstateAgent.Classes import *
from EstateAgent.Parsers import *
from EstateAgent.Scrapers import *


def import_test_data():
    # import test data
    with open('obj/' + "job_dict_hs" + '.pkl', 'rb') as f:
        hs = pickle.load(f)
        # print(hs)
    with open('obj/' + "job_dict_ka" + '.pkl', 'rb') as f:
        ka = pickle.load(f)
        # print(ka)
        return hs, ka


JOB_DICT_HS, JOB_DICT_KA = import_test_data()


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
        i = TestKaParser.test_parser._extract_id()
        self.assertEqual("1000623765", i)

    def test_set_agent(self):
        a = TestKaParser.test_parser._extract_agent()
        self.assertEqual("Connells - Stony Stratford", a.branch)
        self.assertEqual("01908 222 343", a.phone_1)
        self.assertEqual("01908 111 999", a.phone_2)

    def test_set_vendor(self):
        v = TestKaParser.test_parser._extract_vendor()
        self.assertEqual("Mrs Sue Blogs", v.name_1)
        self.assertEqual("07891 123 211", v.phone_1)
        self.assertEqual(None, v.phone_2)
        self.assertEqual("07991 332 456", v.phone_3)

    def test_set_property_type(self):
        p = TestKaParser.test_parser._extract_property_type()
        self.assertEqual("House", p)

    def test_set_beds(self):
        b = TestKaParser.test_parser._extract_beds()
        self.assertEqual("3", b)

    def test_set_floorplan(self):
        f = TestKaParser.test_parser._extract_floorplan()
        self.assertEqual(True, f)

    def test_set_photos(self):
        p = TestKaParser.test_parser._extract_photos()
        self.assertEqual(p, 20)

    def test_set_notes(self):
        n = TestKaParser.test_parser._extract_notes()
        self.assertIn("Agency Preferences: Nice photos only please", n[0])
        self.assertIn("General Notes: Take every angle.", n[1])
        self.assertIn("Please get shots of the approach", n[2])

    def test_set_specific_reqs(self):
        s = TestKaParser.test_parser._extract_specific_reqs()
        self.assertIn("StreetScape", s.keys())

    def test_set_system_notes(self):
        s = TestKaParser.test_parser._extract_system_notes()
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
        i = TestHsParser.test_parser._extract_id()
        self.assertEqual("HSS103120", i)

    def test_set_vendor(self):
        v = TestHsParser.test_parser._extract_vendor()
        self.assertEqual("joe blogs", v.name_1)
        self.assertEqual(None, v.phone_1)

    def test_set_property_type(self):
        p = TestHsParser.test_parser._extract_property_type()
        self.assertEqual("Semi-detached House", p)

    def test_set_appointment(self):
        a = TestHsParser.test_parser.set_appointment()
        self.assertEqual("37 Testy Road, Testtown, Bedfordshire", a.address.street)
        self.assertEqual("MK41 5DA", a.address.postcode)
        self.assertEqual("Sat 08 Dec @ 15:00", a.__str__())


class TestHsScraper(unittest.TestCase):
    s = HsScraper()

    def test__get_job_links__(self):
        test_link = '<a href="https://www.housesimple.com/admin/home-visit-supplier/303133/show">'
        with open("G:/EstateAgent/Tests/obj/HS_dashboard.html", "r") as f:
            html = BeautifulSoup(f, "lxml")
        links = TestHsScraper.s.extract_job_links(html)
        self.assertIn(test_link, str(links[0]))

    def test__get_page_fields__(self):
        test_string = "Northamptonshire, NN5 5DA"
        with open("G:/EstateAgent/Tests/obj/HS_job_page.html", "r") as f:
            html = BeautifulSoup(f, "lxml")
        job_dict = TestHsScraper.s._extract_page_fields(html)
        self.assertIn(test_string, str(job_dict["JOB_DATA_TABLE"][0]))


class TestKaScraper(unittest.TestCase):
    s = KaScraper()

    def test__get_job_links__(self):
        test_link = "javascript:__doPostBack('ctl00$text$GridViewOutstandingCases','Select$0')"
        with open("G:/EstateAgent/Tests/obj/KA_Welcome_page.html", "r") as f:
            html = BeautifulSoup(f, "lxml")
        links = TestKaScraper.s.extract_job_links(html)
        self.assertIn(test_link, str(links[0]))

    def test__get_page_fields__(self):
        agent_test = "H Brown of Connells  MOB:01908 563 993  TEL:01908 563 993  EVE:N/A"
        date_test = "Fri-08 Feb 19 0000"
        history_test = "THIS IS A PLACEHOLDER APPOINTMENT"

        with open("G:/EstateAgent/Tests/obj/KA_job_page.html", "r") as f:
            html = BeautifulSoup(f, "lxml")
        job_dict = TestKaScraper.s._extract_page_fields(html)
        self.assertEqual(job_dict["JOB_DATA_AGENT"], agent_test)
        self.assertEqual(job_dict["JOB_DATA_APPOINTMENT"], date_test)
        self.assertIn(history_test, str(job_dict["JOB_DATA_HISTORY_TABLE"]))
