"""
Parses a set of Adium log files and dumps the data into a database
"""
import os
import sys
import commands
from xml.dom import minidom
import logging

import urllib2
import urllib

CLIENT_ID = "adium"
SERVER = "http://localhost:8000/"

def get_text(node, text=[]):
    if node.nodeType is node.TEXT_NODE:
        text.append(node.data)
    else:
        for childNode in node.childNodes:
            get_text(childNode, text)
    return text

#POST to /messages/msn/tony@angerilli.ca/add (timestamp, message_text, other_account)
def parse_logfile(path, host):
    logging.info("Parsing %s", path)
    filename = os.path.splitext(os.path.split(path)[1])[0]
    other_account = filename.split(" ")[0]
    xmldoc = minidom.parse(path)
    conversations = xmldoc.getElementsByTagName('chat')
    if len(conversations) == 0:
        logging.error("Could not find a conversation in %s", path)
        return
    conversation = conversations[0]
    url = SERVER + "messages/" + urllib.quote(conversation.attributes["service"].value) + "/" + urllib.quote(conversation.attributes["account"].value) + "/add/"
    messages = conversation.getElementsByTagName('message')
    for message in messages:
        print message.attributes["time"].value
        message_text = "\n".join(get_text(message, []))
        if message.attributes["sender"].value == conversation.attributes["account"].value:
            receiver_account = other_account
        else:
            receiver_account = conversation.attributes["account"].value
        if 'alias' in  message.attributes.keys():
            alias = message.attributes["alias"].value
        else:
            alias = message.attributes["sender"].value
        values = {"timestamp":message.attributes["time"].value, "message_text":message_text,
                  "sender_account":message.attributes["sender"].value, "receiver_account":receiver_account,
                  "host":hostname, "client_type":CLIENT_ID, "alias":alias,
                  "owner_account":conversation.attributes["account"].value}
        for key, value in values.items():
            values[key] = value.encode('utf-8')
        data = urllib.urlencode(values)
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request)
        result = response.read()
        print result
        
    xmldoc.unlink()
    
def find_logfiles(path):
    for curPath, directories, files in os.walk(path):
        for curFile in files:
            if curFile.endswith(".xml"):
                parse_logfile(os.path.join(curPath, curFile), hostname)
                #return
    
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    if len(sys.argv) < 2:
        print "Usage: python adium.py <path to log files>"
        sys.exit(1)
    
    root_path = sys.argv[1]
    hostname = commands.getoutput("hostname")
    find_logfiles(root_path)