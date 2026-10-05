import tkinter as tk

from tkinter import font

import cv2

from PIL import Image, ImageTk, ImageEnhance

import numpy as np

import os, math, random

from datetime import datetime

# ============================================================

# SNAPBOX — PINK EDITION

# Run: python3 interface_test.py

# ============================================================

W, H = 1250, 800

BG = "#F8E9EE"

PANEL = "#171216"

PINK = "#D9829A"

LIGHT_PINK = "#F2B9C7"

PALE = "#FFF8FA"

INK = "#211A1F"

MUTED = "#8A737C"

root = tk.Tk()

root.title("SnapBox")

root.geometry(f"{W}x{H}")

root.minsize(1050, 700)

root.configure(bg=BG)

canvas = tk.Canvas(root, bg=BG, highlightthickness=0)

canvas.pack(fill="both", expand=True)

FAMILIES = set(font.families(root))

def pick_font(names, fallback="Helvetica"):

    for n in names:

        if n in FAMILIES:

            return n

    return fallback

DISPLAY = pick_font(["Bodoni 72", "Didot", "Bodoni MT", "Times New Roman"])

SANS = pick_font(["Avenir Next", "Helvetica Neue", "Helvetica"])

FILTERS = ["ORIGINAL", "VINTAGE", "B&W", "CREAM", "COOL", "FADED", "NOIR"]

FRAMES = ["NONE", "CLASSIC", "FILM", "SOFT", "POLAROID", "PEARL", "RIBBON"]

COLLAGES = [2, 3, 4, 5, 8]

PHOTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")

os.makedirs(PHOTO_DIR, exist_ok=True)

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)

cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

mode = "WELCOME"         # WELCOME / CAMERA / REVIEW

panel = None              # FILTERS / FRAMES / COLLAGE

current_filter = "ORIGINAL"

current_frame = "NONE"

collage_target = 1

collage_frames = []

busy = False

count_job = None

flash_job = None

camera_photo = None

review_photo = None

# ---------- drawing ----------

def rounded_box(x1, y1, x2, y2, r=16, fill=PANEL, outline=""):

    pts = [x1+r,y1, x2-r,y1, x2,y1+r, x2,y2-r,

           x2-r,y2, x1+r,y2, x1,y2-r, x1,y1+r]

    return canvas.create_polygon(pts, smooth=True, fill=fill, outline=outline)

def text(x, y, value, size=10, fill=INK, family=None, anchor="center", weight="normal", tags=None):

    f = font.Font(family=family or SANS, size=size, weight=weight)

    return canvas.create_text(x, y, text=value, fill=fill, font=f, anchor=anchor, tags=tags)

def background():

    canvas.delete("all")

    canvas.configure(bg=BG)

    text(42, 38, "SNAPBOX", 25, INK, DISPLAY, "w")

    text(43, 64, "RETRO PHOTO BOOTH", 8, MUTED, SANS, "w", "bold")

    text(W-42, 38, "PINK EDITION", 8, MUTED, SANS, "e", "bold")

def welcome_layout():
    canvas.delete("all")
    canvas.configure(bg=BG)
    text(625, 170, "WELCOME TO", 18, MUTED, SANS, weight="bold")
    text(625, 225, "SNAPBOX", 58, INK, DISPLAY, weight="bold")
    text(625, 285, "YOUR OWN LITTLE PHOTO BOOTH", 11, MUTED, SANS, weight="bold")
    rounded_box(430, 380, 820, 455, 18, PANEL)
    text(625, 417, "CLICK HERE TO START", 12, "#FFFFFF", SANS, weight="bold")
    text(625, 520, "Capture a moment. Make it yours.", 10, "#9D858E", SANS)


