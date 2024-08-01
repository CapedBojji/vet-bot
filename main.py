STALL_AFTER_LOGIN = 20

NUMBER_OF_DAYS = 11

EARLIEST_TIME = "10:00am"

LATEST_TIME = "11:30pm"

LONGEST_SHIFT = 12

WEEKDAYS = [
    "Sunday",
    "Monday",
"Wednesday",
"Thursday",
"Saturday",
]


CHROME_PROFILE_DIRECTORY_PATH = r"/mnt/c/Users/caped/AppData/Local/Google/Chrome/User Data"

LOGIN_URL = "https://idp.amazon.work/idp/profile/SAML2/Unsolicited/SSO?"
LOGGED_IN_URL = "https://atoz.amazon.work/shifts"

USERNAME = "laudboat"

PASSWORD = "OVOxcR6cTXSD"

HOURS_TO_RUN = 10  # Hours

SECONDS_BETWEEN_CHECKS = 10

import datetime
import time
import undetected_chromedriver as uc
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium import webdriver
from datetime import date, timedelta

class Browser:
    
    def __init__(self):
        self.options = ChromeOptions()
        self.options.add_argument(f"--user-data-dir={CHROME_PROFILE_DIRECTORY_PATH}")
        self.options.add_argument(f"--profile-directory=Default")
        # self.options.binary_location = "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
        # self.options.add_argument("--headless")
        # self.driver = uc.Chrome(options=self.options)
        self.driver = webdriver.Chrome(options=self.options) 
        self.driver.get("https://atoz-login.amazon.work/")

    def is_logged_in(self):
        return self.driver.current_url == LOGGED_IN_URL

    def login(self):
        uname = self.driver.find_element(By.XPATH, "//input[@id='login']")
        uname.send_keys(USERNAME)
        pword = self.driver.find_element(By.XPATH, "//input[@id='password']")
        pword.send_keys(PASSWORD)
        submit = self.driver.find_element(By.XPATH, "//button[@id='buttonLogin']")
        submit.click()
        time.sleep(STALL_AFTER_LOGIN)

    def authenticate(self):
        element = self.driver.find_element(By.XPATH, "//input[@value='2']")
        element.click()
        button = self.driver.find_element(By.XPATH, "//button[@id='buttonContinue']")
        button.click()
        time.sleep(4)


    def stall_until_solved(self):
        while True:
            try:
                header = self.driver.find_element(By.XPATH, "//h1[@class='top-h1']")
                if "Verify your identity" in header.text:
                    self.driver.find_element(By.XPATH, "//input[@id='code']")
                    time.sleep(10)
            except:
                break

    def check_verify(self):
        try:
            self.authenticate()
            checkbox = self.driver.find_element(By.XPATH, "//label[@id='trusted-device-option-label']")
            checkbox.click()
            self.stall_until_solved()
        except:
            pass

    def save_cookies(self):
        cookies = self.driver.get_cookies()
        json.dump(cookies, open("cookies", "wt", encoding="utf8"))

    def exit(self):
        self.driver.quit()


    def back_home(self):
        link = self.driver.find_element(By.XPATH, "//ul[contains(@class, 'navbar-left')]/li[@class='active']/a")
        link.click()

    def navigate_to_date(self, date):
        self.driver.get(f"https://atoz.amazon.work/shifts/schedule/find?date={date}")

    def check_automatic_sign_out(self):
        try:
            element = self.driver.find_element(By.XPATH, ".//div[@id='session-expires-modal']")
            print(f'Session expires modal: {element is not None}')
            if element.is_displayed():
                print(f'Session expires modal displayed')
                button = self.driver.find_element(By.XPATH, ".//button[@id='session-expires-modal-btn-stay-in']")
                button.click()
                time.sleep(2)
                print("Stayed in")
        except:
            pass
        

    def pick_shifts(self):
        print("Picking shifts")
        for row in self.driver.find_elements(By.XPATH, "//div[@role='listitem']"):
            print("Checking row")
            try:
                # Grab add shift button, will error if it's not there thus skipping the row
                add_shift = row.find_element(By.XPATH, ".//button[@aria-label='Add shift button']")
                # Grab the text element
                textelem = row.find_element(By.XPATH, ".//div[@data-test-component='StencilText']")
                # Grab the text
                hours = textelem.text
                # Grab the time
                parts = hours.split(" ")
                start, end = parts[0].split("-")
                # Check if the shift extends to the next day
                next_day = False
                if "pm" in start and "am" in end:
                    next_day = True
                # Check if my time preference extends to the next day
                preference_next_day = False
                if "pm" in EARLIEST_TIME and "am" in LATEST_TIME:
                    preference_next_day = True
                # If the shift extends to the next day and my preference doesn't, skip
                if next_day and not preference_next_day:
                    continue
                
                prefered_start = to_military_time(EARLIEST_TIME)
                prefered_end = to_military_time(LATEST_TIME)
                shift_start = to_military_time(start)
                shift_end = to_military_time(end)
                
                # Make sure shift isn't too long
                if get_military_minutes_difference(shift_start, shift_end) > LONGEST_SHIFT * 60:
                    continue
                # check if the shift starts in the prefered time
                if preference_next_day:
                    if shift_start < prefered_start and shift_end > prefered_end:
                        continue
                else:
                    if shift_start < prefered_start or shift_end > prefered_end:
                        continue
                # check if the shift ends in the prefered time
                if next_day:
                    if shift_end < prefered_start and shift_end > prefered_end:
                        continue
                else:
                    if shift_end > prefered_end or shift_end < prefered_start:
                        continue
                print("Shift is good")
                # If all checks pass, click the add shift button
                add_shift.click()
                time.sleep(0.5)
                button = self.driver.find_element(By.XPATH, "//button[@data-test-id='AddOpportunityModalSuccessDoneButton']")
                button.click()
                time.sleep(0.5)
            except Exception as ex:
                pass


