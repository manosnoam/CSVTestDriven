import os
import time
import glob
import subprocess
import random,string
import platform
import re
import sys
import json



USERNAME_ACCESS_KEY = re.compile('^(http|https):\/\/([^:]+):([^@]+)@')
CURRENT_PATH = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
CURL_PATH = CURRENT_PATH + '/curl.exe'

def getLatestFile(pathFile):      
    date_file_list = []
    for folder in glob.glob(pathFile):
        for fileIn in glob.glob(folder + '/*.pdf'):
            stats = os.stat(fileIn)
            lastmod_date = time.localtime(stats[8])
            date_file_tuple = lastmod_date, fileIn
            date_file_list.append(date_file_tuple)
                
    if len(date_file_list) > 0:
        date_file_list.sort()
        filePth=date_file_list[-1][1]
        filePath= str(filePth).replace("\\", "/")
        return filePath
    else:
        return None
    #date_file_list.reverse()  # newest mod date now first
    #for filen in date_file_list:
        #folder, file_name = os.path.split(filen[1])
        #file_date = time.strftime("%m/%d/%y %H:%M:%S", filen[0])
    
    


def get_current_path():    
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        # os.chdir(__location__)
        return location
 
def search_data_in_text(data,text):
        if str(data) in str(text):
            result= 'True'
        else:
            result= 'False'    
        return result
  
  
  



def getNumOfFilesInPath(pathFile,filesType):      
    date_file_list = []
    for folder in glob.glob(pathFile):
        # glob.glob(folder + '/*.pdf'):
        for fileIn in glob.glob(folder + '/*.' + filesType):
            stats = os.stat(fileIn)
            lastmod_date = time.localtime(stats[8])
            date_file_tuple = lastmod_date, fileIn
            date_file_list.append(date_file_tuple)
                
    return len(date_file_list)
       
   
      
def get_subText_from_Text(textName ):
    
    Root= str(textName.split('//')[0])
    if len(Root) == len(str(textName)) :
        Parent = 'None'
        Leaf = 'None' 
    else :
        Parent= str(textName.split('//')[1])
        length = len(Root)+len(Parent)+2
        if length == len(str(textName)) :
            Leaf=Parent
            Parent = 'None'
        else :   
            Leaf= str(textName.split('//')[2])  
              
    return  Root,Parent,Leaf
    

def wait_until_num_of_files_equal(first_variable,pathFile,filesType,Timeout):
    num = 0
    while True :
        second_variable=getNumOfFilesInPath(pathFile,filesType)
        if first_variable == second_variable :
            return 'True'
        else:
            time.sleep(1)
            num = num+1
            if num==Timeout :
                return 'False'


# def IsTextStartWith (self,fullString ,subString):
#     if fullString.startswith(subString):
#         return True
#     else:
#         return False
     
def set_os_env_var(varName, varValue):
    os.environ["varName"] = str(varValue)
    os.system("SETX {0} {1} /M".format(varName,varValue))          
    
def words_to_acronyms(words):
    words = words or ""
    return "".join(re.sub(r"([a-zA-Z])\w+",r"\1",words).split()).upper()



def runShellCommand(command, successPhrase=''):
#     if platform.system() == 'Windows' and isinstance(command, basestring):
#         command = '%s < NUL' % command

    #print '\nRunning Shell Command:\n%s\n' % command
    sys.stderr.write('\nRunning Shell Command:\n%s\n' % command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE) #, stderr=subprocess.STDOUT)
    output = '' #process.communicate()[0] #''
    if process.poll():
        output = process.communicate()[0]
        #print output
    else: 
        # Poll process for new output until finished
        for line in iter(process.stdout.readline, ""):
            #print line,
            #sys.stdout.flush(),
            sys.stderr.write(line)
            output += line
        process.wait()
    exitCode = process.returncode

    if successPhrase:
        print ('\nSearching Process Output for Phrase: %s' % successPhrase)
        #if output.find(successPhrase) != -1:
        if successPhrase.lower() in output.lower():
            print ('Process Output as Expected, includes: "%s"' % successPhrase)
            return output
        else:
            print ('Process Output does NOT include "%s"' % successPhrase)
            sys.stderr.write('\nProcess Output does NOT include "%s"' % successPhrase)
            return ""
    else:
        if exitCode == 0:# or exitCode == 1):
            print('\nProcess Exit Code: OK.')
            return output or True
        else:
            print('\nProcess Exit Code: %s\n' % exitCode)
            sys.stderr.write('\nProcess Exit Code: %s\n' % exitCode)
            return False
            #raise Exception(command)

