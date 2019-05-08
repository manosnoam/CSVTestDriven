#!/usr/bin/env python

'''
DynamicTestSuite.py: Dynamic Data-Driven Library for Robot Framework 3.1.1. 
It generates Test Suites from CSV files of tests parameters
'''
from logging import critical
from robot.model import criticality
from _socket import timeout

__author__ = 'Noam Manos'
__copyright__ = ''
__version__ = '1.0.1'
__maintainer__ = 'Noam Manos'
__email__ = 'manosnoam@gmail.com'
__status__ = 'Production'

import csv
import os
import re
import platform
from collections import OrderedDict
from collections import defaultdict
from robot.api import ResultWriter
from robot.api import TestSuiteBuilder
from robot.api import logger
# from robot.libraries.BuiltIn import BuiltIn
# from robot.running import timeouts
from robot.libraries.OperatingSystem import OperatingSystem
from robot.api import ExecutionResult, ResultVisitor

# CONSTANTS # TODO: move to external conf/suite file
XUNIT_FILE = 'output.xml'
REPORT_FILE = 'report.html'
LOG_FILE = 'log.html'
__cur_path__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
LIB_PATH = __cur_path__
TAG_SKIP = '#skip'
MSG_SKIP = 'Skipping a test marked with #'
MSG_CRITICAL = 'Skipping all tests after critical failure'

			
class ResultSkippedAfterCritical(ResultVisitor):
	
	def visit_suite(self, suite):
		suite.set_criticality(critical_tags='Critical')
		for test in suite.tests:
			# Remove preceding library name and # from test name
			test.name = re.sub(r'.*:', '', test.name).strip()
			if test.status == 'FAIL':
				if 'Critical failure occurred' in test.message:
					test.status = 'NOT_RUN'
					test.message = MSG_CRITICAL
				elif 'No keyword with name' in test.message:
					test.status = 'NOT_RUN'
			if test.status == 'PASS':
				if TAG_SKIP in test.tags:
					test.status = 'NOT_RUN'
					test.message = MSG_SKIP


