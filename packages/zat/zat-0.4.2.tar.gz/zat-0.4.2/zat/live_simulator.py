"""LiveSimulator: This class reads in various Zeek logs. The class utilizes
                 the ZeekLogReader and simply loops over the static zeek log
                 file, replaying rows and changing any time stamps
        Args:
            eps (int): Events Per Second that the simulator will emit events (default = 10)
            max_rows (int): The maximum number of rows to generate (default = None (go forever))
"""

import os
import time
import datetime
import itertools

# Third party
import numpy as np

# Local Imports
from zat import zeek_log_reader
from zat.utils import file_utils


class LiveSimulator(object):
    """LiveSimulator: This class reads in various Zeek logs. The class utilizes the
                      ZeekLogReader and simply loops over the static zeek log file
                      replaying rows at the specified EPS and changing timestamps to 'now()'
    """

    def __init__(self, filepath, eps=10, max_rows=None, only_once=False):
        """Initialization for the LiveSimulator Class
           Args:
               eps (int): Events Per Second that the simulator will emit events (default = 10)
               max_rows (int): The maximum number of rows to generate (default = None (go forever))
        """

        # Compute EPS timer
        # Logic:
        #     - Normal distribution centered around 1.0/eps
        #     - Make sure never less than 0
        #     - Precompute 1000 deltas and then just cycle around
        self.eps_timer = itertools.cycle([max(0, delta) for delta in np.random.normal(1.0/float(eps), .5/float(eps), size=1000)])

        # Initialize the Zeek log reader
        self.log_reader = zeek_log_reader.ZeekLogReader(filepath, tail=False)

        # Store max_rows and only_once flag
        self.max_rows = max_rows
        self.only_once = only_once

    def rows(self):
        """Using the ZeekLogReader this method generates (yields) each row of the log file
           replacing timestamps, looping and emitting rows based on EPS rate
        """

        # Loop forever or until max_rows is reached
        num_rows = 0
        while True:

            # Yield the rows from the internal reader
            for row in self.log_reader.readrows():
                yield self.replace_timestamp(row)

                # Sleep and count rows
                time.sleep(next(self.eps_timer))
                num_rows += 1

                # Check for max_rows
                if self.max_rows and (num_rows >= self.max_rows):
                    return

            # Check for only_once
            if self.only_once:
                return

    @staticmethod
    def replace_timestamp(row):
        """Replace the timestamp with now()"""
        if 'ts' in row:
            row['ts'] = datetime.datetime.utcnow()
        return row


def test():
    """Test for LiveSimulator Python Class"""

    # Grab a test file
    data_path = file_utils.relative_dir(__file__, '../data')
    test_path = os.path.join(data_path, 'conn.log')
    print('Opening Data File: {:s}'.format(test_path))

    # Create a LiveSimulator reader
    data_stream = LiveSimulator(test_path, max_rows=10)
    for line in data_stream.rows():
        print(line)
    print('Read with max_rows Test successful!')


if __name__ == '__main__':
    # Run the test for easy testing/debugging
    test()