#     def _uploadAppToSouceLabs(self, appFile, userName="manosnoam:aef10f9e-b27f-42c7-a2e2-827e8088a37e"):
#         req = RequestsLibrary()
#         url = "http://saucelabs.com/rest/v1/storage/%s/%s?overwrite=true" % (userName, appFile)
#         headers = {'content-type': 'application/octet-stream"'}
#         file = OperatingSystem().get_binary_file(appFile)
        #req.create_session(url=url, headers=headers, cookies, auth, timeout, proxies, verify)
#         Create Session httpbin http://httpbin.org
#         ${file_data}= Get Binary File ${CURDIR}${/}data.json
#         ${files}= Create Dictionary file ${file_data}
#         ${resp}= Post httpbin /post files=${files}
#         ${file}= To Json ${resp.json()['files']['file']}
#         Dictionary Should Contain Key ${file} one
#         Dictionary Should Contain Key ${file} two
 

def uploadAppToSouceLabs(appPath, remote_url, OverwriteFile):
    # Parse username and access_key from the remote_url
    assert USERNAME_ACCESS_KEY.match(remote_url), 'Incomplete remote_url: %s' % remote_url
    username, access_key = USERNAME_ACCESS_KEY.findall(remote_url)[0][1:]
    appFile = os.path.basename(appPath)
    
    output = "Failure in Uploading %s to %s !" % (appPath, remote_url)
    upload = True
    if OverwriteFile.strip().lower() in ("", "false", "no"):
        curlCommand = '{0} -u {1}:{2} https://saucelabs.com/rest/v1/storage/{1}'.format(CURL_PATH, username, access_key)
        output = runShellCommand(curlCommand, appFile)
        if output and appFile in output: 
            upload = False
    if upload:    
        curlCommand = '{0} -u {1}:{2} -X POST "http://saucelabs.com/rest/v1/storage/{1}/{3}?overwrite=true" ' \
                '-H "Content-Type: application/octet-stream" --data-binary "@{4}"'.format(CURL_PATH, username, access_key, appFile, appPath)
        output = runShellCommand(curlCommand, appFile)
    return output



def uploadAppToAppthwack(appPath, AuthKey, OverwriteFile="No"):
    # Parse username and access_key from the remote_url
    appFile = os.path.basename(appPath)
    
    output = "Failure in Uploading %s to Appthwack !" % (appPath)
    mapItem = {"file_id":-1}
    upload = True
    if OverwriteFile.strip().lower() in ("", "false", "no"):
        curlCommand = '{0} -X GET -u "{1}:" https://appthwack.com/api/file'.format(CURL_PATH, AuthKey)
        output = runShellCommand(curlCommand, "file_id")
        if output and appFile in output: 
            upload = False
            listOutput = json.loads(output)
            for mapItem in listOutput:
                appName = mapItem['name']
                if appName == appFile: break
    
    if upload:    
        curlCommand = '{0} -X POST -u "{1}:" https://appthwack.com/api/file ' \
                        '-F "name={2}" -F "save=true" -F "file=@{3}"'.format(CURL_PATH, AuthKey, appFile, appPath)
        output = runShellCommand(curlCommand, "file_id")
        mapItem = json.loads(output)

    if mapItem:
        print ("\nMap Item: \n", mapItem)
        output = mapItem['file_id']
    return str(output)

                        
if __name__ == "__main__":
    pass 
    
    