def camera_layout():

    background()

    # Left: simple decorative panel.

    rounded_box(34, 125, 190, 640, 22, PANEL)

    text(112, 160, "SNAPBOX", 10, "#EBCFD8", SANS, weight="bold")

    text(112, 183, "MAKE A MEMORY", 8, "#9D858E", SANS, weight="bold")

    # Camera shell. The live image is placed ABOVE the shell's inner rectangle.

    canvas.create_rectangle(270, 105, 980, 650, fill=PANEL, outline="")

    canvas.create_rectangle(286, 121, 964, 635, fill="#332A30", outline="#F1C5D1", width=2)

    text(625, 86, "LIVE CAMERA", 9, MUTED, SANS, weight="bold")

    # Right controls.

    rounded_box(1008, 125, 1217, 640, 22, PANEL)

    text(1112, 160, "CREATE", 10, "#EBCFD8", SANS, weight="bold")

    button(1030, 190, 165, 44, "FILTERS", False, enabled=False)

    button(1030, 246, 165, 44, "FRAMES", False, enabled=False)

    button(1030, 302, 165, 44, "COLLAGE", panel == "COLLAGE", enabled=True)

    if panel == "COLLAGE":

        collage_menu()

    # Shutter.

    canvas.create_oval(548, 680, 702, 834, fill=BG, outline="")

    canvas.create_oval(558, 690, 692, 824, fill=PANEL, outline="#FFFFFF", width=3)

    canvas.create_oval(575, 707, 675, 807, fill=LIGHT_PINK, outline="")

    text(625, 757, "●", 24, PANEL, SANS)

    text(625, 670, "SHUTTER", 8, MUTED, SANS, weight="bold")

def button(x, y, w, h, title, selected=False, enabled=True):

    if not enabled:

        bg = "#2A2227"; fg = "#74676E"

    else:

        bg = "#FFFFFF" if selected else "#2A2227"

        fg = PANEL if selected else "#FFFFFF"

    rounded_box(x, y, x+w, y+h, 11, bg)

    text(x+w/2, y+h/2, title, 9, fg, SANS, weight="bold")

def collage_menu():

    # Menu is inside the right panel, never over the live camera.

    x1, y1, x2, y2 = 1022, 360, 1203, 615

    rounded_box(x1, y1, x2, y2, 16, "#211A1F")

    text(1112, 382, "CHOOSE COLLAGE", 9, "#EBCFD8", SANS, weight="bold")

    yy = 402

    for n in COLLAGES:

        active = n == collage_target and len(collage_frames) == 0

        rounded_box(1037, yy, 1188, yy+32, 9, "#FFFFFF" if active else "#30282D")

        text(1112, yy+16, f"{n} PHOTOS", 8, PANEL if active else "#FFFFFF", SANS, weight="bold")

        yy += 39

# ---------- image processing ----------

def fit_cv(frame, w, h):

    fh, fw = frame.shape[:2]

    ratio = max(w/fw, h/fh)

    nw, nh = int(fw*ratio), int(fh*ratio)

    resized = cv2.resize(frame,(nw,nh),interpolation=cv2.INTER_AREA)

    x=(nw-w)//2; y=(nh-h)//2

    return resized[y:y+h,x:x+w].copy()

def apply_filter(img, name):

    if img is None: return None

    out=img.copy()

    if name=="ORIGINAL": return out

    if name=="B&W":

        g=cv2.cvtColor(out,cv2.COLOR_BGR2GRAY)

        return cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)

    if name=="VINTAGE":

        b,g,r=cv2.split(out.astype(np.float32))

        arr=np.dstack([b*.88,g*.98,r*1.06]).clip(0,255).astype(np.uint8)

        pil=Image.fromarray(cv2.cvtColor(arr,cv2.COLOR_BGR2RGB))

        pil=ImageEnhance.Contrast(pil).enhance(.92)

        pil=ImageEnhance.Color(pil).enhance(.72)

        return cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR)

    if name=="CREAM":

        out=cv2.convertScaleAbs(out,alpha=.88,beta=20)

        b,g,r=cv2.split(out); r=np.clip(r*1.04,0,255).astype(np.uint8)

        return cv2.merge([b,g,r])

    if name=="COOL":

        b,g,r=cv2.split(out.astype(np.float32))

        return np.dstack([b*1.08,g,r*.92]).clip(0,255).astype(np.uint8)

    if name=="FADED":

        return cv2.GaussianBlur(cv2.convertScaleAbs(out,alpha=.78,beta=25),(3,3),0)

    if name=="NOIR":

        g=cv2.cvtColor(out,cv2.COLOR_BGR2GRAY)

        g=cv2.convertScaleAbs(g,alpha=1.55,beta=-35)

        return cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)

    return out

