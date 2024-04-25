#Software made by goglesq (@animepfp on Discord) 
#u/goglesq
#https://github.com/goglesquirmintontheiii


import os
import threading
import io
import cv2
import urllib
import requests
import cairosvg
import json
from time import time, sleep
from PIL import Image, ImageDraw, ImageFont, ImageTk
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType
from pynput.keyboard import Key, Controller, HotKey, Listener
import pynput
import importlib
import re
import pyperclip

keyboard = Controller()

def press(key):
    global keyboard
    keyboard.press(key)
    keyboard.release(key)

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
if not os.path.exists(fontpth):
    os.mkdir(fontpth)

backgroundpth = pth+sep+"backgroundpacks"
if not os.path.exists(backgroundpth):
    os.mkdir(backgroundpth)

pluginpth = pth+sep+"plugins"
if not os.path.exists(pluginpth):
    os.mkdir(pluginpth)

icons = {}
lookup = {}

for i in os.listdir(iconpth):
    icop = iconpth + sep + i
    manifest = icop+sep+"manifest.json"
    icolist = icop+sep+"icons.json"
    with open(manifest,"r") as f:
        manf = json.loads(f.read())
    with open(icolist, "r") as f:
        ics = json.loads(f.read())
    icons[i] = { k.lower():v for k,v in manf.items() }
    icons[i]['icons'] = ics
    icons[i]['full'] = os.listdir(icop+sep+"icons")

    lookup[manf["Name"]] = i

cfgpth = pth+sep+"profile.json"

if os.path.exists(cfgpth):
    with open(cfgpth,"r") as f:
       cfg = json.loads(f.read())
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

    if getselection("Would you like to scan for an existing official Streamdeck software? This will let you import your icon and background packs. (y/n): "):
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
        with open(os.path.expanduser('~')+sep+'Desktop'+sep+'streamdeck.desktop','w') as f:
            f.write("[Desktop Entry]\n")
            f.write("Name=Stream deck\n")
            f.write("Version=v0.0.1\n")
            f.write("Icon=streamdeck\n")
            f.write("X-Icon-Path="+pth+sep+'icon.png\n')
            f.write("Exec=/bin/python3 "+pth+sep+"streamdeck.py\n")
            f.write("Terminal=false\n")
            f.write("Type=Application")
    
    exit("Please restart the program so the default profile can be loaded.")


#RESIZE ALL IMAGES TO 120x120 FOR KEYS,
#200x100 FOR ALL ACTIONS,
#800x100 FOR TOUCHSCREEN
   
page = 0
screenbg = Image.new("RGB",(800,100),(0,0,0)) 

def refreshConfigs(*args, **kwargs):
    global cfg
    global page
    global cfgpth
    if os.path.exists(cfgpth):      
        try:
            with open(cfgpth,"r") as f:
                cfg = json.loads(f.read())
                page = 0
                try:
                    loadPage()
                except Exception as e:
                    print("WARNING: Invalid profile file (failed to call loadPage) with error " + str(e))
        except:
            print("WARNING: Invalid profile file (JSON error)")
    else:
        print("WARNING: Profile file not found")
        cfgpth = pth+"/profile.json"
        if os.path.exists(cfgpth):
            print("INFO: Reloading with default config file..")
        else:
            exit("ERROR: System profile file not found, cannot run! Rerunning the program will fix this in most cases.")

def procEnv(text,**kwargs):
    cont = re.findall("\${([^{}]*)}", text)
    glob = globals()
    gkeys = glob.keys()
    loc = locals()
    lkeys = loc.keys()
    kwk = kwargs.keys()
    for i in cont:
        if i in gkeys:
            text = text.replace("${"+i+"}", str(glob[i]))
        elif i in lkeys:
            text = text.replace("${"+i+"}", str(loc[i]))
        elif i in kwk:
            text = text.replace("${"+i+"}", str(kwargs[i]))
        else:
            try:
                text = text.replace("${"+i+"}", str(eval(i,globals(),kwargs if len(kwk) > 0 else loc)))
            except:
                print(f"WARNING: Eval failure during evaluation of '{i}' - did you enter an invalid local or global name?")
    # for k,v in globals().items():
    #     text = text.replace("${"+k+"}", str(v))
    # for k,v in locals().items():
    #     text = text.replace("${"+k+"}", str(v))
    return text

