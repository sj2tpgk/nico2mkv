#!/usr/bin/env python3

# Usage: python slowass.py INPUT FPS DURATION
# Example: python slowass.py input.ass 10 300 > output.ass

import math, re, sys

def parseTime(t): # H:MM:SS.ff or -H:MM:SS.ff; return sec (float)
    if t.startswith("-"): return 0
    m = re.match(r"(\d+):(\d+):(\d+).(\d+)", t)
    return int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 100

def fmtTime(t): # t in sec
    # t = round(t*100) # int(round(t,2)*100) is wrong; try t=2.3
    # assuming t is an accurate real number, we must FLOOR it for mpv to play correctly (not ceil or round)
    t = math.floor(t*100) # int(round(t,2)*100) is wrong; try t=2.3
    f = t % 100; t //= 100
    s = t % 60; t //= 60
    m = t % 60; t //= 60
    h = t % 24
    # h = t // 360000
    # m = (t % 360000) // 6000 # int((int(t) % 3600) / 60)
    # s = t % 6000 # int(t) % 60
    # f = t % 100 # int((t % 1) * 1000)
    return f"{h:01}:{m:02}:{s:02}.{f:02}"

def parseCmd(x):
    m = re.match(r"^\{([^}]*)\}(.*)", x)
    cmds = m[1]
    text = m[2]
    moveCmd = re.search(r"(.*)\\move\(([-0-9, ]*)\)(.*)", cmds)
    if not moveCmd:
        return False, 0, 0, 0, 0, 0
    otherCmds = moveCmd[1] + moveCmd[3]
    x1, y1, x2, y2 = [int(x) for x in moveCmd[2].split(",")]
    # print(cmds, x1, y1, x2, y2, otherCmds, text)
    return True, x1, x2, y1, otherCmds, text

# Helper: given real x and int y, get the int z that minimizes |z/y - x|
def nearestFracNumer(x, y):
    xy1 = x * y
    xy2 = int(xy1)
    return xy2 if (xy1 - xy2) < 0.5 else (xy2+1)

infile = sys.argv[1]
vfps = int(float(sys.argv[2])) # video fps (check with e.g. ffmpeg)
sfps = int(float(sys.argv[3])) # desired fps of subtitles
dur = float(sys.argv[4]) # video duration

sfps = min(sfps, vfps) # ensure vfps >= sfps

numer = nearestFracNumer(1/sfps, vfps)
print(f"ass_fps_limit: video fps={vfps}, subtitle desired fps={sfps}, subtitle output fps={vfps}/{numer}", file=sys.stderr)

sys.stdout.reconfigure(encoding="utf-8")
with open(infile, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line.startswith("Dialogue"):
            print(line)
            continue
        ls = line.strip().split(",", maxsplit=9)
        t1 = parseTime(ls[1])
        t2 = parseTime(ls[2])
        if t2 > dur:
            t1 -= (t2 - dur)
            t2 -= (t2 - dur) # t2 = dur
        isMoveCmd, x1, x2, y, otherCmds, text = parseCmd(ls[9])
        if not isMoveCmd:
            line2 = [ls[0], fmtTime(t1), fmtTime(t2), *ls[3:]]
            print(",".join(line2))
            continue
        it0 = round(t1 * (vfps / numer)) # how many blocks of length (numer/vfps) before t1?
        n = int((vfps / numer) * (t2 - t1)) + 1
        dx = round((x2 - x1) / n) # make movement delta an integer
        for i in range(n):
            it1 = it0 + i
            it2 = it0 + i + 1
            tt1 = (it1 * numer) / vfps
            tt2 = (it2 * numer) / vfps
            newProg = "{" + f"\\pos({round(x1 + dx * i)}, {y}){otherCmds}" + "}" + text
            line2 = [ls[0], fmtTime(tt1), fmtTime(tt2), *ls[3:9], newProg]
            print(",".join(line2))
