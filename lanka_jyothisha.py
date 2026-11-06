# -*- coding: utf-8 -*-
"""
Lanka Jyothisha Desktop - Windows starter application.
Astrological calculations use Swiss Ephemeris (pyswisseph), Lahiri sidereal zodiac.
"""
import csv
import math
import os
import sys
import threading
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import swisseph as swe
except Exception:
    swe = None

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
TZ = ZoneInfo("Asia/Colombo")
SIGNS = ["මේෂ", "වෘෂභ", "මිථුන", "කටක", "සිංහ", "කන්‍යා",
         "තුලා", "වෘශ්චික", "ධනු", "මකර", "කුම්භ", "මීන"]
SIGN_EN = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
           "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NAKSHATRAS = [
"අස්විද","බෙරණ","කැති","රෙහෙණ","මුවසිරස","අද","පුනාවස","පුෂ","අස්ලිස",
"මා","පුවපල්","උත්‍රපල්","හත","සිත","සා","විසා","අනුර","දෙට",
"මූල","පුවසල","උත්‍රසල","සුවණ","දෙනට","සියාවස","පුවපුටුප","උත්‍රපුටුප","රේවතී"
]
PLANETS = [
    ("සූර්ය", "Sun", swe.SUN if swe else 0),
    ("චන්ද්‍ර", "Moon", swe.MOON if swe else 1),
    ("කුජ", "Mars", swe.MARS if swe else 4),
    ("බුධ", "Mercury", swe.MERCURY if swe else 2),
    ("ගුරු", "Jupiter", swe.JUPITER if swe else 5),
    ("සිකුරු", "Venus", swe.VENUS if swe else 3),
    ("ශනි", "Saturn", swe.SATURN if swe else 6),
    ("රාහු", "Rahu", swe.MEAN_NODE if swe else 10),
]
DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,
               "Jupiter":16,"Saturn":19,"Mercury":17}
DASHA_SI = {"Ketu":"කේතු","Venus":"සිකුරු","Sun":"සූර්ය","Moon":"චන්ද්‍ර",
            "Mars":"කුජ","Rahu":"රාහු","Jupiter":"ගුරු","Saturn":"ශනි","Mercury":"බුධ"}

# District administrative-centre coordinates; users can import a richer location CSV.
DISTRICTS = [
("කොළඹ","Colombo",6.848,80.029),("ගම්පහ","Gampaha",7.119,80.021),
("කළුතර","Kalutara",6.576,80.135),("මහනුවර","Kandy",7.215,80.641),
("මාතලේ","Matale",7.698,80.660),("නුවරඑළිය","Nuwara Eliya",7.013,80.757),
("ගාල්ල","Galle",6.204,80.231),("මාතර","Matara",5.945,80.548),
("හම්බන්තොට","Hambantota",6.142,81.121),("යාපනය","Jaffna",9.661,80.025),
("කිලිනොච්චි","Kilinochchi",9.380,80.377),("මන්නාරම","Mannar",8.981,79.904),
("වවුනියාව","Vavuniya",8.751,80.497),("මුලතිව්","Mullaitivu",9.267,80.814),
("මඩකලපුව","Batticaloa",7.731,81.674),("අම්පාර","Ampara",7.297,81.682),
("ත්‍රිකුණාමලය","Trincomalee",8.587,81.215),("කුරුණෑගල","Kurunegala",7.486,80.362),
("පුත්තලම","Puttalam",8.036,79.828),("අනුරාධපුර","Anuradhapura",8.311,80.403),
("පොළොන්නරුව","Polonnaruwa",7.940,81.018),("බදුල්ල","Badulla",6.993,81.055),
("මොනරාගල","Monaragala",6.872,81.350),("රත්නපුර","Ratnapura",6.682,80.399),
("කෑගල්ල","Kegalle",7.251,80.346)
]

