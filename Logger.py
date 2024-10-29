import sys
import os
import logging
import json
from datetime import datetime

class Logger:
    def __init__(self, name='Logger', facility='GENERAL', level=logging.INFO, log_to_file=False, filename=None):

        """
        Initialize the Logger class with an optional facility field.
        
        :param name: Name of the logger.
        :param facility: Facility name for categorizing the log source (e.g., 'DATABASE', 'API', etc.).
        :param level: Logging level (e.g., logging.INFO, logging.DEBUG).
        :param log_to_file: Whether to log to a file (default is False, which logs to stdout).
        :param filename: Base filename for logging output if log_to_file is True (will append .log for regular logs).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.facility = facility
        self.level = level
        self.log_to_file = log_to_file

        # Ensure log filename ends with .log and define a separate filename for exceptions (.ex)
        if log_to_file and filename:
            self.log_filename = filename if filename.endswith('.log') else filename + '.log'
            self.exception_filename = os.path.splitext(self.log_filename)[0] + '.ex'
            
            # Create directories if they do not exist
            os.makedirs(os.path.dirname(self.log_filename), exist_ok=True)
            handler = logging.FileHandler(self.log_filename)
        else:
            handler = logging.StreamHandler(sys.stdout)

        # Define formatter with date, facility, level, and message, comma-delimited with no spaces
        formatter = logging.Formatter(f'%(asctime)s,{self.facility},%(levelname)s,%(message)s', 
                                      datefmt='%Y-%m-%d %H:%M:%S')

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def info(self, message):
        """Log an informational message."""
        self.logger.info(message)

    def debug(self, message):
        """Log a debug message only if the logging level is set to DEBUG."""
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(message)

    def error(self, message):
        """Log an error message."""
        self.logger.error(message)

    def exception(self, e, message):
        """
        Log an exception without traceback in stdout, 
        serialize the exception details to a separate .ex file if file logging is enabled.
        
        :param e: The exception instance.
        :param message: The custom message to log.
        """
        # Print user-friendly message to stdout
        self.logger.error(message)
        
        # Prepare the full error data for serialization
        error_details = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'facility': self.facility,
            'level': 'ERROR',
            'message': message,
            'exception_type': type(e).__name__,
            'exception_message': str(e),
        }
        
        # Write serialized error details to .ex file if file logging is enabled
        if self.log_to_file:
            with open(self.exception_filename, 'a') as f:
                f.write(json.dumps(error_details, indent=4) + '\n')
        else:
            print(json.dumps(error_details,indent=4))

'''
# Example usage
if __name__ == "__main__":
    # Logging with a log file and exception file
    logger = Logger(name='MyLogger', facility='API', level=logging.DEBUG, log_to_file=True, filename='logs/app')
    
    # Regular log messages
    logger.info("This is an info message.")
    logger.debug("This debug message will be shown because DEBUG level is set.")
    logger.error("This is an error message.")

    # Logging an exception to the .ex file
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.exception(e, "An error occurred: division by zero.")
'''