from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time
import pandas as pd
# =============================================================================
# (1) ** PUT YOUR OWN LOG-IN INFO
LOGIN_INFO = {
    'email': 'put_your_id@gmail.com',
    'password': 'put_your_password123'
}
# (2) ** specify your chromedriver path
# given path is when you download it in Downloads folder (my user name: jepp)
CHROME_PATH = '/users/jepp/Downloads/chromedriver'
# =============================================================================

# ED URL
URL_LOGIN = "https://us.edstem.org/login"
URL_FORUM = "https://us.edstem.org/courses/490/discussion/"
URL_PROFILE = "https://us.edstem.org/settings/profile"

SCROLL_PAUSE_TIME = 2
KEY_PAUSE_TIME = 0.3
HOW_MANY_CATEGORY = 13


def main():
    # split by category, as there are too many of posts in total
    # make a list with xpaths of the category button
    list_of_category = []
    for i in range(1, HOW_MANY_CATEGORY + 1, 1):
        cat = str('//*[@id="main"]/div/div/div/div/div/div[1]/div/div[2]/div[1]/div/div[' + str(i) + ']/div').replace(
            " ", "")
        list_of_category.append(cat)

    # open a chrome webdriver
    driver = webdriver.Chrome(CHROME_PATH)
    driver.set_window_size(2560, 1800)  # enlarge the browser, otherwise category: drop-down menu
    driver.implicitly_wait(3)

    # log-in, get to forum and wait a bit
    log_in_to_ed(driver)
    driver.get(URL_FORUM)
    wait_loading(driver, "dtf-group-heading")

    # for each category
    for i in range(len(list_of_category)):
        a_category = list_of_category[i]
        # go to category page, scroll down until no more posts
        go_to_category_and_click(driver, a_category, i)
        infinite_scroll(driver, 15, i)

        # write on csv file
        time.sleep(SCROLL_PAUSE_TIME)
        file_name = str("result_" + str(i) + ".csv").replace(" ", "")
        write_as_csv(driver, file_name)
        driver.find_element_by_xpath(a_category).click()  # close category tab, otherwise mis-located
        convert_to_excel(file_name)


def log_in_to_ed(driver):
    driver.get(URL_LOGIN)
    # 1st LOGIN PAGE ATTEMPT - ID
    driver.find_element_by_name('email').send_keys(LOGIN_INFO['email'])
    driver.find_element_by_xpath('//*[@id="main"]/div/form/button').click()
    # 2nd LOGIN PAGE ATTEMPT - PW
    driver.find_element_by_name('password').send_keys(LOGIN_INFO['password'])
    driver.find_element_by_xpath('//*[@id="main"]/div/form/button').click()
    wait_loading(driver, "dash-courses")


def wait_loading(driver, class_name):
    wait = WebDriverWait(driver, 10)  # make browser waits until the next page, otherwise data-misload
    wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, class_name)))


def infinite_scroll(driver, loop, i):
    if (i == 8 - 1) or (i == 12 - 1):
        num_of_loop = 10  # Assignment & Social has significant posts
    else:
        num_of_loop = 3

    for i in range(loop):
        if you_see_the_end(driver):
            break
        for j in range(num_of_loop):
            ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(SCROLL_PAUSE_TIME)  # go down down down
            for k in range(10):
                ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()
                time.sleep(KEY_PAUSE_TIME)  # go down down down


def you_see_the_end(driver):
    try:
        driver.find_element_by_xpath('//button[text()="No more threads"]')
        # in total page not exists, but in category page there's button indicating the end
        return True
    except:
        return False


def go_to_category_and_click(driver, xpath, i):
    driver.find_element_by_xpath(xpath).click()
    time.sleep(SCROLL_PAUSE_TIME)  # if you don't wait, it will select first post of total page
    wait_loading(driver, "dtf-item")
    if i == 0:
        driver.find_element_by_class_name('dtf-group-more').click()  # General category has 'more post' button
        wait_loading(driver, "dtf-item")
    driver.find_element_by_class_name("dtf-item").click()
    wait_loading(driver, "dtf-title")


def get_title_data(soup, block, name_of_title, name_list):
    single_post = soup.select(block)
    for title in single_post:
        line_of_data = str(title.attrs[name_of_title]).replace(" ", "_").split()
        name_list.append(line_of_data)


def get_text_data(soup, block, name_list):
    single_post = soup.select(block)
    for elem in single_post:
        line_of_data = str(elem.text).replace(" ", "_").split()
        name_list.append(line_of_data)


def write_as_csv(driver, file_name):
    full_data = []
    write_data(driver, full_data)
    final_write_data(full_data, file_name)


def write_data(driver, full_data):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    href_of_post = []
    date_of_post = []
    category_of_post = []
    title_of_post = []
    # WARNING: there is some missing data when fetching. I assume that html is too long...
    get_title_data(soup, '.dtf-item > a', 'href', href_of_post)
    get_title_data(soup, '.dft-thread-date > span', 'title', date_of_post)
    get_text_data(soup, '.dft-thread-category', category_of_post)
    get_text_data(soup, '.dft-thread-title', title_of_post)

    for i in range(len(href_of_post) - 1):
        partial_data = href_of_post[i] + date_of_post[i] + category_of_post[i] + title_of_post[i]
        print(partial_data)
        full_data.append(partial_data)


def final_write_data(full_data, file_name):
    import csv
    with open(file_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(full_data)  # make sure when you coding that you don't overwrite them


def convert_to_excel(file_name):
    xl_path_name = str(file_name).replace(".csv", ".xlsx")
    read_file = pd.read_csv(file_name, sep=',')
    read_file.to_excel(xl_path_name, index=False)

    pass


# This provided line is required at the end of a Python file
# to call the main() function.
if __name__ == '__main__':
    main()
