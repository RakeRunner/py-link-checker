# Python скрипт который проверяет доступность сайтов и страниц

Скрипт проверяет работоспособность сайтов по http статусу, и конкретных страниц проверяя наличие определенного содержимого. Может отправлять уведомления о проблемах на указанные E-mail'ы. Работает асинхронно и может обрабатывать большое количество сайтов параллельно. 

## Установка

```
# 1. устанавливаем все необходимые пакеты:
pip3 install -r requirements.txt

# 2. копируем файл конфигурации:
cp config.yaml.dist config.yaml
```

## Конфигурация
пример конфигурации

```
# максимальное кол. одновременных проверок
max_parallel_checks: 3

# список сайтов / страниц для проверки
sites:
- domain: "www.google.com"
  # по умолчанию скрипт проверяет сайты по https, но таким образом можно заставить скрипт проверять этот домен по http
  http: true
  # можно добавить сразу несколько url для проверки
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

# настройки логера
logger:
  # log level: DEBUG / INFO / ERROR
  level: 'INFO'
  log_to_screen: true
  log_to_file: false
  log_file_path: 'log.txt'

# список E-mail для получения уведомлений об ошибках
administration:
  - email: "some-admin-email@gmail.com"
  - email: "some-admin2-email@gmail.com"

# настройки smtp через который будут отправляться уведомления
smtp_notifi:
  enabled: false
  host: "smtp.gmail.com"
  # port: 587
  username: "someuser@gmail.com"
  password: "some-password-here"
```

## Использование

```
./site_checker.py
```

## Системные требования
* python 3 >= 3.5.3
* aiohttp >= 2.3.6
* aiosmtplib >= 1.0.2
* PyYAML >= 3.12