def vignette(img, strength=.10):

    h,w=img.shape[:2]

    Y,X=np.ogrid[:h,:w]

    dx=(X-w/2)/(w/2); dy=(Y-h/2)/(h/2)

    mask=1-strength*np.clip((dx*dx+dy*dy)/2,0,1)

    return np.clip(img*mask[...,None],0,255).astype(np.uint8)

def add_frame_cv(img,name):

    out=img.copy(); h,w=out.shape[:2]

    def rect(m,col=(25,25,25),th=5):

        cv2.rectangle(out,(m,m),(w-m-1,h-m-1),col,th)

    if name=="CLASSIC": rect(8,(245,242,236),9)

    elif name=="FILM":

        rect(8,(20,20,20),12)

        for yy in range(22,h-15,35):

            cv2.rectangle(out,(12,yy),(28,yy+18),(235,235,235),-1)

            cv2.rectangle(out,(w-29,yy),(w-13,yy+18),(235,235,235),-1)

    elif name=="SOFT": rect(9,(220,188,190),15)

    elif name=="POLAROID":

        rect(10,(255,255,255),20)

        cv2.putText(out,"SNAPBOX",(w-155,h-25),cv2.FONT_HERSHEY_SIMPLEX,.55,(110,110,110),1,cv2.LINE_AA)

    elif name=="PEARL": rect(8,(205,195,185),9)

    elif name=="RIBBON":

        rect(8,(45,28,35),6)

        pink=(190,105,135)

        light=(220,145,165)

        # elegant corner bows

        for cx,cy in [(58,58),(w-58,h-58)]:

            cv2.ellipse(out,(cx-24,cy-8),(cx,cy+10),20,0,360,pink,-1)

            cv2.ellipse(out,(cx,cy-8),(cx+24,cy+10),-20,0,360,pink,-1)

            cv2.circle(out,(cx,cy),10,light,-1)

            cv2.fillPoly(out,[np.array([[cx-6,cy+6],[cx-30,cy+32],[cx-8,cy+18]],np.int32)],pink)

            cv2.fillPoly(out,[np.array([[cx+6,cy+6],[cx+30,cy+32],[cx+8,cy+18]],np.int32)],pink)

        # tiny flowers, kept sparse

        for cx,cy in [(76,h-52),(w-76,52)]:

            for ang in range(0,360,72):

                rad=np.deg2rad(ang)

                px=int(cx+12*np.cos(rad)); py=int(cy+12*np.sin(rad))

                cv2.circle(out,(px,py),7,(225,160,180),-1)

            cv2.circle(out,(cx,cy),6,(245,205,100),-1)

    return out

# ---------- display ----------

def show_camera_frame(frame):

    global camera_photo

    # Crop the live feed to the exact camera window so it is always visible.

    fitted = fit_cv(frame, 678, 494)

    rgb=cv2.cvtColor(fitted,cv2.COLOR_BGR2RGB)

    pil=Image.fromarray(rgb).resize((678,494),Image.Resampling.LANCZOS)

    camera_photo=ImageTk.PhotoImage(pil)

    canvas.delete("CAMERA_IMAGE")

    canvas.create_image(286,144,image=camera_photo,anchor="nw",tags="CAMERA_IMAGE")

    canvas.tag_raise("CAMERA_IMAGE")

def make_collage():

    imgs=list(collage_frames)

    if not imgs: return None

    if len(imgs)==1: return imgs[0].copy()

    cellw,cellh=300,220

    gap,pad=14,20

    if collage_target==2: cols,rows=2,1

    elif collage_target==3: cols,rows=3,1

    elif collage_target==4: cols,rows=2,2

    elif collage_target==5: cols,rows=3,2

    else: cols,rows=4,2

    out=np.full((rows*cellh+(rows+1)*gap,cols*cellw+(cols+1)*gap,3),248,np.uint8)

    for i,img in enumerate(imgs):

        thumb=fit_cv(img,cellw,cellh)

        r=i//cols; c=i%cols

        yy=gap+r*(cellh+gap); xx=gap+c*(cellw+gap)

        out[yy:yy+cellh,xx:xx+cellw]=thumb

    return out

