# did not think it'd need concurrency, if you can think of a reason let me know
import socket, re, ssl
from time import sleep
from os import strerror

def pluginDetect(pluginname):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (secure == 1):	ssocket = ssl.wrap_socket(s)
	else:	ssocket = s
        connmsg = ssocket.connect_ex((host,port))
        while (connmsg != 0):
                print("ERROR:\t%s" % strerror(connmsg))
                sleep(2.1)
                connmsg = ssocket.connect_ex((host,port))
	ssocket.send("GET "+path+"wp-content/plugins/"+pluginname+"/readme.txt HTTP/1.1\r\nHost: "+host+"\r\n\r\n")
	sleep(1)
	chunk = ssocket.recv(200)
	if (chunk.find("200 OK") > 0):
		trigger = 0
		while (chunk.find("Description") <= 0 and trigger != 8):
			sleep(1)
			chunk += ssocket.recv(200)
			trigger += 1
		if (trigger == 8):
			print("error looking for description for %s" % pluginname)
			return 1
		ssocket.close()
		versionreg = re.compile("Stable tag:(.+)",re.IGNORECASE)
		versionfind = versionreg.findall(chunk)[0]
		print("%s%s" % (pluginname, versionfind))
		f = open(plugout,"a")
		f.write("%s%s\n" % (pluginname,versionfind))
		f.close()
		return 0	
	elif (chunk.find("500 Internal") > 0):
		ssocket.close()
		print("500 internal server error seen! You may be sending too fast!")
		return 1
	else:
		ssocket.close()
		print("Different response seen. Possibly 403 Forbidden to readme file?\n" % chunk)
		return 1

def themeDetect(theme):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if (secure == 1):	ssocket = ssl.wrap_socket(s)
	else:   ssocket = s
        connmsg = ssocket.connect_ex((host,port))
        while (connmsg != 0):
                print("ERROR:\t%s" % strerror(connmsg))
                sleep(2.1)
                connmsg = ssocket.connect_ex((host,port))
        ssocket.send("GET "+path+"wp-content/themes/"+theme+"/style.css HTTP/1.1\r\nHost: "+host+"\r\n\r\n")
        sleep(1)
        chunk = ssocket.recv(200)
        if (chunk.find("200 OK") > 0):
                while (chunk.find("*/") <= 0):
                        sleep(1)
                        chunk += ssocket.recv(200)
                ssocket.close()
                versionreg = re.compile("Version:(.+)", re.IGNORECASE)
                versionfind = versionreg.findall(chunk)[0]
                print("%s%s" % (theme, versionfind))
                f = open(themeout,"a")
                f.write("%s%s\n" % (theme,versionfind))
                f.close()
                return 0
        elif (chunk.find("500 Internal") > 0):
                ssocket.close()
                print("500 internal server error seen! You may be sending too fast!")
                return 1
        else:
                ssocket.close()
                print("Different response seen. Possibly 403 Forbidden to readme file?\n" % chunk)
                return 1

def wordpressDetect():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (secure == 1):	ssocket = ssl.wrap_socket(s)
	else:	ssocket = s
        connmsg = ssocket.connect_ex((host,port))
        while (connmsg != 0):
        	print("ERROR:\t%s" % strerror(connmsg))
                sleep(2.1)
                connmsg = ssocket.connect_ex((host,port))
        ssocket.send("GET "+path+" HTTP/1.1\r\nHost: "+host+"\r\n\r\n")
        sleep(1)
        chunk = ssocket.recv(400)
        if (chunk.find("200 OK") > 0):
		print("Running WordPress Meta Generator version detector")
		trigger = 0
		while (chunk.find("meta name=\"generator\" content=\"") <= 0 and trigger != 8):
			sleep(1)
			chunk += ssocket.recv(400)
			trigger += 1
		ssocket.close()
		if (trigger != 8):
			metafind = re.compile("meta name=\"generator\" content=\"WordPress (.+)\"")
			metaversion = metafind.findall(chunk)[0]
			print("WordPress Version %s" % metaversion)
			f = open(wpout,"a")
			f.write("WordPress Version (meta generator):\t%s\n" % metaversion)
			f.close()
		else:	print("Timeout, meta generator may not be available")
	
	# css color code version detect
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (secure == 1):	ssocket = ssl.wrap_socket(s)
        else:	ssocket = s
        connmsg = ssocket.connect_ex((host,port))
        while (connmsg != 0):
        	print("ERROR:\t%s" % strerror(connmsg))
                sleep(2.1)
                connmsg = ssocket.connect_ex((host,port))
        ssocket.send("GET "+path+"wp-login.php HTTP/1.1\r\nHost: "+host+"\r\n\r\n")
	chunk = ssocket.recv(400)
	if (chunk.find("200 OK") > 0):
		trigger = 0
		print("Running WordPress CSS color version detection")
		while (chunk.find("</head>") <= 0 and trigger != 8):
			sleep(1)
			chunk += ssocket.recv(200)
			trigger += 1
		ssocket.close()
		if (trigger != 8):
			colorfind = re.compile("fresh[\w\.\d]+\?ver=([\.\d\w\s-]+)")
			colorversion = colorfind.findall(chunk)[0]
			if (colorversion == "20081210"):	print("WordPress Version 2.7 or 2.7.x")
			elif (colorversion == "20090610"):	print("WordPress Version 2.8")
			elif (colorversion == "20090625"):	print("WordPress Version 2.8.x")
			elif (colorversion == "20091217"):	print("WordPress Version 2.9 or 2.9.x")
			elif (colorversion == "20100610"):	print("WordPress Version 3.0 or 3.0.x")
			elif (colorversion == "20110121"):	print("WordPress Version 3.1 or 3.1.x")
			elif (colorversion == "20110703"):	print("WordPress Version 3.2 or 3.2.x")
			elif (colorversion == "20111206"):	print("WordPress Version 3.3 or 3.3.x")
			else:	print("WordPress Version: %s" % str(colorversion))
			f = open(wpout,"a")
			f.write("WordPress Version (css version):\t%s\n" % str(colorversion))
			f.close()
		else:	print("Timeout seen, CSS version detection possibly not available")
	return 0

def detect(pluginlist,themelist,hosti,pathi,porti,securei,plugouti,wpouti,themeouti,opt):
	global host
	host = hosti
	global port
	port = porti
	global secure
	secure = securei
	global path
	path = pathi
	global plugout
	plugout = plugouti
	global wpout
	wpout = wpouti
	global themeout
	themeout = themeouti
	
	if (opt == 1 or opt == 4 or opt == 5 or opt == 7):
		print("Starting plugin version scanner")
		for plugin in pluginlist:
			plugin = str(plugin.strip("\n"))
			while (pluginDetect(plugin) != 0):	sleep(1)
	if (opt == 2 or opt == 4 or opt >= 6):
		print("Starting theme version scanner")
		for theme in themelist:
			theme = str(theme.strip("\n"))
			while (themeDetect(theme) != 0):	sleep(1)
	if (opt == 3 or opt >= 5):
		print("Starting WordPress version scanner")
		while (wordpressDetect() !=  0):	sleep(1)	
