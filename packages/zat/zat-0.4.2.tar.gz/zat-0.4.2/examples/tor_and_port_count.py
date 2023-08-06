"""Tor detection and SSL port count example"""

import os
import sys
import argparse
import re
from collections import Counter

# Local imports
from zat import zeek_log_reader

if __name__ == '__main__':
    # Example to check for potential Tor connections and give a summary of different ports
    # used for SSL connections. Please note that your Zeek installation must stamp the
    # ssl.log file with the 'issuer' field. More info can be found here:
    # https://docs.zeek.org/en/master/script-reference/proto-analyzers.html#zeek-ssl

    # Set up the regex search that is used against the issuer field
    issuer_regex = re.compile('CN=www.\w+.com')

    # Set up the regex search that is used against the subject field
    subject_regex = re.compile('CN=www.\w+.net')

    # Collect args from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('zeek_log', type=str, help='Specify a zeek log to run ZeekLogReader test on')
    parser.add_argument('-t', action='store_true', default=False, help='Sets the program to tail a live Zeek log')
    args, commands = parser.parse_known_args()

    # Check for unknown args
    if commands:
        print('Unrecognized args: %s' % commands)
        sys.exit(1)

    # Sanity check that this is a ssl log
    if 'ssl' not in args.zeek_log:
        print('This example only works with Zeek ssl.log files..')
        sys.exit(1)

    # File may have a tilde in it
    if args.zeek_log:
        args.zeek_log = os.path.expanduser(args.zeek_log)

        # Run the zeek reader on the ssl.log file looking for potential Tor connections
        reader = zeek_log_reader.ZeekLogReader(args.zeek_log, tail=args.t)
        # Just a counter to keep an eye on how many possible Tor connections we identify
        number = 0
        # A empty list to use for the port statistics
        ports = []

        for row in reader.readrows():
            # Add the destination port to the list of ports
            ports.append(row['id.resp_p'])
            # Pull out the Certificate Issuer
            try:
                issuer = row['issuer']
            except KeyError:
                print('Could not find the issuer field in your ssl.log. Please verify your log file.')
                sys.exit(1)
            # Check if the issuer matches the known Tor format
            if issuer_regex.match(issuer):
                # Pull out the Certificate Subject
                try:
                    subject = row['subject']
                except KeyError:
                    print('Could not find the subject field in your ssl.log. Please verify your log file.')
                    sys.exit(1)
                # Check if the subject matches the known Tor format
                if subject_regex.match(subject):
                    print('\nPossible Tor connection found')
                    print('From: {:s} To: {:s} Port: {:d}'.format(row['id.orig_h'], row['id.resp_h'], row['id.resp_p']))
                    number +=1

        # If we are not tailing a live log file, let's print some stats.
        if not args.t:
            # First let's print (if any) the number of possible Tor connections that were found
            print('\nTotal number of possible Tor connections found: {:d}'.format(number))
            # Now let's do the stats on and printing of the port count
            portcount = Counter(ports)
            print('\nPort statistics')
            for port, count in portcount.most_common():
                print('{:<7} {:d}'.format(port, count))
