import socket, re, itertools, ssl
from os import strerror
from multiprocessing import Pool, Lock, active_children
from time import sleep

global lock
lock = Lock()

class BrutePlugins(object):
	def __init__(self,plugin):
		self.plugin = plugin

	def run(self):
		self.donothing = 0
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if (secure == 1):	self.ssocket = ssl.wrap_socket(self.s)
		else:	self.ssocket = self.s
		self.connmsg = self.ssocket.connect_ex((host,port))
		while (self.connmsg != 0):
			print("ERROR:\t%s" % strerror(self.connmsg))
			sleep(2.1)
			self.connmsg = self.ssocket.connect_ex((host,port))
		self.ssocket.send("HEAD "+path+"wp-content/plugins/"+self.plugin+"/ HTTP/1.1\r\nHost: "+host+"\r\n\r\n")
		self.chunk = self.ssocket.recv(20)
		while (len(self.chunk) < 20):
			sleep(1)
			self.chunk += self.ssocket.recv(20)
		self.ssocket.close()
		if (self.chunk.find("200 OK") > 0):
			print("Valid plugin found:\t%s" % self.plugin)
			lock.acquire()
			f = open(plugfound,"a")
			f.write(self.plugin+"\n")
			f.close()
			lock.release()
		elif (self.chunk.find("403 Forb") > 0): # plugins finally locking down directories
			print("Valid plugin found:\t%s" % self.plugin)
			lock.acquire()
			f = open(plugfound,"a")
			f.write(self.plugin+"\n")
			f.close()
			lock.release()
		elif (self.chunk.find("500") > 0):
			print(str(self.plugin))
			print("500 Internal Server Error Seen, you might be sending too fast!")
			print("Logged to file as 500 in case of locked directory. If you see lots of these, please slow down scanner")
			lock.acquire()
			f = open(plugfound,"a")
			f.write("500 (possible): "+self.plugin+"\n")
			f.close()
			lock.release()
			return 0
		elif (self.chunk.find("404") > 0): self.donothing = 1
		else:
			print("Irregular server response seen.\n%s" % str(self.chunk))
			return 1
		return 0

def worker(plugins):
	for plugin in plugins:
		plugin = str(plugin.strip("\n"))
		while (BrutePlugins(plugin).run() != 0):	sleep(1)
	
def grouper(iterable,n,fillvalue=None):
    it = iter(iterable)
    def take():
        while 1: yield list(itertools.islice(it,n))
    return iter(take().next,[])

def brutePlugin(pluginlist,foundplug,hosti,pathi,porti,securei,psize):
	global host
	host = hosti
	global port
	port = porti
	global secure
	secure = securei
	global plugfound
	plugfound = foundplug
	global path
	path = pathi
	f = open(plugfound,'w').close()
	listsize = (len(pluginlist))
	
	# manage pool
	if (psize == 0):	psize = 5
	if (list <= psize):	chunksize = 1
	else:	chunksize = ((listsize / psize) + (listsize % psize))
	print("Plugin list size: %d\tChunk size: %d\tPool size: %d" % ((listsize),chunksize,psize))
	print("Plugin bruteforcing started")
	pool = Pool(processes=psize)
        for chunk in itertools.izip(grouper(pluginlist,chunksize)):  pool.map_async(worker,chunk)
        pool.close()
        try:
                while(len(active_children()) > 0): # how many active children do we have
                        sleep(2)
                        ignore = active_children()
        except KeyboardInterrupt:       exit('CTRL^C caught, exiting...\n\n')
	print("Plugin bruteforce complete")
