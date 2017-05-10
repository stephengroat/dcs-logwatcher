[![Build Status](https://travis-ci.org/stephengroat/dcs-logwatcher.svg?branch=master)](https://travis-ci.org/stephengroat/dcs-logwatcher)

### Requirements
1. Linux: `≥ 2.6.13`
2. Python version: `≥ 2.7`
3. Packages: `pyitnoify`

### Installation
```
pip install -r requirements.txt
pip install .
```

### Usage
```
$ dcs-logwatcher --help
usage: dcs-logwatcher [-h] [--output OUTPUT] [--status_url STATUS_URL]
                      [--mon_file MON_FILE]

Process nginx logs to create statd summary every 5 seconds.

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       path to output file to create or append to (default:
                        stdout)
  --status_url STATUS_URL
                        first digit of status code to display url detail
                        (default: 5)
  --mon_file MON_FILE   file to monitor (default: /var/log/ngninx/access.log)
```

### Docker command for testing
```
docker build -t dcs-logwatcher ./
docker run -v /var/log/nginx:/var/log/nginx dcs-logwatcher
docker run -v [path-on-local-machine]:/var/log/nginx -p [local-port]:80 nginx
```

### TODO
 - [ ] check impact of monitoring inode of entire folder (maybe focus on single file for performance)
 - [ ] auto PEP8
 - [ ] auto code coverage reports
 - [ ] Unit testing
