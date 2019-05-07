*** Settings ***

Documentation  Keywords Resources
Library			../Libraries/OperatingSystemUtil.py
Library		   String
Resource	   ../Variables/Variables.txt

*** Keywords ***


###########  GENERAL TEST-CASE KEYWORDS  ###########

Login with new user  [Arguments]  ${Username}  ${Password}
	[Timeout]  2 minutes
	Set Tags	Critical Test
	Set Test Message	Login with Username:${Username} 	append=yes
	Sleep  5
	