def getData(img : Image):
    otp = io.BytesIO()
    try:
        img.save(otp,format="JPEG")
    except:
        background = Image.new("RGB", img.size, (0, 0, 0))
        background.paste(img, mask=img.split()[3])
        background.save(otp,format="JPEG")
    return otp.getvalue()

def readSvg(path):
    out = io.BytesIO()
    cairosvg.svg2png(url=path,write_to=out)
    return Image.open(out)

def filterOpen(path, expectedSize=(120,120)) -> Image:
    if path.endswith('.svg'):
        return readSvg(path).resize(expectedSize)
    else:
        return Image.open(path).resize(expectedSize)

def filteredStrip(text):
    if text == ' ':
        return text
    else:
        return text.strip()

def splitArgs(text,**kwargs):
    istr = False
    escape = False
    actions = []
    args = []
    cur = ""
    for i in text:
        if i == '.':
            if istr:
                cur += i
            else:
                args.append(procEnv(filteredStrip(cur),**kwargs))
                cur = ""
        elif i == ';':
            if istr:
                cur += i
            else:
                if len(cur) > 0:
                    args.append(procEnv(filteredStrip(cur),**kwargs))
                    cur = ""
                actions.append(args[:])
                args = []
        else:
            if escape or (i not in "\\\""):
                escape = False
                cur += i
            else:
                if i == "\\":
                    escape = True
                elif i == "\"":
                    istr = not istr
    if len(cur) > 0:
        args.append(procEnv(filteredStrip(cur),**kwargs))
    if len(args) > 0:
        actions.append(args)
    return actions
    

def handleAction(actionString,**kwargs):
    global keyboard
    global page
    actions = splitArgs(actionString,**kwargs)
    for splt in actions:
        domain = splt[0]
        args = splt[2:]
        sub = splt[1] if len(splt) > 1 else None

        if domain == "page":
            if sub == "next":
                page = (page + 1) % len(cfg["pages"])
                loadPage()
            elif sub == "previous":
                if page > 0:
                    page -= 1
                    loadPage()
                else:
                    page = len(cfg["pages"]) - 1
                    loadPage()
            elif sub == "refresh":
                loadPage()
        elif domain == "key":
            keyboard.press(sub)
        elif domain == "script":
            pass
            #importlib.import_module(sub)
        elif domain == "media":
            if sub == "pause":
                press(Key.media_play_pause)     
            elif sub == "next":
                press(Key.media_next)
            elif sub == "previous":
                press(Key.media_previous)
            elif sub == "stop":
                press(Key.pause)
            elif sub == "volumeUp":
                press(Key.media_volume_up)
            elif sub == "volumeDown":
                press(Key.media_volume_down)
            elif sub == "mute":
                press(Key.media_volume_mute)
            elif sub == "stop":
                press(HotKey.parse("<269025045>")[0])
        elif domain == "write":
            for k in args[1]:
                press(k)
        elif domain == "hotkey":
            hk = HotKey.parse(sub) #CTRL-V, CTRL-C, etc
            for i in hk:
                keyboard.press(i)
            for i in hk:
                keyboard.release(i)
        elif domain == "press" or domain == "push":
            hk = HotKey.parse(sub)
            for i in hk:
                keyboard.press(i)
        elif domain == "release":
            hk = HotKey.parse(sub)
            for i in hk:
                keyboard.release(i)
        elif domain == "profile":
            if sub == "refresh":
                refreshConfigs()
            elif sub == "load":
                fl = args[0]
                if os.path.exists(fl):
                    cfgpth = fl
                    refreshConfigs()
                else:
                    if not fl.endswith(".json"): fl += ".json"
                    corrected = pth+fl
                    if os.path.exists(corrected):
                        cfgpth = corrected
                        refreshConfigs()
                    else:
                        print("WARNING: Profile file not found")
        elif domain == "eval":
            eval(sub)
        elif domain == "exec":
            exec(sub)

