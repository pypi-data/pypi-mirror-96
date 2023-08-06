#!/usr/bin/env python
from __future__ import print_function
import sys
from csr_cloud.token_api import Token_api as token_api

def main(argv):

    # Establish a connection to the token server
    conn = token_api()

    # Verify server is up
    rc = conn.is_server_up()
    if rc != 0:
        print("failed connection to token manager rc=%d" % rc)
        sys.exit()

    # Request server to clear the default AAD application
    result = conn.clear_aad_app_list()
    if result != 'OK':
        print("Failed to clear AAD application list: %s" % result)
        sys.exit()

    conn.disconnect()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
