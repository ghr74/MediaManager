import os
import subprocess
import glob
import r128gain
from ffmpy import ffprobe
from avhandler import AudioFromVideo, ImageFromVideo, ImageCommentValue

# from shutil import move
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4, MP4Cover
from os import remove, rename
from shutil import move
from re import sub

input_path = r"PATH TO BASE FILE FOLDER"
output_path = r"PATH TO OUTPUT (MEDIA COLLECTION)"

list_of_webms = glob.glob(input_path + r"\*.webm")

list_of_m4as = glob.glob(input_path + r"\*.m4a")

list_of_mp4s = glob.glob(input_path + r"\*.mp4")

output_file_name = None
Width = None
Height = None
path_to_img = None

if len(list_of_m4as) > 0:
    for fullsong in list_of_m4as:
        song = fullsong.rsplit("\\", 1)[1]
        artist, title = song.rsplit(".", 1)[0].split(" - ", 1)
        m4aasong = fullsong.rsplit(".", 1)[0] + ".m4aa"
        output_file_name = fullsong.rsplit(".", 1)[0] + ".m4a"
        rename(fullsong, m4aasong)
        AudioFromVideo(m4aasong, output_file_name, artist, title, faststart=True)
        remove(m4aasong)

if len(list_of_webms) > 0:
    for f in list_of_webms:
        probe = ffprobe(f)
        if probe.AVType() == "Video":
            path_to_img = f.rsplit(".", 1)[0] + ".jpg"
            Width, Height = ImageFromVideo(f, path_to_img, probe)
        else:
            noidxname = sub(r"._\d.webm", ".webm", f)
            artist, title = (
                noidxname.rsplit("\\", 1)[1].rsplit(".", 1)[0].split(" - ", 1)
            )
            output_file_name = noidxname.rsplit(".", 1)[0] + ".opus"
            AudioFromVideo(f, output_file_name, artist, title)

    if output_file_name:
        audio = OggOpus(output_file_name)
        vcomment_value = ImageCommentValue(path_to_img, Width, Height)
        audio["METADATA_BLOCK_PICTURE"] = [vcomment_value]
        audio.save()
        for f in list_of_webms:
            remove(f)
        remove(path_to_img)

if len(list_of_mp4s) > 0:
    for fullsong in list_of_mp4s:
        artist, title = fullsong.rsplit("\\", 1)[1].rsplit(".", 1)[0].split(" - ", 1)
        output_file_name = fullsong.rsplit(".", 1)[0] + ".m4a"
        path_to_img = fullsong.rsplit(".", 1)[0] + ".jpg"
        ImageFromVideo(fullsong, path_to_img)
        AudioFromVideo(fullsong, output_file_name, artist, title, faststart=True)

    if output_file_name:
        audio = MP4(output_file_name)
        with open(path_to_img, "rb") as img:
            audio["covr"] = [MP4Cover(img.read(), imageformat=MP4Cover.FORMAT_JPEG)]
        audio.save()
        for f in list_of_mp4s:
            remove(f)
        remove(path_to_img)


if output_file_name:

    r128gain.process([output_file_name])
    move(output_file_name, output_path)