def handleEvent(event,**kwargs): #Ex: screen.up or button.0.press
    global cfg 
    global page
    parts = event.split('.')
    kwargs["event"] = event
    if parts[0] == "screen":
        pg = cfg["pages"][page]
        if "screen" in pg.keys():
            evt = parts[-1]
            if evt in pg["screen"].keys():
              
                handleAction(pg["screen"][evt],**kwargs)
    else:
        device = parts[0]+"."+parts[1]
        if device in cfg["pages"][page].keys():
            dev = cfg["pages"][page][device]
            evt = parts[-1]
            if evt in dev.keys():
                handleAction(dev[evt],**kwargs)

def eventExists(event):
    global cfg 
    global page
    parts = event.split('.')
    if parts[0] == "screen":
        pg = cfg["pages"][page]
        if "screen" in pg.keys():
            evt = parts[-1]
            if evt in pg["screen"].keys():
                return True
    else:
        device = parts[0]+"."+parts[1]
        if device in cfg["pages"][page].keys():
            dev = cfg["pages"][page][device]
            evt = parts[-1]
            if evt in dev.keys():
                return True
    return False

def handleImage(img : str, expectedSize = (120,120)) -> Image:
    global lookup
    global icons
    if img == "":
        return Image.new("RGB",expectedSize,(0,0,0))
    if os.path.exists(img):
        return filterOpen(img,expectedSize)
    else:
        domain = img.split('/')[0]
        pg = None
        if domain in icons.keys():
            pg = icons[domain]
            path = domain
        elif domain in lookup.keys():
            pg = icons[lookup[domain]]
            path = lookup[domain]
        if pg:
            realpath = None
            for i in pg['icons']:
                name = img.split('/')[1]
                if name in [i['path'], i['name']]:
                    realpath = iconpth+sep+path+sep+"icons"+sep+i['path']
                    break
            if realpath:
                return filterOpen(realpath,expectedSize)
            else:
                print("Warning: icon does not exist")
                return Image.new("RGB",expectedSize,(0,0,0))
        else:
            print("Warning: icon does not exist")
            return Image.new("RGB",expectedSize,(0,0,0))

def font(v,size=20):
    if os.path.exists(fontpth+sep+v+".ttf"):
        return ImageFont.truetype(fontpth+sep+v+".ttf",size)

def handleArgs(v : dict, args : dict):
    keys = v.keys()
    out = {k:val[1](v[k]) if k in keys else val[0] for k,val in args.items()}
    
    if 'font_size' in keys:
        out["font"] = font(out['font']  if "font" in keys else "Roboto-Regular",v["font_size"])
    return out

loadedPlugins = []

