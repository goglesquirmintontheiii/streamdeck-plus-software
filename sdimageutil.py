from PIL import Image, ImageDraw
import io
import cairosvg
import os



lookup = {}
icons = {}
iconpth = "/"
sep = "/"

def readSvg(path : str):
    """Read an svg as a PIL image using cairosvg"""
    out = io.BytesIO()
    cairosvg.svg2png(url=path,write_to=out)
    return Image.open(out)

def filterOpen(path, expectedSize=(120,120)) -> Image:
    """Open any image, and auto-resize it to expectedSize"""
    if path.endswith('.svg'):
        return readSvg(path).resize(expectedSize)
    else:
        return Image.open(path).resize(expectedSize)
    
def getData(img : Image):
    """Get image data"""
    otp = io.BytesIO()
    try:
        img.save(otp,format="JPEG")
    except:
        background = Image.new("RGB", img.size, (0, 0, 0))
        background.paste(img, mask=img.split()[3])
        background.save(otp,format="JPEG")
    return otp.getvalue()

def add_corners(im, rad):
    """Add corners to an image"""
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    blackimg = Image.new("RGB",(w,h),(0,0,0))
    blackimg.paste(im)
    new = Image.new("RGBA",(w,h),(42,42,42,255))
    new.paste(blackimg,mask=alpha)
    return new

def handleImage(img : str, expectedSize : tuple = (120,120)) -> Image:
    """Returns an image. Set globals lookup, icons, and iconpth for it to work fully."""
    global iconpth
    global sep
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
