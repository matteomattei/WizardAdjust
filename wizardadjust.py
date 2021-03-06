#!/usr/bin/env python2

import sys, os, datetime, re, csv
if sys.version_info < (3,0):
	import Tkinter as tkinter
	import tkMessageBox as mbox
else:
	import tkinter
	import tkinter.messagebox as mbox

def isStandard(elem, std, standards):
	"""Check if an element is a standard"""
	for s in standards:
		if s[0]==std and s[1]==elem:
			if DEBUG: print('std_elem=%s elem=%s std_std=%s std_item=%s' % (s[0],elem,s[1],std))
			return (True,s[2])
	return (False,False)

def copyfile(file1,file2):
	"""Copy file1 in file2"""
	f = open(file1,'rb')
	buf = f.read()
	f.close()
	f = open(dest,'wb')
	f.write(buf)
	f.close()

def replacechar(mylist,search,rep):
	"""Replace search character in every item of mylist with rep character"""
	pattern = re.compile('^[0-9.eE-]+$')
	l = []
	for i in mylist:
		if pattern.search(i)!=None:
			l.append(i.replace(search,rep))
		else:
			l.append(i)
	return l

DESTINATION_DIR = ''
STANDARD_FILE = ''
if sys.platform=='win32':
	DESTINATION_DIR = os.path.join(os.environ['USERPROFILE'], 'WizardAdjust','results')
	STANDARD_FILE = os.path.join(os.environ['USERPROFILE'], 'WizardAdjust','defstd.txt')
elif sys.platform.startswith('linux'):
	DESTINATION_DIR = '/tmp/results'
	STANDARD_FILE = os.path.join(os.getcwd(),'defstd.txt')

### This is necessary to hide background TK box ###
window = tkinter.Tk()
window.wm_withdraw()
###################################################

DEBUG=False

# PRELIMINARY CHECKS
if len(sys.argv)==1:
	mbox.showinfo(title="WizardAdjust Error", message="Please provide a Wizard generated file.")
	sys.exit(1)

if not os.path.isfile(sys.argv[1]):
	mbox.showinfo(title="WizardAdjust Error", message='The provideded Wizard generated file does not exists: '+sys.argv[1])
	sys.exit(1)

if not os.path.isfile(STANDARD_FILE):
	mbox.showinfo(title="WizardAdjust Error", message='Standard file is not present at '+STANDARD_FILE)
	sys.exit(1)

# CREATE DESTINATION DIRECTORY IF NOT EXISTS
if not os.path.exists(DESTINATION_DIR):
	os.makedirs(DESTINATION_DIR)

# COPY ORIGINAL FILE
now = datetime.datetime.now()
filename = now.strftime('%Y-%m-%d_%H%M%S')+'_'+os.path.basename(sys.argv[1])
dest = os.path.join(DESTINATION_DIR,filename)
copyfile(os.path.normpath(sys.argv[1]),dest)

f = open(dest,'r')
l = f.readlines()
f.close()

# ELEMENT
element = l[0].strip()
if DEBUG: print(element)

# GENERATED FILE
pattern = re.compile('^UNK[0-9]+-AV')
lines = []
for i in l:
	if pattern.search(i)!=None:
		lines.append(i.strip().split('\t'))

# STANDARD FILE
standards = []
try:
	f = open(STANDARD_FILE,'r')
	reader = csv.reader(f, delimiter=';')
	for i in reader:
		if len(i)==0: continue
		standards.append(i)
	f.close()
except:
	mbox.showinfo(title="WizardAdjust Error", message='Malformed standard file '+STANDARD_FILE)
	sys.exit(1)

# COMPUTATION
filename = filename.strip('.txt')+'.csv'
dest_file = os.path.join(DESTINATION_DIR,filename)
if sys.version_info >= (3,0,0):
	f = open(dest_file, 'w', newline='')
else:
	f = open(dest_file, 'wb')
writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
header = ['Action','Sample ID','True value(mg/l)','Conc (mg/lt)','Abs.','DF','SG#','Date','Time','Actual conc(mg/l)']
writer.writerow(header)
conc_std = 0
ass_std = 0
dil_std = 0
for line in lines:
	if DEBUG: print(line)
	std = isStandard(element, line[1], standards)
	if std[0]==True:
		conc_std = float(std[1])
		ass_std = float(line[4])
		dil_std = float(line[5])
		line.append(str(conc_std))
		line = replacechar(line,'.',',')
		writer.writerow(line)
		continue
	if ass_std == 0 or dil_std == 0:
		line.append(str(conc_std))
		line = replacechar(line,'.',',')
		writer.writerow(line)
		continue
	if DEBUG: print('((conc_std=%d * ass=%d) / ass_std=%d) * (dil=%d / dil_std=%d)' % (conc_std, float(line[4]), ass_std, float(line[5]), dil_std))
	conc = (conc_std * float(line[4]) / ass_std) * (float(line[5]) / dil_std)
	line.append(str(conc))
	line = replacechar(line,'.',',')
	writer.writerow(line)
f.close()

