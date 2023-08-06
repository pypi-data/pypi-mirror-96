﻿



import os
import time
import traceback
import sys
import abc
import datetime
import re

import jk_exceptionhelper

from .ExceptionInChildContextException import ExceptionInChildContextException
from .EnumLogLevel import *
from .IDCounter import IDCounter





def _getLogLevelStrMap(bPrefixWithSpacesToSameLength = False):
	maxLogLevelLength = len("STACKTRACE")
	for logLevel in EnumLogLevel:
		s = _getLogLevelStr(logLevel)
		if len(s) > maxLogLevelLength:
			maxLogLevelLength = len(s)
	logLevelToStrDict = {}
	for logLevel in EnumLogLevel:
		s = _getLogLevelStr(logLevel)
		if bPrefixWithSpacesToSameLength:
			while len(s) < maxLogLevelLength:
				s = " " + s
		logLevelToStrDict[logLevel] = s
	return logLevelToStrDict
#





def _getLogLevelStr(logLevel):
	s = str(logLevel)
	pos = s.rfind(".")
	if pos >= 0:
		s = s[pos+1:]
	return s
#













class AbstractLogger(object):
	__metaclass__ = abc.ABCMeta

	_logLevelToStrDict = _getLogLevelStrMap(True)

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, idCounter):
		if idCounter is None:
			idCounter = IDCounter()
		else:
			assert isinstance(idCounter, IDCounter)
		self._idCounter = idCounter
		self._indentationLevel = 0
		self._parentLogEntryID = None
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Protected Methods
	################################################################################################################################

	#
	# Create a log entry data record.
	#
	# @param		int logEntryID			The ID of this log entry or <c>None</c> if not applicable.
	# @param		int indentation			The current indentation level. Top level entries will have a value of zero here.
	#										This value is always zero if the feature is not supported.
	# @param		int parentLogEntryID	A log entry ID of the parent of this log entry or <c>None</c> if not applicable (or not supported).
	# @param		EnumLogLevel logLevel	A singleton that represents the log level.
	# @param		str text				A text to associate with this log entry.
	# @param		list newList			Typically specify an empty list here that will hold child log entries in the future.
	#
	def _createDescendLogEntryStruct(self, logEntryID, indentation, parentLogEntryID, logLevel, text, newList):
		timeStamp = time.time()

		return ("desc", logEntryID, indentation, parentLogEntryID, timeStamp, logLevel, text, newList)
	#

	#
	# Creates a log entry data record.
	#
	# @param		int logEntryID			The ID of this log entry or <c>None</c> if not applicable.
	# @param		int indentation			The current indentation level. Top level entries will have a value of zero here.
	#										This value is always zero if the feature is not supported.
	# @param		int parentLogEntryID	A log entry ID of the parent of this log entry or <c>None</c> if not applicable (or not supported).
	# @param		EnumLogLevel logLevel	A singleton that represents the log level.
	# @param		obj textOrException		Either an exception object or a text
	#
	def _createNormalLogEntryStruct(self, logEntryID, indentation, parentLogEntryID, logLevel, textOrException):
		timeStamp = time.time()

		if isinstance(textOrException, BaseException):
			exceptionObject = jk_exceptionhelper.analyseException(textOrException, ignoreJKTypingCheckFunctionSignatureFrames=True, ignoreJKTestingAssertFrames=True)
			return (
				"ex",
				logEntryID,
				indentation,
				parentLogEntryID,
				timeStamp,
				logLevel,
				exceptionObject.exceptionClassName,
				exceptionObject.exceptionTextHR,
				[ (x.filePath, x.lineNo, x.callingScope, x.sourceCodeLine) for x in exceptionObject.stackTrace ]
			)

		return (
			"txt",
			logEntryID,
			indentation,
			parentLogEntryID,
			timeStamp,
			logLevel,
			textOrException.rstrip('\n')
		)
	#

	#
	# Perform a descending operation. Overwrite this method in subclasses.
	#
	# @param		list logEntryStruct			A log entry structure. See <c>_logi()</c> for a detailed description.
	# @return		AbstractLogger				Return a logger instance representing the logger for a descended level.
	#
	@abc.abstractmethod
	def _descend(self, logEntryStruct):
		raise NotImplementedError('subclasses must override _descend()!')
	#

	#
	# Perform the log operation. This is the heart of each logger. Overwrite this method in subclasses.
	#
	# @param		list logEntryStruct						A log entry structure. Each entry consists of the following elements:
	#														0) <c>str</c> ---- The type of the log entry: "txt", "ex", "desc"
	#														1) <c>str</c> ---- The ID of the log entry or <c>None</c> if unused
	#														2) <c>int</c> ---- The indentation level
	#														3) <c>str</c> ---- The ID of the parent log entry or <c>None</c> if unused
	#														4) <c>float</c> ---- The time stamp in seconds since epoch
	#														5) <c>EnumLogLevel</c> ---- The type of the log entry
	#														If the log entry is a text entry:
	#														6) <c>str</c> ---- The text of the log message
	#														If the log entry is a descending entry:
	#														6) <c>str</c> ---- The text of the log message
	#														7) <c>list</c> ---- A list containing nested log items
	#														If the log entry is an exception:
	#														6) <c>str</c> ---- The exception class name
	#														7) <c>str</c> ---- The exception text
	#														8) <c>list</c> ---- A list of stack trace elements or <c>None</c>
	#														Each stack trace element has the following structure:
	#														0) <c>str</c> ---- The source code file path
	#														1) <c>int</c> ---- The source code line number
	#														2) <c>str</c> ---- The source code module name
	#														3) <c>str</c> ---- The source code line in plain text where the error occurred
	# @param		bool bNeedsIndentationLevelAdaption		If <c>True</c> is specified the log entry record still needs adaption at the
	#														indentation level field. This is because it was generated somewhere else and
	#														therefor has been provided by a different logger in a maybe different indentation
	#														context.
	#
	@abc.abstractmethod
	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption):
		raise NotImplementedError('subclasses must override _logi()!')
	#

	#
	# This method is invoked in order to log a list of log entries. After adapting the indentation level to the indentation level
	# currently used by this logger either <c>_logi()</c> is called or <c>_descend()</c> in order to perform the logging.
	#
	# The default implementation provided here will perform indentation level adaption as needed. In order to do so a copy of the
	# raw log entry is created.
	#
	# @param		list logEntryStruct						A log entry structure. See <c>_logi()</c> for a detailed description.
	# @param		bool bNeedsIndentationLevelAdaption		If <c>True</c> is specified the log entry records still needs adaption at the
	#														indentation level field. This is because it was generated somewhere else and
	#														therefor has been provided by a different logger in a maybe different indentation
	#														context.
	#
	def _logiAll(self, logEntryStructList, bNeedsIndentationLevelAdaption):
		for logEntryStruct in logEntryStructList:
			#logEntryStruct = list(logEntryStruct)
			#logEntryStruct[2] = self._indentationLevel
			self._logi(logEntryStruct, bNeedsIndentationLevelAdaption)
			if logEntryStruct[0] == "desc":
				logEntryStructClone = (
					logEntryStruct[0],
					logEntryStruct[1],
					logEntryStruct[2],
					logEntryStruct[3],
					logEntryStruct[4],
					logEntryStruct[5],
					logEntryStruct[6],
					[]
				)
				self._descend(logEntryStructClone)._logiAll(logEntryStruct[7], bNeedsIndentationLevelAdaption)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def log(self, logLevel:EnumLogLevel, logData):
		if logLevel == EnumLogLevel.TRACE:
			self.trace(logData)
		elif logLevel == EnumLogLevel.DEBUG:
			self.debug(logData)
		elif logLevel == EnumLogLevel.NOTICE:
			self.notice(logData)
		elif logLevel == EnumLogLevel.INFO:
			self.info(logData)
		elif logLevel == EnumLogLevel.STDOUT:
			self.stdout(logData)
		elif logLevel == EnumLogLevel.SUCCESS:
			self.success(logData)
		elif logLevel == EnumLogLevel.WARNING:
			self.warn(logData)
		elif logLevel == EnumLogLevel.ERROR:
			self.error(logData)
		elif logLevel == EnumLogLevel.STDERR:
			self.stderr(logData)
		elif logLevel == EnumLogLevel.EXCEPTION:
			self.exception(logData)
		else:
			raise Exception("This log level is not supported: {}".format(logLevel))
	#

	#
	# Perform logging with log level ERROR.
	#
	# @param	string text		The text to write to this logger.
	#
	def error(self, text):
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.ERROR, text), False)
	#

	#
	# Perform logging with log level EXCEPTION.
	#
	# @param	Exception exception		The exception to write to this logger.
	#
	def exception(self, exception):
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.EXCEPTION, exception), False)
	#

	#
	# Perform logging with log level ERROR.
	# This method is intended to be used in conjunction with STDERR handlers.
	#
	# @param	string text		The text to write to this logger.
	#
	def stderr(self, text):
		text = text.rstrip('\n')
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.STDERR, text), False)
	#

	#
	# Perform logging with log level STDOUT.
	# This method is intended to be used in conjunction with STDOUT handlers.
	#
	# @param	string text		The text to write to this logger.
	#
	def stdout(self, text):
		text = text.rstrip('\n')
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.STDOUT, text), False)
	#

	#
	# Perform logging with log level SUCCESS.
	#
	# @param	string text		The text to write to this logger.
	#
	def success(self, text):
		text = text.rstrip('\n')
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.SUCCESS, text), False)
	#

	#
	# Perform logging with log level WARNING. This method is provided for convenience and is identical with <c>warn()</c>.
	#
	# @param	string text		The text to write to this logger.
	#
	def warning(self, text):
		text = text.rstrip('\n')
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.WARNING, text), False)
	#

	#
	# Perform logging with log level WARNING. This method is provided for convenience and is identical with <c>warning()</c>.
	#
	# @param	string text		The text to write to this logger.
	#
	def warn(self, text):
		text = text.rstrip('\n')
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.WARNING, text), False)
	#

	#
	# Perform logging with log level INFO.
	#
	# @param	string text		The text to write to this logger.
	#
	def info(self, text):
		text = text.rstrip('\n')
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.INFO, text), False)
	#

	#
	# Perform logging with log level NOTICE.
	#
	# @param	string text		The text to write to this logger.
	#
	def notice(self, text):
		text = text.rstrip('\n')
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.NOTICE, text), False)
	#

	#
	# Perform logging with log level DEBUG.
	#
	# @param	string text		The text to write to this logger.
	#
	def debug(self, text):
		text = text.rstrip('\n')
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.DEBUG, text), False)
	#

	#
	# Perform logging with log level TRACE.
	#
	# @param	string text		The text to write to this logger.
	#
	def trace(self, text):
		text = text.rstrip('\n')
		self._logi(self._createNormalLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.TRACE, text), False)
	#

	#
	# Create a nested logger. This new logger can than be used like the current logger, but all log messages will be delivered
	# to an subordinate log structure (if supported by this logger).
	#
	def descend(self, text):
		logEntryStruct = self._createDescendLogEntryStruct(self._idCounter.next(), self._indentationLevel, self._parentLogEntryID, EnumLogLevel.INFO, text, [])
		self._logi(logEntryStruct, False)
		return self._descend(logEntryStruct)
	#

	#
	# If this logger is buffering log messages, clear all log messages from this buffer.
	# If this logger has references to other loggers, such as a <c>FilterLogger</c>
	# or a <c>MulticastLogger</c>
	#
	def clear(self):
		pass
	#

	#
	# Close this logger. Some logger make use of additional resources (such as files) which will be (permanently) closed by invoking this method.
	# By default this method does nothing. Some loggers may overwrite this method in order to make use of that functionality. After closing
	# a logger you should not invoke any more logging methods of that logger. Loggers that make use of <c>close()</c> should reject any logging
	# request after a <c>close()</c> has been invoked. <c>close()</c> must always be implemented as an indempotent operation: Redundant calls to <c>close()</c>
	# should cause no problems.
	#
	def close(self):
		pass
	#

	def __enter__(self):
		return self
	#

	def __exit__(self, ex_type, ex_value, ex_traceback):
		if ex_type != None:
			if isinstance(ex_value, ExceptionInChildContextException):
				return False
			#e = ex_type(value)
			#self.exception(e)
			self.exception(ex_value)
			raise ExceptionInChildContextException(ex_value)
		return False
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	@staticmethod
	def exceptionToJSON(ex):
		exceptionObject = jk_exceptionhelper.analyseException(ex, ignoreJKTypingCheckFunctionSignatureFrames=True, ignoreJKTestingAssertFrames=True)

		return {
			"exClass": exceptionObject.exceptionClassName,
			"exText": exceptionObject.exceptionTextHR,
			"exStack": [ [x.filePath, x.lineNo, x.callingScope, x.sourceCodeLine] for x in exceptionObject.stackTrace ],
		}
	#

#

