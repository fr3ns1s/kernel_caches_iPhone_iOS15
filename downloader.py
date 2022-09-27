import re
import pexpect
import requests
import json
import os,shutil
import sys, getopt


curr_dir = os.path.realpath(os.curdir);
debug = False

def download_fw(filter_versions,filter_devices,dev_kernel):
    
    r = requests.get('https://api.ipsw.me/v4/devices')
    if r.status_code == 200:
       json_devices = json.loads(r.text)
       if json_devices == None or len(json_devices) == 0:
           print("Devices not found!")
           exit(-1)
    if len(filter_devices) >0:
        devices = [x for x in json_devices for xs in filter_devices if xs in x['identifier']]
    else:
        devices = json_devices
    print("Devices found: {0}".format(len(devices)))
    for device in devices:
        r = requests.get('https://api.ipsw.me/v4/device/' + device["identifier"] + '?type=ipsw')
        if r.status_code != 200:
            continue
        json_firmwares = json.loads(r.text)
        if json_firmwares == None or len(json_firmwares["firmwares"]) == 0:
           print("Firmwares not found for {0}".format(device["identifier"]))
           continue
        json_firmwares = json_firmwares["firmwares"]
        if len(filter_versions) > 0:
            firmwares = [x for x in json_firmwares for xs in filter_versions if xs in x['version']]
        else:
            firmwares = json_firmwares
        print("Firmwares for {0} found: {1}".format(device["identifier"],len(firmwares)))
        dir_device_path = os.path.join(curr_dir, device["name"] + "__" + device["identifier"] + "")
        if os.path.isdir(dir_device_path) == False:
            os.mkdir(dir_device_path)
        for firmware in firmwares:
            print("Analyzing {0} {1}".format(device["identifier"],firmware["version"]))
            child = pexpect.spawn("./pzb " + firmware["url"] )
            try:
                child.expect(b' $')
                if debug:print(child.before)
            except pexpect.EOF:
                break  
            child.write("ls\n".encode())
            fw_dir_list = ""
            try:
                child.expect(b' $')
                fw_dir_list = child.before
            except pexpect.EOF:
                break
            if debug:print(fw_dir_list)
            kernelfiles = re.findall("kernelcache.d.*" if dev_kernel else "kernelcache.r.*",fw_dir_list)
            if len(kernelfiles) != 0:
                print("Kernelfiles found: {0}".format(len(kernelfiles)))
                folder_name = firmware["version"] + "__" + firmware["buildid"]
                dir_path = os.path.join(dir_device_path, folder_name)
                if os.path.isdir(dir_path) == False:
                    os.mkdir(dir_path)
                for kernelfile in kernelfiles:
                    print("Downloading {0}".format(kernelfile))
                    kernelfile_file_path = os.path.join(curr_dir, kernelfile.replace("\r",""))
                    child.write(("get " + kernelfile + "\n").encode())
                    try:
                        child.expect([b"download succeeded",b"Error"])
                        shutil.move(kernelfile_file_path,dir_path)
                    except:
                         break


def download_beta_fw(filter_versions,filter_devices,dev_kernel):
   
    r = requests.get('https://api.ipsw.me/v4/devices')
    if r.status_code == 200:
       json_devices = json.loads(r.text)
       if json_devices == None or len(json_devices) == 0:
           print("Devices not found!")
           exit(-1)
    if len(filter_devices) >0:
        devices = [x for x in json_devices for xs in filter_devices if xs in x['identifier']]
    else:
        devices = json_devices
    print("Devices found: {0}".format(len(devices)))
    for device in devices:
        r = requests.get('https://api.m1sta.xyz/betas/' + device["identifier"])
        if r.status_code != 200:
            continue
        json_firmwares = json.loads(r.text)
        if json_firmwares == None or len(json_firmwares) == 0:
           print("Firmwares not found for {0}".format(device["identifier"]))
           continue
        if len(filter_versions) > 0:
            firmwares = [x for x in json_firmwares for xs in filter_versions if xs in x['version']]
        else:
            firmwares = json_firmwares
        print("Firmwares for {0} found: {1}".format(device["identifier"],len(firmwares)))
        dir_device_path = os.path.join(curr_dir, device["name"] + "__" + device["identifier"] + "")
        if os.path.isdir(dir_device_path) == False:
            os.mkdir(dir_device_path)
        for firmware in firmwares:
            print("Analyzing {0} {1}".format(device["identifier"],firmware["version"]))
            child = pexpect.spawn("./pzb " + firmware["url"] )
            try:
                child.expect(b' $')
                if debug:print(child.before)
            except pexpect.EOF:
                break  
            child.write("ls\n".encode())
            fw_dir_list = ""
            try:
                child.expect(b' $')
                fw_dir_list = child.before
            except pexpect.EOF:
                break
            if debug:print(fw_dir_list)
            kernelfiles = re.findall("kernelcache.d.*" if dev_kernel else "kernelcache.r.*",fw_dir_list)
            if len(kernelfiles) != 0:
                print("Kernelfiles found: {0}".format(len(kernelfiles)))
                folder_name = firmware["version"] + "__" + firmware["buildid"]
                dir_path = os.path.join(dir_device_path, folder_name)
                if os.path.isdir(dir_path) == False:
                    os.mkdir(dir_path)
                for kernelfile in kernelfiles:
                    print("Downloading {0}".format(kernelfile))
                    kernelfile_file_path = os.path.join(curr_dir, kernelfile.replace("\r",""))
                    child.write(("get " + kernelfile +"\n").encode())
                    try:
                        child.expect([b"download succeeded",b"Error"])
                        shutil.move(kernelfile_file_path,dir_path)
                    except:
                        break
    
def print_help():
    print("downloader.py -v '15.7 16' -m 'iPhone11,2'")
    print("downloader.py -v '15.7 16' -m 'iPhone11,2' -b 1")
    print("pass -d 1 for download only development kernelcache")
  

def main(argv):
    
    filter_versions = []
    filter_devices = []
    beta_fw = 0
    dev_kernel = 0
    
    pzb_path = os.path.join(curr_dir, "pzb")
    if not os.path.isfile(pzb_path):
        print("Error: missing pzb!\nPlease download from https://github.com/tihmstar/partialZipBrowser")
        exit(-1)
    try:
        opts, args = getopt.getopt(argv,"h:v:m:d:b:",["type_download=","version=","model=","dev_kernel=","beta=="])
    except getopt.GetoptError:
        print_help()
        exit(-1)
    for opt, arg in opts:
        if opt == "-h":
            print_help()
            exit(-1)
        elif opt in ("-v","--version"):
            filter_versions = arg.split()
        elif opt in ("-m","--model"):
            filter_devices = arg.split()
        elif opt in ("-d","--dev_kernel"):
            dev_kernel = int(arg)
        elif opt in ("-b","--beta"):
            beta_fw = int(arg)
  
    if beta_fw == 0:
        download_fw(filter_versions,filter_devices,dev_kernel)
    else:
        download_beta_fw(filter_versions,filter_devices,dev_kernel)
   
            
if __name__ == "__main__":  
    main(sys.argv[1:])
   