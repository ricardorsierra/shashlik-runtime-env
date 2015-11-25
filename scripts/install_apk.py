#!/bin/python3

import sys
import os
import subprocess
import re
import argparse
import shutil
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument("apk", help="the APK to isntall")
args = parser.parse_args()
apk_path = args.apk

def message(msg): #def message being a much lesser known 80s rock band
    subprocess.run(args=["kdialog",
                         "--title", "Shashlik",
                         "--msgbox", msg])

try:
    aapt_output = subprocess.run(args=["/home/david/Android/Sdk/build-tools/23.0.1/aapt",
                                    "dump",
                                    "badging",
                                    apk_path],
                                check=True,
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
except:
    sys.exit("Could not get APK info")


apk_info = {}

#some lines are formatted as adsf:'awere'
#others are formatted as asdf: foo='awerwe' zzz='asdfwer'

#this script doesn't really work as user-permission comes up mulitple times, but it'll do for the bits we want

for line in aapt_output.stdout.split('\n'):
    if (not ':' in line):
        continue

    [key,value] = line.split(':', 1)
    apk_info[key] = value

r = re.compile(r"name='([^']*)'")
m = r.search(apk_info["package"])
if not m:
    sys.exit("Could not extract package name")
package_name = m.group(1)
app_name = apk_info["application-label"].strip("'")

icon_path=""
for size in [640, 480, 320, 240, 213, 160, 120]:
    entry = "application-icon-" + str(size)
    if entry in apk_info:
        icon_path = apk_info[entry].strip("'")
        break

if "native-code" in apk_info and not "x86" in apk_info["native-code"]:
    sys.exit("This package does not contain x86 native code, and can't run. Please find another APK built for x86")

shashlik_dir = os.path.expanduser("~/.local/share/shashlik/")
app_dir = os.path.expanduser("~/.local/share/applications/")

try:
    os.mkdir(shashlik_dir)
except:
    pass
try:
    os.mkdir(app_dir)
except:
    pass

#copy APK for pending installation when we first run it
shutil.copyfile(apk_path, shashlik_dir + package_name + ".apk")

#write desktop file and extract icon
desktop_file = open(app_dir + "/" + package_name + ".desktop", "w")
desktop_file.write("[Desktop Entry]\n")
desktop_file.write("Name=" + app_name + "\n")
desktop_file.write("Icon=" + shashlik_dir + package_name + ".png\n")
desktop_file.write("Exec=/home/david/daveshashlik2/scripts/emu " + package_name + "\n")

desktop_file.write("Terminal=false\n")
desktop_file.write("Type=Application\n")
desktop_file.write("Categories=Network;FileTransfer;Game;\n") #TODO
desktop_file.write("Encoding=UTF-8\n")

if icon_path:
    apk_zip = zipfile.ZipFile(apk_path)
    icon_in = apk_zip.open(icon_path, "r")
    icon_out = open(shashlik_dir + package_name + ".png", "wb")
    icon_out.write(icon_in.read())

desktop_file.close()
subprocess.run("kbuildsycoca5", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


message ("Successfully installed %s" % app_name)