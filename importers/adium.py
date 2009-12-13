"""
Parses a set of Adium log files and sends the data to a log server

The Adium log format is described here: http://trac.adium.im/wiki/XMLLogFormat
"""
import os
import sys
import commands
import logging
import glob
import urllib2
import urllib

from optparse import OptionParser
from xml.dom import minidom
from socket import gethostname

CLIENT_ID = "adium"

def get_text(node, text=[]):
    if node.nodeType is node.TEXT_NODE:
        text.append(node.data)
    else:
        for childNode in node.childNodes:
            get_text(childNode, text)
    return text

#POST to /messages/msn/tony@angerilli.ca/add (timestamp, message_text, other_account)
def parse_logfile(path, host, server):
    logging.info("Parsing %s", path)
    filename = os.path.splitext(os.path.split(path)[1])[0]
    other_account = filename.split(" ")[0]
    xmldoc = minidom.parse(path)
    conversations = xmldoc.getElementsByTagName('chat')
    if len(conversations) == 0:
        logging.error("Could not find a conversation in %s", path)
        return
    conversation = conversations[0]
    url = server + "messages/" + urllib.quote(conversation.attributes["service"].value) + "/" + urllib.quote(conversation.attributes["account"].value) + "/add/"
    messages = conversation.getElementsByTagName('message')
    for message in messages:
        logging.debug(message.attributes["time"].value)
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
                  "host":host, "client_type":CLIENT_ID, "alias":alias,
                  "owner_account":conversation.attributes["account"].value}
        for key, value in values.items():
            values[key] = value.encode('utf-8')
        data = urllib.urlencode(values)
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request)
        result = response.read()
        logging.debug(result)
        
    xmldoc.unlink()
    
def find_logfiles(path):
    logfiles = []
    for curPath, directories, files in os.walk(path):
        for curFile in files:
            if curFile.endswith(".xml"):
                logfiles.append(os.path.join(curPath, curFile))
    return logfiles
    
#All importers must implement the following interface
def get_option_parser():
    parser = OptionParser()
    parser.add_option("-p", "--path", 
                      default=os.path.join(os.path.expanduser("~"), "Library/Application Support/Adium 2.0/Users/Default/Logs"),
                      dest="base_path",
                      help="Choose a specific path to parse for logfiles")
    parser.add_option("-n", "--network",
                      default=None,
                      help="An instant messaging network type to process (i.e. MSN, Jabber, ICQ, etc..)")
    parser.add_option("-a", "--account",
                      default="*",
                      help="A specific account to process (i.e. user@hotmail.com). Requires that network be set.")
    
    return parser

def parse(argv, server):
    parser = get_option_parser()
    (options, args) = parser.parse_args()
    if options.network:
        for log_dir in glob.glob(os.path.join(options.base_path, "%s.%s" % (options.network, options.account))):
            logfiles = find_logfiles(log_dir)
    else:
        logfiles = find_logfiles(options.base_path)
    for logfile in logfiles:
        parse_logfile(logfile, gethostname(), server)
    