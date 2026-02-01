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


## Troubleshooting

- Problem: Emoji is not shown with mpv

  Solution: Install a *monochrome* emoji font such as [Noto-Emoji-Monochrome](https://github.com/zjaco13/Noto-Emoji-Monochrome). You may additionally need `--sub-font='Note Emoji Medium'` option. ([relevant github issue](https://github.com/mpv-player/mpv/issues/8919#issuecomment-1823566773))

- Problem: Video has been removed on niconico, but I have at least one of video, comment data or video metadata.

  Solution: If video is missing, try searching in youtube/bilibili/youku for reposts (or create a dummy video of the same duration). If comment data or video metadata is missing, try salvaging from NII ニコニコ動画コメント等データ (create account and download/transform data with `salvage_json` script). ニコログ also helps salvagint metadata. In either case, prepare TITLE.mkv, TITLE.comments.json, TITLE.info.json, and run `nico2mkv.bash --regen TITLE.mkv`


## Options
```
usage: nico2mkv.py [-h] [--fps MAX_DANMAKU_FPS] [--add-info] [--keep-files] [--yt-format FORMAT] [--yt-username USERNAME]
                   [--yt-password PASSWORD] [--extension-picky-0] [--regen MKV]
                   videoID

positional arguments:
  videoID               video ID or URL

options:
  -h, --help            show this help message and exit
  --fps MAX_DANMAKU_FPS
                        danmaku fps
  --add-info            add video info as danmaku at the beginning of the video
  --keep-files          do not remove intermediate files (for debugging)
  --yt-format FORMAT    yt-dlp --format: video format i.e. quality
  --yt-username USERNAME
                        yt-dlp --username: account id
  --yt-password PASSWORD
                        yt-dlp --password: account password
  --extension-picky-0   yt-dlp: pass "--extension-picky 0" to ffmpeg; workaround for allowed extension error
  --regen MKV           regenerate this .mkv (.comments.json and .info.json must exist and options videoID and yt-* are ignored)
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
