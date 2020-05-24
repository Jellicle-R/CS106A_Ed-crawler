# CS106A_Ed-crawler
Fetch post data and write them as xlsx format

Install

Download chromedriver (https://sites.google.com/a/chromium.org/chromedriver/)
You will need to specify the path in the code.

pip install selenium
pip install beautifulsoup4
pip install pandas

>> Please make sure to put your (1)id/pw on ed (2) chromedriver path into the code in following part

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
