#!/usr/bin/env python

import sys
import os
import subprocess
import shutil
import urllib
import fileinput
import apt
import platform
import argparse
import dbus
from datetime import datetime

def basedir():
    path = os.path.dirname(os.path.abspath(sys.argv[0]))

    if not path:
        path = "."

    return path

def cmd(c):
    print('cmd ' + c)
    result = subprocess.Popen(c,
                              shell=True,
                              stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              close_fds=True)
    try:
        result.communicate()
    except KeyboardInterrupt:
        pass
    print('resunt.returncode: %s', result.returncode)
    return (result.returncode == 0)
    

def copy_file(src, dst):
    path = os.path.join(basedir(), src)

    if not os.path.isfile(path):
        die("Copy failed. Source " + path + "doesn't exist.")

    if not os.path.isdir(os.path.dirname(dst)):
        die("Copy failed destination folder " +
            os.path.dirname(dst) + " doesn't exist.")

    sudo("cp {0} {1}".format(path,dst))
    log("Copied {0} to {1}.".format(path, dst))

def copy_folder(src, dst):
    path = os.path.join(basedir(), src)

    if not os.path.isdir(path):
        die("Copy failed. Source folder " + path + " doesn't exist.")

    sudo("cp -Rf {0}/. {1}".format(path,dst))
    log("Copied directory {0} to {1}".format(path,dst))

def die(err):
    print("ERROR: " + err)
    sys.exit(1)

def path_exists(path):
    return os.path.isfile(path) or os.path.isdir(path)

def log(msg):
    print("RACHEL: " + msg)

def sudo(s):
    if not cmd("sudo %s" % s):
       die(s + " command failed")

def install(s):
    sudo("DEBIAN_FRONTEND=noninteractive apt-get -y install " + s)

