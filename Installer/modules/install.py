import os
import shutil
import subprocess

from zipfile import ZipFile

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

def install_modules():
    path=os.environ['MODULES_PATH']
    zim=0
    zip=0

    isExist = os.path.exists(path)

    if(isExist):
        print("Installing custom modules")
        dir_list= os.listdir(path)

        print("Modules to install:", path)
        for x in dir_list:
            target="%s/%s"%(path,x)
            if x.endswith(".zip"):
                # Prints only text file present in My Folder
                with ZipFile(target, 'r') as zipObj:
                    print("Extracting: %s " % x)
                    zipObj.extractall('/var/www/modules')
                    zip+=1
                    # print(x)
            if x.endswith(".zim"):
                shutil.copyfile(target,'/var/www/modules/%s'%x)
                zim+=1
                
                
        modules_list=os.listdir('/var/www/modules')
        print("%s zip files added, %s zim files added "%(zip,zim))
        print(modules_list)
        if(zim>0 or zip>0):
            print('run --sync')
            cmd('/usr/bin/python3 /var/kiwix/bin/rachel_kiwix.py --sync')
            cmd('/etc/init.d/apache2 reload')
            
            
    else:
        print("volume %s not found, no modules will be installed"%  path)

def main():
    install_modules()
if __name__=="__main__":
    main()