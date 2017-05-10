import pyinotify
from operator import itemgetter
import re
import os
import sys
import difflib
from collections import defaultdict
import QLock


class LogDirectory(pyinotify.ProcessEvent):
    def __init__(self, log, file_object, status_url, mon_file):
        self._lock = QLock.QLock()
        if file_object == sys.stdout:
            self._file_object = file_object
        else:
            self._file_object = open(file_object, 'w+')
        self._log = log
        self._status_url = status_url
        self._mon_file = mon_file

    def process_IN_MODIFY(self, event):
        if event.name == os.path.basename(self._mon_file):
            # TODO sgroat be more aggressive about unlock, may disorder output
            self._lock.acquire()
            self.process_access_log()
            self._lock.release()

    def process_IN_CREATE(self, event):
        # logrotate moves and creates a new file
        if event.name == os.path.basename(self._mon_file):
            self._lock.acquire()
            self._log = ""
            self._lock.release()

    def process_default(self, event):
        pass

    def process_access_log(self):
        diff = self.diff_logs()
        if diff:
            status_codes = {'5': {'count': 0},
                            '4': {'count': 0},
                            '3': {'count': 0},
                            '2': {'count': 0}}
            status_codes[self._status_url]['urls'] = defaultdict(int)
            self.process_log(diff=diff, status_codes=status_codes)
            self.print_logs(status_codes=status_codes)

    # diff previous log with new log and find added lines
    def diff_logs(self):
        new_log = open(self._mon_file, 'r').readlines()
        diff = []
        for line in difflib.ndiff(self._log, new_log):
            # '+ ' is the notation for line added at start of each line
            if line[:2] == '+ ':
                # skip character added by diff
                diff.append(line[2:])
        # update log for comparison
        self._log = new_log
        return diff

    # process logs using regex to split each line
    @staticmethod
    def process_log(diff, status_codes):
        # TODO sgroat watch out for ipv6?
        regex = r'(?P<remote_addr>.*?)\ \-(\ (?P<http_x_forwarded_for>.*?)\ \-\ (?P<http_x_realip>.*?))?\ \-\ \[(?P<time_local>.*?)\](\ (?P<scheme>.*?)\ (?P<http_x_forwarded_proto>.*?)\ (?P<x_forwarded_proto_or_scheme>.*?))?\ \"(?P<request_type>.*?)\ (?P<url>.*?)\ (?P<request_num>.*?)\"\ (?P<status>.*?)\ (?P<body_bytes_sent>.*?)\ \"(?P<http_referer>.*?)\"\ \"(?P<http_user_agent>.*?)\"'
        for line in diff:
            output = re.match(regex, line)
            if output is not None:
                # increment status code count
                status_code = output.groupdict()['status'][0]
                if status_code in status_codes:
                    status_codes[status_code]['count'] += 1
                    if 'urls' in status_codes[status_code]:
                        # record url for targeted status codes
                        url = output.groupdict()['url']
                        status_codes[status_code]['urls'][url] += 1
            # TODO sgroat should an error be raised for regex fails?
            # else:
                # raise ValueError('regex match fail on log file line')

    # print out values
    def print_logs(self, status_codes):
        for status_code, val in sorted(status_codes.items(), key=itemgetter(0)):
            self._file_object.write(status_code + '0x:' + str(status_codes[status_code]['count']) + "|s\n")
            if 'urls' in status_codes[status_code]:
                for req, count in status_codes[status_code]['urls'].iteritems():
                    self._file_object.write(req + ':' + str(count) + "|s\n")
        self._file_object.flush()
