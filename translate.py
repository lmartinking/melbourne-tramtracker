"""
Author: Michael Cooper <michael.cooper@hitwise.com>

XMLify a dict
"""

from xml.dom.minidom import parseString, Node
from pyexpat import ExpatError

def xml_to_dict(xml_string):
	'''
	Convert an XML string to a dictionary object for easy access in python.

	eg:
	<test>123</test> -> {'test':123}
	'''
	try:
		dom = parseString(xml_string)
	except ExpatError:
		assert False, 'String was not valid XML.\n%s' % xml_string
	return dom_to_dict(dom)

def dom_to_dict(dom):
	'''
	Convert a XML dom tree to a dict (recursive function)
	'''
	ret = {}
	for node in dom.childNodes:
		if node.nodeType == Node.ELEMENT_NODE:
			if node.nodeName in ret:
				if type(ret[node.nodeName]) == list:
					ret[node.nodeName].append(dom_to_dict(node))
				else:
					ret[node.nodeName] = [ret[node.nodeName], dom_to_dict(node)]
			else:
				ret[node.nodeName] = dom_to_dict(node)
		elif node.nodeType == Node.TEXT_NODE:
			if not node.nodeValue.isspace():
				return node.nodeValue
		else:
			ret[node.nodeName] = node.nodeValue
	return ret