def review_layout():

    global review_photo

    background()

    # photo area

    rounded_box(205,105,930,660,22,PANEL)

    base=make_collage()

    if base is not None:

        base=apply_filter(base,current_filter)

        base=vignette(base,.10)

        base=add_frame_cv(base,current_frame)

        rgb=cv2.cvtColor(base,cv2.COLOR_BGR2RGB)

        pil=Image.fromarray(rgb)

        ratio=min(690/pil.width,500/pil.height)

        pil=pil.resize((int(pil.width*ratio),int(pil.height*ratio)),Image.Resampling.LANCZOS)

        review_photo=ImageTk.PhotoImage(pil)

        canvas.create_image(568,380,image=review_photo,anchor="center",tags="REVIEW_IMAGE")

    # right panel

    rounded_box(950,105,1217,660,20,PANEL)

    text(975,135,"YOUR PHOTO",9,"#D7C8CE",SANS,"w",weight="bold")

    button(970,153,108,34,"FILTERS",panel=="FILTERS",True)

    button(1088,153,108,34,"FRAMES",panel=="FRAMES",True)

    button(970,197,226,34,"COLLAGE",panel=="COLLAGE",True)

    if panel=="FILTERS":

        option_list(970,246,226,FILTERS,current_filter)

    elif panel=="FRAMES":

        option_list(970,246,226,FRAMES,current_frame)

    elif panel=="COLLAGE":

        text(1083,265,"COLLAGE ALREADY CAPTURED",9,"#FFFFFF",SANS,weight="bold")

        text(1083,287,"Retake to choose another layout.",8,"#BDB0B6",SANS)

    else:

        text(1083,300,"MAKE IT YOURS",12,"#FFFFFF",DISPLAY)

        text(1083,330,"Pick a filter or frame.",9,"#BDB0B6",SANS)

    # bottom actions

    rounded_box(205,680,930,750,18,PANEL)

    button(235,696,190,38,"RETAKE",False,True)

    button(445,696,330,38,"SAVE PHOTO",True,True)

    text(850,715,"saved photos",8,"#A9979F",SANS)

def option_list(x,y,w,items,selected):

    yy=y

    for item in items:

        active=item==selected

        rounded_box(x,yy,x+w,yy+34,10,"#FFFFFF" if active else "#272126")

        text(x+w/2,yy+17,item,9,PANEL if active else "#FFFFFF",SANS,weight="bold")

        yy+=40

# ---------- camera / capture ----------

def camera_loop():

    if mode=="CAMERA":

        ret,frame=cap.read()

        if ret:

            frame=cv2.flip(frame,1)

            show_camera_frame(frame)

    root.after(30,camera_loop)

def flash():

    canvas.delete("FLASH")

    canvas.create_rectangle(286,144,964,638,fill="#FFFFFF",outline="",tags="FLASH")

    canvas.tag_raise("FLASH")

    root.after(110,lambda:canvas.delete("FLASH"))

def countdown(n):

    global count_job

    if not busy: return

    canvas.delete("COUNT")

    f=font.Font(family=DISPLAY,size=96,weight="normal")

    canvas.create_text(625,390,text=str(n),fill="#FFFFFF",font=f,tags="COUNT")

    canvas.tag_raise("COUNT")

    if n>1:

        count_job=root.after(700,lambda:countdown(n-1))

    else:

        count_job=root.after(700,capture_photo)

def start_countdown():

    canvas.delete("COUNT")

    f=font.Font(family=DISPLAY,size=28)

    canvas.create_text(625,390,text="GET READY",fill="#FFFFFF",font=f,tags="COUNT")

    canvas.tag_raise("COUNT")

    root.after(600,lambda:countdown(3))

def take_photo(event=None):

    global busy

    if mode!="CAMERA" or busy: return

    # If collage menu is open, clicks there are handled separately.

    busy=True

    start_countdown()

