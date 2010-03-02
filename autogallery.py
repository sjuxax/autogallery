#!/usr/bin/env python
# -*- coding: utf-8 -*-

# autogallery.py -- a simple script for automatically generating photo galleries
# author: Jeff Cook <jeff@deserettechnology.com>
# offered under the MIT license

import os, sys, getopt #for path navigation and argument handling
import Image #for thumbnailing, Python Image Library
import zipfile, tarfile #for archive reading/writing
import ConfigParser #for parsing config file

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["rex", "regen", "regenall"])
except getopt.GetoptError, e:
    print "Argument error:    ", e
    print " Use --rex to re-extract support files."
    sys.exit(2)

rex, regen = 0, 0

for opt, arg in opts:
    if opt in ("--rex"):
        rex = 1
    if opt in ("--regen"):
        regen = 1
    if opt in ("--regenall"):
        rex = 1
        regen = 1

if os.path.isfile('supportfiles/template.html') == 0 or rex == 1:
    print "extracting supporting files ..."
    support = tarfile.open('supportfiles.tar.bz2', 'r:bz2')
    support.extractall()
    support.close()
else:
    print "seems files have been extracted already, use --rex to unpack anyway and overwrite"


pwd = os.getcwdu()
dircontents = os.listdir(pwd)

images = []

config = ConfigParser.ConfigParser()
config.readfp(open('supportfiles/config.cfg'))

filetypes = config.get('autogallery', 'filetypes')
filetypes = [element.strip() for element in filetypes.split(',')]
filetypes = tuple(filetypes)

print "finding images in directory ..."
for item in dircontents:
    for filetype in filetypes:
        if item.find(filetype) != -1:
            images.append(item)
        else:
            pass

print "checking for zip file..."

if os.path.isfile('images.zip') == 0 or regen == 1:
    print "zip not found, creating"    
    zippy = zipfile.ZipFile('images.zip', 'w')
    for image in images:
        zippy.write(image.encode('CP437'))
    zippy.close()
    print "zip created"
else:
    print "zip exists, not recreating"

zipfilesize = os.path.getsize('images.zip')

ziplinks = '<a href="images.zip">zipfile</a> ('+ str(zipfilesize/1024/1024) +' MB)'

print "creating thumbs dir ..."

thumbsdir = str(pwd + '/' + 'thumbs')
try:
    os.mkdir(thumbsdir)
except OSError, e:
    if e.errno == 17:
        print "\nthumbs directory already exists\n"
    else:
        raise

size = int(config.get('autogallery', 'max-x')), int(config.get('autogallery', 'max-y'))

for image in images:
    if os.path.isfile(pwd + '/thumbs/' + 's_' + image) == 0 or regen == 1:
        print "creating image thumbnail for " + image + " ... \t"
        im = Image.open(pwd + '/' + image)
        im.thumbnail(size)
        im.save(pwd + '/thumbs/' + 's_' + image, "JPEG")
    else:
        print "thumb exists for " + image + ", not rebuilding"

dirnamelist = pwd.split('/')
dirname = dirnamelist[-1]

imagelinks = ''
nofxlinks = ''

for image in images:
    imagelinks += config.get('autogallery', 'imagefxlink', vars={'image': image, 'dirname': dirname}) + "\n\t\t"
#    imagelinks += '<a href="' + image + '" rel="prettyPhoto['+ dirname +']" title="'+ image +'"><img src="thumbs/s_'+ image +'" /></a>'

title = config.get('autogallery', 'title', vars={'dirname': dirname})
fxtags = config.get('autogallery', 'fxtags')

print "opening and writing files ..."

template = open('supportfiles/template.html', 'r') #open template file
index = open('index.html', 'w') #open index file

templatecontents = template.read()

templatecontents = templatecontents.replace('{DIRNAME}', title)
templatecontents = templatecontents.replace('{ZIPS}', ziplinks)

buildnofx = config.get('autogallery', 'buildnofx')

if buildnofx == "1":
    for image in images:
        nofxlinks += config.get('autogallery', 'imagenofxlink', vars={'image': image, 'dirname': dirname}) + "\n\t\t"

    nofx = open('nofx.html', 'w') #open effectless index file

    nofxcontents = templatecontents.replace('{FXTAGS}', fxtags)
    nofxcontents = nofxcontents.replace('{IMAGECODE}', nofxlinks)
    nofx.write(nofxcontents)
    nofx.close()

templatecontents = templatecontents.replace('{FXTAGS}', fxtags)
templatecontents = templatecontents.replace('{IMAGECODE}', imagelinks)
index.write(templatecontents)
index.close()