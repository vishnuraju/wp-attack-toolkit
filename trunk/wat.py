# TODO: timthumb exploit
# TODO: find wp-config backups
# TODO: if backup software, bruteforce backup file
# TODO: cross-reference plugin versions
# TODO: sequential ordering on plugin generation for easy kill times
# each list starts with next value [0,5,10] [1,6,11] [2,7,12] [3,8,13] [4,9,14]
from sys import argv
from os import strerror

def usage(arg,argType):
	print("\n%s" % arg)
	exitvalue = []
	if (argType[0] == "showall"):
		exitvalue.append('''python %s <option>\tDisplay options for specific function
\ngetplugins\tPull new or update plugin list
bruteplugins\tBruteforce plugins from list
getthemes\tPull new or update theme list
brutethemes\tBruteforce themes from list
versiondetect\tDetect plugins and/or WordPress versions
bruteusers\tBruteforce usernames from list
brutepasswords\tBruteforce passwords for single or multiple users
generic\t\tGeneric target options/settings
processing\tSet concurrent processes running at a time\n''' % argv[0])	
	if (argType[0] == "getplugins"):
		exitvalue.append('''Generate Plugin List\tPull new or update plugin list
\tgetplugins\tIf no arguments given, defaults chosen for all of options
\t-page #\tStart of plugin page to start on (default is first)
\t-endpage #\tEnd of plugin pages to finish on (default is max)
\t-pluginlist <filename>\tPlugin list output file (default is lists/plugins.lst)
\t-append\tToggle append mode to append to list instead of write over (default is off)
Example:\tpython %s getplugs <options> <processes>\n''' % argv[0])
	if (argType[0] == "getthemes"):
		exitvalue.append('''Generate Theme List\tPull new or update theme list
\tgetthemes\tIf no arguments given, defaults chosen for all options
\t-page #\tStart of theme page to start on (default is first)
\t-endpage #\tEnd of theme pages to finish on (default is max)
\t-themelist <filename>\Theme list output file (default is lists/themes.lst)
\t-append\tToggle append mode to append to list instead of write over (default is off)
Example:\tpython %s getthemes <options> <processes>\n''' % argv[0])
	if (argType[0] == "bruteplugins"):
		exitvalue.append('''\nBruteforce Plugins
\tbruteplugins\tProvide at least generic options, defaults chosen for rest of options
\t-pluginlist <filename>\tInput for possible plugins (default lists/plugins.lst)
\t-foundplug <filename>\tOutput for found plugins (default output/pluginsfound.lst)
\t-versions\tFind versions for plugins. 0 off, 1 on (default is 0)
Example:\tpython %s bruteplugins <options> <generic> <processes>\n''' % argv[0])
	if (argType[0] == "brutethemes"):
		exitvalue.append('''\nBruteforce Themes
\tbrutethemes\tProvide at least generic options, defaults chosen for rest of options
\t-themelist <filename>\tInput for possible themes (default is lists/themes.lst)
\t-themev <filename>\tOutput for found themes (default is output/themesfound.lst)
\t-versions\tFind versions for themes. 0 off, 1 on (default is 0)
Example:\tpython %s brutethemes <options> <generic> <processes>\n''' % argv[0])
	if (argType[0] == "versiondetect"):
		exitvalue.append('''\nVersion Detection\tDetect plugins and/or WordPress version
\tversiondetect\tProvide at least generic options, defaults chosen for rest
\t-plugv <filename>\tDetect plugin versions from input (default output/pluginsfound.lst)
\t-themev <filename>\tDetect theme versions from input (default is output/themesfound.lst)
\t-opt #\t1 plugins only, 2 themes only, 3 WordPress only, 4 plugins and themes, 5 plugins and WordPress, 6 themes and WordPress, 7 all (default 7)
\t-plugout\tPlugin version output (default output/plugins.version)
\t-themeout\tTheme version output (default output/themes.version)
\t-wpout\tWordPress version output (default output/wordpress.version)
Example:\tpython %s versiondetect <options> <generic> <processes>\n''' % argv[0])
	if (argType[0] == "bruteusers"):
		exitvalue.append('''\nBruteforce Usernames
\tbruteusers\tProvide at least generic options, defaults chosen for rest of options
\t-userlist <filename>\tInput filename for new line seperated usernames (default lists/users.lst)
\t-usersfound <filename>\tOutput filename for any found users (default output/usersfound.lst)
Example:\tpython %s bruteusers <options> <generic> <processes>\n''' % argv[0])
	if (argType[0] == "brutepasswords"):
		exitvalue.append('''\nBruteforce Passwords
\tbrutepasswords\tProvide at least generic options, defaults chosen for rest of options
\t-usersfound <filename>\tInput filename for new line seperated usernames (default output/usersfound.lst)
\t-passlist <filename>\tInput filename for new line seperated passwords (default lists/passwords.lst)
\t-logins <filename>\tOutput for login credentials (default output/logins.lst)
Example:\tpython %s brutepasswords <options> <generic> <processes>\n''' % argv[0])
	if (argType[1] == "generic"):
		exitvalue.append('''\nGeneric Options
\t-host <sample.com> or <www.sample.com> or <ip>\tSet remote host fqdn or ip
\t-dir /path/to/blog/\tGive full path to blog on remote server (default is /)
\t-port #\tProvide port number (default is 80)
\t-ssl\tToggle support for SSL (sets port to 443)
*You can test if these options are right by using python %s <generic>\n''' % argv[0])
	if (argType[0] == "processing"):
		exitvalue.append('''\nMultiple Processing\tWorkload is divided amongst number of concurrent processes
\t-processes #\tAmount of processes to use (default is 10)\n''')
	exit("\n".join(exitvalue[0:]))

