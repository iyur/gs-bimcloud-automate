import argparse
import sys
import lib
import time
import datetime
from multiprocessing import Process

def worker(server, logtime):
	cmd = argparse.ArgumentParser()
	cmd.add_argument('-p', '--password', required=True, help='Password.')
	cmd.add_argument('-d', '--debug', required=False, help='Debug exceptions.', action='store_true')
	arg = cmd.parse_args()

	cloud = lib.Cloud(server, 'masteradmin', arg.password, 'archimatika.com', logtime)

	try:
		cloud.collect()
	except Exception as err:
		print(getattr(err, 'message', str(err) or repr(err)), file=sys.stderr)
		if arg.debug:
			raise err
		else:
			exit(1)

if __name__ == '__main__':

	servers = ['http://tw.archimatika.com:22000', 'http://tw.archimatika.com:24000', 'http://tw.archimatika.com:25000']
	logtime = int(time.time())
	db = lib.DB()
	db.logEntry(logtime)
	print(datetime.datetime.fromtimestamp(logtime))

	processes = []
	for server in servers:
		p = Process(target=worker, args=(server,db.lid,))
		processes.append(p)
		p.start()

	for p in processes:
		p.join()

# 1682249720
# 1682163320