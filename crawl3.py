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
from selenium.webdriver.support.ui import WebDriverWait
import collections
from collections import Counter

from musical_for_beginners.model.mfb_classifier import MusicalForBeginners
from datetime import date
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

chrome_options=Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-proxy-server')
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument('--proxy-bypass-list=*')
chrome_options.add_argument('--disable-gpu')
browser=webdriver.Chrome('C:/Users/kihyu/AppData/Local/Programs/Python/chromedriver.exe', chrome_options=chrome_options)
browser.implicitly_wait(10)

file1=open('info.txt','r')
mongo_info=file1.readline().strip("\n")
url=file1.readline().strip("\n")
###mongodb info###
from pymongo import MongoClient
client = MongoClient(host=mongo_info,port=27017)
db = client['nlp_testing_site_local_pc']
collection = db['play']
actor_collection=db['performers']
theater_collection=db['theater']
review_collection=db['review']
#################

browser.get(url)
time.sleep(5)
totcnt_str=browser.find_element_by_xpath('//*[@id="su_con"]/div[3]/p/span').text
if("," in totcnt_str):
    totcnt_str=totcnt_str.replace(",","")
totcnt=int(totcnt_str)
browser.implicitly_wait(100000)
totpage=(int(totcnt/30))
if(totpage*30<totcnt):
    totpage+=1
####################################################################

classifier = MusicalForBeginners()