# (arg|opt)parse looks pretty, but has data checks we don't need
# ========= arg parsing/setting
troubleshoot = 0 # troubleshoot connection
x = 0 # counter for ags
getplugs = 0
getthemes = 0
bruteuserlist = 0
brutepasswords = 0
brutepluginlist = 0
brutethemes = 0
versiondetect = 0
path = "/" # directory path for server WP
port = 80 # default port number
versiontick = 0 # version detection after bf
secure = 0 # ssl enabled
psize = 10 # pool size (amount of processes concurrently)
append = 0 # append instead of write over
wpout = "output/wordpress.version" # wordpress version
themev = "output/themesfound.lst"
themeout = "output/themes.version" # themes versions
themefound = "lists/themes.lst"
vplug = "output/plugins.version" # plugin version
plugfile = "lists/plugins.lst" # plugin list output
userfile = "lists/users.lst" # user input file
usersfound = "output/usersfound.lst" # users found output file
passlist = "lists/passwords.lst" # password input list
logins = "output/logins.lst" # logins found output file
foundplug = "output/pluginsfound.lst"
if (len(argv) < 2):	usage("Not enough arguments given",["showall",''])
for arg in argv:
	if (str(arg) == "-h"):
		usage('',["showall",''])
	elif (str(arg) == "getplugins"):
		try:	argv[x+1]
		except:	usage("getplugins arguments:",["getplugins",''])
		getplugs = 1
		page = 0
		endpage = 0
	elif (str(arg) == "getthemes"):
		try:	argv[x+1]
		except:	usage("getthemes arguments:",["getthemes",''])
		getthemes = 1
		page = 0
		endpage = 0
	elif (str(arg) == "-append"):
		append = 1
	if (str(arg) == "-page"):
		try:	page = int(argv[x+1])
		except:	usage("-pages not properly set",["getplugins",''])
	elif (str(arg) == "-endpage"):
		try:	endpage = int(argv[x+1])
		except:	usage("-endpages not properly set",["getplugins",''])
	elif (str(arg) == "bruteusers"):
		try:	argv[x+1]
		except:	usage("bruteusers arguments:",["bruteusers","generic"])
		bruteuserlist = 1
	elif (str(arg) == "-userlist"):
		try:	userfile = str(argv[x+1])
		except:	usage("-userlist not properly set",["bruteusers",''])
	elif (str(arg) == "-usersfound"):
		try:	usersfound = str(argv[x+1])
		except:	usage("-usersfound not properly set",["bruteusers",''])
	elif (str(arg) == "brutepasswords"):
		try:	argv[x+1]
		except:	usage("brutepasswords arguments:",["brutepasswords","generic"])
		brutepasswords = 1
	elif (str(arg) == "-passlist"):
		try:	passlist = str(argv[x+1])
		except:	usage("-passlist not properly set",["brutepasswords",''])
	elif (str(arg) == "-logins"):
		try:	logins = str(argv[x+1])
		except:	usage("-logins not properly set",["brutepasswords",''])
	elif (str(arg) == "bruteplugins"):
		opt = 1
		try:	argv[x+1]
		except:	usage("bruteplugins arguments:",["bruteplugins","generic"])
		brutepluginlist = 1
	elif (str(arg) == "-pluginlist"):
		try:	plugfile = str(argv[x+1])
		except:	usage("-pluginlist not properly set",["bruteplugins",''])
	elif (str(arg) == "-foundplug"):
		try:	foundplug = str(argv[x+1])
		except:	usage("-foundplug not properly set",["bruteplugins",''])
	elif (str(arg) == "-versions"):
		try:	versiontick = int(argv[x+1])
		except:	usage("-versions not properly set",["bruteplugins",''])
	elif (str(arg) == "brutethemes"):
		brutethemes = 1
		opt = 2
		try:	argv[x+1]
		except:	usage("brutethemes arguments:",["brutethemes","generic"])
	elif (str(arg) == "-themelist"):
		try:	themefound = str(argv[x+1])
		except:	usage("-themelist not properly set",["brutethemes",''])
	elif (str(arg) == "-themefound"):
		try:	themefound = str(argv[x+1])
		except:	usage("-themefound not properly set",["brutethemes",''])
	elif (str(arg) == "versiondetect"):
		opt = 7
		try:	argv[x+1]
		except:	usage("versiondetect arguments:",["versiondetect","generic"])
		versiondetect = 1
		foundplug = "output/pluginsfound.lst"
	elif (str(arg) == "-opt"):
		try:	opt = int(argv[x+1])
		except:	usage("-opt not properly set",["versiondetect",''])
	elif (str(arg) == "-plugv"):
		try:	foundplug = str(argv[x+1])
		except:	usage("-plugv not properly set",["versiondetect",''])
	elif (str(arg) == "-themev"):
		try:	themev = str(argv[x+1])
		except:	usage("-themev not properly set",["versiondetect",''])
	elif (str(arg) == "-themeout"):
		try:	themeout = str(argv[x+1])
		except:	usage("-themeout not properly set",["versiondetect",''])
	elif (str(arg) == "-wpout"):
		try:	wpout = str(argv[x+1])
		except:	usage("-wpout not properly set",["versiondetect",''])
	elif (str(arg) == "-plugout"):
		try:	vplug = str(argv[x+1])
		except:	usage("-plugout not properly set",["versiondetect",''])
	elif (str(arg) == "generic"):
		try:	argv[x+1]
		except:	usage("Generic options:",['',"generic"])
	elif (str(arg) == "-host"):
		try:	host = str(argv[x+1])
		except: usage("-host not properly set",['',"generic"])
		if (host.find(".") <= 0):	
			usage("-host not properly set",['',"generic"])
	elif (str(arg) == "-dir"):
		try:	path = str(argv[x+1])
		except:	usage("-dir not properly set",['',"generic"])
		if (path.find("/") <= 0):
			usage("-dir path not properly set",['',"generic"])
	elif (str(arg) == "-port"):
		try:	port = int(argv[x+1])
		except:	usage("-port not properly set",['',"generic"])
	elif (str(arg) == "-ssl"):
		secure = 1
		port = 443
	elif (str(arg) == "processing"):
		try:	argv[x+1]
		except:	usage("Processing options:",["processing",''])
	elif (str(arg) == "-processes"):
		try:	psize = int(argv[x+1])
		except:	usage("-processes not properly set",["processing",''])
	x += 1

