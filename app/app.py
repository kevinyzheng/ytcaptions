from flask import Flask, render_template, send_from_directory, send_file
import json
import yt_dlp
import os


app = Flask(__name__)


def get_video_info(video_id):
    try:
        ydl_opts = {
            "quiet": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.sanitize_info(ydl.extract_info(video_id, download=False))
            subtitles = list(info_dict["subtitles"].keys())
            automatic_captions = info_dict["automatic_captions"].keys()
            orig_lang = [lang for lang in automatic_captions if "-orig" in lang]
        if len(subtitles) > 0:
            ydl_opts = {
                "skip_download": True,
                "quiet": True,
                "writesubtitles": True,
                "subtitleslangs": subtitles,
                "outtmpl": 'transcripts/%(id)s.%(ext)s'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(ydl.download([video_id]))
        if len(orig_lang) > 0:
            ydl_opts = {
                "skip_download": True,
                "quiet": True,
                "writeautomaticsub": True,
                "subtitleslangs": orig_lang,
                "outtmpl": 'transcripts/%(id)s.auto.%(ext)s'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(ydl.download([video_id]))
        with open(f"metadata/{video_id}.json", 'w') as f:
            json.dump(info_dict, f)
        return info_dict
    except Exception as e:
        print(e)
        return e


@app.route("/request/<path:videoid>")
def transcript_request_handler(videoid):
    video_info = get_video_info(videoid)
    if isinstance(video_info, Exception):
        return f"<p>error {videoid}, {video_info}</p>"
    return f"<p>{video_info}</p>"


@app.route("/transcripts/")
def list_transcripts():
    return render_template('transcripts.html', files=[file for file in os.listdir('transcripts') if file.endswith(".vtt")])


@app.route("/transcripts/<path:filename>")
def get_transcript(filename):
    return send_from_directory(os.path.join(app.root_path, "transcripts"), filename, as_attachment=True, download_name=filename)


if __name__ == '__main__':
    app.run()

# get_video_info("https://www.youtube.com/watch?v=pycbzWxdwr8")  # only auto captions
# get_video_info("https://www.youtube.com/watch?v=uiMRFP5SNw8")  # no captions
# get_video_info("https://www.youtube.com/watch?v=prSZoL-8eqo")  # spanish, uploaded, cc format


"""
- write info json
- if captions: download all captions
- if auto captions:
    - find "-orig"
    - download "lang-orig"
- else use voxlingua107 and vosk
"""
# get_video_info("cqII5wZn8AQ")  # uploaded captions
