from email.message import EmailMessage
from email.utils import localtime
import logging
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler
import os
import smtplib
import socket
import sys
from threading import Timer
from time import time
import traceback

logging_setup = None


def setup_logging(app_name=None):
    global logging_setup
    logging_setup = LoggingSetup(app_name)
    logging_setup.setup()


class LoggingSetup:
    def __init__(self, app_name=None):
        self.app_name = app_name

        self.debug = False
        self.systemd_log = False

        self.file_log = None
        self.file_log_count = 14
        self.file_log_when_rotate = "w0"

        self.syslog = False
        self.syslog_tag = None
        self.syslog_address = "/dev/log"

        self.smtp_log = False
        self.smtp_log_address = ("localhost", 25)
        self.smtp_log_sender = None
        self.smtp_log_recipient = "root"

        self.default_level = logging.INFO
        self.default_stderr_level = logging.WARNING
        self.default_file_level = self.default_level
        self.default_syslog_level = self.default_level
        self.default_smtp_level = logging.WARNING

        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.formatter_without_timestamp = logging.Formatter("%(levelname)s - %(message)s")
        self.formatter_tagged_format = ": %(levelname)s - %(message)s"

    def setup(self):
        if self.app_name is None:
            try:
                # use project root directory name as app_name
                main_file = sys.modules["__main__"].__file__
                self.app_name = str(os.path.realpath(os.path.dirname(main_file)).split(os.sep)[-1])
            except AttributeError:
                self.app_name = os.path.basename(os.getcwd())

        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)

        stream_formatter = self.formatter
        if self.systemd_log or "SYSTEMD_LOG" in os.environ:
            stream_formatter = self.formatter_without_timestamp

        handler = StreamHandler(sys.stderr)
        handler.setLevel(self.default_stderr_level)
        handler.setFormatter(stream_formatter)
        logger.addHandler(handler)

        handler = StreamHandler(sys.stdout)
        handler.setLevel(self.default_level)
        if self.debug or "DEBUG_LOG" in os.environ:
            handler.setLevel(logging.DEBUG)
        handler.addFilter(LessThanFilter(self.default_stderr_level))
        handler.setFormatter(stream_formatter)
        logger.addHandler(handler)

        if self.file_log or "FILE_LOG" in os.environ:
            file = os.environ["FILE_LOG"] if "FILE_LOG" in os.environ else self.file_log
            directory = os.path.dirname(file)
            if not os.path.exists(directory):
                os.makedirs(directory)
            count = int(os.environ["FILE_LOG_COUNT"]) if "FILE_LOG_COUNT" in os.environ else self.file_log_count
            handler = TimedRotatingFileHandler(file, when=self.file_log_when_rotate, backupCount=count)
            handler.setFormatter(self.formatter)
            handler.setLevel(self.default_file_level)
            logger.addHandler(handler)

        if self.syslog or "SYSLOG" in os.environ:
            tag = os.environ["SYSLOG_TAG"] if "SYSLOG_TAG" in os.environ else self.syslog_tag
            if not tag:
                tag = self.app_name
            address = self.syslog_address
            if "SYSLOG_ADDRESS" in os.environ:
                address = os.environ["SYSLOG_ADDRESS"]
                if ":" in address:
                    parts = address.split(":")
                    address = (parts[0], parts[1])
            handler = logging.handlers.SysLogHandler(address)
            handler.setFormatter(logging.Formatter(tag + self.formatter_tagged_format))
            handler.setLevel(self.default_syslog_level)
            logger.addHandler(handler)

        if self.smtp_log or "SMTP_LOG" in os.environ:
            if "SMTP_LOG_ADDRESS" in os.environ:
                parts = os.environ["SMTP_LOG_ADDRESS"].split(":")
                address = (parts[0], parts[1] if len(parts) > 1 else 25)
            else:
                address = self.smtp_log_address

            sender = os.environ["SMTP_LOG_SENDER"] if "SMTP_LOG_SENDER" in os.environ else self.smtp_log_sender
            if not sender:
                sender = self.app_name + "@"
                if os.name == "nt":
                    sender += socket.gethostname()
                else:
                    sender += socket.getfqdn()

            recipient = os.environ["SMTP_LOG_RECIPIENT"] if "SMTP_LOG_RECIPIENT" in os.environ else None
            if not recipient:
                recipient = self.smtp_log_recipient

            handler = BufferingSMTPHandler(address, sender, recipient, self.app_name)
            handler.setFormatter(self.formatter)
            handler.setLevel(self.default_smtp_level)
            logger.addHandler(handler)