class DynamicTestSuite():
	'''
	DynamicTestSuite.py: Dynamic Data-Driven Library for Robot Framework 3.1.1. 
	It generates Test Suites from CSV files of tests parameters
	'''
	
	ROBOT_LIBRARY_SCOPE = 'GLOBAL'
	# ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
	
	def __init__(self):
		self.suites = []
		self.suiteName = None
		self.globalVariables = []
		self.csvFileName = ''
		self.suiteTagName = ''
		self.currentTestLibrary = ''
	
	def create_test_suite_from_csv(self, csvFilePath, suiteResource, suiteTagName='Data-Driven Test', suiteNameSuffix=None):
		self.suiteTagName = suiteTagName
		csvFilePath = csvFilePath.replace('\\', '/')
		suiteNameSuffix = suiteNameSuffix or ''  # (%s)' % platform.node()
		
		if os.path.isdir(csvFilePath):
			csvFiles = OperatingSystem().list_files_in_directory(csvFilePath, pattern='*.csv', absolute=True)
		else: 
			csvFiles = [csvFilePath]
		
		for csvFileName in csvFiles:
			# self.csvFileName = csvFileName
			logger.info(F'\nGenerating Test Suite from: {csvFileName}', also_console=True)
			suite = TestSuiteBuilder().build(suiteResource.replace('\\', '/'))
			
			suite.name = F'{os.path.splitext(os.path.basename(csvFileName))[0]}{suiteNameSuffix}'
			# suite.name = os.path.basename(csvFileName)
			suite.doc = csvFileName
			suite.resource.imports.library('BuiltIn')
			
			testDictList = self.convert_csv_to_list_of_dictionaries(csvFileName)
			for testDict in testDictList:
				if len(testDict) > 0:
					self.add_test_case_to_suite(suite, testDict)
			self.suites.append(suite)
	
	def add_test_case_to_suite(self, suite, testDict):
		'''
		Collecting all test param inside testDict (a CSV row representing robot keyword with params)
		Each value is a list of strings, usually with 1 string item, 
		except for data key, which has multiple strings (test params)
		'''
		
		testCase = None
		actionName = ''
		actionKeyword = None
		suiteLibrary = None
		timeoutSeconds = ''
		tagList = []
		step = ''
		testData = OrderedDict()  # Dictionary of all test data input for the keyword.

		for key in testDict:
			value = testDict[key]
			if type(value) is not list:
				continue
			# testDataParams = False
			if key == 'step':
				step = value.pop()
				# if value.startswith('#') or value == '':
				if step == '':
					return  # TODO: change TestCase status to SKIPPED
				# step = value  # 'Step %02d' % int(value)
			elif key == 'action':
				actionKeyword = value.pop().strip()
				# if step.startswith('#'):
				# 	actionKeyword = F'#{actionKeyword}'
			elif key == 'library':
				suiteLibrary = value.pop().strip()
			elif key == 'timeout':
				timeoutSeconds = value.pop().strip()
			elif key == 'tags':
				tagList = value.pop().split()
			elif key == 'data':
				''' 
				Once got to 'data', all of the rest of params are considered test data inputs for the keyword
				testData is populated with $key=value, or with p{i}=value if no $key is defined 
				'''
				testDataParams = value
			# if testDataParams:
				for i, paramValue in enumerate(testDataParams):
					paramKey = F'p{i}'
					if paramValue.startswith('$'):
						paramKey, paramValue = paramValue.replace(' ', '').split('=', 1)
					testData[paramKey.lstrip('$')] = paramValue or None
		
		''' creating test from the testDict robot params and data '''
		if actionKeyword:
			actionName = F'{actionKeyword}'
			actionKeyword = re.sub(r'\s+', '_', actionKeyword).lower()
			if suiteLibrary:
				self.currentTestLibrary = suiteLibrary
				# suite.resource.imports.library(F'{suiteLibrary}')
				suite.resource.imports.library(os.path.join(LIB_PATH, F'{suiteLibrary}.py'))
				# suite.resource.imports.library(os.path.join(LIB_PATH, F'{suiteLibrary}.py'), args=[('ROBOT_LIBRARY_SCOPE=GLOBAL')])
				# suite.resource.imports[-1].__class__.ROBOT_LIBRARY_SCOPE = 'GLOBAL'
				# setattr(suite.resource.imports[-1].__class__, 'ROBOT_LIBRARY_SCOPE', 'GLOBAL')
				# suite.resource.imports.library.args = ('ROBOT_LIBRARY_SCOPE=GLOBAL')
			else:
				suiteLibrary = self.currentTestLibrary
			testCase = suite.tests.create(actionName, tags=tagList, timeout='0')  # , doc='%s'%testData.items() )
			testCase.name = F'Step {step} ({testCase.id}): {actionName}'
			testCase.doc = F'{suiteLibrary}.{actionKeyword}: \n' + ', '.join([F'{k}={v}' for k, v in testData.items()])
			if timeoutSeconds:
				# testCase.timeout = timeouts.TestTimeout(timeoutSeconds, tttt)
				testCase.timeout.value = timeoutSeconds
				testCase.timeout.message = F'Timeout of {timeoutSeconds} seconds has exceeded while executing: {suiteLibrary}:{actionKeyword}'
			if step.startswith('#'):
				testCase.keywords.create(F'Pass Execution', args=[MSG_SKIP, TAG_SKIP], type='kw')
			else:
				testCase.keywords.create(F'{suiteLibrary}.setup', args=[], type='setup')
				testCase.keywords.create(F'{suiteLibrary}.{actionKeyword}', args=[F'{k}={v}' for k, v in testData.items()], type='kw') 
				testCase.keywords.create('Default Tests Teardown', args=[], type='teardown')
				
	def run_tests(self, outputDir=None):
		''' Report and xUnit files can be generated based on the  result object. '''
		for suite in self.suites:
			outputDir = outputDir or suite.name.replace(' ', '_')
			
			logger.info(F'\n###############  Running Test Suite: {suite.name}  ###############', also_console=True)

			result = suite.run(variable=self.globalVariables, output=XUNIT_FILE, outputdir=outputDir, \
					 report=None, log=None, critical='Critical', exitonfailure=True, pythonpath=self.get_current_path())
			tests_status = (result.return_code == 0)
			logger.info(F'\nChecking skipped tests due to critical failures', also_console=True)
			revisitOutputFile = os.path.join(outputDir, XUNIT_FILE)
			result = ExecutionResult(revisitOutputFile) 
			result.visit(ResultSkippedAfterCritical())
			result.save(revisitOutputFile)
			
			logger.info(F'\n###############  Generating {REPORT_FILE} and {LOG_FILE} ###############', also_console=True)
			writer = ResultWriter(result)
			writer.write_results(outputdir=outputDir, report=REPORT_FILE, log=LOG_FILE, critical='Critical')  # xunit=XUNIT_FILE)
			# ResultWriter(os.path.join(outputDir, XUNIT_FILE)).write_results(\
			# critical='Critical Test', report=REPORT_FILE, output=XUNIT_FILE, outputdir=outputDir, consolecolors='on', log=LOG_FILE, name=suite.name)
		return tests_status

	def convert_csv_to_list_of_dictionaries(self, csvFileName, defaultField='_'):
		'''
		Parsing CSV file, and converting it to list of dictionaries (of type collections.defaultdict). 
		'''
		
		logger.info(F'\n###############  Parsing CSV file: {csvFileName} ###############', also_console=True)
		dictList = []
		
		def _getDefaultField(field):
			if field:
				self.defaultField = field.replace(' ', '').lower()
			return self.defaultField
					
		with open(csvFileName, 'rt') as csvfile:
			reader = csv.reader(csvfile)
			fieldnames = [_getDefaultField(field) for field in next(reader)]
			
			for row in reader:
				testParams = defaultdict(list)
				for key, value in zip(fieldnames, row):
					if key and value:
						testParams[key].append(value)
				if len(testParams) > 0:
					logger.info(dict(testParams), also_console=True)
					dictList.append(testParams)
		return dictList
# 			return [defaultdict(list)[key].append(value) for key, value in zip(fieldnames, next(reader)) if key and value]
	
	def _convert_csv_to_list_of_dictionaries(self, csvFileName):
		print ('Parsing CSV file: %s ' % (csvFileName))
		with open(csvFileName) as f:
			dictList = [{k.replace(' ', '').lower():v for k, v in row.items() if k is not None}
					for row in csv.DictReader(f, skipinitialspace=True)]
		return dictList
	
	@staticmethod 
	def get_current_path():
		# __cur_path__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		# os.chdir(__cur_path__)
		return __cur_path__

	def add_global_variable(self, varName, varValue):
		# setattr(self, varName, varValue) #equivalent to: self.varname= 'something'
		# globals()[varName] = varValue
		variable = '%s:%s' % (varName, varValue)
		self.globalVariables.append(variable)
		
	def import_variables_file(self, variableFilePath):
		for suite in self.suites:
			suite.resource.imports.variables(variableFilePath.replace('\\', '/'))

