from selenium import webdriver
from time import sleep

class UNOGSBot():
    def __init__(self,headless=0):
        options=webdriver.ChromeOptions()
        if headless: 
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--headless')
            options.add_argument('start-maximized')
            options.add_argument('disable-infobars')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
        self.driver=webdriver.Chrome(options=options)
        self.driver.get('https://unogs.com')
        print('Webdriver initiated')
        sleep(1)
    def search(self, s):
        ##search movie and go
        #search_field = self.driver.find_element_by_xpath('//*[@id="navbar"]/form/div/input')
        #search_field.click()
        #search_field.clear()
        #search_field.send_keys(s)
        #go_btn= self.driver.find_element_by_xpath('//*[@id="navbar"]/form/div/span[2]/input')
        #go_btn.click()
        #sleep(1)
        
        print('Webdriver: %s' % s)
        self.driver.get('https://unogs.com/search/'+s)
        sleep(1)
        print('Webdriver: searching %s' % s)
        #find first result and click to expand
        first_result=self.driver.find_elements_by_xpath('/html/body/div[9]/div[1]/div[2]/div')
        if first_result:
            first_result[0].click()
            sleep(1)

            #find if germany is there
            de_card=self.driver.find_elements_by_xpath('//*[@id="titleDetails"]/div/div/div[3]/div[3]/div[5]/div[3]/*[@id="39"]')
            if de_card:
                print('Title is available in germany: %s' % s)
                #get url title for movie on netflix
                title=self.driver.find_element_by_xpath('//*[@id="titleDetails"]/div/div/div[1]/h4/a')
                sleep(1)
                text=title.text
                x=self.driver.find_element_by_xpath('//*[@id="titleDetails"]/div/div/div[1]/button')
                x.click()
                sleep(0.2)
                return text
            else:
                print('Title is not available in germany: %s' % s)
                x=self.driver.find_element_by_xpath('//*[@id="titleDetails"]/div/div/div[1]/button')
                x.click()
                sleep(0.2)
                return ''
        
        print('Title could not be found: %s' % s)
        return ''

bot=UNOGSBot(headless=1)