# Natural relationship matrix (Parashari-style natural friendships).
FRIENDS = {
"Sun":{"friend":["Moon","Mars","Jupiter"],"enemy":["Venus","Saturn"],"neutral":["Mercury"]},
"Moon":{"friend":["Sun","Mercury"],"enemy":[],"neutral":["Mars","Jupiter","Venus","Saturn"]},
"Mars":{"friend":["Sun","Moon","Jupiter"],"enemy":["Mercury"],"neutral":["Venus","Saturn"]},
"Mercury":{"friend":["Sun","Venus"],"enemy":["Moon"],"neutral":["Mars","Jupiter","Saturn"]},
"Jupiter":{"friend":["Sun","Moon","Mars"],"enemy":["Mercury","Venus"],"neutral":["Saturn"]},
"Venus":{"friend":["Mercury","Saturn"],"enemy":["Sun","Moon"],"neutral":["Mars","Jupiter"]},
"Saturn":{"friend":["Mercury","Venus"],"enemy":["Sun","Moon","Mars"],"neutral":["Jupiter"]},
"Rahu":{"friend":[],"enemy":[],"neutral":["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]}
}
OWN_SIGNS = {
"Sun":[4], "Moon":[3], "Mars":[0,7], "Mercury":[2,5],
"Jupiter":[8,11], "Venus":[1,6], "Saturn":[9,10], "Rahu":[10]
}
EXALT = {"Sun":0,"Moon":1,"Mars":9,"Mercury":5,"Jupiter":3,"Venus":11,"Saturn":6}
DEBIL = {"Sun":6,"Moon":7,"Mars":3,"Mercury":11,"Jupiter":9,"Venus":5,"Saturn":0}
DIG_BALA_HOUSES = {"Jupiter":1,"Mercury":1,"Sun":10,"Mars":10,
                   "Moon":4,"Venus":4,"Saturn":7,"Rahu":None}

def dms(lon):
    lon = lon % 360
    sidx = int(lon // 30)
    x = lon - 30*sidx
    d = int(x); mfloat = (x-d)*60; m = int(mfloat); sec = round((mfloat-m)*60)
    if sec >= 60: sec=0; m+=1
    if m >= 60: m=0; d+=1
    if d >= 30: d=0; sidx=(sidx+1)%12
    return SIGNS[sidx], d, m, sec

def fmt_dms(lon):
    s,d,m,sec = dms(lon)
    return f"{s} {d:02d}° {m:02d}' {sec:02d}\""

def nakshatra_info(lon):
    span = 360/27
    x = lon % 360
    idx = min(26, int(x/span))
    within = x - idx*span
    pada = min(4, int(within/(span/4))+1)
    return NAKSHATRAS[idx], pada, idx

def navamsa_sign(lon):
    sign = int((lon%360)//30)
    within = (lon%30)
    pada = min(8, int(within/(30/9)))
    modality = sign % 3
    # movable signs start from themselves; fixed from 9th; dual from 5th
    start = sign if modality == 0 else (sign+8)%12 if modality == 1 else (sign+4)%12
    return (start+pada)%12

def jd_from_local(dt):
    utc = dt.astimezone(timezone.utc)
    return swe.julday(utc.year, utc.month, utc.day,
                      utc.hour + utc.minute/60 + utc.second/3600, swe.GREG_CAL)

def get_chart(dt, lat, lon):
    if swe is None:
        raise RuntimeError("Swiss Ephemeris නැත. pip install pyswisseph කරන්න.")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = jd_from_local(dt)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    planets = {}
    for si, en, body in PLANETS:
        xx, ret = swe.calc_ut(jd, body, flags)
        planets[en] = {"lon": xx[0] % 360, "speed": xx[3]}
    rahu = planets["Rahu"]["lon"]
    planets["Ketu"] = {"lon":(rahu+180)%360, "speed":-planets["Rahu"]["speed"]}
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    asc, mc = ascmc[0]%360, ascmc[1]%360
    return jd, planets, [x%360 for x in cusps], asc, mc

def house_of(lon, cusps, asc):
    # Map longitude to the next cusp interval (Placidus cusp longitudes).
    for i in range(12):
        a = cusps[i] % 360
        b = cusps[(i+1)%12] % 360
        x = lon % 360
        width = (b-a)%360
        dist = (x-a)%360
        if dist < width or (i == 11 and math.isclose(dist,width)):
            return i+1
    return 1

def dignity(en, lon):
    sign = int((lon%360)//30)
    if en in EXALT and sign == EXALT[en]: return "උච්ච"
    if en in DEBIL and sign == DEBIL[en]: return "නීච"
    if sign in OWN_SIGNS.get(en,[]): return "ස්වක්ෂේත්‍ර"
    return "සාමාන්‍ය / තාවකාලික මිත්‍ර-සතුරු තීරණය වෙනම"

def drishti_targets(en, house):
    offsets = {"Mars":[4,7,8],"Jupiter":[5,7,9],"Saturn":[3,7,10]}
    return [((house-1+x-1)%12)+1 for x in offsets.get(en,[7])]

def dasha_rows(birth_dt, moon_lon, years_ahead=120):
    nak, pada, idx = nakshatra_info(moon_lon)
    lord = DASHA_ORDER[idx%9]
    span = 360/27
    elapsed_fraction = ((moon_lon%360)-idx*span)/span
    remaining = DASHA_YEARS[lord]*(1-elapsed_fraction)
    start_idx = DASHA_ORDER.index(lord)
    cursor = birth_dt
    rows = []
    # First balance then full cycles, with antardasha nested proportionally.
    maha_list = [(lord, remaining)]
    for k in range(1, 30):
        maha_list.append((DASHA_ORDER[(start_idx+k)%9],
                          DASHA_YEARS[DASHA_ORDER[(start_idx+k)%9]]))
    for maha, yrs in maha_list:
        if cursor > birth_dt + timedelta(days=365.25636*years_ahead):
            break
        end = cursor + timedelta(days=yrs*365.25636)
        sub_order_start = DASHA_ORDER.index(maha)
        sub_cursor = cursor
        for j in range(9):
            sub = DASHA_ORDER[(sub_order_start+j)%9]
            sub_years = yrs * DASHA_YEARS[sub] / 120
            sub_end = sub_cursor + timedelta(days=sub_years*365.25636)
            praty_cursor = sub_cursor
            praty_start = DASHA_ORDER.index(sub)
            for k in range(9):
                praty = DASHA_ORDER[(praty_start+k)%9]
                praty_years = sub_years * DASHA_YEARS[praty] / 120
                praty_end = praty_cursor + timedelta(days=praty_years*365.25636)
                rows.append((maha, sub, praty, praty_cursor, praty_end))
                praty_cursor = praty_end
            sub_cursor = sub_end
        cursor = end
    return nak, pada, lord, rows

def load_location_rows(path):
    rows=[]
    with open(path,encoding="utf-8-sig",newline="") as f:
        # Open Admin Data CSV begins with a licence/comment line before its header.
        cleaned = (line for line in f if line.strip() and not line.lstrip().startswith("#"))
        reader=csv.DictReader(cleaned)
        for r in reader:
            # Accept columns from Open Admin Data all-flat.csv
            level = (r.get("level") or "").strip()
            if level and level not in ("2","3","4"): continue
            name_en = r.get("name.en") or r.get("name_en") or r.get("name") or ""
            name_si = r.get("name.local") or r.get("name_si") or name_en
            district = r.get("parent.name.en") or r.get("district") or ""
            lat = r.get("geo.lat") or r.get("latitude") or r.get("lat")
            lon = r.get("geo.lon") or r.get("longitude") or r.get("lon")
            try: rows.append((name_si, name_en, float(lat), float(lon), district))
            except Exception: continue
    return rows

class JyothishaApp:
    def __init__(self, root):
        self.root=root
        root.title("ලංකා ජ්‍යෝතිෂ | Lanka Jyothisha Desktop")
        root.geometry("1200x820")
        root.minsize(980,680)
        self.locations = [(si,en,lat,lon,en) for si,en,lat,lon in DISTRICTS]
        self.last_result=None
        self.nak_attributes = {}
        self.load_nak_attributes()
        self.build_ui()

    def load_nak_attributes(self):
        path = APP_DIR / "nakshatra_attributes_template.csv"
        if not path.exists() and getattr(sys, "frozen", False):
            path = Path(getattr(sys, "_MEIPASS", APP_DIR)) / "nakshatra_attributes_template.csv"
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    key = (row.get("Nakshatra") or "").strip()
                    if key:
                        self.nak_attributes[key] = row
        except Exception:
            self.nak_attributes = {}

    def build_ui(self):
        style=ttk.Style()
        try: style.theme_use("clam")
        except: pass
        style.configure("Treeview",rowheight=25)
        top=ttk.Frame(self.root,padding=12); top.pack(fill="x")
        ttk.Label(top,text="ලංකා ජ්‍යෝතිෂ",font=("Nirmala UI",20,"bold")).pack(side="left")
        ttk.Label(top,text="2000–2150 | Lahiri | Sidereal | Placidus",font=("Nirmala UI",10)).pack(side="right")
        frm=ttk.LabelFrame(self.root,text="ජන්ම දිනය / වේලාව / ස්ථානය",padding=10)
        frm.pack(fill="x",padx=12,pady=5)
        self.date=tk.StringVar(value="2000-07-11")
        self.time=tk.StringVar(value="16:30:00")
        self.loc=tk.StringVar(value="Negombo / මීගමුව")
        self.search=tk.StringVar()
        for label,var,width in [("දිනය YYYY-MM-DD",self.date,16),("වේලාව HH:MM:SS",self.time,14)]:
            box=ttk.Frame(frm);box.pack(side="left",padx=6)
            ttk.Label(box,text=label).pack(anchor="w")
            ttk.Entry(box,textvariable=var,width=width).pack()
        box=ttk.Frame(frm);box.pack(side="left",padx=8,fill="x",expand=True)
        ttk.Label(box,text="ස්ථානය (සෙවීමට නම ටයිප් කරන්න)").pack(anchor="w")
        self.loc_combo=ttk.Combobox(box,textvariable=self.loc,values=[f"{x[1]} / {x[0]}" for x in self.locations],width=38)
        self.loc_combo.pack(fill="x")
        self.loc_combo.bind("<KeyRelease>",self.filter_locations)
        ttk.Button(frm,text="ස්ථාන CSV ආයාත කරන්න",command=self.import_locations).pack(side="left",padx=8)
        ttk.Button(frm,text="ගණනය කරන්න",command=self.calculate).pack(side="left",padx=8)
        ttk.Button(frm,text="CSV Export",command=self.export_chart).pack(side="left",padx=4)
        ttk.Button(frm,text="විනාඩි දත්ත නිපදවන්න",command=self.generate_minutes).pack(side="left",padx=4)

        note=ttk.Label(self.root,text="සටහන: උපන් කේන්දර දශා ගණනයට උපන් දිනය/වේලාව/ස්ථානය යොදන්න. විනාඩි දත්ත Export කිරීම තෝරාගත් ස්ථානය සඳහා පමණි.",foreground="#7a4b00")
        note.pack(anchor="w",padx=16,pady=2)

        nb=ttk.Notebook(self.root);nb.pack(fill="both",expand=True,padx=12,pady=8)
        self.tabs={}
        for key,title in [("graha","ග්‍රහ පිහිටීම් / බල"),("bhava","ලග්නය / භාව / නවාංශක"),("nak","නැකත් ගුණ"),("dasha","මහා දශා / අන්තර් දශා"),("yoga","ග්‍රහ දෘෂ්ටි / යෝග"),("about","ක්‍රමවේද / සීමා")]:
            frame=ttk.Frame(nb,padding=8);nb.add(frame,text=title);self.tabs[key]=frame
        self.graha_tree=self.make_tree(self.tabs["graha"],["ග්‍රහයා","රාශිය/ස්ඵුට","වේගය °/දින","ගමන","ගෞරවය","භාව","දික්බල"])
        self.bhava_text=self.make_text(self.tabs["bhava"])
        self.nak_text=self.make_text(self.tabs["nak"])
        self.dasha_tree=self.make_tree(self.tabs["dasha"],["මහා දශාව","අන්තර් දශාව","ප්‍රත්‍යන්තර දශාව","ආරම්භය","අවසානය"])
        self.yoga_text=self.make_text(self.tabs["yoga"])
        self.about_text=self.make_text(self.tabs["about"])
        self.about_text.insert("end",
"""ගණනයේ මූලික සැකසුම්
• Swiss Ephemeris / pyswisseph
• Lahiri Ayanamsa සහ Sidereal Zodiac
• Placidus භාව ක්‍රමය
• Mean Rahu; Ketu = Rahu + 180°
• ශ්‍රී ලංකා වේලා කලාපය Asia/Colombo (ඓතිහාසික DST ඇතුළුව)

වැදගත් සීමා සහ තහවුරු කළ යුතු අංග
• දික්බල මෙහි මූලික දිශා-ස්ථාන නියමය අනුව පෙන්වයි; සම්පූර්ණ ෂඩ්බල (Shadbala) ගණනය නොවේ.
• නැකත් ගණ/යෝනි/වෘක්ෂ/ලිංග/නාඩි/පක්ෂි/ගෝත්‍ර/වර්ණ/රජ්ජු/භූත වගුව සම්ප්‍රදාය අනුව වෙනස් විය හැකි නිසා හිස් template එකක් සපයා ඇත. ඔබගේ පිළිගත් වගුව ආයාත කළ හැක.
• යෝග හඳුනාගැනීමේදී දැනට සීමිත මූලික යෝග කිහිපයක් පමණක් පෙන්වයි; සියලුම යෝග සම්පූර්ණයෙන් නොවේ.
• විංශෝත්තරී දශා උපන් චන්ද්‍ර නැකත අනුව ගණනය කරයි. වෙනත් දශා පද්ධති මෙහි ඇතුළත් නැත.
• පරිපූර්ණ ගණනයකට යෝග, ග්‍රහ මිත්‍රත්වය, ශඩ්බල සහ නැකත් ගුණ වගු පාරම්පරික මූලාශ්‍රයකින් තහවුරු කරන්න.
""")
        self.status=tk.StringVar(value="සූදානම්")
        ttk.Label(self.root,textvariable=self.status,relief="sunken",anchor="w").pack(fill="x",side="bottom")

    def make_tree(self,parent,cols):
        f=ttk.Frame(parent);f.pack(fill="both",expand=True)
        tree=ttk.Treeview(f,columns=cols,show="headings")
        for c in cols:
            tree.heading(c,text=c);tree.column(c,width=145,anchor="center")
        sy=ttk.Scrollbar(f,orient="vertical",command=tree.yview)
        sx=ttk.Scrollbar(f,orient="horizontal",command=tree.xview)
        tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
        tree.grid(row=0,column=0,sticky="nsew");sy.grid(row=0,column=1,sticky="ns");sx.grid(row=1,column=0,sticky="ew")
        f.rowconfigure(0,weight=1);f.columnconfigure(0,weight=1)
        return tree

    def make_text(self,parent):
        t=tk.Text(parent,wrap="word",font=("Nirmala UI",11))
        sy=ttk.Scrollbar(parent,orient="vertical",command=t.yview);t.configure(yscrollcommand=sy.set)
        t.pack(side="left",fill="both",expand=True);sy.pack(side="right",fill="y")
        return t

    def filter_locations(self,event=None):
        q=self.loc.get().lower()
        vals=[f"{x[1]} / {x[0]}" for x in self.locations if q in x[1].lower() or q in x[0].lower()]
        self.loc_combo["values"]=vals[:100]

    def selected_location(self):
        val=self.loc.get()
        for x in self.locations:
            if val == f"{x[1]} / {x[0]}" or val.lower()==x[1].lower() or val.lower()==x[0].lower():
                return x
        # allow manually typed "name|lat|lon"
        if "|" in val:
            p=val.split("|")
            if len(p)>=3: return (p[0],p[0],float(p[1]),float(p[2]),p[0])
        raise ValueError("ස්ථානය ලැයිස්තුවෙන් තෝරන්න හෝ නම/අක්ෂාංශ/දේශාංශ ලබාදෙන්න.")

    def import_locations(self):
        path=filedialog.askopenfilename(title="ස්ථාන CSV තෝරන්න",filetypes=[("CSV","*.csv")])
        if not path:return
        try:
            rows=load_location_rows(path)
            if not rows: raise ValueError("latitude/longitude සහ place name තීරු සොයාගත නොහැකි විය.")
            self.locations.extend(rows)
            vals=[f"{x[1]} / {x[0]}" for x in self.locations]
            self.loc_combo["values"]=vals
            self.status.set(f"ස්ථාන {len(rows)}ක් ආයාත කළා.")
            messagebox.showinfo("ආයාත කිරීම සාර්ථකයි",f"ස්ථාන {len(rows)}ක් එකතු කළා.")
        except Exception as e: messagebox.showerror("දෝෂය",str(e))

    def calculate(self):
        try:
            date=datetime.strptime(self.date.get().strip(),"%Y-%m-%d").date()
            tm=datetime.strptime(self.time.get().strip(),"%H:%M:%S").time()
            dt=datetime.combine(date,tm).replace(tzinfo=TZ)
            loc=self.selected_location()
            si,en,lat,lon,district=loc
            jd,planets,cusps,asc,mc=get_chart(dt,lat,lon)
            houses={p:house_of(data["lon"],cusps,asc) for p,data in planets.items()}
            for item in self.graha_tree.get_children():self.graha_tree.delete(item)
            for si_name,en_name,_ in PLANETS:
                data=planets[en_name];h=houses[en_name]
                dignity_text=dignity(en_name,data["lon"])
                motion="වක්‍ර" if data["speed"]<0 else "සෘජු"
                dig_house=DIG_BALA_HOUSES.get(en_name)
                dig="උසස් දිශා ස්ථානය" if h==dig_house else ("නැත / මධ්‍යම" if dig_house else "නියමය වෙනම")
                self.graha_tree.insert("", "end", values=(si_name,fmt_dms(data["lon"]),f"{data['speed']:.5f}",motion,dignity_text,h,dig))
            k=planets["Ketu"]
            self.graha_tree.insert("", "end", values=("කේතු",fmt_dms(k["lon"]),f"{k['speed']:.5f}","වක්‍ර" if k["speed"]<0 else "සෘජු",dignity("Rahu",k["lon"]),houses["Ketu"],"නියමය වෙනම"))
            navasc=navamsa_sign(asc)
            self.bhava_text.delete("1.0","end")
            self.bhava_text.insert("end",f"ස්ථානය: {en} / {si} | {lat:.5f}, {lon:.5f}\nදිනය/වේලාව: {dt.isoformat()}\n\n")
            self.bhava_text.insert("end",f"ලග්නය: {fmt_dms(asc)}\nනවාංශක ලග්නය: {SIGNS[navasc]}\nMC: {fmt_dms(mc)}\n\nභාව ආරම්භක ස්ඵුට:\n")
            for i,c in enumerate(cusps,1): self.bhava_text.insert("end",f"භාව {i}: {fmt_dms(c)}\n")
            self.bhava_text.insert("end","\nනවාංශක ග්‍රහ පිහිටීම්:\n")
            for si_name,en_name,_ in PLANETS:
                self.bhava_text.insert("end",f"{si_name}: {SIGNS[navamsa_sign(planets[en_name]['lon'])]}\n")
            self.bhava_text.insert("end",f"කේතු: {SIGNS[navamsa_sign(k['lon'])]}\n")
            moon_nak,pada,idx=nakshatra_info(planets["Moon"]["lon"])
            self.nak_text.delete("1.0","end")
            self.nak_text.insert("end",f"ජන්ම නැකත: {moon_nak}\nපාදය: {pada}\nචන්ද්‍ර රාශිය: {fmt_dms(planets['Moon']['lon'])}\n\n")
            self.nak_text.insert("end","ඔබ ලබාදුන් නැකත් ගුණ:\n")
            attrs = self.nak_attributes.get(moon_nak, {})
            attr_labels = [("ගණ","Gana"),("යෝනි","Yoni"),("වෘක්ෂ","Tree"),("ලිංග","Gender"),
                           ("නාඩි","Nadi"),("පක්ෂි","Bird"),("ගෝත්‍ර","Gotra"),
                           ("වර්ණ","Varna"),("රජ්ජු","Rajju"),("භූත","Bhuta")]
            for si_label, en_label in attr_labels:
                value = (attrs.get(en_label) or "").strip()
                self.nak_text.insert("end",f"{si_label}: {value if value else 'reference වගුවේ අගයක් ඇතුළත් කර නැත'}\\n")
            self.nak_text.insert("end","\\nමෙම අගයන් සඳහා App folder එකේ nakshatra_attributes_template.csv ගොනුව ඔබ භාවිත කරන සම්ප්‍රදායට අනුව පුරවා නැවත App එක විවෘත කරන්න.\\n")
            nak, pada, lord, drows=dasha_rows(dt,planets["Moon"]["lon"])
            for item in self.dasha_tree.get_children():self.dasha_tree.delete(item)
            for maha,sub,praty,start,end in drows:
                self.dasha_tree.insert("","end",values=(DASHA_SI[maha],DASHA_SI[sub],DASHA_SI[praty],start.strftime("%Y-%m-%d %H:%M"),end.strftime("%Y-%m-%d %H:%M")))
            self.yoga_text.delete("1.0","end")
            self.yoga_text.insert("end","ග්‍රහ දෘෂ්ටි (රාශි/භාව සම්බන්ධතා):\n")
            for si_name,en_name,_ in PLANETS:
                h=houses[en_name]
                targets=drishti_targets(en_name,h)
                self.yoga_text.insert("end",f"{si_name} (භාව {h}) → භාව {', '.join(map(str,targets))}\n")
            self.yoga_text.insert("end","\nමූලික යෝග පරීක්ෂාව:\n")
            sun=planets["Sun"]["lon"];mer=planets["Mercury"]["lon"]
            moon=planets["Moon"]["lon"];jup=planets["Jupiter"]["lon"];mars=planets["Mars"]["lon"]
            def ang(a,b):return abs((a-b+180)%360-180)
            yogas=[]
            if ang(sun,mer)<=10:yogas.append("බුධ-ආදිත්‍ය යෝගය (සූර්ය-බුධ 10° ඇතුළත)")
            if ang(moon,mars)<=10:yogas.append("චන්ද්‍ර-මංගල යෝගය (චන්ද්‍ර-කුජ 10° ඇතුළත)")
            if ((houses["Jupiter"]-houses["Moon"])%12) in (0,3,6,9):
                yogas.append("ගජකේසරි යෝගය (ගුරු චන්ද්‍රයාගෙන් කේන්ද්‍ර භාවයක)")
            if yogas:
                for y in yogas:self.yoga_text.insert("end","• "+y+"\n")
            else:self.yoga_text.insert("end","මෙම සරල නියම අනුව මූලික යෝග හමු නොවීය.\n")
            self.yoga_text.insert("end","\nසම්පූර්ණ යෝග පරීක්ෂාව, දෘෂ්ටි බල ප්‍රමාණාත්මක ගණනය සහ ෂඩ්බල මෙහි තවම සම්පූර්ණයෙන් ක්‍රියාත්මක කර නැත.\n")
            self.last_result=(dt,loc,jd,planets,cusps,asc,mc,houses)
            self.status.set(f"ගණනය සාර්ථකයි: {en} | {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            messagebox.showerror("ගණනය කළ නොහැක",str(e))

    def export_chart(self):
        if not self.last_result:
            messagebox.showwarning("දත්ත නැත","මුලින් ගණනය කරන්න.");return
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile="jyothisha_chart.csv")
        if not path:return
        dt,loc,jd,planets,cusps,asc,mc,houses=self.last_result
        si,en,lat,lon,district=loc
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            w=csv.writer(f);w.writerow(["Field","Value"])
            w.writerow(["DateTime",dt.isoformat()]);w.writerow(["Place",en]);w.writerow(["Latitude",lat]);w.writerow(["Longitude",lon])
            w.writerow(["Ascendant",fmt_dms(asc)]);w.writerow(["Navamsa Ascendant",SIGNS[navamsa_sign(asc)]]);w.writerow(["MC",fmt_dms(mc)])
            for i,c in enumerate(cusps,1):w.writerow([f"House_{i}",fmt_dms(c)])
            w.writerow([]);w.writerow(["Planet","Longitude","Speed_deg_per_day","Motion","Dignity","House","Nakshatra","Pada","Navamsa"])
            for si_name,en_name,_ in PLANETS:
                d=planets[en_name];n,p,_=nakshatra_info(d["lon"])
                w.writerow([si_name,fmt_dms(d["lon"]),d["speed"],"Retrograde" if d["speed"]<0 else "Direct",dignity(en_name,d["lon"]),houses[en_name],n,p,SIGNS[navamsa_sign(d["lon"])]])
            n,p,_=nakshatra_info(planets["Ketu"]["lon"])
            w.writerow(["කේතු",fmt_dms(planets["Ketu"]["lon"]),planets["Ketu"]["speed"],"Retrograde",dignity("Rahu",planets["Ketu"]["lon"]),houses["Ketu"],n,p,SIGNS[navamsa_sign(planets["Ketu"]["lon"])]])
            w.writerow([])
            w.writerow(["Maha Dasha","Antardasha","Pratyantardasha","Start","End"])
            _, _, _, drows = dasha_rows(dt, planets["Moon"]["lon"])
            for maha, sub, praty, start, end in drows:
                w.writerow([DASHA_SI[maha],DASHA_SI[sub],DASHA_SI[praty],
                            start.strftime("%Y-%m-%d %H:%M:%S"),end.strftime("%Y-%m-%d %H:%M:%S")])
        messagebox.showinfo("Export සාර්ථකයි",f"CSV ගොනුව සුරැකුවා:\n{path}")

    def generate_minutes(self):
        try:
            loc=self.selected_location()
            start=datetime.strptime(self.date.get(),"%Y-%m-%d").date()
        except Exception as e:
            messagebox.showerror("දෝෂය",str(e));return
        win=tk.Toplevel(self.root);win.title("විනාඩි දත්ත නිපදවීම");win.geometry("480x260")
        ttk.Label(win,text="ආරම්භක දිනය දැනට ඇති දිනයයි. අවසන් දිනය යොදන්න (2000–2150).").pack(padx=12,pady=10)
        endvar=tk.StringVar(value="2000-07-31")
        ttk.Entry(win,textvariable=endvar,width=18).pack()
        ttk.Label(win,text="මෙම ස්ථානය සඳහා සෑම විනාඩියකටම ග්‍රහ දේශාංශ සහ ලග්නය CSV ලෙස ලියයි.").pack(padx=12,pady=8)
        def run():
            try:
                end=datetime.strptime(endvar.get(),"%Y-%m-%d").date()
                if end<start or start.year<2000 or end.year>2150: raise ValueError("2000–2150 අතර වලංගු දිනයක් තෝරන්න.")
                minutes=int((end-start).days+1)*1440
                if minutes>1000000:
                    if not messagebox.askyesno("විශාල ගොනුව",f"වාර්තා {minutes:,}ක් පමණ වේ. දිගු කාලයක් ගත විය හැක. දිගටම කරගෙන යන්නද?"):return
                path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile=f"{loc[1]}_minute_data.csv")
                if not path:return
                win.destroy()
                def worker():
                    si,en,lat,lon,district=loc
                    try:
                        swe.set_sid_mode(swe.SIDM_LAHIRI)
                        with open(path,"w",newline="",encoding="utf-8-sig",buffering=1024*1024) as f:
                            w=csv.writer(f)
                            w.writerow(["LocalDate","Weekday","LocalTime","Place","Latitude","Longitude","Ascendant","Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"])
                            current=datetime.combine(start,datetime.min.time()).replace(tzinfo=TZ)
                            stop=datetime.combine(end+timedelta(days=1),datetime.min.time()).replace(tzinfo=TZ)
                            while current<stop:
                                jd=get_jd_fast(current)
                                flags=swe.FLG_SWIEPH|swe.FLG_SIDEREAL|swe.FLG_SPEED
                                vals=[]
                                for _,en_name,body in PLANETS:
                                    xx,_=swe.calc_ut(jd,body,flags);vals.append(fmt_dms(xx[0]))
                                rahu_lon=swe.calc_ut(jd,swe.MEAN_NODE,flags)[0][0]
                                ketu=(rahu_lon+180)%360
                                _,ascmc=swe.houses_ex(jd,lat,lon,b'P',swe.FLG_SIDEREAL)
                                w.writerow([current.strftime("%Y-%m-%d"),current.strftime("%A"),current.strftime("%H:%M:%S"),en,lat,lon,fmt_dms(ascmc[0]),*vals,fmt_dms(ketu)])
                                current+=timedelta(minutes=1)
                        self.root.after(0,lambda:messagebox.showinfo("සාර්ථකයි",f"CSV සුරැකුවා:\n{path}"))
                    except Exception as ex:
                        self.root.after(0,lambda:messagebox.showerror("දෝෂය",str(ex)))
                threading.Thread(target=worker,daemon=True).start()
                self.status.set("විනාඩි දත්ත නිපදවමින්...")
            except Exception as e:messagebox.showerror("දෝෂය",str(e))
        ttk.Button(win,text="CSV නිපදවන්න",command=run).pack(pady=10)

def get_jd_fast(dt):
    utc=dt.astimezone(timezone.utc)
    return swe.julday(utc.year,utc.month,utc.day,utc.hour+utc.minute/60.0,swe.GREG_CAL)

def main():
    if swe is None:
        root=tk.Tk();root.withdraw()
        messagebox.showerror("Dependency missing","Swiss Ephemeris අවශ්‍යයි.\n\nCommand Prompt:\npy -m pip install pyswisseph")
        return
    root=tk.Tk()
    app=JyothishaApp(root)
    root.mainloop()

if __name__=="__main__":
    main()
