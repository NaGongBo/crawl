from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import re
import requests
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from datetime import date
from selenium.common.exceptions import NoSuchElementException
browser=webdriver.Chrome('/home/boogahead/.local/bin/chromedriver')
browser.implicitly_wait(10)

#url='https://mobileticket.interpark.com/goods/22000970'
url='https://www.kopis.or.kr/por/db/pblprfr/pblprfr.do?menuId=MNU_00020&searchWord=&searchType=total#1#01##aaab#0#1#PF190785#FC001666######^02##########'
#url='https://www.kopis.or.kr/por/db/pblprfr/pblprfr.do?menuId=MNU_00020&searchType=total&searchWord=#2#01##aaab#0#1########^02##########'
#url='https://www.kopis.or.kr/por/db/pblprfr/pblprfr.do?menuId=MNU_00020&searchType=total&searchWord=#4#01##aaab#0#1########^02##########'

###mongodb info###
from pymongo import MongoClient
client = MongoClient(host='mongodb://dongi_admin:djWjekehdrl_capstone1@3.34.137.43',port=27017)
db = client['labeling_pool']
collection = db['test_collection']
#################

browser.get(url)
time.sleep(2)
totcnt=int(browser.find_element_by_xpath('//*[@id="su_con"]/div[3]/p/span').text)
browser.implicitly_wait(100000)
#while(1):
#    time.sleep(1)
print(int(totcnt))
totpage=int(totcnt/30)
if(totpage*30<totcnt):
    totpage+=1
