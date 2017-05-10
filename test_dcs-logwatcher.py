import unittest
import time
import sys
import os
import threading
import pyinotify
from collections import defaultdict
from logwatcher import LogDirectory

# Tests for regex
class LogDirectoryProcessLogTest(unittest.TestCase):
  def test_process_log_basic(self):
    diff = ['80.154.42.54 - - [23/Aug/2010:15:25:35 +0000] "GET /phpmy-admin/scripts/setup.php HTTP/1.1" 404 347 "-" "ZmEu"']
    status_codes = {'4': {'count': 0, 'urls': defaultdict(int)}}
    LogDirectory.LogDirectory.process_log(diff, status_codes)
    self.assertEqual(status_codes['4']['count'], 1)
    self.assertEqual(status_codes['4']['urls'].keys(), ['/phpmy-admin/scripts/setup.php'])
  def test_process_log_basic_other(self):
    diff = ['10.10.180.161 - 72.34.110.66, 192.33.28.238 - - - [03/Aug/2015:15:50:06 +0000]  https https https "GET / HTTP/1.1" 200 20027 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36"']
    status_codes = {'2': {'count': 0, 'urls': defaultdict(int)}}
    LogDirectory.LogDirectory.process_log(diff, status_codes)
    self.assertEqual(status_codes['2']['count'], 1)
    self.assertEqual(status_codes['2']['urls'].keys(), ['/'])
  def test_process_log_sample_log(self):
    diff = open('sample.log', 'r').readlines()
    status_codes = {'5': {'count': 0, 'urls': defaultdict(int)},
                    '4': {'count': 0, 'urls': defaultdict(int)},
                    '3': {'count': 0, 'urls': defaultdict(int)},
                    '2': {'count': 0, 'urls': defaultdict(int)}}
    LogDirectory.LogDirectory.process_log(diff, status_codes)
    print status_codes
    self.assertEqual(status_codes['2']['count'], 3551)
    self.assertEqual(status_codes['3']['count'], 40)
    self.assertEqual(status_codes['4']['count'], 155)
    self.assertEqual(status_codes['5']['count'], 0)

# TODO sgroat find way to test timing
class LogDirectoryTest(unittest.TestCase):
  def test_general_function(self):
    wm = pyinotify.WatchManager()
    # output to /tmp/output.log, monitor 500s on /tmp/access.log
    notifier = pyinotify.ThreadedNotifier(wm,
                                          LogDirectory.LogDirectory(log='',
                                                                    file_object='/tmp/output.log',
                                                                    status_url='5',
                                                                    mon_file=os.path.abspath('/tmp/access.log')))
    wm.add_watch(os.path.dirname(os.path.abspath('/tmp/access.log')), pyinotify.ALL_EVENTS)
    # fake inotify event, prevent need to use loop() function
    notifier.check_events()
    notifier.read_events()
    notifier.process_events()
    # simulate write to log
    log = open('/tmp/access.log', 'w+')
    sample_log = open('sample.log', 'r').readlines()
    for line in sample_log:
      print>>log, line
    log.flush()
    log.close()
    notifier.check_events()
    notifier.read_events()
    notifier.process_events()
    # read output log
    output = open('/tmp/output.log', 'r')
    output_lines = output.readlines()
    self.assertEqual(output_lines[0], '20x:3551|s\n')
    self.assertEqual(output_lines[1], '30x:40|s\n')
    self.assertEqual(output_lines[2], '40x:155|s\n')
    self.assertEqual(output_lines[3], '50x:0|s\n')
  # Test similar to test_general_function, but also includes a simulated logrotate
  def test_logrotate(self):
    wm = pyinotify.WatchManager()
    notifier = pyinotify.ThreadedNotifier(wm,
                                          LogDirectory.LogDirectory(log='',
                                                                    file_object='/tmp/output.log',
                                                                    status_url='5',
                                                                    mon_file=os.path.abspath('/tmp/access.log')))
    wm.add_watch(os.path.dirname(os.path.abspath('/tmp/access.log')), pyinotify.ALL_EVENTS)
    notifier.check_events()
    notifier.read_events()
    notifier.process_events()
    log = open('/tmp/access.log', 'w+')
    sample_log = open('sample.log', 'r').readlines()
    for line in sample_log:
      print>>log, line
    log.flush()
    log.close()
    # simlulate logrotate
    os.rename('/tmp/access.log','/tmp/access.log.1')
    log = open('/tmp/access.log', 'w+')
    for line in sample_log:
      print>>log, line
    log.flush()
    log.close()
    notifier.check_events()
    notifier.read_events()
    notifier.process_events()
    output = open('/tmp/output.log', 'r')
    output_lines = output.readlines()
    self.assertEqual(output_lines[0], '20x:3551|s\n')
    self.assertEqual(output_lines[1], '30x:40|s\n')
    self.assertEqual(output_lines[2], '40x:155|s\n')
    self.assertEqual(output_lines[3], '50x:0|s\n')
    self.assertEqual(output_lines[4], '20x:3551|s\n')
    self.assertEqual(output_lines[5], '30x:40|s\n')
    self.assertEqual(output_lines[6], '40x:155|s\n')
    self.assertEqual(output_lines[7], '50x:0|s\n')


