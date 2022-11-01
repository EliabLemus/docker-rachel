#!/usr/bin/env python

import sys
import os
import subprocess
import argparse
import psutil
import glob
import sqlite3
import pathlib
from sqlite3 import Error

def cmd(c):
    result = subprocess.Popen(c,
                              shell=True,
                              stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              close_fds=True)
    try:
        result.communicate()
    except KeyboardInterrupt:
        pass
    return (result.returncode == 0)

def die(err):
    print ("ERROR: " + err)
    sys.exit(1)

def success(msg):
    print (msg)
    sys.exit(0)

def path_exists(path):
    return os.path.isfile(path) or os.path.isdir(path)

def log(msg):
    print(msg)

def sudo(s):
    if not cmd("sudo DEBIAN_FRONTEND=noninteractive %s" % s):
       die(s + " command failed")

def db_connect(db_path):
    db = None

    if(path_exists(db_path)):
        try:
            db = sqlite3.connect(db_path)
        except Error as e:
            log(e)
    else:
        log("admin database does not exist.")

    return db

def getHidden():
    log("Getting hidden modules")
    db_path = "/var/www/admin/admin.sqlite"
    db      = db_connect(db_path)

    if db is None:
        return db

    cur = db.cursor()
    cur.execute('SELECT moddir FROM modules WHERE hidden = 1')
    res = cur.fetchall()
    data=[]

    for row in res:
        data.append(row[0])

    return data

def removeHidden(zims,hidden):
    for dir in hidden:
        for z in zims:
            if dir in z:
                log("Removing hidden zim " + z)
                zims.remove(z)

    return zims

def do_startKiwix():

    library = '/var/kiwix/library.xml'

    if not path_exists(library):
        log(library + " does not exist.")
        library = '/var/kiwix/sample-library.xml'
        log("Starting kiwix with sample library.")

    rv = subprocess.call(['/var/kiwix/bin/kiwix-serve',
                     '--port=81',
					 '--library',
					 library], shell=False)
    if rv == 0:
        success("Successfully started kiwix-serve with " + library)
    else:
        success("Failed to start kiwix-serve with " + library)

def do_stopKiwix():
    wasRunning = False

    for process in psutil.process_iter():
        if process.name() == 'kiwix-serve':
            log("Killing kiwix-serve process")
            process.kill()
            wasRunning = True

    return wasRunning

def stop():
    do_stopKiwix()
    success("Kiwix has been stopped")

def start():
    do_stopKiwix()
    buildLibrary()
    do_startKiwix()

def getZims(path):
    log("Searching for zims")
    pat  = glob.iglob(path, recursive=True)
    zims = list(pat)

    for zim in zims:
        suffix = pathlib.Path(zim).suffix
        if suffix == ".idx":
            zims.remove(zim)
            continue

    return zims
    
def getIndex(zim):
    path = os.path.dirname(zim) 
    path = os.path.dirname(path) + "/index/*.idx*"  
    pat  = glob.iglob(path, recursive=True)
    idxs = list(pat)

    for i in idxs:
        suffix = pathlib.Path(i).suffix
        
        if suffix == ".idx":
            return i;
            
    log("No index file found")
    return ""

def buildLibrary():
    web_root   = "/var/www/"
    mod_path   = web_root + "modules"
    usb_path   = web_root + "USB"
    kiwix_path = "/var/kiwix/"
    lib_path   = kiwix_path + "library.xml"
    man_path   = kiwix_path + "bin/kiwix-manage"

    if(path_exists(lib_path)):
        log("Deleting " + lib_path)
        os.remove(lib_path)

    hidden = getHidden()
    zims   = getZims(web_root + '**/*.zim*')

    if zims != None and hidden != None:
        zims = removeHidden(zims, hidden)

    if zims == None or len(zims) is 0:
        log("No zims were found")
        return

    for z in zims:
        log("Adding " + z + " to the library")
        index_path = ""
        index = getIndex(z)

        if index != "":
            if path_exists(index):
                log("Using index " + index)
                index_path = "--indexPath=" + index
            
        sudo(man_path + " " + lib_path + " add " + z + " " + index_path)

    log("Finished building the Kiwix Library")

def sync():
    wasRunning = do_stopKiwix()
    buildLibrary()

    if wasRunning:
        do_startKiwix()
    else:
        success("Sync completed")

def parse_args():
    global args
    parser  = argparse.ArgumentParser()
    ks_args = parser.add_argument_group(description='kiwix-serve Options')
    ks_args.add_argument('--start',
                          action='store_true',
                          dest='start',
                          help='Start kiwix-serve with library.xml.')
    ks_args.add_argument('--stop',
                          action='store_true',
                          dest='stop',
                          help='Stop all kiwix-serve processes.')
    ks_args.add_argument('--restart',
                          action='store_true',
                          dest='restart',
                          help='Restart kiwix-serve.')
    ks_args.add_argument('--sync',
                          action='store_true',
                          dest='sync',
                          help='Sync the library and restart if was running.')
    args = parser.parse_args()

def main():
    parse_args()

    if args.start:
        start()

    if args.stop:
        stop()

    if args.restart:
        start()

    if args.sync:
        sync()

if __name__== "__main__":
  main()
