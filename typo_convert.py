#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple script to speed the conversion of my old typomap shorthand files
to LanguageTool XML.
"""

__appname__ = "typomap-to-LanguageTool converter"
__author__  = "Stephan Sokolow (deitarion/SSokolow)"
__version__ = "0.0"
__license__ = "GNU GPL 3.0 or later"

import os, re
import lxml.etree as ET

import logging
log = logging.getLogger(__name__)

# -- Code Here --
def convert(infile, cat_name):
    root = ET.Element("category", name=cat_name)
    root.append(ET.Comment("TODO: Hand-tune this and fill in the example tags."))

    indata = infile.read().decode('utf8')
    indata = re.sub(r'(?s)/\*.*?\*/', '', indata)
    for line in indata.split('\n'):
        line = re.sub('\t+', '\t', line.strip())

        if line and not line.startswith('#'):
            fields = line.split('\t', 2)
            while len(fields) < 3:
                fields.append('')

            name, suggestion, description = fields

            id = re.sub('[^a-zA-Z0-9-]', '_', name).upper()

            tokens = name.split()
            suggestions = [x.strip() for x in suggestion.split('|')]

            rule = ET.SubElement(root, 'rule', id=id, name=name.title())
            pattern = ET.SubElement(rule, 'pattern')
            pattern.text = ''
            for tok_str in tokens:
                token = ET.SubElement(pattern, 'token')
                token.text = tok_str
                token.tail = ''

            msg = ET.SubElement(rule, 'message')
            msg.text = "Did you mean "
            for sug in suggestions:
                suggestion = ET.SubElement(msg, 'message')
                suggestion.text = sug
                suggestion.tail = " or "
            suggestion.tail = "? " + description

            inc = ET.SubElement(rule, 'example', type='incorrect')
            inc.text = ''
            mkr = ET.SubElement(inc, 'marker')
            mkr.text = name
            mkr.tail = ''

            for sug in suggestions:
                cor = ET.SubElement(rule, 'example', type='correct')
                cor.text = ''
                mkr = ET.SubElement(cor, 'marker')
                mkr.text = sug
                mkr.tail = ''

    return root


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(version="%%prog v%s" % __version__,
            usage="%prog [options] <argument> ...",
            description=__doc__.replace('\r\n','\n').split('\n--snip--\n')[0])
    parser.add_option('-v', '--verbose', action="count", dest="verbose",
        default=2, help="Increase the verbosity. Can be used twice for extra effect.")
    parser.add_option('-q', '--quiet', action="count", dest="quiet",
        default=0, help="Decrease the verbosity. Can be used twice for extra effect.")

    #Reminder: %default can be used in help strings.
    #TODO: Make sure that textwrap in description/epilog is correct.

    opts, args  = parser.parse_args()

    # Set up clean logging to stderr
    log_levels = [logging.CRITICAL, logging.ERROR, logging.WARNING,
                  logging.INFO, logging.DEBUG]
    opts.verbose = min(opts.verbose - opts.quiet, len(log_levels) - 1)
    opts.verbose = max(opts.verbose, 0)
    logging.basicConfig(level=log_levels[opts.verbose],
                        format='%(levelname)s: %(message)s')


    all_root = ET.Element("rules", lang='en')
    for path in args:
        with open(path, 'rU') as fh:
            all_root.append(convert(fh, os.path.basename(path).decode('utf8')))

    tree = ET.ElementTree(all_root)
    print ET.tostring(all_root, encoding='utf-8', pretty_print=True)