print('total number of pages = ',totpage)#finding total number of pages to go through
####################################################################
"""
인터파크 감상평이 없는곳도 있다 거기도 예외처리
그리고 더보기스크롤 제대로 안되는거 같음 고쳐야함
해결완료

total number of plays 가 totcnt랑 맞으면 싹다 break 하고 끝내도록 하기
"""
######################################################################
#################testing function
testing=1#change to 0 if not testing
for j in range(totpage):
    cnt=0
    number_of_plays_on_this_page=0
    play_list=browser.find_elements_by_class_name('tag_a')
    for i in play_list:
        if number_of_plays_on_this_page>=30:
            break # we're done with going through tis page-> go to next page
        browser.refresh()
        entire_list=browser.find_element_by_xpath('//*[@id="search_listType01"]/ul')
        play_list=entire_list.find_elements_by_class_name('tag_a')
        if(play_list[cnt].text!=""):
            number_of_plays_on_this_page+=1
            enter_play_detail="https://www.kopis.or.kr/por/db/pblprfr/pblprfrView.do?menuId=MNU_00020&mt20Id="
            print(play_list[cnt].text)
            print(play_list[cnt].get_attribute("href"))
            playnumber=play_list[cnt].get_attribute("href")
            playnumber=playnumber[26:34]
            print(playnumber)
            enter_play_detail+=playnumber
            browser.get(enter_play_detail)
            print('entered play detail page')
            #browser.implicitly_wait(10)
            go_to_seller=browser.find_element_by_xpath('//*[@id="su_con"]/div[1]/div[3]/a')
            go_to_seller.click()
            do_you_have_interpark=0 #flag to see if interpark link exists
            poster_link=browser.find_element_by_xpath('//*[@id="su_con"]/div[2]/div[1]/p/img').get_attribute('src')
            browser.implicitly_wait(3)
            try:#checks whether theres an interpark link
                interpark_finder=browser.find_element_by_partial_link_text('인터파크')
                interpark_finder.click()#interpark exists
                print('found interpark!')
                do_you_have_interpark=1
            except:
                print('interpark does not exist!')
                close_seller_link_button=browser.find_element_by_xpath('//*[@id="lpop04"]/div[1]/button')
                close_seller_link_button.click()
                browser.back() # go back to original link
            if(do_you_have_interpark):#crawl interpark review comments
                #print('FUFUSDFUAUDSFUASD')
                original_link=browser.window_handles[0]
                added_link=browser.window_handles[1]
                browser.switch_to.window(added_link)
                change_to_mobile=browser.current_url
                print('포스터 링크:',poster_link)
                print('PC 예매 링크:',change_to_mobile)
                mobile_base='https://mobileticket.interpark.com/goods/'
                #changed=re.sub('[^0-9]', '', change_to_mobile)
                changed=change_to_mobile[36:]
                mobile_base+=changed
                #while(1):
                #    time.sleep(100)
                #browser.get(mobile_base)
                #browser.switch_to.window(added_link)
                browser.close()
                browser.switch_to.window(original_link)
                #browser.implicitly_wait(1000)
                print('모바일 예매 링크:',mobile_base)
                browser.get(mobile_base)
                print("looking for warning signs")

                #browser.implicitly_wait(500)
                #browser.implicitly_wait(30)
                print("YESYESYSEYSEYSYe")
                if(browser.find_element_by_xpath('//*[@id="root"]/div[6]/div/div[3]/button[1]') is None==True):
                    fuckwarning=browser.find_element_by_xpath('//*[@id="root"]/div[6]/div/div[3]/button[1]')
                    fuckwarning.send_keys(' ') #야로나 워닝 날려버리는거 --> 옛날꺼에는 워닝 안떠서 연도 보고 파악해야할듯
                #else:# ####################20220514 여기 문제있는것 같다
                    #browser.implicitly_wait(500)
                #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                if(browser.find_elements_by_xpath('//*[@id="productsTab"]/ul/li[3]/a')):#checks if review tab exist
                    print('review box exists. attempting to read reviews')
                    reviewbox=browser.find_element_by_xpath('//*[@id="productsTab"]/ul/li[3]/a')
                    browser.execute_script("arguments[0].click();",reviewbox) #관람후기 클릭
                    #print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
                    SCROLL_PAUSE_TIME = 0.5
                    # Get scroll height
                    last_height = browser.execute_script("return document.body.scrollHeight")
                    #print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
                    #while True:
                    click_more=True
                    #while browser.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[5]/div[2]/div[2]/button'):
                    #print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
                    while click_more:
                        # while loop checks whether "더보기" button still exists
                        # Scroll down to bottom
                        try:
                            time.sleep(1)
                            element=browser.find_element_by_css_selector('#epilogueTabContent > button')
                            browser.execute_script("arguments[0].click();",element)
                        except:
                            print("I AM OUT")
                            break
                    print('review scrolled down to the end')
                    browser.implicitly_wait(10)
                    receiver=browser.page_source
                    #print('asdlkjf;askdjf;lsakdj;fa')
                    soup=BeautifulSoup(receiver,'lxml')
                    review_title=soup.find_all("div",class_="userBoardTitle")
                    review=soup.find_all("div",{"class":"boardContentTxt"})
                            #review=
                    total=len(review_title)
                        #save all review titles and reviews
                    print(total)
                        #now call pandas to let it out
                    titles=[]
                    reviews=[]
                    csv_name=''
                    results=[]
                    label=0
                    print('saving reviews to csv file')
                    for i in range(len(review_title)):
                        results.append(review_title[i].text+' '+review[i].text)
                        #titles.append(review_title[i].get_text())
                        #reviews.append((review[i].get_text()))
                        #df=pd.DataFrame({'Title': titles,'Text':reviews})
                        df=pd.DataFrame({'review':results,'labeled':label})
                        df=df.replace('\n',' ',regex=True)
                        csv_name=changed+'.csv'
                        df.to_csv(csv_name,index=False,encoding="utf-8-sig")
                    print("Done crawling this play!")
                    if(total>0):
                        print('there is something to put into db!')
                        data = pd.read_csv(csv_name,lineterminator='\n')
                        #data.reset_index(inplace=True)
                        data_dict = data.to_dict("records")
                        collection.insert_many(data_dict)
                        print("finished exporting to mongodb!")
                browser.back()
                time.sleep(5)
                browser.back()
        else:
            print('not the case')
        cnt+=1
        print('CNT=',cnt)
    next_page_button=browser.find_element_by_css_selector('#su_con > div.pageing.prfList > div > a.icv.pbml')
    #next_page_button.click()
    browser.execute_script('arguments[0].click();',next_page_button)
