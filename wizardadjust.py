#!/usr/bin/env python

import sys, os, datetime, shutil, re, csv

DESTINATION_DIR = '/tmp/generated'
STANDARD_FILE = '/home/matteo/GIT/WizardAdjust/defstd.csv'
DEBUG=False

def isStandard(elem, std, standards):
    for s in standards:
        if s[0]==std and s[1]==elem:
            if DEBUG: print('std_elem=%s elem=%s std_std=%s std_item=%s' % (s[0],elem,s[1],std))
            return (True,s[2])
    return (False,False)

# PRELIMINARY CHECKS
if len(sys.argv)<1:
    print('Please provide a Wizard generated file.')
    sys.exit(0)

if not os.path.isfile(sys.argv[1]):
    print('The provideded Wizard generated file does not exists: '+sys.argv[1])
    sys.exit(1)

if not os.path.isfile(STANDARD_FILE):
    print('Standard file is not present at '+STANDARD_FILE)
    sys.exit(1)

# COPY ORIGINAL FILE
now = datetime.datetime.now()
filename = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'_'+str(now.hour)+':'+str(now.minute)+':'+str(now.second)+'_'+os.path.basename(sys.argv[1])
dest = os.path.join(DESTINATION_DIR,filename)
shutil.copy2(sys.argv[1],dest)

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
f = open(STANDARD_FILE,'r')
reader = csv.reader(f, delimiter=',')
for i in reader:
    standards.append(i)
f.close()

# COMPUTATION
filename = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'_'+str(now.hour)+':'+str(now.minute)+':'+str(now.second)+'_RES_'+element+'.csv'
dest_file = os.path.join(DESTINATION_DIR,filename)
if sys.version_info >= (3,0,0):
    f = open(dest_file, 'w', newline='')
else:
    f = open(dest_file, 'wb')
f = open(dest_file,'w')
writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
conc_std = 0
ass_std = 0
dil_std = 0
for line in lines:
    std = isStandard(element, line[1], standards)
    if std[0]==True:
        conc_std = float(std[1])
        ass_std = float(line[4])
        dil_std = float(line[5])
        writer.writerow(line)
        continue
    if DEBUG: print('((conc_std=%d * ass=%d) / ass_std=%d) * (dil=%d / dil_std=%d)' % (conc_std, float(line[4]), ass_std, float(line[5]), dil_std))
    conc = (conc_std * float(line[4]) / ass_std) * (float(line[5]) / dil_std)
    line[4] = conc
    writer.writerow(line)
f.close()
