import logging
import os
from datetime import datetime


class DailyLogHandler(logging.FileHandler):
 

    def __init__(self, log_file_path, log_file, mode='a', encoding=None):
        """
        Initialize the handler with the directory path and base log filename.

        Args:
            log_file_path (str): Directory where log files will be saved.
            log_file (str): Base name of the log file (prefix before date).
            mode (str): File mode, default is 'append'.
            encoding (str): Encoding for the log file.
        """
        self.log_file_path = log_file_path
        self.log_file = log_file
        # Initialize parent FileHandler with the full filename for today
        super().__init__(self.get_filename(), mode, encoding)

    def get_filename(self):
        """
        Generate the full filename for the current date's log file.

        Returns:
            str: Full path to the log file with the current date appended.
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        filename = os.path.join(self.log_file_path, f"{self.log_file}{current_date}.log")
        return filename

    def should_change_file_to(self, new_file):
        """
        Check if the log handler should switch to a new file.

        Args:
            new_file (str): New target filename.

        Returns:
            bool: True if new_file is different from current file.
        """
        return new_file != self.baseFilename

    def emit(self, record):
        """
        Emit a log record.

        Overrides the emit method to:
        - Ensure the log directory exists.
        - Switch log files if the date has changed.
        """
        self.acquire()  # Lock for thread safety
        try:
            # Create log directory if it doesn't exist
            if not os.path.exists(self.log_file_path):
                os.makedirs(self.log_file_path)

            # If the date changed, update the log file stream
            if self.should_change_file_to(self.get_filename()):
                self.stream.close()  # Close the old stream
                self.baseFilename = self.get_filename()
                self.stream = self._open()  # Open new file stream

            super().emit(record)  # Write the log record to file
        finally:
            self.release()  # Release lock


def setup_logging(log_file_path, log_file):
    """
    Configure the root logger with the DailyLogHandler.

    Args:
        log_file_path (str): Directory path for log files.
        log_file (str): Base name prefix for log files.
    """
    # Define the log message format and timestamp format
    log_format = '%(asctime)s - %(levelname)s - %(message)s - Line %(lineno)d'
    log_date_format = '%Y-%m-%d %H:%M:%S'

    # Get the root logger
    logger = logging.getLogger('')

    ## TEST
    ####logger.setLevel(logging.DEBUG)  # Capture all logs at DEBUG level and above
    

    # Avoid adding multiple handlers if this function is called repeatedly
    for handler in logger.handlers:
        if isinstance(handler, DailyLogHandler):
            return  # Handler already added, skip

    # Create and configure the daily rotating file handler
    log_handler = DailyLogHandler(log_file_path, log_file, encoding="utf-8")
    log_handler.setLevel(logging.DEBUG)  # File handler captures DEBUG and above
    log_handler.setFormatter(logging.Formatter(log_format, log_date_format))

    # Add the handler to the root logger
    logger.addHandler(log_handler)
