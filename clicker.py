from selenium.webdriver.common.by import By
from datetime import datetime
import Scrapers
import ConfigKA
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def __wait_clickable__(id_, delay=10):
    """
    Wait for 'delay' seconds for a DOM element with given 'id_' to become clickable.
    Return TimeoutException if method fails
    :param id_ : string. A valid CSS id tag
    :param delay: int delay in seconds
    :return selenium WebElement"""

    wait = WebDriverWait(driver, delay)
    return wait.until(EC.element_to_be_clickable((By.ID, id_)))

def change_appt(new_appt, reason=None):
    DATE_FORMAT = "%d/%m/%Y"  # dd/mm/yyyy
    TIME_FORMAT = "%H%M"  # HHMM
    if reason is None:
        reason = ConfigKA.CHANGE_APPT_BUTTONS["CHANGE_SELECT_OPTIONS"]["VENDOR_REQ"]
    change_appt_btn = driver.find_element_by_id(ConfigKA.JOB_PAGE_BUTTONS["JOB_CHANGE_APPT"])
    change_appt_btn.click()

    select_drop = Select(__wait_clickable__(ConfigKA.CHANGE_APPT_BUTTONS["CHANGE_SELECT"]))
    select_drop.select_by_visible_text(reason)

    text_box = __wait_clickable__(ConfigKA.CHANGE_APPT_BUTTONS["CHANGE_TEXT_BOX"])
    print(type(text_box))
    date_box = __wait_clickable__(ConfigKA.CHANGE_APPT_BUTTONS["CHANGE_APPT_DATE"])
    time_box = __wait_clickable__(ConfigKA.CHANGE_APPT_BUTTONS["CHANGE_APPT_TIME"])
    text_box.send_keys(".")
    date_box.clear()
    date_box.send_keys(new_appt.strftime(DATE_FORMAT))
    time_box.clear()
    time_box.send_keys(new_appt.strftime(TIME_FORMAT))



# driver = webdriver.Chrome(ConfigKA.CHROME_DRIVER)
# driver.get("file:///G:/EstateAgent/Tests/obj/ChangeApptPopUp.html")

s = Scrapers.KaScraper()
driver = s._logon(
        landing_pg="https://www.keyagent-portal.co.uk/Site/Dea/Dea.aspx?DEA=272ca14b-8535-453f-bf30-10e5c0318651&Quote"
                   "=8972d072-238a-4b2a-aaea-5dd7c8a53892&Logged=True")
driver.implicitly_wait(30)
new_appt = datetime(2018, 12, 24, 13, 45)
change_appt(new_appt)
