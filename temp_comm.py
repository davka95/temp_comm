#!/user/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import configparser
import datetime
import RPi.GPIO as GPIO
from time import sleep
import requests
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import os
#import faulthandler

#sys.settrace
#config
config = configparser.ConfigParser()

#statisks log fails
config.read('/opt/temp_comm/config.ini')

#datetime
now = datetime.datetime.now()

#faulthandler.enable()
#pin_config
red_pin = int(config['SETTINGS']['red_pin'])
green_pin = int(config['SETTINGS']['green_pin'])
yellow_pin = int(config['SETTINGS']['yellow_pin'])
agent_url = config['SETTINGS']['agent_url']
agent_port = int(config['SETTINGS']['agent_port'])
user_timer = int(config['SETTINGS']['user_timer'])
#17
turnon_pin = int(config['SETTINGS']['turnon_pin'])
#25
start_temp_pin = int(config['SETTINGS']['start_temp_pin'])
log_path = config['SETTINGS']['log_path']
response_status = 404
termometer_read = False

class S(BaseHTTPRequestHandler):

	def do_GET(self):
		global termometer_read
		log(self.path)
		print(self.path)
		if self.path == "/get-health":
			termometer_read = False
			print("before main")
			main()

			if response_status != 404:
				print("if: ", response_status)
				self.send_response(200)
				self.send_header('Content-type', 'application/json')
				self.send_header('Access-Control-Allow-Origin', '*')
				self.end_headers()
				json_string = json.dumps({"status": response_status})
				self.wfile.write(json_string.encode(encoding='utf_8'))
			else:
				self.send_response(404)
				self.send_header('Content-type', 'application/json')
				self.end_headers()
				print("else: ", response_status)
	def do_OPTIONS(self):
		print("Options request")
		self.send_response(200, "ok")
		self.send_header('Content-type', 'application/json')
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
		self.send_header('Access-Control-Allow-Methods', 'GET')
		self.end_headers()

def main():
	global response_status

	GPIO.setmode(GPIO.BCM)
	#paarbauda vai ierice ir ieslegta
	GPIO.setup(turnon_pin, GPIO.OUT)
	GPIO.output(turnon_pin, GPIO.LOW)
	time.sleep(1)
	GPIO.cleanup(turnon_pin)

	time.sleep(2)
	#temperaturas merisana
	GPIO.setup(start_temp_pin, GPIO.OUT)
	GPIO.output(start_temp_pin, GPIO.LOW)
	time.sleep(1)
	GPIO.cleanup(start_temp_pin)

	#pin setup
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(red_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	GPIO.setup(yellow_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	GPIO.setup(green_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

	#sāk klausīties gpio pinu eventus
	GPIO.add_event_detect(green_pin, GPIO.RISING, callback = make_request, bouncetime = 300)
	GPIO.add_event_detect(yellow_pin, GPIO.RISING, callback = make_request, bouncetime = 300)
	GPIO.add_event_detect(red_pin, GPIO.RISING, callback = make_request, bouncetime = 300)

	for i in range(user_timer):
		if termometer_read == True:
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(turnon_pin, GPIO.OUT)
			GPIO.output(turnon_pin, GPIO.LOW)
			time.sleep(1)
			GPIO.cleanup(turnon_pin)
			break
		time.sleep(0.5)
	if termometer_read == False:
		#Darbības pēc config.ini nodefineta timeout
		GPIO.remove_event_detect(green_pin)
		GPIO.remove_event_detect(red_pin)
		GPIO.remove_event_detect(yellow_pin)
		response_status = 0

def make_request(pin):
	global response_status
	global termometer_read
	termometer_read = True
	log("nolasitais merijums: " + str(pin))
	print('nolasits merijums: ' + str(pin))

	#request status
	if pin == green_pin:
		response_status = 1
	if pin == yellow_pin:
		response_status = 2
	if pin == red_pin:
		response_status = 3

	#Vairs neklausas PINus
	GPIO.remove_event_detect(green_pin)
	GPIO.remove_event_detect(red_pin)
	GPIO.remove_event_detect(yellow_pin)
#	time.sleep(1)
#	GPIO.cleanup()
#	GPIO.setmode(GPIO.BCM)
#	GPIO.setup(turnon_pin, GPIO.OUT)
#	GPIO.output(turnon_pin,GPIO.LOW)
#	time.sleep(1)
#	GPIO.cleanup()
def log(text):
	if text == "":
		return
	if not os.path.isdir(log_path):
		os.makedirs(log_path)
	dt_now = datetime.datetime.now()
	f = open(log_path + "/" + dt_now.strftime("%Y-%m-%d") + "_log.txt", "a+")
	f.write(dt_now.strftime("%Y-%m-%d %I:%M:%S.%f ") + text + '\n')
	f.close()

def run(server_class=HTTPServer, handler_class=S, port=8080):
	server_address = (agent_url, agent_port)
	httpd = server_class(server_address, handler_class)
	log('starting server')
	print('starting server')
	httpd.serve_forever()

if __name__ == '__main__':
	from sys import argv

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		run()
