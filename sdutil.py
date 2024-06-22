import re
import os
from PIL import ImageFont

sep="/"
fontpth="/"

def getselection(prompt):
    temp = input(prompt)
    return temp.lower() in ["y","yes","yeah"]

def procEnv(text,globals={},**kwargs):
    cont = re.findall("\${([^{}]*)}", text)
    gkeys = globals.keys()
    lkeys = []
    kwk = kwargs.keys()
    for i in cont:
        if i in gkeys:
            text = text.replace("${"+i+"}", str(globals[i]))
        elif i in lkeys:
            text = text.replace("${"+i+"}", str(locals[i]))
        elif i in kwk:
            text = text.replace("${"+i+"}", str(kwargs[i]))
        else:
            try:
                text = text.replace("${"+i+"}", str(eval(i,globals(),kwargs if len(kwk) > 0 else locals)))
            except:
                print(f"WARNING: Eval failure during evaluation of '{i}' - did you enter an invalid local or global name?")

    return text


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
    
def font(v,size=20):
    if os.path.exists(fontpth+sep+v+".ttf"):
        return ImageFont.truetype(fontpth+sep+v+".ttf",size)

def handleArgs(v : dict, args : dict):
    keys = v.keys()
    out = {k:val[1](v[k]) if k in keys else val[0] for k,val in args.items()}
    
    if 'font_size' in keys:
        out["font"] = font(out['font']  if "font" in keys else "Roboto-Regular",v["font_size"])
    return out
