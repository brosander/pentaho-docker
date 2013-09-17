#!/usr/bin/python

import argparse
import StringIO
import sys
from lxml import etree

def setTag(parent, tag, text):
  value = parent.find(tag)
  if value is None:
    value = etree.SubElement(parent, tag)
  value.text = text

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''
  This script is designed to edit the xml property files used to configure hadoop (e.g. core-site.xml)
  ''')
  parser.add_argument('-f', '--filename', help='Filename to edit', required=True)
  parser.add_argument('-p', '--property', help='Property to set', required=True)
  parser.add_argument('-v', '--value', help='Value to set', required=True)
  parser.add_argument('-i', '--inplace', action='store_true', help='Edit the file in place')
  args = parser.parse_args()
  parser = etree.XMLParser(remove_blank_text=True,remove_comments=False)
  tree = etree.parse(args.filename, parser=parser)
  root = tree.getroot()
  found = False
  for property in root.findall('property'):
    name = property.find('name')
    if name is not None and name.text == args.property:
      found = True
      setTag(property, 'value', args.value)
  if not found:
    property = etree.SubElement(root, 'property')
    setTag(property, 'name', args.property)
    setTag(property, 'value', args.value)
  output = etree.tostring(tree, encoding='UTF-8', xml_declaration=True, pretty_print=True) 
  if args.inplace:
    with open(args.filename, 'w') as f:
      f.write(output)
  else:
    print output