def get_today_date() -> date :
    return date.today()

def add_one_day(input_date: date):
    # Add one day to the date
    return input_date + timedelta(days=1)

def get_day_of_week(input_date: date):
    return input_date.strftime("%A")

def to_military_time(time):
    hour, minute = time.split(":")
    hour = int(hour)
    if hour == 12 and "am" in time:
        hour = 0
    elif "pm" in time and hour != 12:
        hour += 12
    minute = int(minute[:2])   
    return hour * 100 + minute

def get_military_minutes_difference(time1, time2):
    minutes1 = time1 % 100
    minutes2 = time2 % 100
    hours1 = time1 // 100
    hours2 = time2 // 100
    if hours1 < hours2:
        hour = hours2 - hours1
        minute = minutes2 - minutes1
        return hour * 60 + minute
    else:
        hour = hours1 - hours2
        minute = minutes1 - minutes2
        return hour * 60 + minute

        
def parse_hour(hora):
    hour, mint = hora.split(":")
    minute = "".join([i for i in mint if i.isdigit()])
    section = mint[len(minute):]
    hour, minute = int(hour), int(minute)
    if section == "pm" and hour != 12:
        hour += 12
    return (hour, minute)

def earlier_time(time1, time2):
    if time1[0] > time2[0]:
        return time2
    elif time1[0] < time2[0]:
        return time1
    elif time1[1] > time2[1]:
        return time2
    else:
        return time1

def time_diff(time1, time2):
    if time1[0] < time2[0]:
        midnight_offset = 24 - time2[0]
        time2 = list(time2)
        time2[0] = - midnight_offset
    diff = time1[0] - time2[0]
    diff -= time1[1] / 60
    diff += time2[1] / 60
    return diff

def main():
    start = time.time()
    browser = Browser()
    time.sleep(10)
    if not browser.is_logged_in():
        browser.login()
    browser.check_verify()
    browser.save_cookies()
    time.sleep(STALL_AFTER_LOGIN)
    while time.time() - start < HOURS_TO_RUN * 60 * 60:
        try:
            done = time.time()
            today = get_today_date()
            days_to_run = NUMBER_OF_DAYS
            for i in range(days_to_run):
                print(i)  
                browser.check_automatic_sign_out()
                if i== 0 or i == 1 or i == 2:
                    print("Skipping")
                    today = add_one_day(today)
                    continue
                if (str.capitalize(get_day_of_week(today)) in WEEKDAYS):
                    browser.navigate_to_date(today)
                    # Wait for the page to load
                    time.sleep(1)
                    browser.pick_shifts()
                today = add_one_day(today)
                time.sleep(1)
            while time.time() - done < SECONDS_BETWEEN_CHECKS:
                time.sleep(1)
        except Exception as ex:
            pass
    browser.exit()

if __name__ == "__main__":
    main()
    