def capture_photo():

    global busy, collage_frames, mode, panel

    canvas.delete("COUNT")

    ret,frame=cap.read()

    if not ret:

        busy=False

        return

    frame=cv2.flip(frame,1)

    shot=fit_cv(frame,900,506)

    collage_frames.append(shot.copy())

    flash()

    busy=False

    panel=None

    if len(collage_frames) < collage_target:

        # Keep camera alive and clearly tell user what is next.

        camera_layout()

        text(625,108,f"COLLAGE • PHOTO {len(collage_frames)} / {collage_target} • CLICK SHUTTER FOR NEXT",

             9,INK,SANS,weight="bold")

    else:

        mode="REVIEW"

        review_layout()

def start_snapbox():
    global mode, panel, collage_frames, collage_target, current_filter, current_frame, busy
    mode = "CAMERA"
    panel = None
    collage_frames = []
    collage_target = 1
    current_filter = "ORIGINAL"
    current_frame = "NONE"
    busy = False
    camera_layout()


# ---------- actions ----------

def start_collage(n):

    global collage_target, collage_frames, mode, panel, current_filter, current_frame, busy

    collage_target=n

    collage_frames=[]

    current_filter="ORIGINAL"

    current_frame="NONE"

    panel=None

    busy=False

    mode="CAMERA"

    camera_layout()

    text(625,108,f"COLLAGE • {n} PHOTOS • PHOTO 1 OF {n}",9,INK,SANS,weight="bold")

def retake():

    global mode,panel,collage_frames,collage_target,current_filter,current_frame,busy

    mode="CAMERA"; panel=None; collage_frames=[]; collage_target=1

    current_filter="ORIGINAL"; current_frame="NONE"; busy=False

    camera_layout()

def save_photo():

    if not collage_frames: return

    final=make_collage()

    final=apply_filter(final,current_filter)

    final=vignette(final,.10)

    final=add_frame_cv(final,current_frame)

    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")

    path=os.path.join(PHOTO_DIR,f"snapbox_{stamp}.jpg")

    cv2.imwrite(path,final,[cv2.IMWRITE_JPEG_QUALITY,95])

    review_layout()

    text(568,635,"SAVED ✓  "+os.path.basename(path),9,"#FFFFFF",SANS,weight="bold")

    root.after(2200,review_layout)

# ---------- mouse ----------

def click(event):

    global panel,current_filter,current_frame

    x,y=event.x,event.y

    if mode=="WELCOME":
        if 430 <= x <= 820 and 380 <= y <= 455:
            start_snapbox()
        return

    if mode=="CAMERA":

        # Collage button: opens the working layout selector.

        if 1030<=x<=1195 and 302<=y<=346:

            panel="COLLAGE"

            camera_layout()

            return

        # Collage selector popup

        if panel=="COLLAGE" and 1037<=x<=1188 and 402<=y<=595:

            yy=402

            for n in COLLAGES:

                if yy<=y<=yy+36:

                    start_collage(n)

                    return

                yy+=43

        # shutter

        if 548<=x<=702 and 680<=y<=799:

            take_photo()

            return

    elif mode=="REVIEW":

        if 970<=x<=1078 and 153<=y<=187:

            panel="FILTERS"; review_layout(); return

        if 1088<=x<=1196 and 153<=y<=187:

            panel="FRAMES"; review_layout(); return

        if 970<=x<=1196 and 197<=y<=231:

            panel="COLLAGE"; review_layout(); return

        if panel=="FILTERS":

            for i,n in enumerate(FILTERS):

                yy=246+i*40

                if yy<=y<=yy+34:

                    current_filter=n; review_layout(); return

        elif panel=="FRAMES":

            for i,n in enumerate(FRAMES):

                yy=246+i*40

                if yy<=y<=yy+34:

                    current_frame=n; review_layout(); return

        if 235<=x<=425 and 696<=y<=734:

            retake(); return

        if 445<=x<=775 and 696<=y<=734:

            save_photo(); return

canvas.bind("<Button-1>",click)

root.bind("<space>",take_photo)

root.bind("<Escape>",lambda e: retake() if mode=="REVIEW" else None)

def close():

    try: cap.release()

    except: pass

    root.destroy()

root.protocol("WM_DELETE_WINDOW",close)

welcome_layout()

root.after(30,camera_loop)

root.mainloop()