import argparse, datetime, importlib.util, json, os, re, shutil, subprocess, sys

# Check required external programs are installed
assert shutil.which("ffmpeg"), "ffmpeg is not installed"
assert shutil.which("git"), "git is not installed"

# Helper: subprocess.run with logs
def run(*args, **kwargs):
    print(args, kwargs)
    try:
        return subprocess.run(*args, **kwargs)
    except subprocess.CalledProcessError as e:
        print(f"Error[{e.returncode}] in {e.cmd}", file=sys.stderr)
        print(decode(e.stderr), file=sys.stderr)
        exit(1)

# Helper: guess encoding and decode
def decode(bs):
    for enc in ["utf-8", "shift-jis", "cp932", "euc-jp"]:
        try:
            return bs.decode(enc)
        except UnicodeDecodeError:
            pass
    assert False


### Setup

THIS_DIR = os.path.dirname(os.path.realpath(__file__)) # directory of script.py

# Ensure yt-dlp dependencies are installed
if not importlib.util.find_spec("yt_dlp"):
    run(["pip", "install", "--no-deps", "-U", "yt-dlp"])

# Download and patch yt-dlp
YTDLP_DIR = os.path.join(THIS_DIR, "yt-dlp")
if not os.path.isdir(YTDLP_DIR):
    run(["git", "clone", "https://github.com/yt-dlp/yt-dlp"],     cwd=THIS_DIR)
    run(["git", "checkout", "4d9231"],                            cwd=YTDLP_DIR)
    run(["git", "apply", os.path.join(THIS_DIR, "yt-dlp.patch")], cwd=YTDLP_DIR)

# Download and patch danmaku2ass
DANMAKU2ASS_DIR = os.path.join(THIS_DIR, "danmaku2ass")
if not os.path.isdir(DANMAKU2ASS_DIR):
    run(["git", "clone", "https://github.com/m13253/danmaku2ass"],     cwd=THIS_DIR)
    run(["git", "checkout", "b1a9df"],                                 cwd=DANMAKU2ASS_DIR)
    run(["git", "apply", os.path.join(THIS_DIR, "danmaku2ass.patch")], cwd=DANMAKU2ASS_DIR)


### Program

# Parse options
def argtype_nicovideo(s):
    if re.match(r"[a-z]{2}[0-9]+", s): return s
    elif m := re.search(r"watch/([a-z]{2}[0-9]+)", s): return m[1]
    raise argparse.ArgumentTypeError(f"Invalid video id or url: {s}")
parser = argparse.ArgumentParser()
parser.add_argument("--fps", dest="max_danmaku_fps", type=int, default=0, help="danmaku fps")
parser.add_argument("--add-info", action="store_true", help="add video info as danmaku at the beginning of the video")
parser.add_argument("--keep-files", action="store_true", help="do not remove intermediate files (for debugging)")
parser.add_argument("--quality", default="bestvideo+bestaudio", help="video quality (yt-dlp -f flag)")
parser.add_argument("--regen", default="", help="regenerate .mkv (.comments.json and .info.json must exist. options quality and videoID are ignored)")
parser.add_argument("videoID", type=argtype_nicovideo, help="video ID or URL")
args = parser.parse_args()

if 0 == len(args.regen):

    # Get filename of video to be created (and check availability online)
    res1 = run([
        "python", os.path.join(YTDLP_DIR, "yt_dlp", "__main__.py"),
        "--print", "filename",
        f"https://www.nicovideo.jp/watch/{args.videoID}",
    ], check=True, capture_output=True)

    base = re.search(r"(.*).mp4", decode(res1.stdout))[1]

    # Download video, thumbnail, ass, info json
    run([
        "python", os.path.join(YTDLP_DIR, "yt_dlp", "__main__.py"),
        "-f", args.quality,
        "--write-info-json", "--add-metadata",
        "--write-thumbnail",
        "--get-comments", "--write-sub", "--all-subs",
        f"https://www.nicovideo.jp/watch/{args.videoID}",
    ], check=True)

else:

    # (regenerate) get base name, check necessary files exist
    assert args.regen.endswith(".mkv"), f"not ends with .mkv: {args.regen}"
    assert os.path.exists(args.regen), f"does not exist: {args.regen}"
    base = args.regen[:-4] # remove .mkv
    assert os.path.exists(f"{base}.info.json"), f"does not exist: {base}.info.json"
    assert os.path.exists(f"{base}.comments.json"), f"does not exist: {base}.comments.json"

    # Extract video and audio (strip sub)
    run([
        "ffmpeg", "-y", "-v", "8",
        "-i", f"{base}.mkv",
        "-c", "copy",
        f"{base}.mp4"
    ])


with open(f"{base}.info.json", "rb") as f:
    info = json.loads(decode(f.read()))
resolution = info["resolution"]  # ex. "640x360"
height     = info["height"]      # ex. 360
duration   = info["duration"]    # ex. 123.0 (seconds)
fps        = info.get("fps", 30) # ex. 14.0
uploadDate = info["_api_data"]["video"]["registeredAt"] # ex. 2010-09-06T20:07:34+09:00

# Create ass from yt-dlp output json
run([
    "python", os.path.join(DANMAKU2ASS_DIR, "danmaku2ass.py"),
    "-f",  "NiconicoYtdlpJson",
    "-a",  "0.6",
    "-s",  resolution,
    "-fs", str(24 * (height / 360)),
    "-o",  f"{base}.ass1",
    f"{base}.comments.json"
], check=True)

# Create low-fps ass (optional)
if args.max_danmaku_fps > 0:
    with open(f"{base}.ass", "w") as f:
        run([
            "python", os.path.join(THIS_DIR, "ass_fps_limit.py"),
            f"{base}.ass1", str(fps), str(args.max_danmaku_fps), str(duration)
        ], check=True, stdout=f)
else:
    shutil.copy(f"{base}.ass1", f"{base}.ass")

# Add info text ass (optional)
if args.add_info:
    with open(f"{base}.ass", "a") as f:
        run([
            "python", os.path.join(THIS_DIR, "ass_video_info.py"),
            f"{base}.info.json",
        ], check=True, stdout=f)

# Combine video and ass into mkv
run([
    "ffmpeg", "-y", "-v", "8",
    "-i", f"{base}.mp4",
    "-itsoffset", "-0.2", # make subs 0.2 sec earlier
    "-i", f"{base}.ass",
    "-c", "copy",
    f"{base}.mkv"
], check=True)

# Set output mtime to video upload date
timestamp = datetime.datetime.fromisoformat(uploadDate).timestamp()
for ext in ["mkv", "ass", "ass1", "comments.json", "info.json", "jpg", "mp4"]:
    if os.path.exists(f"{base}.{ext}"):
        os.utime(f"{base}.{ext}", (timestamp, timestamp))

# Remove intermediate files (optional)
if not args.keep_files:
    os.remove(f"{base}.mp4")
    os.remove(f"{base}.ass")
    os.remove(f"{base}.ass1")