def install_webserver():
    log("Installing Web Server.")
    log("Installing apache2")
    install("apache2")
    install("libxml2-dev")
    log("Finished installing apache2")
    log("Installing PHP")
    
    # Install the latest php version
    install("php")

    if not path_exists("/etc/php"):
        die("PHP not installed correctly")
        
    if not path_exists("/usr/lib/php"):
        die("PHP not installed correctly")

    usr_dirs    = os.listdir("/usr/lib/php")
    
    for path in os.listdir("/etc/php"):
        if not os.path.isdir(os.path.join("/etc/php", path)):
            continue

        log("Found /etc/php dir " + path)
        
        if path in usr_dirs:
            log("PHP directory version match found")
            php_version = path
            break      
    
    if php_version == "":
        log("Failed to get PHP version")
        log("Setting PHP version to args default")
        php_version = args.php_version       
        
    log("Using PHP version " + php_version)
    log("Checking PHP version package availability")
    package_name = "php" + php_version
    
    # search for the new package 
    sub_php = subprocess.Popen(['apt-cache', 'search', package_name], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.STDOUT)
    stdout,stderr = sub_php.communicate()
    sub_out = stdout.decode("utf-8")
    
    if not sub_out:
         log(package_name + " package was not found in apt repository")    

    log(package_name + " package found in apt-cache search")  
    install("php" + php_version)
    install("php" + php_version + "-common")
    install("php" + php_version + "-cgi")
    install("php" + php_version + "-dev")
    install("php" + php_version + "-mbstring")
    install("php" + php_version + "-sqlite3")
    install("libapache2-mod-php" + php_version)
    log("Getting PHP extension directory")
    out = subprocess.Popen(['php-config', '--extension-dir'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    extension_dir = stdout.decode("utf-8")
    
    if not extension_dir:
        die("No PHP extension dir found")
        
    log("Found PHP extension directory at " + extension_dir)
    copy_file("files/rachel/stem.so", extension_dir)
    sudo("sh -c 'echo \'extension=stem.so\' >> /etc/php/" + php_version + "/cli/php.ini'")
    sudo("sh -c 'echo \'extension=stem.so\' >> /etc/php/" + php_version + "/apache2/php.ini'")
    sudo("sh -c 'sed -i \"s/upload_max_filesize *= *.*/upload_max_filesize = 512M/\" /etc/php/" + php_version + "/apache2/php.ini'")
    sudo("sh -c 'sed -i \"s/post_max_size *= *.*/post_max_size = 512M/\" \
    /etc/php/" + php_version + "/apache2/php.ini'")
    sudo("service apache2 stop")
    copy_file("files/apache2/apache2.conf", "/etc/apache2/apache2.conf")
    copy_file("files/apache2/contentshell.conf", "/etc/apache2/sites-available/contentshell.conf")
    sudo("a2dissite 000-default")
    sudo("a2ensite contentshell.conf")
    sudo("a2enmod php" + php_version + " proxy proxy_html rewrite")

    if path_exists("/etc/apache2/mods-available/xml2enc.load"):
        sudo("a2enmod xml2enc")

    sudo("service apache2 restart")
    sudo("apt-get clean")
    log("Web Server has been successfully installed.")

def install_content():
    log("Installing content.")

    log("Fixing common interface names")   
    common_file = basedir() + "/files/contentshell/admin/common.php"

    # with open(common_file, "r") as common_read:
    #     lines = common_read.readlines()

    # for index, line in enumerate(lines):
    #     if "#LAN_REPLACE" in line:
    #         lan_line     = "        $lan_iface  = '" + args.lan_iface + "';\n"
    #         lines[index] = lan_line
    #     if "#WIFI_REPLACE" in line:
    #         if args.wifi_hotspot:
    #             wifi_line = "        $wifi_iface = '" + args.wifi_iface + "';\n"
    #             lines[index] = wifi_line
        
    # with open(common_file, "w") as common_write:
    #     common_write.writelines(lines)
            
    log("Finished fixing common interface names")
    log("Copying content shell to system")
    # sudo("rm -rf /tmp/rachel_installer")
    sudo("rm -rf /var/www")
    sudo("mkdir /var/www")
    copy_folder(basedir() + "/files/contentshell", "/var/www")
    sudo("chown -R www-data:www-data /var/www")
    sudo("usermod -a -G adm www-data")
    # sudo("chmod 777 /var/www/modules/en-file_share/uploads/")    
    log("Finished copying content shell to system")
    log("Content has been sucessfully installed.")

def create_school_id():
    log("Writing School ID file")
    id_file = open("/etc/school-id", "w")
    id_file.write(args.school_id)
    id_file.close()
    log("Finished creating School ID file")

def install_networking():
    install_networking_packages()
    setup_network_files()
    
    if args.wifi_hotspot:
        install_nm_hotspot()

def install_networking_packages():
    log("Installing packages")
    sudo("apt-get remove dnsmasq-base -y")
    install("net-tools")
    install("dnsmasq")
    install("dhcpcd5")	
    sudo("sh -c 'echo DNSStubListener=no >> /etc/systemd/resolved.conf'")
    sudo("update-rc.d dnsmasq enable")
    sudo("systemctl restart systemd-resolved")
    log("Networking packages successfully installed.")

def setup_network_files():
    log("Setting up config files")
    sudo("systemctl stop dnsmasq")
    sudo("systemctl stop dhcpcd")
    subnet     = "255.255.255.0"
    wifi_ip    = "10.10.10.10"
    wifi_start = "10.10.10.100"
    wifi_end   = "10.10.10.199"    
    log("Configuring dhcpcd.conf")

    if path_exists("/etc/dhcpcd.conf"):
        copy_file("/etc/dhcpcd.conf", "/etc/dhcpcd.conf.bak")

    # Note: Might need major refactoring for memory efficiency, etc
    with open("/etc/dhcpcd.conf", "r") as f:
        lines = f.readlines()

    with open("/etc/dhcpcd.conf", "w") as dhcpcd:   
        for line in lines:
            if line.lstrip().startswith("#"):
                dhcpcd.write(line)
                continue
            if "interface " in line:
                log("Removing interface line.")
                continue
            if "static ip_address" in line:
                log("Removing static ip_address line")
                continue     
          
            dhcpcd.write(line)
        
        if args.wifi_hotspot:
            wifi_line1 = "interface " + args.wifi_iface + "\n"
            wifi_line2 = "static ip_address=" + wifi_ip + "/24\n"    
            dhcpcd.write(wifi_line1)
            dhcpcd.write(wifi_line2)
            
    log("Finished configuring dnsmasq.conf")
    log("Configuring dnsmasq.conf")

    if path_exists("/etc/dnsmasq.conf"):
        copy_file("/etc/dnsmasq.conf", "/etc/dnsmasq.conf.bak")

    with open("/etc/dnsmasq.conf", "r") as f:
        lines = f.readlines()

    with open("/etc/dnsmasq.conf", "w") as dnsmasq: 
        for line in lines:
            if line.lstrip().startswith("#"):
                dnsmasq.write(line)
                continue
            if "interface=" in line:
                log("Removing interface line.")
                continue
            if "dhcp-range=" in line:
                log("Removing dhcp-range line.")
                continue
            if "address=/" in line:
                log("Removing address= line")
                continue
          
            dnsmasq.write(line)
        
        if args.wifi_hotspot:
            wifi_line1 = "interface=" + args.wifi_iface + "\n"
            wifi_line2 = "dhcp-range=" + wifi_start + "," + wifi_end + "," + subnet + ",24h\n"    
            dnsmasq.write(wifi_line1)
            dnsmasq.write(wifi_line2)
            
            if args.homepage:
                wifi_line3 = "address=/" + args.homepage + "/" + wifi_ip + "\n"
                dnsmasq.write(wifi_line3)                       
      
    log("Finished configuring dnsmasq.conf")      
    log("Configuring /etc/hosts")

    if path_exists("/etc/hosts"):
        copy_file("/etc/hosts", "/etc/hosts.bak")
    
    with open("/etc/hosts", "r") as f:
        lines = f.readlines()
        
    with open("/etc/hosts", "w") as hosts: 
        for line in lines:
            if line.lstrip().startswith("#"):
                hosts.write(line)
                continue
            if wifi_ip in line:
                log("Removing wifi static ip line.")
                continue   
          
            hosts.write(line)
                   
        if args.wifi_hotspot:
            wifi_line = wifi_ip + " rachel\n"
            hosts.write(wifi_line)
    
    log("Finished configuring /etc/hosts")
    sudo("systemctl start dhcpcd")
    sudo("systemctl start dnsmasq")
    log("Finished setting up config files")

def install_nm_hotspot():
    log("Installing Hotspot.")

    # UUID provided from first install by andrewc
    uuid = "e973b865-9ee8-4a73-a7ad-a9f1100a9605"

    # Connection dbus dictionary 
    wifi_con = dbus.Dictionary({ 
        "type": "802-11-wireless", 
        "uuid": uuid, 
        "id": "RACHEL",
        "autoconnect": dbus.Boolean(True)})

    # Connection wifi settings
    s_wifi = dbus.Dictionary({
        "ssid": dbus.ByteArray(args.wifi_ssid.encode("utf-8")),
        "mode": "ap"})
        
    addr1 = dbus.Dictionary({"address": "10.10.10.10", "prefix": dbus.UInt32(24), "gateway" : "10.10.10.10"})

    s_ip4 = dbus.Dictionary({
        "address-data": dbus.Array([addr1], signature=dbus.Signature("a{sv}")),
        "gateway": "10.10.10.10",
        "method": "shared"})

    s_ip6  = dbus.Dictionary({"method": "shared"})

    con = dbus.Dictionary({
        "connection": wifi_con,
        "802-11-wireless": s_wifi,
        "ipv4": s_ip4,
        "ipv6": s_ip6})

    bus          = dbus.SystemBus()
    service_name = "org.freedesktop.NetworkManager"
    proxy        = bus.get_object(service_name, 
                                  "/org/freedesktop/NetworkManager/Settings")
    settings     = dbus.Interface(proxy, "org.freedesktop.NetworkManager.Settings")
    proxy        = bus.get_object(service_name, "/org/freedesktop/NetworkManager")
    nm           = dbus.Interface(proxy, "org.freedesktop.NetworkManager")
    devpath      = nm.GetDeviceByIpIface(args.wifi_iface)
    con_path     = settings.AddConnection(con)
    proxy        = bus.get_object(service_name, devpath)
    device       = dbus.Interface(proxy, "org.freedesktop.NetworkManager.Device")
    acpath       = nm.ActivateConnection(con_path, devpath, "/")
    proxy        = bus.get_object(service_name, acpath)
    
    # Ip forwarding configuration 
    copy_file("files/networking/sysctl.conf", "/etc/sysctl.conf")
    sudo("sysctl -w net.ipv4.ip_forward=1")
    sudo("iptables -t nat -A POSTROUTING -o " + args.lan_iface + " -j MASQUERADE")
    sudo("iptables -A FORWARD -i " + args.wifi_iface + " -o " + args.lan_iface + " -j ACCEPT")
    sudo("iptables -A FORWARD -i " + args.lan_iface + " -o " + args.wifi_iface + " -m state --state RELATED,ESTABLISHED -j ACCEPT")
    sudo("sh -c 'iptables-save > /etc/iptables.ipv4.nat'")

    if path_exists("/etc/rc.local"):
        sudo("sh -c 'sed -i \"s/^exit 0//\" /etc/rc.local'")
        sudo("sh -c 'echo iptables-restore \< /etc/iptables.ipv4.nat >> /etc/rc.local'")
        sudo("sh -c 'echo exit 0 >> /etc/rc.local'")
    else:
       copy_file("files/rachel/rc.local", "/etc/rc.local")
    
    copy_file("files/networking/hostname", "/etc/hostname")
    
def install_kiwix():
    log("Installing Kiwix")
    # install('python3-psutil')
    sudo("mkdir -p /var/kiwix/bin")
    kiwix_version = "3.1.2"
    url   = "https://download.kiwix.org/release/kiwix-tools/"
    # tools = "kiwix-tools_linux-x86_64-0.9.0.tar.gz"
    tools = "kiwix-tools_linux-x86_64-3.2.0-5.tar.gz"
    url   = url + tools
    log("Downloading version " + kiwix_version + " of kiwix.")
    sudo("sh -c 'wget -O - " + url + " | tar -xvz --strip 1 -C /var/kiwix/bin'")
    copy_file("files/kiwix/kiwix-sample.zim", "/var/kiwix/sample.zim")
    sudo("chown -R root:root /var/kiwix/bin")
    copy_file("files/kiwix/kiwix-sample-library.xml",
              "/var/kiwix/sample-library.xml")
    copy_file("files/kiwix/rachel_kiwix.py",
              "/var/kiwix/bin/rachel_kiwix.py")
    sudo("chmod +x /var/kiwix/bin/rachel_kiwix.py")
    copy_file("files/kiwix/kiwix", "/etc/init.d/kiwix")
    sudo("chmod +x /etc/init.d/kiwix")
    sudo("update-rc.d kiwix defaults")
    # sudo("service kiwix start")
    sudo("sh -c 'echo " + kiwix_version + " >/etc/kiwix-version'")
    log("Kiwix has been successfully installed.")

def install_kiwix_deb():
    log("Installing Kiwix")
    # install('python3-psutil')
    sudo("mkdir -p /var/kiwix/bin")
    kiwix_version = "3.1.2"
    url   = "https://download.kiwix.org/release/kiwix-tools/"
    # tools = "kiwix-tools_linux-x86_64-0.9.0.tar.gz"
    tools = "kiwix-tools_linux-armhf-3.2.0-5.tar.gz"
    url   = url + tools
    log("Downloading version " + kiwix_version + " of kiwix.")
    sudo("sh -c 'wget -O - " + url + " | tar -xvz --strip 1 -C /var/kiwix/bin'")
    copy_file("files/kiwix/kiwix-sample.zim", "/var/kiwix/sample.zim")
    sudo("chown -R root:root /var/kiwix/bin")
    copy_file("files/kiwix/kiwix-sample-library.xml",
              "/var/kiwix/sample-library.xml")
    copy_file("files/kiwix/rachel_kiwix.py",
              "/var/kiwix/bin/rachel_kiwix.py")
    sudo("chmod +x /var/kiwix/bin/rachel_kiwix.py")
    copy_file("files/kiwix/kiwix", "/etc/init.d/kiwix")
    sudo("chmod +x /etc/init.d/kiwix")
    sudo("update-rc.d kiwix defaults")
    # sudo("service kiwix start")
    sudo("sh -c 'echo " + kiwix_version + " >/etc/kiwix-version'")
    log("Kiwix has been successfully installed.")

    
def install_kolibri():
    log("Installing Kolibri.")
    install("software-properties-common")
    install("dirmngr")
    sudo("add-apt-repository ppa:learningequality/kolibri-proposed -y")
    sudo("apt-get update")
    sudo("yes no |apt-get install kolibri")
    copy_file("files/kolibri/daemon.conf", "/etc/kolibri/daemon.conf")
    copy_file("files/kolibri/kolibri_initd", "/etc/init.d/kolibri")
    sudo("sh -c 'echo 0.14.3 > /etc/kolibri-version'")
    
    with open("/etc/kolibri/username", "w") as kolibri:
        kolibri.write("root")
    
    sudo("apt-get clean")
    
    log("Kolibri has been successfully installed.")

def install_kolibri_deb():
    log("Installing Kolibri.")
    # sudo("add-apt-repository ppa:learningequality/kolibri-proposed -y")
    install("kolibri")
    copy_file("files/kolibri/daemon.conf", "/etc/kolibri/daemon.conf")
    copy_file("files/kolibri/kolibri_initd", "/etc/init.d/kolibri")
    sudo("sh -c 'echo 0.14.3 > /etc/kolibri-version'")
    
    with open("/etc/kolibri/username", "w") as kolibri:
        kolibri.write("root")
    
    sudo("apt-get clean")
    
    log("Kolibri has been successfully installed.")


def setup_permissions():
    log("Setting up permissions.")
    # copy_file("files/rachel/rachel_sudoers", "/etc/sudoers.d/rachel")
    # sudo("chown root:root /etc/sudoers.d/rachel")
    # sudo("chmod 0440 /etc/sudoers.d/rachel")
    # log("Successfully set up permissions.")

def setup_rachel():
    log("Finalizing RACHEL Settings") 
    log("Creating RACHEL version file")
    
    if path_exists('/etc/rachel-version'):
        os.remove('/etc/rachel-version')
        
    with open('/etc/rachel-version', 'w') as file:
        file.write(str(datetime.now()))
        
    log("Finished writing RACHEL version file")        
    log("Setting up RACHEL PID path")
    copy_file("files/rachel/rc.local", "/etc/rc.local")
    sudo("chmod 755 /etc/rc.local")
    log("Finished setting up RACHEL PID.")        
    log("Rachel has been successfully installed.")
    sys.exit(0)

def check_args():
    log("Checking arguments")
    
    # if not args.lan_iface: 
    #     die("No LAN interface provided. A LAN interface is required for this installation")
    
    if not args.school_id:
        die("No School ID provided. A School ID is required for this installation")
    
    # Check  school-id is a number in range of 0-255
    school_id = int(args.school_id)

    if not school_id in range(0,255):
        die("The School ID provided, " + args.school_id + " is not a valid number in the range of 0-255")

    iface_names = os.listdir('/sys/class/net/')
    
    # Check that the provided ethernet interface exists    
    en_exists = False
    
    # for iface in iface_names:
    #     if args.lan_iface in iface:
    #         en_exists = True

    # if not en_exists:
    #     die("The provided LAN interface " + args.lan_iface + " does not exist")

    # if args.wifi_hotspot:
    #     if not args.wifi_iface:
    #         die("No WIFI interface provided. A WIFI interface is required when hotspot installation is selected")

        # Check wifi channel is in 0-11 range 
        # wifi_channel = int(args.wifi_channel)

        # if not wifi_channel in range(0,11):
        #     die("The WIFI channel provided, " + wifi_channel + " is not a number in the valid range of 0-11")   

        # # Check that the provided wifi interface exists        
        # wl_exists = False
    
        # for iface in iface_names:
        #     if args.wifi_iface in iface:
        #         wl_exists = True    

        # if not wl_exists:
        #     die("The provided WIFI interface " + args.wifi_iface + " could not be found") 

        # # Check that the provided SSID isn't empty
        # if len(args.wifi_ssid) == 0:
        #     die("The provided SSID is empty")

    log("Finished checking arguments")

def parse_args():
    log("Parsing command line arguments")
    global args
    parser   = argparse.ArgumentParser()
    service_args = parser.add_argument_group(description='Service Options')    
    service_args.add_argument('--kiwix',
                         action='store_true',
                         help='Install Kiwix',
                         dest='kiwix')
    service_args.add_argument('--kiwix_deb',
                        action='store_true',
                        help='Install Kiwix',
                        dest='kiwix_deb')
    service_args.add_argument('--kolibri',
                         action='store_true',
                         help='Install Kolibri',
                         dest='kolibri')
    service_args.add_argument('--kolibri_deb',
                         action='store_true',
                         help='Install Kolibri Debian',
                         dest='kolibri_deb')
    service_args.add_argument('--php-version',
                         action='store',
                         default='7.2',
                         help='PHP version to override',
                         dest='php_version')
    net_args = parser.add_argument_group(description='Network Options')   
    net_args.add_argument('--lan-iface',
                         action='store',
                         help='LAN Interface',
                         dest='lan_iface')
    net_args.add_argument('--wifi-hotspot',
                         action='store_true',
                         help='Install a WIFI hotspot',
                         dest='wifi_hotspot')
    net_args.add_argument('--wifi-ssid',
                         action='store',
                         help='WIFI SSID to use',
                         dest='wifi_ssid')
    net_args.add_argument('--wifi-channel',
                         action='store',
                         help='WIFI Channelto use',
                         dest='wifi_channel')                         
    net_args.add_argument('--wifi-iface',
                         action='store',
                         help='WIFI Interface',
                         dest='wifi_iface')                       
    rachel_args = parser.add_argument_group(description='RACHEL Options')
    rachel_args.add_argument('--school-id',
                         action='store',
                         help='School ID.',
                         dest='school_id')
    rachel_args.add_argument('--homepage',
                         action='store',
                         help='RACHEL Homepage Address.',
                         dest='homepage')
    args = parser.parse_args()
    log("Successfully parsed command line arguments.")

def main():
    log("Beginning installation.")
    parse_args()
    check_args()
    setup_permissions()
    create_school_id()
    install_content()
    
    if args.kiwix:
        install_kiwix()
        
    install_webserver()
    
    if args.kolibri:
        install_kolibri()
    
    if args.kolibri_deb:
        install_kolibri_deb()
    # install_networking()
    setup_rachel()

if __name__== "__main__":
  main()
