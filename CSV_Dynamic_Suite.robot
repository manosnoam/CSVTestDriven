*** Comments ***

Make sure to define ${RobotRunner} as main module to run, for example, define this alias:
/usr/local/lib/python3.6/site-packages/robot/run.py

Here's an example how to run/debug CSVRobotDriven with Pydev:
Call ${RobotRunner} with the following parameters: 
--output NONE --log NONE --report NONE --nostatusrc --loglevel TRACE --variable Variables_File:Variables/test_props_example.py --variable CSV_Tests_Path:"Tests/Skynet_TC_1.csv" CSV_Dynamic_Suite.robot

In eclipse, in order to use ${string_prompt}, put in the debug configuration (under program arguments):
--output NONE --log NONE --report NONE --loglevel TRACE --variable Variables_File:Variables/test_props_example.py --variable CSV_Tests_Path:${string_prompt:CSV Path:"Tests/Skynet_TC_1.csv"} CSV_Dynamic_Suite.robot


-------------------------------------------------------------

Jenkins Command example, using parameters:

PROJECT_DIR = C:/Builds/manual/dbm_Testing/OnDemand/CvTest
TEST_SOFTWARE_FOLDER = \\jenbld1\builds\eagle-ci\dbm_Testing\OnDemand\CvTest
DOC_PATH = C:/builds/workspace/CV_Robot_Test
Variables_Locators = Variables/Locators_Eagle.py
APP_SERVER = DBM8-APP191
CD_TEST_CASES = Clinical_Document_Tests/Basic_Test_Data.csv
VITAL_TEST_CASES = Vital_Tests/Vitals_Test_Data.csv
CSV_TESTS_DIR=Basic_Tests

@echo ***** Creating params.txt *****

echo --variable DOC_PATH:%DOC_PATH% >> params.txt
echo --variable Variables_File:%PROJECT_DIR%/%Variables_Locators% >> params.txt
echo --variable APP_SERVER:%APP_SERVER% >> params.txt

@echo ***** Getting latest revision from GIT *****

if exist "%PROJECT_DIR%" (rd "%PROJECT_DIR%" /s /q)
xcopy "%TEST_SOFTWARE_FOLDER%\*.*" "%PROJECT_DIR%" /s /e /i /z /y /f /r

@echo ***** Running Pybot Command and then Rebot (to merge into single report) *****

pybot --output NONE --report NONE --log NONE --critical "Critical Test" --nostatusrc -A params.txt --loglevel TRACE --variable CSV_Tests_Path:%CSV_TESTS_DIR%  %PROJECT_DIR%/CV_Dynamic_Suite.txt
rebot --critical "Critical Test" --nostatusrc --output output.xml *_output.xml

*** Settings ***
Documentation		Data Driven Tests, dynamicly created using Keywords as Test Cases - Based on CSV Test Data file 

Library				Libraries/DynamicTestSuite.py
Library				OperatingSystem
Library				Screenshot  
Library				String
#Library			AppiumLibrary

#Resource			Keywords/Keywords.txt
#Resource			Variables/Variables.txt

#Suite Teardown		Default Suite Teardown

*** Test Cases ***

  
Dynamic TestCases Creation from CSV Files
	#[Timeout]  30 minutes
	[Tags]    critical
	
	${CSV_Tests_Path} =  Get Variable Value   ${CSV_Tests_Path}   None
    Pass Execution If 	'${CSV_Tests_Path}' == 'None' 	Starting CSV Tests
    
    DynamicTestSuite.create_test_suite_from_csv  csvFilePath=${CURDIR}/${CSV_Tests_Path}   suiteResource=${SUITE SOURCE}   suiteTagName=CSV Robot Driven   
	Set Global Variable 	${SUITE NAME} 	${CSV_Tests_Path}
	Append To Environment Variable    Path    ${CURDIR}
	
	${Variables_File} =  Get Variable Value   ${Variables_File}   None
    Run Keyword If  '${Variables_File}' != 'None'  Import Variables File   ${CURDIR}/${Variables_File}
    
    #${APP_SERVER} =  Get Variable Value   ${APP_SERVER}   None
    #Run Keyword If  '${APP_SERVER}' != 'None'  DynamicTestSuite.add_global_variable   APP_SERVER  ${APP_SERVER}
    
    #${DOC_PATH} =  Get Variable Value   ${DOC_PATH}   None
    #Run Keyword If  '${DOC_PATH}' != 'None'  DynamicTestSuite.add_global_variable   DOC_PATH  ${DOC_PATH}
    #${RC} =    DynamicTestSuite.run_tests
    ${tests_status} =  DynamicTestSuite.run_tests
	
	#${BROWSER_NAME} =  Get Variable Value   ${BROWSER_NAME}   None
	#${Browser_short_name} =  OperatingSystemUtil.words_to_acronyms   ${BROWSER_NAME}
	#DynamicTestSuite.create_reports 	${Browser_short_name}
	#Libraries.DynamicTestSuite.Create Reports 	${device_name}
	#Close Application
	
	# Pass Execution 	End of Dynamic Test Suite
	Should Be True      ${tests_status} == ${TRUE}     End of Dynamic Test Suite


*** Keywords ***

	
Default Suite Teardown
	# Mandatory Keyword to End whole Suite - Do Not Remove
	${globalVar} =  Get Variable Value   ${CSV_Tests_Path}   None
    Pass Execution If 	'${globalVar}' != 'None' 	Closing All Open Browsers
    #Append To File  	CV_Env_Vars.properties 	 BROWSER_NAME=${BROWSER_NAME}\n
	#Run Keyword And Continue On Failure   Close All Browsers
	#Close Application
	Pass Execution  Finished CSV Tests Execution
	
Default Tests Teardown
    # Mandatory Keyword to End each Test - Do Not Remove
	Sleep  0.1		
	#log to console  \nCapture Page Screenshot if Test Failed
	${screenshotName} = 	Replace String Using Regexp 	${SUITE NAME}-${TEST NAME} 	(\\s|:) 	_
	#Run Keyword If Test Failed   CustomAppiumLibrary.Capture Page Screenshot  ${screenshotName}_device.png
	#Run Keyword If Test Failed   Take Screenshot  name=${screenshotName}_desktop.jpg		width=300px

  
  