def loadPage():
    global page
    global cfg
    global deck
    global screenbg
    global btns
    global dials
    global bg
    global selAcc
    destroyProps()
    notLoaded = [i for i in range(8)]
    argparse = {
                        "xy": ((0,90), tuple),
                        "text": ("", procEnv),
                        "fill": (None, tuple),
                        "font": (font("Roboto-Regular"), font),
                        "anchor": (None, str),
                        "spacing": (4, int),
                        "align": ("middle", str),
                        "direction": (None, str),
                        "features": (None,tuple),
                        "language": (None, str),
                        "stroke_width": (0, int),
                        "stroke_fill": (None, tuple),
                        "embedded_color": (False, bool),
                        "font_size": (25, int)
                    }
    for dev, val in cfg["pages"][page].items():
        sp = dev.split('.')
        domain = sp[0]
        if domain == "screen":
            if 'image' in val.keys():
                screenbg = handleImage(procEnv(val['image'],device=dev,properties=val),(800,100))
            else:
                screenbg = handleImage("",(800,100))
            if 'text' in val.keys():
                    argparse["xy"] = ((0,0),tuple)
                    #https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
                    draw = ImageDraw.Draw(screenbg)
                    draw.text(**handleArgs(val['text'] if isinstance(val['text'],dict) else {"text": val['text']}, argparse))
            im=ImageTk.PhotoImage(screenbg)
            bg.config(image=im)
            bg.im = im
            deck.set_touchscreen_image(getData(screenbg), 0, 0, 800, 100)
        elif domain == "button":
            
            if 'iconOn' in val.keys():
                notLoaded.remove(int(sp[1]))
                img = handleImage(procEnv(val['iconOn'],device=dev,properties=val))
                if 'text' in val.keys():
                    draw = ImageDraw.Draw(img)
                    targs = handleArgs(val['text'] if isinstance(val['text'],dict) else {"text": val['text']}, argparse)
                    _, _, w, h = draw.textbbox((0, 0), val['text']['text'] if isinstance(val['text'],dict) else val['text'], font=targs["font"])
                    W, H = img.size
                    argparse["xy"] = ((0,77),tuple)#(((100-w)/2,77),tuple)#(((W/2)-(w/2), 77), tuple)
                    draw.text(**handleArgs(val['text'] if isinstance(val['text'],dict) else {"text": val['text']}, argparse))
                deck.set_key_image(int(sp[1]),getData(img))
                _im = ImageTk.PhotoImage(img)
                btns[int(sp[1])].config(image=_im)
                btns[int(sp[1])].im = _im
        elif domain == "dial":
            dn = int(sp[1])
            if 'image' in val.keys():
                img = handleImage(procEnv(val['image'],device=dev,properties=val),(100,100))                
                screenbg.paste(img, ((dn*200)+50,0), mask=img.split()[3])
                if 'text' in val.keys():
                    draw = ImageDraw.Draw(screenbg)
                    targs = handleArgs(val['text'] if isinstance(val['text'],dict) else {"text": val['text']}, argparse)
                    _, _, w, h = draw.textbbox((0, 0), val['text']['text'] if isinstance(val['text'],dict) else val['text'], font=targs["font"])
                    argparse["xy"] = ((((100-w)/2) + (dn*200) + 50, 75), tuple)
                    draw.text(**handleArgs(val['text'] if isinstance(val['text'],dict) else {"text": val['text']}, argparse))
                im=ImageTk.PhotoImage(screenbg)
                bg.config(image=im)
                bg.im = im
                deck.set_touchscreen_image(getData(screenbg), 0, 0, 800, 100)
        elif domain == "plugins":
            for v in val['paths']:
                plug = pluginpth+sep+v+".py"
                if plug not in loadedPlugins:
                    with open(plug, "r") as f:
                        cont = f.read()
                        def startPlugin(contents=cont):
                            print("Loading plugin")
                            exec(cont,globals(),locals())
                            
                        threading.Thread(target=startPlugin).start()
                        loadedPlugins.append(plug)
                    
            
    for i in notLoaded:
        blankimg = Image.new("RGB",(120,120),(0,0,0))
        blank2 = ImageTk.PhotoImage(blankimg)
        btns[i].config(image=blank2)
        btns[i].im = blank2 
        deck.set_key_image(i,getData(blankimg))

# callback when lcd is touched
def touchscreen_event_callback(deck, evt_type, value):
    if evt_type == TouchscreenEventType.SHORT:
        pos = (value['x'], value['y'])
        if pos[0] >= 50 and pos[0] <= 150:
            handleEvent("dial.0.touchShort")
        elif pos[0] >= 250 and pos[0] <= 350:
            handleEvent("dial.1.touchShort")
        elif pos[0] >= 450 and pos[0] <= 550:
            handleEvent("dial.2.touchShort")
        elif pos[0] >= 650 and pos[0] <= 750:
            handleEvent("dial.3.touchShort")
        else:
            handleEvent("screen.touchShort")
        #print("Short touch @ " + str(value['x']) + "," + str(value['y']))

    elif evt_type == TouchscreenEventType.LONG:
        pos = (value['x'], value['y'])
        if pos[0] >= 50 and pos[0] <= 150:
            handleEvent("dial.0.touchLong")
        elif pos[0] >= 250 and pos[0] <= 350:
            handleEvent("dial.1.touchLong")
        elif pos[0] >= 450 and pos[0] <= 550:
            handleEvent("dial.2.touchLong")
        elif pos[0] >= 650 and pos[0] <= 750:
            handleEvent("dial.3.touchLong")
        else:
            handleEvent("screen.touchLong")
        #print("Long touch @ " + str(value['x']) + "," + str(value['y']))

    elif evt_type == TouchscreenEventType.DRAG:
        src = [value['x'], value['y']]
        dst = [value['x_out'], value['y_out']]
        domain = "screen"
        dial_src = src[0] // 200
        dial_dst = dst[0] // 200
        if dial_src == dial_dst:
            domain = "dial."+str(dial_src)

        diff = [dst[0] - src[0], dst[1] - src[1]]
        if abs(diff[0]) > abs(diff[1]):
            if diff[0] > 0: #right
                evt = f"{domain}.right"
            else: #left
                evt = f"{domain}.left"
        else:
            if diff[1] > 0: #down
                evt = f"{domain}.down"
            else: #up
                evt = f"{domain}.up"
        if eventExists(evt):
            handleEvent(evt)
        else:
            handleEvent(evt.replace(domain,"screen"))


