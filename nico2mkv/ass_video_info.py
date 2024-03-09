import datetime, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

infojson = json.load(open(sys.argv[1], "r", encoding="utf-8"))

s_tags = ""
tmp = ""
for i, tag in enumerate(infojson["tags"]):
    s_tags = s_tags + tag + " "
    tmp    = tmp    + tag + " "
    if i < len(infojson["tags"]) - 1 and 50 < len(re.sub(r"[^\x00-\xff]", "xx", tmp)):
        tmp = ""
        s_tags += r"\n"

s_desc = infojson["description"].replace("\n", r"\n") # real newline to backslash + n

s_date = datetime.datetime.fromtimestamp(infojson["timestamp"]).strftime("%Y-%m-%d")

dur = 03.00
fs  = 12
mx  = 10
my  = fs * 2

PlayResX = infojson["width"]
PlayResY = infojson["height"]

l_tags = 1 + s_tags.count(r"\n") # how many lines in s_tags
y_tags = PlayResY - my
y_desc = y_tags - (fs * (1 + l_tags))
x_date = PlayResX - mx

dic1 = {
    "fs": fs, "dur": dur,
    "mx": mx, "y_tags": y_tags, "y_desc": y_desc, "x_date": x_date,
    "s_tags": s_tags, "s_desc": s_desc, "s_date": s_date,
}

# force writing in utf-8
print(r"""
[V4+ Styles]
Style: ColorC, Droid Sans Japanese, {fs}, &H00FFFFbb, &H00FFFFbb, &H66000000, &H66000000, 0, 0, 0, 0, 100, 100, 0.00, 0.00, 1, 2, 0, 7, 0, 0, 0, 0
Style: ColorM, Droid Sans Japanese, {fs}, &H00FFbbFF, &H00FFFFbb, &H66000000, &H66000000, 0, 0, 0, 0, 100, 100, 0.00, 0.00, 1, 2, 0, 7, 0, 0, 0, 0
Style: ColorY, Droid Sans Japanese, {fs}, &H00bbFFFF, &H00bbFFFF, &H66000000, &H66000000, 0, 0, 0, 0, 100, 100, 0.00, 0.00, 1, 2, 0, 7, 0, 0, 0, 0
[Events]
Dialogue: 2,0:00:00.00,0:00:{dur},ColorY,,0000,0000,0000,,{{\\an1}}{{\\pos({mx},{y_tags})}}{s_tags}
Dialogue: 2,0:00:00.00,0:00:{dur},ColorC,,0000,0000,0000,,{{\\an1}}{{\\pos({mx},{y_desc})}}{s_desc}
Dialogue: 2,0:00:00.00,0:00:{dur},ColorM,,0000,0000,0000,,{{\\an3}}{{\\pos({x_date},{y_tags})}}{s_date}
""".format(**dic1))