# =============== Troubleshooting connect options for later
def testArgs(host,path,port,secure):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if (secure == 1):	ssocket = ssl.wrap_socket(s)
	else:	ssocket = s
	connmsg = ssocket.connect_ex((host,port))
	if (connmsg != 0):	exit("Error connecting:\t%s" % strerror(connmsg))
	ssocket.send("HEAD "+path+" HTTP/1.1\r\nHost: "+host+"\r\n\r\n")
	sleep(2)
	chunk = ssocket.recv(400)
	if (chunk.find("200 OK") <= 0):	exit("\nError trying %s%s\n\n%s" % (host,path,chunk))
	else:	print("Connection looks good for %s%s" % (host,path))
	ssocket.close()
		
if (troubleshoot == 1):
	import socket,ssl
	from time import sleep
	testArgs(host,path,port,secure)
if (getplugs == 1):
	from lib import spiderplugins
	if (append != 1):
		try:	plugclear = open(plugfile,'w').close()
		except IOError,e:	usage(("Write denied on file:\t%s" % e),["getplugs",''])
	spiderplugins.spiderman(page,endpage,psize,plugfile)
if (getthemes == 1):
	from lib import spiderthemes
	if (append != 1):
		try:	themeclear = open(themefound,'w').close()
		except IOError,e:	usage(("Write denied on file:\t%s" % e),["getthemes",''])
	spiderthemes.spiderman(page,endpage,psize,themefound)