# callback when dials are pressed or released
def dial_change_callback(deck, dial, event, value):
    if event == DialEventType.PUSH:
        handleEvent(f"dial.{dial}.{['release','press'][int(value)]}")
    elif event == DialEventType.TURN:
        handleEvent(f"dial.{dial}.{['counterclockwise','clockwise'][int(value > 0)]}")

times = [0,0,0,0,0,0,0,0]

def keychange(deck, key, state):
    global times
    handleEvent(f"button.{key}.{['release','press'][int(state)]}")
    if state == True:
        times[key] = time()
    else:
        diff = time() - times[key]
        if diff > 1.5:
            handleEvent(f"button.{key}.pushLong")
        else:
            handleEvent(f"button.{key}.pushShort")

for i in range(60):
    decks = DeviceManager().enumerate()
    if i == 59 and len(decks) == 0:
        exit("Warning: no streamdecks found (x60)")
    try:
        deck = decks[0]
        break
    except:
        print(f"Warning: no streamdecks found (x{i+1})")
        sleep(2)

try:
    deck.open()
    deck.reset()
except:
    print("ERROR: Could not access found streamdeck. You may have to run the program as root, or allow your user to access USB devices.")
    exit("Using `sudo echo 'SUBSYSTEM==\"usb\", MODE=\"0660\", GROUP=\"{YOUR_USERNAME_HERE}\"' > /etc/udev/rules.d/00-usb-permissions.rules` should fix any permissions-related issues.")
deck.set_key_callback(keychange)
deck.set_touchscreen_callback(touchscreen_event_callback)
deck.set_dial_callback(dial_change_callback)


from tkinter import VERTICAL,Y,RIGHT,FALSE,LEFT,BOTH,TRUE,NW,Tk
from tkinter import ttk, PhotoImage, Button, Label, Entry
import tkinter as tk

#Software made by goglesq (@animepfp on Discord) 
#u/goglesq
#https://github.com/goglesquirmintontheiii

class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

#Software made by goglesq (@animepfp on Discord) 
#u/goglesq
#https://github.com/goglesquirmintontheiii

root = Tk(className="Streamdeck")
root.configure(background="#2A2A2A")
root.title("Stream deck app")

sty = ttk.Style()
sty.configure('MyFrame.TFrame',background="#3A3A3A")

frm = ttk.Frame(root, padding=10,style='MyFrame.TFrame')
frm.place(x=0,y=625)

frm2 = ttk.Frame(root,padding=10,style="MyFrame.TFrame")
frm2.place(x=200,y=0)


rootX = 50
rootY = 50

btns = []
dials = []

phi = PhotoImage(width=1, height=1)

propList = {}
bprop = {"iconOn":str,"text": json.loads,"press":str,"release":str,"pushLong":str,"pushShort":str}
dprop = {"image":str,"text": json.loads,"press":str,"release":str,"clockwise":str,"counterclockwise":str,"up":str,"down":str,"left":str,"right":str,"touchShort":str,"touchLong":str}
sprop = {"image":str,"text":json.loads,"touchShort":str,"touchLong":str,"up":str,"down":str,"left":str,"right":str}
selElem = None
selAcc = ""

def saveToCfg():
    with open(cfgpth,"w") as f:
        f.write(json.dumps(cfg))

def fetchPropDict():
    global selAcc
    global bprop
    global sprop
    global dprop
    if selAcc.startswith("button"):
        return bprop
    elif selAcc.startswith("dial"):
        return dprop
    elif selAcc.startswith("screen"):
        return sprop
    else:
        return None

def saveProps(propDict=None,save=True):
    global propList
    global selElem
    global selAcc
    if propDict is None:
        propDict = fetchPropDict()
    tmp = {}
    for k,v in propList.items():
        text = v[1].get()
        if text != "":
            try:
                tmp[k]=propDict[k](text)
            except:
                tmp[k]=text
    if save:
        cfg["pages"][page][selAcc] = tmp
        saveToCfg()
    return tmp

