# grab updated list of themes
# TurboBorland
# Highly suggest not running this. Super slow grabbing the themes
import socket, re, itertools
from time import sleep
from os import strerror
from multiprocessing import Pool, Lock, active_children

global lock
lock = Lock()

class getThemes(object):
	def __init__(self,pages):
		self.pages = pages

	def run(self):
		self.maxsize = self.pages[-1]
                self.theme_list = []
                self.find_names = re.compile("\/wp\-content\/themes\/(.+)\/screenshot.png")
		for self.page in self.pages:
                        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.connmsg = self.s.connect_ex(("wordpress.org",80))
                        while (self.connmsg != 0):
                                print("Error grabbing page:\t%s" % strerror(self.connmsg))
                                sleep(2.1) # minimum timeout for next socket
                                self.connmsg = self.s.connect_ex(("wordpress.org",80))
                        self.s.send("GET /extend/themes/browse/popular/page/"+str(self.page)+"/ HTTP/1.1\r\nHost: wordpress.orgr\n\r\n")
                        # I could lock, but...who cares? lock acquire and release if you do
                        print("Spidering theme page %d of %d" % (self.page,self.maxsize))
                        sleep(2)
                        self.chunk = self.s.recv(8000)
			# TODO: This will restart entire chunk
                        if (self.chunk.find("500 Internal") > 0):
                                print("500 Internal Server Error! You are sending too fast!")
                                return 1
			while (self.chunk.find("http://wordpress.org/about/privacy/") <= 0):
                                sleep(1)
                                self.chunk += self.s.recv(2048)
				#print("%s" % str(len(self.chunk)))
				# TODO: slow networks take a shit on this part
                        self.s.close()
                        self.names = self.find_names.findall(self.chunk)
                        for self.name in self.names:
                                lock.acquire()
                                self.theme_list.append(str(self.name))
                                lock.release()
                lock.acquire()
                f = open(themeout,"a")
                for self.theme in self.theme_list:    f.write(str(self.theme)+"\n")
                f.close()
                lock.release()
		print("end")
                return 0

# gop 1 will be theme, gop 2 plugin, gop 3 both
# pool broker
def worker(page):
	while (getThemes(page).run() != 0):	sleep(1)

def grouper(iterable,n,fillvalue=None):
    it = iter(iterable)
    def take():
	while 1: yield list(itertools.islice(it,n))
    return iter(take().next,[])

def spiderman(page,endpage,psize,themef):
	global themeout
	themeout = themef
	
	if (page <= 2 or endpage <=2):
		theme_list = []
		find_names = re.compile("\/wp\-content\/themes\/(.+)\/screenshot.png")
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connmsg = s.connect_ex(("wordpress.org",80))
		while (connmsg != 0):
			print("Error grabbing page:\t%s" % strerror(connmsg))
			sleep(2.1)
			connmsg = s.connect_ex(("wordpress.org",80))
		print("Spidering initial theme page")
		s.send("GET /extend/themes/browse/popular/ HTTP/1.1\r\nHost: wordpress.org\r\n\r\n")
		sleep(2)
		chunk = s.recv(8000)
		while (chunk.find("http://wordpress.org/about/privacy/") <= 0):
			sleep(1)
			chunk += s.recv(2048)
		s.close()
		names = find_names.findall(chunk)
		if (endpage <= 1):	endpage = int(re.findall("\/extend\/themes\/browse\/popular\/page\/(\d{3,})", chunk)[0])
		if (page <= 1):
			for name in names:	theme_list.append(str(name))
			page = 2
			f = open(themeout,"a")
			for theme in theme_list:	f.write(str(theme)+"\n")
			f.close()
	endpage += 1
	
	# pool management
	pagecount = (endpage-page)
	if (pagecount <= psize):	
		psize = pagecount
		chunksize = 1
		pool = Pool(processes=psize)
	else:
		pool = Pool(processes=psize)
                chunksize = ((pagecount / psize) + (pagecount % psize))
        print("Max Pages: %d\tPages: %d\tChunk size: %d\tPool size: %d" % (int(endpage-1),pagecount,chunksize,psize))
	print("Starting theme spider")
	for chunk in itertools.izip(grouper(range(page,endpage),chunksize)):  pool.map_async(worker,chunk)
	pool.close()
        try:
                while(len(active_children()) > 0): # how many active children do we have
                        sleep(2)
                        ignore = active_children()
        except KeyboardInterrupt:       exit("CTRL^C caught, exiting...\n\n")
	print("Theme spidering complete. Output located at %s." % str(themeout))
