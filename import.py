"""
A frontend for the importer scripts.  This is the program that you run
to do an import of existing log files.

The following interface is required of all importers to be usable by this frontend:

#All importers must implement the following interface
def get_option_parser(): pass

def parse(argv): pass
"""
import sys
import logging
from optparse import OptionParser
import glob

import importers

def get_im_type_names():
    return [n.split("importers/")[1].split(".")[0] for n in glob.glob("importers/*.py") if "__init__" not in n]

def get_im_module(name):
    mod = __import__("importers", fromlist=[name])
    return getattr(mod, name)
    
def print_usage():
    print "Usage: python import.py <server url> <importer type> [importer options]"
    im_types = get_im_type_names()
    print "Valid importer types are: %s" % ",".join(im_types)
    for im_type in im_types:
        print "\nOptions for %s are:" % im_type
        im_mod = get_im_module(im_type)
        for option in im_mod.get_option_parser().option_list:
            print "\t%s: %s" % (option, option.help)
    
    print "\nExample: python import.py http://localhost:8000 adium --network=ICQ"

def main(args):
    if len(args) < 3 or args[1].startswith("-") or args[2].startswith("-"):
        print_usage()
        return 1
    
    server = args[1]
    im_type = args[2]
    try:
        im_mod = get_im_module(im_type)
    except (ImportError, AttributeError), e:
        print "ERROR: Invalid IM App type: %s\n" % im_type
        print_usage()
        return 1
        
    try:
        im_mod.parse(args, server)
    except Exception, e:
        print "Error parsing logfiles: %s" % (e.message)
        logging.exception("Parse Error")
        return 1
        
    return 0
    
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    sys.exit(main(sys.argv))
    