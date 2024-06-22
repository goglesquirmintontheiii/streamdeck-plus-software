#Installer script

#check release id from https://api.github.com/repos/goglesquirmintontheiii/streamdeck-plus-software/releases
#download all scripts from https://api.github.com/repos/goglesquirmintontheiii/streamdeck-plus-software/contents/

import os
import requests
import zipfile
import shutil

def getselection(prompt):
    temp = input(prompt)
    return temp.lower() in ["y","yes","yeah"]

sep = os.path.sep

pth = os.path.expanduser('~')+sep+".streamdeck"
if not os.path.exists(pth):
    os.mkdir(pth)

iconpth = pth+sep+"iconpacks"
if not os.path.exists(iconpth):
    os.mkdir(iconpth)

fontpth = pth+sep+"fonts"

backgroundpth = pth+sep+"backgroundpacks"


pluginpth = pth+sep+"plugins"
if not os.path.exists(pluginpth):
    os.mkdir(pluginpth)

cfgpth = pth+sep+"profile.json"



def download_main_files():
    filelist = requests.get("https://api.github.com/repos/goglesquirmintontheiii/streamdeck-plus-software/contents/").json()
    
    for file in filelist:
        if not file['name'].endswith(".zip"):
            with open(pth+"/"+file['name'], "wb") as f:
                f.write(requests.get(file['download_url']).content)
    print("Done!")
    #print("Copying script to ~/.streamdeck.. (this is required for the desktop shortcut to work)")
    #shutil.copyfile(__file__,pth+"/streamdeck.py")


if os.path.exists(cfgpth):
    pass
else:
    with open(cfgpth,"w") as f:
        f.write("""{
    "pages": [{
        "button.0": {
            "press": "media.stop",
            "iconOn": ""
        }
    }]
}
""") 
    print("Seems you're new to the software!")
    #if getselection("Would you like to scan for an existing official Streamdeck software? This will let you import your icon and background packs. (y/n): "):
    if False: # -- Not implemented yet -- needs a bit of work first, but it's not my top priority
        input("Press enter when you've mounted your windows drive (so the program can reach it easily). This will scan /media/ for drives that have Windows on them.")
        users = os.listdir("/media")
        for directory in users:
            if not os.path.isfile("/media/"+directory):
                user = os.listdir("/media/"+directory)
                for subdir in os.listdir(user):
                    if not os.path.isfile("/media/"+directory+"/"+subdir):
                        subdcont = os.listdir("/media/"+directory+"/"+subdir)
                        if "Windows" in subdcont and "Users" in subdcont:
                            winbase = "/media/"+directory+"/"+subdir
                            winusers = os.listdir(winbase+"/Users")
                            for winuser in winusers:
                                if not os.path.isfile(winbase+"/Users/"+winuser):
                                    wupath = winbase+"/Users/"+winuser


    if getselection("Would you like to create a desktop shortcut? (y/n): "):
        with open(os.path.expanduser('~')+sep+'Desktop'+sep+'stream_deck.desktop','w') as f:
            f.write("[Desktop Entry]\n")
            f.write("Name=Stream deck\n")
            f.write("Version=v0.0.1\n")
            f.write("Icon="+pth+sep+'icon.png\n')
            f.write("Exec=/bin/python3 "+pth+sep+"sdplus.py\n")
            f.write("Terminal=false\n")
            f.write("Type=Application")
    if getselection("Would you like to download a small icon pack from the repo? (1.1MB) (y/n): "):
        print("Downloading icons..")
        iconz = requests.get("https://github.com/goglesquirmintontheiii/streamdeck-plus-software/raw/main/baseicons.zip").content
        print("Saving baseicons.zip..")
        with open(pth+"/"+"tempicons.zip", "wb") as f:
            f.write(iconz)
        print("Unzipping..")
        with zipfile.ZipFile(pth+"/"+"tempicons.zip") as z:
            z.extractall(iconpth)
        os.remove(pth+"/"+"tempicons.zip")
    if getselection("Almost done! Would you like to download the elgato background packs for the LCD display? (4.6MB) (y/n): "):
        print("Downloading backgrounds..")    
        backz = requests.get("https://github.com/goglesquirmintontheiii/streamdeck-plus-software/raw/main/backgroundpacks.zip").content
        print("Saving backgroundszip.zip..")
        with open(pth+"/backgroundszip.zip","wb") as f:
            f.write(backz)
        print("Unzipping..")
        if os.path.exists(backgroundpth):
            os.rmdir(backgroundpth)
        with zipfile.ZipFile(pth+"/backgroundszip.zip") as z:
            z.extractall(pth)
        os.remove(pth+"/backgroundszip.zip")
    print("Downloading fonts.. (6.94MB)")
    fontz = requests.get("https://github.com/goglesquirmintontheiii/streamdeck-plus-software/raw/main/fonts.zip").content
    print("Saving fonts..")
    with open(pth+"/fontszip.zip", "wb") as f:
        f.write(fontz)
    print("Unzipping..")
    with zipfile.ZipFile(pth+"/fontszip.zip") as z:
        z.extractall(pth)
    os.remove(pth+"/fontszip.zip")
    print("Downloading streamdeck icon..")
    with open(pth+"/icon.png","wb") as f:
        f.write(requests.get("https://raw.githubusercontent.com/goglesquirmintontheiii/streamdeck-plus-software/main/icon.png").content)
    print("Downloading all other necessary items to ~/.streamdeck ...")
    download_main_files()
    if not os.path.exists(backgroundpth):
        os.mkdir(backgroundpth)
    if not os.path.exists(fontpth):
        os.mkdir(fontpth)