def removePage():
    global page
    if page != 0:
        cfg["pages"].pop(page)
        page -= 1
        loadPage()
        buildPages()
        saveToCfg()

def addPage():
    global page
    thisbg = ""
    if "screen" in cfg["pages"][page].keys():
        if "image" in cfg["pages"][page]["screen"].keys():
            thisbg = cfg["pages"][page]["screen"]["image"]
    if thisbg != "":
        cfg["pages"].append({"screen":{"left":"page.previous","right":"page.next","image":thisbg}})
    else:
        cfg["pages"].append({"screen":{"left":"page.previous","right":"page.next"}})
    page = len(cfg["pages"])-1
    loadPage()
    buildPages()
    saveToCfg()

def buildPages():
    global cfg
    global frm2
    for c in frm2.grid_slaves():
        c.destroy()
    for i in range(len(cfg["pages"])):
        def sp(i=i):
            global page
            page=i
            loadPage()
        Button(frm2,text=str(i+1),command=sp,borderwidth=0,bg="#3A3A3A",activebackground="#3F3F3F",fg="white",activeforeground="white").grid(row=0,column=i)
    Button(frm2,text="+",command=addPage,borderwidth=0,bg="#3A3A3A",activebackground="#3F3F3F",fg="white",activeforeground="white").grid(row=0,column=i+1)
    Button(frm2,text="-",command=removePage,borderwidth=0,bg="#3A3A3A",activebackground="#3F3F3F",fg="white",activeforeground="white").grid(row=0,column=i+2)


def destroyProps():
    global frm
    global selAcc
    selAcc = ""
    for i in frm.grid_slaves():
        i.destroy()
    for i in frm.slaves():
        i.destroy()

def copyJson():
    global selAcc
    if selAcc != "":
        otp = saveProps()
        otp["domain"]=selAcc.split('.')[0]
        pyperclip.copy(json.dumps(otp))

def pasteJson(warn=True):
    global selAcc
    global propList
    global selElem
    global selAcc
    propDict = fetchPropDict()
    this = selAcc.split(".")[0]

    if selAcc != "":
        try:
            content = pyperclip.paste()
            if len(content) > 1000:
                return
            js = json.loads(content)
            if isinstance(js,dict):
                dom = js["domain"] if "domain" in js.keys() else None
                if dom is None:
                    if warn:
                        print("WARNING: 'domain' key not found; cannot paste this JSON")
                    return
                elif dom == this:
                    tmp = {k:v for k,v in js.items() if k != "domain"}
                    cfg["pages"][page][selAcc] = tmp
                    saveToCfg()
                    refreshConfigs()
                    loadPage()
                    destroyProps()
                    if warn:
                        print("Pasted")
                elif warn:
                    print(f"WARNING: Domain mismatch, you tried to paste a {dom} into a {this}")
            elif warn:
                print("WARNING: Invalid JSON pasted")
        except Exception as e:
            if warn and isinstance(e,json.JSONDecodeError):
                print("WARNING: Non-JSON text pasted")
            elif warn:
                print(f"PASTE ERROR: {e}")

