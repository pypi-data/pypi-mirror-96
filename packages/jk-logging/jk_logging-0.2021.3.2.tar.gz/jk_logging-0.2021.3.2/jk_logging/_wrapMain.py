


import re
import sys

from .ExceptionInChildContextException import ExceptionInChildContextException
from .AbstractLogger import AbstractLogger
from .ConsoleLogger import ConsoleLogger
from .ColoredLogMessageFormatter import ColoredLogMessageFormatter, COLOR_LOG_MESSAGE_FORMATTER







def wrapMain(log:AbstractLogger = None):

	class _LogCtx(object):

		def __init__(self, log):
			self.log = log
		#

		def __enter__(self):
			return self.log
		#

		def __exit__(self, ex_type, ex_value, ex_traceback):
			if ex_type != None:
				if ex_type == SystemExit:
					return False
				if not isinstance(ex_value, ExceptionInChildContextException):
					self.log.error(ex_value)
				sys.exit(1)
	
			return True
		#

	#

	if log is None:
		log = ConsoleLogger.create(logMsgFormatter=COLOR_LOG_MESSAGE_FORMATTER)
	else:
		assert isinstance(log, AbstractLogger)

	return _LogCtx(log)

#











