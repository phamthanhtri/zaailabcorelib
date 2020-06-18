import sys
import os
os.environ['SERVICE_ENV_SETTING'] = str.upper(sys.argv[1])
from zaailabcorelib.http_server.server import Server