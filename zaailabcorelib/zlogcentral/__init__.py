from zaailabcorelib.zlogcentral.api import LogClient, LogJob
from gevent import monkey as fix_gevent
fix_gevent.patch_all()
Zlogcentral = LogClient("10.40.34.20",10000)