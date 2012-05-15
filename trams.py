#!/usr/bin/env python

import re
import time
import urllib2
import iso8601
import xml.dom.minidom

from translate import xml_to_dict

def get_tram_arrivals(stop_number):
	my_url = 'http://webpids.tramtracker.com.au/pidsservice/pids.asmx'

	# They seem happy if I give them this :-)
	my_guid = '00000000-0000-0000-0000-000000000000'

	# Holy shit all this just to get the next arrival times!
	post_data = """
	<?xml version="1.0" encoding="utf-8"?>
	<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">

	<soap:Header>
		<PidsClientHeader xmlns="http://www.yarratrams.com.au/pidsservice/">
			<ClientGuid>{guid}</ClientGuid>
			<ClientType>WEBPID</ClientType>
			<ClientVersion>1.1.0</ClientVersion>
			<ClientWebServiceVersion>6.4.0.0</ClientWebServiceVersion>
		</PidsClientHeader>
	</soap:Header>

	<soap:Body>
		<GetNextPredictedRoutesCollection xmlns="http://www.yarratrams.com.au/pidsservice/">
		<stopNo>{stop_number}</stopNo>
		<routeNo>0</routeNo>
		<lowFloor>false</lowFloor>
		</GetNextPredictedRoutesCollection>
	</soap:Body>
	</soap:Envelope>
	"""
	post_data = post_data.format(guid=my_guid, stop_number=str(stop_number))

	# Haha it doesn't like nice formatting
	post_data = post_data.replace("\n", "").replace("\t", "")

	req = urllib2.Request(url=my_url, data=post_data, headers = {
		'Content-Type': 'text/xml',
		'SOAPAction': 'http://www.yarratrams.com.au/pidsservice/GetNextPredictedRoutesCollection'
		})

	f = urllib2.urlopen(req)

	xml_string = f.read()

	data = xml_to_dict(xml_string)
	data = data['soap:Envelope']['soap:Body']['GetNextPredictedRoutesCollectionResponse']['GetNextPredictedRoutesCollectionResult']['diffgr:diffgram']['DocumentElement']['ToReturn']
	data = [pythonify_this(tram) for tram in data]

	return data

def pythonify_this(data):
	def uncamel(name):
		s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
		return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

	def pythonify(value):
		if value == "true":
			value = True
		elif value == "false":
			value = False

		if value == {}:
			value = None

		if isinstance(value, basestring) and value.replace("-", "").isdigit():
			value = int(value)
			
		if isinstance(value, basestring) and re.match('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
			value = int(iso8601.parse_date(value).strftime("%s"))

		return value

	return {uncamel(key):pythonify(value) for key, value in data.iteritems()}

def main(stop_id):
	data = get_tram_arrivals(stop_id)

	for idx, tram in enumerate(data):
		print "Route:   ", tram['route_no']
		print "Dest:    ", tram['destination']

		wait_time = tram['predicted_arrival_date_time'] - time.mktime(time.localtime())
		wait_time = int(wait_time / 60)
		
		if wait_time > 0:
			print "Arrival: ", wait_time, "mins"
		elif wait_time < 0:
			print "Arrival: ", abs(wait_time), "mins (late)"
		else:
			print "Arrival:  Now"

		if idx < len(data) - 1:
			print

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Print tram arrival times')
	parser.add_argument('--stop-id', type=int, required=True, help='Tram Stop ID')
	args = parser.parse_args()
	main(args.stop_id)