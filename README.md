# Python script that checks the availability of sites and pages

The script checks the health of sites on the http status, and specific pages checking for the presence of certain content. Can send notification of problems to the specified E-mails. Works asynchronously and can process a large number of sites in parallel. 

## Installation

```
# 1. install all necessary modules:
pip3 install -r requirements.txt

# 2. copy the configuration file:
cp config.yaml.dist config.yaml
```

## Configuration
Configuration example

```
# maximum number of concurrent checks
max_parallel_checks: 3

# list of sites/pages to check
sites:
- domain: "www.google.com"
  # by default, the script connects to the sites by https, but for a specific domain, you can choose to connect to http
  http: true
  # you can add multiple pages at once
  urls:
    - uri: "/"
      check_text: "Google"
    - uri: "/analytics/"
      check_text: "Google Analytics"

# - domain: "branchup.pro"
#   urls:
#     - uri: "/"
#       check_text: "some text of front page..."
# ...

# logger settings
logger:
  # log level: DEBUG / INFO / ERROR
  level: 'INFO'
  log_to_screen: true
  log_to_file: false
  log_file_path: 'log.txt'

# email list for notifications
administration:
  - email: "some-admin-email@gmail.com"
  - email: "some-admin2-email@gmail.com"

# configuring smtp through which the script will send mail
smtp_notifi:
  enabled: false
  host: "smtp.gmail.com"
  # port: 587
  username: "someuser@gmail.com"
  password: "some-password-here"
```

## Using

```
./site_checker.py
```

## System requirements
* python 3 >= 3.5.3
* aiohttp >= 2.3.6
* aiosmtplib >= 1.0.2
* PyYAML >= 3.12