if (bruteuserlist == 1):
	from lib import bruteusers
	try:	userlist = open(userfile,'r').readlines()
	except IOError,e:	usage(("-userlist not properly set:\t%s" % e),["bruteusers",''])
	try:	open(usersfound,'w').close()
	except IOError,e:	usage(("-usersfound not properly set:\t%s" % e),["bruteusers",''])
	#try:	
	bruteusers.bruteUser(userlist,psize,host,path,port,secure,usersfound)
	#except:	usage("Not enough arguments supplied.",["bruteusers","generic"])
if (brutepluginlist == 1):
	from lib import bruteplugins
	try:	pluginlist = open(plugfile,'r').readlines()
	except IOError,e:	usage(("-pluginlist not properly set:\t%s" % e),["bruteplugins",''])
	try:	open(foundplug,'w').close()
	except IOError,e:	usage(("-foundplug not properly set:\t%s" % e),["bruteplugins",''])
	try:	bruteplugins.brutePlugin(pluginlist,foundplug,host,path,port,secure,psize)
	except:	usage("Not enough arguments supplied",["bruteplugins","generic"])
if (brutethemes == 1):
	from lib import brutethemes
	try:	themes = open(themefound,'r').readlines()
	except IOError,e:	usage(("-themelist not properly set:\t%s" % e),["brutethemes",''])
	try:	open(themev,'w').close()
	except IOError,e:	usage(("-themev not properly set:\t%s" % e),["brutethemes",''])
	try:	brutethemes.bruteThemes(themes,themev,host,path,port,secure,psize)
	except:	usage("Not enough arguments supplied",["brutethemes","generic"])
if (versiondetect == 1 or versiontick == 1):
	from lib import versiondetect
	try:	themes = open(themev,'r').readlines()
	except IOError,e:	usage(("-themelist not properly set:\t%s" % e),["versiondetect",''])
	try:	open(themeout,'w').close()
	except IOError,e:	usage(("-themeout not properly set:\t%s" % e),["versiondetect",''])
	try:	pluginlist = open(foundplug,'r').readlines()
	except IOError,e:	usage(("-foundplug not properly set:\t%s" % e),["versiondetect",''])
	try:	open(wpout,'w').close()
	except IOError,e:	usage(("-wpout not properly set:\t%s" % e),["versiondetect",''])
	try:	open(vplug,'w').close()
	except IOError,e:	usage(("-vout not properly set:\t%s" % e),["versiondetect",''])
	try:	versiondetect.detect(pluginlist,themes,host,path,port,secure,vplug,wpout,themeout,opt)
	except:	usage("Not enough arguments supplied",["versiondetect",''])
if (brutepasswords == 1):
	from lib import brutepasswords
	try:	userlist = open(usersfound,'r').readlines()
	except IOError,e:	usage(("-usersfound not properly set:\t%s" % e),["brutepasswords",''])
	try:	passwords = open(passlist,'r').readlines()
	except IOError,e:	usage(("-passlist not properly set:\t%s" % e),["brutepasswords",''])
	try:	open(logins,'w').close()
	except IOError,e:	usage(("-logins not properly set:\t%s" % e),["brutepasswords",''])
	try:	brutepasswords.brutePasses(userlist,passwords,host,path,port,secure,psize,logins)
	except:	usage("Not enough arguments supplied",["brutepasswords","generic"])	