for j in range(totpage):
    cnt=0
    number_of_plays_on_this_page=0
    play_list=browser.find_elements_by_class_name('tag_a')
    for i in play_list:
        if number_of_plays_on_this_page>=30:
            break # we're done with going through tis page-> go to next page
        browser.refresh()
        time.sleep(3)
        entire_list=browser.find_element_by_xpath('//*[@id="search_listType01"]/ul')
        play_list=entire_list.find_elements_by_class_name('tag_a')
        if(play_list[cnt].text!=""):
            number_of_plays_on_this_page+=1
            enter_play_detail="https://www.kopis.or.kr/por/db/pblprfr/pblprfrView.do?menuId=MNU_00020&mt20Id="
            play_title=play_list[cnt].text
            playnumber=play_list[cnt].get_attribute("href")
            playnumber=playnumber[26:34]
            enter_play_detail+=playnumber
            browser.get(enter_play_detail)
            go_to_seller=browser.find_element_by_xpath('//*[@id="su_con"]/div[1]/div[3]/a')
            go_to_seller.click()
            do_you_have_interpark=0 #flag to see if interpark link exists
            poster_link=browser.find_element_by_xpath('//*[@id="su_con"]/div[2]/div[1]/p/img').get_attribute('src')
            browser.implicitly_wait(3)
            try:
                yes24_link=browser.find_element_by_partial_link_text('예스24')
                yes24_link=yes24_link.get_attribute('href')
            except:
                yes24_link=None
            browser.implicitly_wait(3)
            try:#checks whether theres an interpark link
                interpark_finder=browser.find_element_by_partial_link_text('인터파크')
                interpark_finder.click()#interpark exists
                do_you_have_interpark=1
            except:
                close_seller_link_button=browser.find_element_by_xpath('//*[@id="lpop04"]/div[1]/button')
                close_seller_link_button.click()
                browser.back() # go back to original link
                time.sleep(3)
            if(do_you_have_interpark):#crawl interpark review comments
                original_link=browser.window_handles[0]
                added_link=browser.window_handles[1]
                browser.switch_to.window(added_link)
                change_to_mobile=browser.current_url
                mobile_base='https://mobileticket.interpark.com/goods/'
                changed=change_to_mobile[36:]#########################interpark_id
                mobile_base+=changed
                browser.close()
                browser.switch_to.window(original_link)
                browser.get(change_to_mobile)
                ########################################################
                ####PC interpark_id
                actor_id_list=[None]
                actor_role_list=[None]
                casting_list_checker=browser.find_elements_by_class_name("castingList")
                if(casting_list_checker):
                    expand_actor_list_checker=browser.find_elements_by_class_name("contentToggleBtn")
                    if(expand_actor_list_checker):
                        expand_actor_list=browser.find_element_by_class_name("contentToggleBtn")
                        browser.execute_script('arguments[0].click();',expand_actor_list)
                    actor_list=browser.find_elements_by_class_name('castingItem')
                    actor_cnt=0
                    for j in actor_list:
                        if(actor_cnt<10):
                            ###goes through actor list and put em into db
                            role=j.find_element_by_class_name('castingActor').text
                            name=j.find_element_by_class_name('castingName').text
                            actor_id=j.find_element_by_class_name('castingLink').get_attribute("href")
                            actor_id_cutter_loc=actor_id.find('=')+1
                            actor_id=actor_id[actor_id_cutter_loc:]
                            actor_existence_query={"actor_id":actor_id}
                            if actor_collection.count_documents(actor_existence_query)==0:
                                ###checks whether actor id exists in db and adds if needed
                                performer_insertion={"actor_id":actor_id,"actor_name":name}
                                y=actor_collection.insert_one(performer_insertion)
                                actor_id_list.append(actor_id)
                                actor_role_list.append(role)
                                actor_cnt+=1
                    del actor_id_list[0]
                    del actor_role_list[0]
                    time.sleep(1)
                    #####finished going through actor list if there is one
                playdb_checker=browser.find_elements_by_class_name('is-playdb')
                playdb_checker_flag=0 ####checks if theres a playdb link
                playdb_link=None
                if(playdb_checker):# if exists
                    playdb_link=browser.find_element_by_class_name('is-playdb').get_attribute("href")#look for playdb button
                    browser.get(playdb_link)
                    time.sleep(3)
                    genre=browser.find_element_by_xpath('//*[@id="wrap"]/div[3]/div[1]/div[2]/table/tbody/tr[1]/td[2]/a[2]').text
                    playtime=browser.find_element_by_xpath('//*[@id="wrap"]/div[3]/div[1]/div[2]/table/tbody/tr[2]/td[2]').text
                    playdb_checker_flag=1
                    browser.back()
                    time.sleep(3)
                #if playdb link does not exist, find what we can from kopis

                ##go back to interpark pc website after going through playdb
                #########################################################
                ##########################################################
                ####goes to mobile link from here
                browser.get(mobile_base)
                time.sleep(2)
                #############33
                result_counter=Counter()
                comment_existence=0
                ###############
                if(browser.find_elements_by_xpath('//*[@id="productsTab"]/ul/li[3]/a')):#checks if review tab exist
                    reviewbox=browser.find_element_by_xpath('//*[@id="productsTab"]/ul/li[3]/a')
                    browser.execute_script("arguments[0].click();",reviewbox) #관람후기 클릭
                    SCROLL_PAUSE_TIME = 0.5
                    # Get scroll height
                    last_height = browser.execute_script("return document.body.scrollHeight")
                    click_more=True
                    while click_more:
                        # while loop checks whether "더보기" button still exists
                        # Scroll down to bottom
                        try:
                            time.sleep(1)
                            element=browser.find_element_by_css_selector('#epilogueTabContent > button')
                            browser.execute_script("arguments[0].click();",element)
                        except:
                            break
                    browser.implicitly_wait(10)
                    receiver=browser.page_source
                    soup=BeautifulSoup(receiver,'lxml')
                    review_title=soup.find_all("div",class_="userBoardTitle")
                    review=soup.find_all("div",{"class":"boardContentTxt"})
                    total=len(review_title)
                        #save all review titles and reviews
                        #now call pandas to let it out
                    titles=[]
                    reviews=[]
                    csv_name=''
                    results=[]
                    for i in range(len(review_title)):
                        results.append(review_title[i].text+' '+review[i].text)
                        insert_review={"play_id":changed,"review":results}
                        df=pd.DataFrame({'play_id':changed,'review':results})
                        df=df.replace('\n',' ',regex=True)
                        csv_name=changed+'.csv'
                        save_loc='C:/Users/kihyu/Desktop/root/capstone1/archive/'
                        save_loc+=csv_name
                        df.to_csv(save_loc,index=False,encoding="utf-8-sig")
                    if(total>0):
                        comment_existence=1
                        data = pd.read_csv(save_loc,lineterminator='\n').rename(columns={'review\r':'review'})
                        data= classifier.make_prediction_to_unseen_df(data)
                        for i in data.label:
                            result_counter.update(i)

                        data_dict = data.to_dict("records")
                        review_collection.insert_many(data_dict)
                browser.back()
                ###back to interpark pc
                time.sleep(2)
                browser.back()
                ### back to kopis play detail page
                time.sleep(2)
                if(playdb_checker_flag==0):
                    genre=browser.find_element_by_xpath('//*[@id="su_con"]/div[1]/div[1]/span').text
                    playtime=browser.find_element_by_xpath('//*[@id="su_con"]/div[2]/div[2]/ul/li[1]/div/dl/dd').text
                location_link=browser.find_element_by_xpath('//*[@id="su_con"]/div[2]/div[2]/ul/li[2]/div/dl/dd/a').get_attribute('href')
                location_id=location_link[-8:]
                age_restriction=browser.find_element_by_xpath('//*[@id="su_con"]/div[2]/div[2]/ul/li[4]/div/dl/dd').text
                browser.get(location_link)
                location_address=browser.find_element_by_xpath('//*[@id="su_con"]/ul[1]/li[4]/div/dl/dd').text
                theater_name=browser.find_element_by_xpath('//*[@id="su_con"]/ul[1]/li[1]/div[1]/dl/dd').text
                theater_existence_query={"theater_id":location_id}
                if theater_collection.count_documents(theater_existence_query)==0:
                    theather_insertion={"theater_id":location_id,"theater_name":theater_name,"theater_address":location_address}
                    z=theater_collection.insert_one(theather_insertion)
                final_result_counter=result_counter.most_common(n=8)
                final_result_counter_insertion={}
                ####creates a dictionary for mongodb insertion
                if comment_existence==1:
                    for i in range(0,8):
                        final_result_counter_insertion[final_result_counter[i][0]]=int(final_result_counter[i][1])
                ###
                mydict={"title":play_title,"performance_info":changed,"interpark_link":change_to_mobile,"yes24_link":yes24_link,"poster":poster_link,"theater_id":location_id,"playtime":playtime,"age_restriction":age_restriction,"genre":genre,"synopsis":playdb_link,'actor_id_list':actor_id_list,'actor_role_lst':actor_role_list,'counter':final_result_counter_insertion}
                x=collection.insert_one(mydict) ###db overall insertion
                browser.back()
                time.sleep(2)
                browser.back()
                time.sleep(2)
                ##back to kopis list
        cnt+=1
    time.sleep(10)
    next_page_button=browser.find_element_by_css_selector('#su_con > div.pageing.prfList > div > a.icv.pbml')
    browser.execute_script('arguments[0].click();',next_page_button)
