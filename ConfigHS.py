import pw

"""Configuration file containing complete specifications for accessing a config's webpage to enable
scraping of job
related data
"""
# Environment variables-------------------------------------------------------------------------------------------------
CHROME_DRIVER = "C:\Python36\selenium\webdriver\chrome\chromedriver.exe"
TIME_FORMAT = "%d/%m/%Y @ %H:%M"

# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------          LOG ON DATA                ----------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

CLIENT = "House Simple"
WELCOME_PAGE = "https://www.housesimple.com/admin/dashboard"
USERNAME = pw.USERNAME
PASSWORD = pw.PASSWORD
LOGIN_PAGE = "https://www.housesimple.com/admin/dashboard"
LANDING_PAGE = "https://www.housesimple.com/admin/dashboard"
USERNAME_FIELD = "_username"
PASSWORD_FIELD = "_password"
LOGIN_BUTTON = "_submit"

# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------        HTML ID TAGS FOR DATA        ----------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

JOB_PAGE_DATA = {
        "ID":          "Reference",
        "ADDRESS":     "Address",
        "BEDS":        "Number of bedrooms",
        "PROPERTY":    "Property type",
        "APPOINTMENT": "Appointment time",
        "VENDOR":      "Name"
}
JOB_PAGE_TABLES = {
        "JOB_DATA_TABLE": "table"
}

# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------          HTML BUTTONS               ----------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

JOB_PAGE_BUTTONS = {
        "JOB_DECLINE":           "ctl00_main_ButtonDecline",
        "JOB_ADD_NOTE":          "ctl00_main_ButtonAddNoteAppointment",
        "JOB_SAVE_APPT":         "ctl00_main_ButtonSaveAppointment",
        "JOB_SAVE_NO_APPT":      "ctl00_main_ButtonSaveNoAppointment",
        "JOB_CHANGE_APPT":       "ctl00_main_ButtonChangeAppointment",
        "JOB_NO_APPT_DROPDOWN":  "ctl00_main_DropDownListNoAppointment",
        "JOB_DATE_ENTRY":        "ctl00_main_TextBoxAppointmentDate",
        "JOB_TIME_ENTRY":        "ctl00_main_TextBoxAppointmentTime",
        "JOB_FAST_UPLOAD":       "ctl00_main_ButtonFastUpload",
        "JOB_CONFIRM_FLOORPLAN": "ctl00_main_ConfirmFloorplanUpload",
        "JOB_CONFIRM_PHOTOS":    "ctl00_main_ConfirmPhotoUpload",
        "JOB_BACK":              "ctl00_main_ButtonBack"
}
UPLOAD_PAGE_BUTTONS = {
        "UPLOAD_SELECT_FLOORPLAN": "fileFloorplans",
        "UPLOAD_UPLOAD_FLOORPLAN": "ancFloorplans",
        "UPLOAD_SELECT_PHOTOS":    "filePhotos",
        "UPLOAD_UPLOAD_PHOTOS":    "ancPhotos",
        "UPLOAD_CLOSE":            "ButtonClose",
}

# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------          CLIENT SPECIFIC            ----------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

CONFIRMED_HOME_VISIT_TABLE = "table"  # class="sonata-home-visit-block-home-visit-container table table-condensed"
JOB_STATUS = "Status"  # column heading name for Job Status
JOB_OPEN = "Confirmed"  # matches  CONFIRMED_HOME_VISIT_TABLE <span class="label--success" for open job
