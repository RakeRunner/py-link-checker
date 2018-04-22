#!/usr/bin/env python3

import yaml
import asyncio
import aiohttp
import aiosmtplib
from email.mime.text import MIMEText
import os
import sys
import logging

# sends a notification by all means specified in the config
async def notifi(site, errors):
	text = ''

	# we form the text of the notice
	text += 'Domain: %s\n\n' % site['domain']
	text += 'Errors:\n'
	for error in errors:
		text += 'Url: "%s"\n' % error['url']
		text += 'Message:\n%s\n\n' % error['message']

	log.info(text)

	# send notification by email
	if 'smtp_notifi' in config:
		# default smtp configuration
		smtp_notifi = {
			'enabled': False,
			'port': 587,
			**config['smtp_notifi']
		}

		if type(smtp_notifi) is bool and smtp_notifi['enabled']:
			emails = []
			if 'administration' in config:
				for admin in config['administration']:
					if 'email' in admin:
						emails.append(admin['email'])
			if len(emails) > 0:
				smtp = aiosmtplib.SMTP(hostname=smtp_notifi['host'], port=smtp_notifi['port'], loop=loop, use_tls=False)

				mail_text += '---------------------------\n\n'
				mail_text += text
				mail_text += '---------------------------'

				await smtp.connect()
				await smtp.starttls()
				await smtp.auth_login(smtp_notifi['username'], smtp_notifi['password'])

				message = MIMEText(mail_text)
				message['From'] = 'info@branchup.pro'
				message['Subject'] = 'SITE PROBLEM - %s (errors:%s)' % (site['domain'], len(errors))

				await smtp.send_message(message, recipients=emails)

async def check_site(site):
	with await sem:
		if 'urls' not in site:
			site['urls'] = [{'uri':'/'}]

		find = False
		for uri_info in site['urls']:
			if uri_info['uri'] == '/':
				find = True
				break
		if find is False:
			site['urls'].append({'uri':'/'})

		errors = []
		for uri_info in site['urls']:
			uri = uri_info['uri']
			if uri[0] != '/':
				uri = '/%s' % uri

			proto = 'https'
			if 'http' in site and site['http'] is True:
				proto = 'http'

			url = '%s://%s%s' % (proto, site['domain'], uri)

			log.info('check: %s' % url)

			try:
				async with aiohttp.ClientSession() as session:
					async with session.get(url, verify_ssl=False) as response:
						html = await response.text()

						if response.status != 200:
							errors.append({
								'url': url,
								'message': 'Bad site status: %s' % response.status
								})
							continue
						else:
							if 'check_text' in uri_info:
								if uri_info['check_text'] not in html:
									errors.append({
										'url': url,
										'message': 'Cant find text: "%s"' % uri_info['check_text']
										})
									continue
								
			except aiohttp.client_exceptions.InvalidURL as e:
				errors.append({
					'url': url,
					'message': 'Invalid URL' % url 
					})
								
			except aiohttp.client_exceptions.ClientConnectorError as e:
				errors.append({
					'url': url,
					'message': 'Client connector error' 
					})
			except Exception as e:
				exception_code = str(sys.exc_info()[0])
				errors.append({
					'url': url,
					'message': 'Other error [%s] - %s' % (exception_code, repr(e))
					})

		if len(errors) > 0:
			await notifi(site, errors)

if __name__ == '__main__':
	BASE_PATH = os.path.dirname(os.path.abspath(__file__))
	CONFIG_PATH = '%s/config.yaml' % BASE_PATH

	if not os.path.exists(CONFIG_PATH):
		if os.path.exists('%s/config.yaml.dist' % BASE_PATH):
			print('Copy the file config.yaml.dist and name the new file config.yaml !')
		else:
			print('Can\'t find config.yaml file !')

		exit()

	# main config load
	config = {}
	with open(CONFIG_PATH, 'r') as f:
		config = yaml.load(f)

	if 'logger' not in config:
		config['logger'] = {}

	config['logger'] = {
		'log_to_screen': True,
		'log_to_file': False,
		'log_file_path': 'log.txt',
		'level': 'INFO',
		**config['logger'],
	}

	# setup logging
	log = logging.getLogger(__name__)
	log.setLevel(getattr(logging, config['logger']['level']))

	logFormatter = logging.Formatter('%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s')

	if type(config['logger']['log_to_screen']) is bool and config['logger']['log_to_screen']:
		consoleHandler = logging.StreamHandler()
		consoleHandler.setFormatter(logFormatter)
		log.addHandler(consoleHandler)

	if type(config['logger']['log_to_file']) is bool and config['logger']['log_to_file']:
		fileHandler = logging.FileHandler(config['logger']['log_file_path'])
		fileHandler.setFormatter(logFormatter)
		log.addHandler(fileHandler)

	if 'max_parallel_checks' not in config:
		config['max_parallel_checks'] = 3
	
	sem = asyncio.Semaphore(config['max_parallel_checks'])

	def main():
		if 'sites' not in config or len(config['sites']) == 0:
			log.error('There are no sites in the list!')
			exit()

		loop = asyncio.get_event_loop()

		gathers = []
		if 'sites' in config:
			for site in config['sites']:
				gathers.append(check_site(site))

		loop.run_until_complete(asyncio.gather(*gathers))

		loop.close()

	try:
		main()
	except KeyboardInterrupt:
		sys.exit()