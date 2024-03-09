# Nico2mkv

Nico2mkv downloads nicovideo with comments embedded.

Given url or video id, it downloads video and comments, and outputs a single MKV video file that also contains comments (danmaku).
To play the video, use a player such as `mpv` and `parole` that supports MKV subtitles.

This program internally uses `yt-dlp`, `danmaku2ass` and `ffmpeg`.


## Usage:

Requires: `python` `git` `ffmpeg`

Windows (cmd.exe or powershell)
```
git clone https://codeberg.org/sj2tpgk/nico2mkv
.\nico2mkv.bat sm12018774
```

Linux
```
git clone https://codeberg.org/sj2tpgk/nico2mkv
./nico2mkv.bash sm12018774
```

To play the video, use a player with mkv subtitle support: `mpv`, `parole` etc.
```
mpv --sub=1 XXXX.mkv
```
 

## Options
```
usage: nico2mkv.py [-h] [--fps MAX_DANMAKU_FPS] [--add-info] [--keep-files] [--quality QUALITY]
                   videoID

positional arguments:
  videoID               video ID or URL

options:
  -h, --help            show this help message and exit
  --fps MAX_DANMAKU_FPS
                        danmaku fps
  --add-info            add video info as danmaku at the beginning of the video
  --keep-files          do not remove intermediate files (for debugging)
  --quality QUALITY     video quality (yt-dlp -f flag)
```


## Manual way (for developers)

1. Ensure yt-dlp dependencies are installed. (e.g. `pip install yt-dlp`)
1. Clone http://github.com/yt-dlp/yt-dlp and apply `yt-dlp.patch` from this repo
   (this adds supports for new comment api)
1. Clone https://github.com/m13253/danmaku2ass and apply `danmaku2ass.patch` from this repo
   (this adds supports for yt-dlp output above)
1. Download video and comment json using yt-dlp:
    ```
    python yt_dlp/__main__.py \
      --write-info-json --add-metadata \
      --write-thumbnail --get-comments \
      --write-sub --all-subs \
      "https://www.nicovideo.jp/watch/sm12018774"
    ```
1. Generate .ass file using danmaku2ass (adjust filename and resolution):
    ```
    python danmaku2ass/danmaku2ass.py \
      -f NiconicoYtdlpJson \
      -s 640x360 \
      -a 0.6 \
      -o danmaku.ass \
      XXXX.comments.json
    ```
1. Combine .mp4 and .ass using ffmpeg (adjust filenames):
    ```
    ffmpeg -y -v 8 -i XXXX.mp4 -i danmaku.ass -c copy out.mkv
    ```


## Links

* yt-dlp: http://github.com/yt-dlp/yt-dlp
* danmaku2ass: https://github.com/m13253/danmaku2ass
* archive team page: https://wiki.archiveteam.org/index.php/Niconico


## TODO

* download all comments, not just 1000
* pull request to yt-dlp and danmaku2ass