def buildProps(dev,propDict,saveFunc):
    global propList
    global cfg
    global selElem
    global selAcc
    propList={}
    destroyProps()
    selAcc = dev
    selElem = cfg["pages"][page][dev] if dev in cfg["pages"][page].keys() else {}
    idx = 0
    for k,f in propDict.items():
        propList[k] = (Label(frm,text=k+": ",width=len(k+": "),bg="#3A3A3A",fg="white"),Entry(frm,width=50,bg="#3A3A3A",fg="white"))
        propList[k][0].grid(row=idx//2,column=(idx%2)*2)
        if k in selElem.keys():
            propList[k][1].insert(0,str(selElem[k]) if k != "text" else (json.dumps(selElem[k]) if isinstance(selElem[k],dict) else selElem[k]))
        propList[k][1].grid(row=idx//2,column=((idx%2)*2)+1)
        idx += 1
    save = Button(frm,text="Copy",width=10,command=copyJson,bg="#3A3A3A",fg="white")
    save.grid(row=(len(propDict.keys())//2)+1,column=0,columnspan=1,pady=3)
    save = Button(frm,text="Save",width=50,command=saveFunc,bg="#3A3A3A",fg="white")
    save.grid(row=(len(propDict.keys())//2)+1,column=1,columnspan=2,pady=3)
    save = Button(frm,text="Paste",width=10,command=pasteJson,bg="#3A3A3A",fg="white")
    save.grid(row=(len(propDict.keys())//2)+1,column=3,columnspan=1,pady=3)

def selectButton(idx):
    buildProps("button."+str(idx),bprop,saveProps)
    
def selectDial(idx):
    buildProps("dial."+str(idx),dprop,saveProps)

def selectScreen():
    buildProps("screen",sprop,saveProps)

def on_press(key):
    global selAcc
    global cfg
    global page
    if key.state == 4 and key.keysym == "v":
        pass#pasteJson(True)
    elif key.keysym == "Delete" and selAcc != "":
        cfg["pages"][page].pop(selAcc,None)
        saveToCfg()
        loadPage()
    else:
        pass

def print_key(key : Key | str):
    if isinstance(key,str):
        print(key)
    elif isinstance(key,Key):
        print(key.value,key.name)
    else:
        print(f"Unknown key: {key.value}, {type(key.value)}")

def on_release(key):
    pass
    #print(key)


ref_button = Button(root,height=1,width=15,text="Reload profile",command=refreshConfigs,fg="white",bg="#2A2A2A",font=('Calibri 15 bold'))
ref_button.place(x=0,y=0)
#show_ico = Button(root,height=1,width=15,text="View icons",command=refreshConfigs,fg="white",bg="#2A2A2A",font=('Calibri 15 bold'))
#show_ico.place(x=200,y=0)

for i in range(8):
    btns.append(None)
    def selectLocal(i=i):
        selectButton(i)
    btns[i] = Button(root, image=phi, height=120, width=120, command=selectLocal, bg="black", activebackground="black")
    btns[i].place(x=((i % 4)*190)+rootX+50, y = ((i // 4)*140)+rootY)

bg = Button(root,image=phi, height=100, width = 800, bg="black",command=selectScreen)
bg.place(x=rootX,y=290+rootY)

for i in range(4):
    dials.append(None)
    def selectLocal(i=i):
        selectDial(i)
    dials[i] = Button(root,image=phi, height=120, width=120, command=selectLocal,bg="black",activebackground="black")
    dials[i].place(x=((i % 4)*190)+rootX+50, y = ((i // 4)*140)+rootY+420)

#vsf = VerticalScrolledFrame(root)
#vsf.place(x=250,y=250)
#vsf.interior.configure(width=500,height=5000,style="MyFrame.TFrame")
#Button(vsf.interior,width=50,height=20,text="Hi there").place(x=50,y=50)

buildPages()
loadPage()

if os.path.exists(pth+sep+"icon.png"):
    ico = ImageTk.PhotoImage(Image.open(pth+sep+"icon.png"))
    root.wm_iconphoto(False,ico)
elif os.path.exists(pth+sep+"icon.svg"):
    ico = ImageTk.PhotoImage(readSvg(pth+sep+"icon.svg"))
    root.wm_iconphoto(False,ico)

#Listener(print_key,on_release=on_release).start()

root.bind('<KeyPress>',on_press)
root.bind('<KeyRelease>',on_release)
root.mainloop()

# while True:
#     cmd = input("Enter a command: ")
#     if cmd == "reload":
#         with open(cfgpth,"r") as f:
#             cfg = json.loads(f.read())
#             page = 0
#             loadPage()
#     elif cmd == "quit":
#         break
#     elif cmd == "help":
#         lst = {"help": "Shows a list of commands", "quit": "Stops the program", "reload": "Reloads the loaded profile"}
#     else:
#         print(f"Unrecognized command '{cmd}'. Type 'help' for a list of commands.")
            


#config docs
#Objects: screen, button, dial

#Screen:
#- events: up, down, left, right, touchShort, touchLong
#- properties: image

#Button: 
#- events: press, release
#- properties: imageOn, imageOff, text

#Dial events: press, clockwise, counterclockwise
#Dial has no properties ^

#Software made by goglesq (@animepfp on Discord) 
#u/goglesq
#https://github.com/goglesquirmintontheiii