class LessThanFilter(logging.Filter):
    def __init__(self, exclusive_maximum, name="lessThanFilter"):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        return 1 if record.levelno < self.max_level else 0


class BufferingSMTPHandler(logging.Handler):
    credentials = None
    secure = False
    timeout = 5.0

    timer = None
    buffer = None
    last_flush = 0
    flush_timeouts = None
    flush_timeout_current = 0
    postpone_flush = False

    def __init__(self, host, sender, recipients, subject_prefix=None):
        logging.Handler.__init__(self)
        self.buffer = []
        self.host = host
        self.sender = sender
        self.recipients = recipients
        self.subject_prefix = subject_prefix
        self.flush_timeouts = [5, 300, 1800, 3600]

        self.flush_on_timeout()

    def should_flush(self):
        if self.postpone_flush:
            return False

        timeout = self.flush_timeouts[self.flush_timeout_current]
        if self.last_flush < time() - timeout:
            if self.last_flush < time() - timeout * 1.1:
                self.flush_timeout_current = 0
            else:
                if self.flush_timeout_current < len(self.flush_timeouts) - 1:
                    self.flush_timeout_current += 1
            return True

        return False

    def flush_on_timeout(self):
        self.timer = Timer(min(self.flush_timeouts), self.flush_on_timeout)
        self.timer.daemon = True
        self.timer.start()

        self.flush_maybe()

    def emit(self, record):
        self.buffer.append(record)

        self.flush_maybe()

    def flush_maybe(self):
        self.acquire()
        try:
            if self.should_flush():
                self.flush()
        except Exception as e:
            print("BufferingSMTPHandler failed: " + str(e), file=sys.stderr)
            traceback.print_exc()
        finally:
            self.release()

    def flush(self):
        if len(self.buffer) > 0:
            self.send_email()
            self.buffer = []
            self.last_flush = time()

    def close(self):
        try:
            self.acquire()
            self.flush()
        finally:
            self.timer.cancel()
            try:
                logging.Handler.close(self)
            finally:
                self.release()

    def send_email(self):
        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = ",".join(self.get_recipients())
        message["Subject"] = self.construct_subject()
        message["Date"] = localtime()

        content = []
        for record in self.buffer:
            content.append(self.format(record))
        message.set_content("\n".join(content))

        host, port = self.get_host_port()
        smtp = smtplib.SMTP(host, port, timeout=self.timeout)

        if self.secure:
            smtp.starttls()
            smtp.ehlo()

        username, password = self.get_credentials()
        if username is not None:
            smtp.login(username, password)

        smtp.send_message(message)
        smtp.quit()

    def get_recipients(self):
        recipients = self.recipients
        if isinstance(recipients, str):
            recipients = [recipients]
        return recipients

    def get_host_port(self):
        if isinstance(self.host, (list, tuple)):
            return self.host
        return self.host, smtplib.SMTP_PORT

    def get_credentials(self):
        if isinstance(self.credentials, (list, tuple)):
            return self.credentials
        elif self.credentials is not None:
            raise Exception("unsupported credentials format: " + str(type(self.credentials)))
        return None, None

    def construct_subject(self):
        level = 0
        level_name = None
        override_level = 0
        override_value = None

        for record in self.buffer:
            if level < record.levelno:
                level = record.levelno
                level_name = record.levelname.lower()

            if hasattr(record, "subject"):
                if override_level < record.levelno:
                    override_level = record.levelno
                    override_value = record.subject

        subject = None
        if override_value:
            subject = override_value
        elif level_name:
            subject = level_name

        if self.subject_prefix and subject:
            subject = self.subject_prefix + ": " + subject

        return subject
