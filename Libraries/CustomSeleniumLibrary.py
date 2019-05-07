#!/usr/bin/env python

"""CustomSeleniumLibrary.py: Customized Selenium2Library for Robot Framework, to be used with DynamicTestSuite.py"""

__author__ = "Noam Manos"
__copyright__ = "Copyright 2014, Galil-Software"
__version__ = "1.0.1"
__maintainer__ = "Noam Manos"
__email__ = "manosnoam@gmail.com"
__status__ = "Production"

import time
from Selenium2Library import Selenium2Library
from selenium import webdriver
#from robot.api import logger
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#import re
#from robot import utils
#from selenium.webdriver.common.keys import Keys

class CustomSeleniumLibrary(Selenium2Library):
    """ class that inherits from Selenium2Library """
    
    def __init__(self):
        super(CustomSeleniumLibrary, self).__init__(run_on_failure='Nothing')
        #self.register_keyword_to_run_on_failure("Nothing")
        
        
    def getDriver(self):
        driver = self._current_browser()
        return driver
    
    def getDriverCapabilities(self, keyName=None):
        driver = self._current_browser()
        #logger.info("\nWebDriver Capabilities:\n %s" % driver.capabilities, html=False, also_console=True)
        if keyName:
            return driver.capabilities[keyName]
        else:
            return driver.capabilities
    
    def element_double_click (self , webElement_Tag):
        driver = self.getDriver()
        action = webdriver.ActionChains(driver)
        action.double_click(webElement_Tag).perform()
        #time.sleep(0.5)
    
   
    def wait_until_element_contain_text(self, div_Id,Timeout):
        driver=self.getDriver()
        imptyString=''
        num = 0
        while True :
            elem = driver.find_element_by_id(div_Id)
            elemText=str(elem.text).strip()
            if elemText == imptyString :
            #if elemText is None :
                time.sleep(1)
                num = num+1
                if num==Timeout :
                    return 'False'
            else:
                return 'True'

    
    def click_tag_text_in_div_id(self, text, div_id=None, tagType='a', doubleClick=None ):
        driver=self.getDriver()
        linkdiv = driver.find_element_by_id(div_id) if div_id else driver
        elements = linkdiv.find_elements_by_tag_name(tagType) 
        for tag in elements:
            elemText=tag.text
            if text in elemText:
                if doubleClick:
                    self.element_double_click(tag)
                else:
                    tag.click()
                    #tag.send_keys("\n") 
                return tag.get_attribute("class")
                break
        result= 'False'
        return  result
   

   

    def click_tag_text_in_div_class(self, textName, div_class=None, tagType='a', ClickOn= 0 ):
        driver = self.getDriver()
        folderName= str(textName.split('//',1)[0])
        
        if len(folderName) == len(str(textName)) :
            subFolderName = ""
        else :
            subFolderName= str(textName.split('//',1)[1])
            
        linkdiv = driver.find_element_by_class_name(div_class) if div_class else driver
        elements = linkdiv.find_elements_by_tag_name(tagType) 
        for tag in elements:
            if folderName in tag.text:
                if ClickOn==2:
                    self.element_double_click(tag)
                elif ClickOn==1:
                    tag.click()
                    #tag.send_keys("\n"
                break  # stop iterating over the partially matched elements.
        if subFolderName != "" :
            strtxt=str(tag.text.split('(',1)[1])
            reportsNum= int(strtxt.split(')',1)[0])
            
            for i in range(1,reportsNum+1):
                element_path = ("..//following-sibling::div//div[%s]//span[2]" % (i)) 
                documentElement = tag.find_element_by_xpath(element_path)
                if subFolderName in documentElement.text:  
                   
                    if ClickOn==2:
                        self.element_double_click(documentElement)
                    elif ClickOn==1:
                        tag.click()
                    tag = documentElement
                    break  # stop iterating over the p             
        return tag
             
             
        
    def click_folder_text_in_div_id(self, textName, div_Id=None, tagType='a', ClickOn= 0 ):
        driver = self.getDriver()
        folderName= str(textName.split('//',1)[0])
        tag=None
        if len(folderName) == len(str(textName)) :
            subFolderName = ""
        else :
            subFolderName= str(textName.split('//',1)[1])
        time.sleep(1)    
        linkdiv = driver.find_element_by_id(div_Id) if div_Id else driver
        time.sleep(1)
        elements = linkdiv.find_elements_by_tag_name(tagType) 
        for tag in elements:
            if folderName in tag.text:
                if ClickOn==2:
                    self.element_double_click(tag)
                elif ClickOn==1:
                    tag.click()
                    #tag.send_keys("\n"
                break  # stop iterating over the partially matched elements.
            else :
                tag=None
        
        if subFolderName != "" :
            strtxt=str(tag.text.split('(',1)[1])
            reportsNum= int(strtxt.split(')',1)[0])
            
            for i in range(1,reportsNum+1):
                time.sleep(1)
                element_path = ("..//following-sibling::div//div[%s]//span[2]" % (i)) 
                documentElement = tag.find_element_by_xpath(element_path)
                if subFolderName in documentElement.text:  
                   
                    if ClickOn==2:
                        self.element_double_click(documentElement)
                    elif ClickOn==1:
                        tag.click()
                    tag = documentElement
                    return tag  # stop iterating over the p  
            tag=None  
                         
        return tag
        
        
    def click_document_index_in_folder(self, folderName, div_class, documentIndex=1):
        folderElement = self.click_tag_text_in_div_class(folderName, div_class , tagType='span', ClickOn=2)
        element_path = ("..//following-sibling::div//div[%s]//span[2]" % (documentIndex))   
        documentElement = folderElement.find_element_by_xpath(element_path)
        #self.element_double_click(documentElement)
        documentElement.click() 
      
 
    def click_document_in_folder(self, folderName, div_Id, documentName):
        try:
            folderElement = self.click_folder_text_in_div_id(folderName, div_Id , tagType='span', ClickOn=2)
            #reportsNum = int(re.sub(ur'\D', '', folderElement.text))
            if folderElement is None :
                return 'FolderFalse'
            else :
                result= 'False'
                strtxt=str(folderElement.text.split('(',1)[1])
                reportsNum= int(strtxt.split(')',1)[0])
                for i in range(1,reportsNum+1):
                    element_path = ("..//following-sibling::div//div[%s]//span[2]" % (i)) 
                    documentElement = folderElement.find_element_by_xpath(element_path)
                    if documentName in str(documentElement.text):
                        time.sleep(1)
                        documentElement.click()
                        return documentElement.get_attribute("class")
                        result= 'True'
                return result
        except:
            return 'False'
        
     
     
    def Wait_For_Popup_Window(self,Timeout):
        driver=self.getDriver()
        time.sleep(1)
        for second  in range(1,Timeout+1):
            windows=driver.window_handles
            num_of_windows=len(windows)
            if num_of_windows >1 :
                result= 'True'
                return result
            time.sleep(1)
        return 'False'
                    
    def Handle_Popup_Window(self):
        driver=self.getDriver()
        time.sleep(1)
        try:
            driver.window_handles
            driver.switch_to_window(driver.window_handles[1])
            result= 'True'
            return result
        except:
            return 'False'
        
        
    def Close_From_Popup_Window(self):
        driver=self.getDriver()
        time.sleep(1)
        try:
            driver.window_handles
            #num_of_windows=len(windows)
            driver.switch_to_window(driver.window_handles[1])
            time.sleep(1)
            driver.close()
            time.sleep(1)
            driver.switch_to_window(driver.window_handles[0])
            result= 'True'
            return result
        except:
            #driver.switch_to_window(driver.window_handles[0])
            return 'False'
        
            
    def kill(self):
        """Kill the browser.

        This is useful when the browser is stuck.
        """
        try:
            if self.process:
                self.process.kill()
                self.process.wait()
        except WindowsError:
            # kill may not be available under windows environment
            pass
      
      
     
    def varify_count_documents_in_folder(self, folderName, div_Id, documentsNum):
        folderElement = self.click_folder_text_in_div_id(folderName, div_Id , tagType='span', ClickOn=0)
        strtxt=str(folderElement.text.split('(',1)[1])
        reportsNum= int(strtxt.split(')',1)[0])
        if reportsNum != int(documentsNum):
            result= 'False'
            return  result
            
        else:
            for i in range(1,reportsNum+1):
                element_path = ("..//following-sibling::div//div[%s]//span[2]" % (i))  
                try :
                    folderElement.find_element_by_xpath(element_path)
                except :
                    result= 'False'
                    return  result                   
                
            result= 'True'
            return  result


    def searching_data_in_report(self, id_txt,data_search):
        driver = self.getDriver()
        elem = driver.find_element_by_id(id_txt)
        txt_report=str(elem.text)
        
        if data_search in txt_report:
            #print ("'%s' is found" % (data_search))
            result= 'True'
        else:
            #print ("'%s' not found" % (data_search))
            result= 'False'
            
        return result
 
 
    def click_element_in_common_id (self, elementId,index):
        driver = self.getDriver()
        elements = driver.find_elements_by_id(elementId)
        num=1
        for elem in elements:
            if  num == int(index):
                elem.click()
                #elem.set_active(True)
                break  # stop iterating o
            num=num+1
                

    def click_button_in_popup_common_class_name (self, elementClass,buttonPath):
        driver = self.getDriver()
        elements = driver.find_elements_by_class_name(elementClass)
        displayName = 'block'
        for elem in elements:
            if   displayName in str(elem.get_attribute('display')):
                button=elem.find_element_by_xpath(buttonPath)
                button.click()   
                break
        

    def click_element_with_common_class_and_index (self, elementClass,index,elementPath):
        driver = self.getDriver()
        elements = driver.find_elements_by_class_name(elementClass)
        
        if index > int(len(elements)) :
            return 'False'
        
        else :
            try:
                elem=elements[index-1].find_element_by_xpath(elementPath)
                elem.click()  
                return 'True' 
            except : 
                return 'False'  
        





    def handle_alert(self): 
        driver = self.getDriver() 
        try:
            driver.switch_to_alert()
            #alert.accept()
            return 'True'

        except:
            return 'False'                  



        
    def click_Ok_in_alert(self): 
        driver = self.getDriver() 
        try:
            alert = driver.switch_to_alert()
            alert.accept()
            return "alert accepted"

        except:
            return "no alert"        
  
    def is_element_present_by_xpath(self,path):
        driver = self.getDriver() 
        try:
            driver.find_element_by_xpath(path)
            return 'True'
        except: 
            return 'False'     
             
    def is_element_present(self, how, what):
        driver = self.getDriver() 
        try:
            driver.find_element(by=how, value=what) # to find page elements
        except NoSuchElementException, e: print e
        return True             
    
    def is_text_present(self, text):
        driver = self.getDriver() 
        try:
            body = driver.find_element_by_tag_name("body") # find body tag element
        except NoSuchElementException, e: print e
        return text in body.text # check if the text is in body's text

    def close_alert_and_get_its_text(self):
        driver = self.getDriver() 
        try:
            alert = driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True        
        return True

    def minus(self,first,second):
        return first-second
    def decrement(self,num):
        return num-1

    def click_element_with_script(self,Path): 
        driver = self.getDriver() 
        try:
            mnEle=driver.find_element_by_xpath(Path)
            driver.execute_script("arguments[0].click();" , mnEle)
            #action = webdriver.ActionChains(driver)
            #action.move_to_element(mnEle).perform()
            #time.sleep(5)
            #driver.find_element_by_xpath(Path).click()    
            #action.move_by_offset(xoffset, yoffset)
            #action.double_click(webelement).perform()         
            return 'True'
        except:
            return 'False'    
              
    def Double_Click_On_element_and_loacate_By(self, how, what):
        driver = self.getDriver() 
        try:
            element=driver.find_element(by=how, value=what) # to find page elements
            self.element_double_click(element)
        except NoSuchElementException, e: print e
        return True     
#    def wait_for_Data_Processing (self, elementId):
#            driver = self.getDriver()
#            elem = driver.find_element_by_id(elementId)
#            while True:  
#                if elem.get_attribute("display").contains("none"):
#                    break
#                time.sleep(1)
#            return    