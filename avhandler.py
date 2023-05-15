from ffmpy import ffmpegStatementFactory, ffmpegFlags as flags, ffprobe
import base64
from mutagen.flac import Picture
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4, MP4Cover
from os import remove

AudioStatementFactory = ffmpegStatementFactory()
AudioStatementFactory.SetYesFlag()
AudioStatementFactory.SetNoVideoFlag()
AudioStatementFactory.SetCodecOption(flags.CODEC_AUDIO, flags.CODEC_COPY)


def ImageCommentValue(path_to_img, width=1280, height=720):

    with open(path_to_img, "rb") as h:
        data = h.read()

    picture = Picture()
    picture.data = data
    picture.type = 3
    picture.desc = u""
    picture.mime = u"image/jpeg"
    picture.width = width
    picture.height = height
    picture.depth = 24

    picture_data = picture.write()
    encoded_data = base64.b64encode(picture_data)
    vcomment_value = encoded_data.decode("ascii")

    return vcomment_value


def ImageFromVideo(input_file, output_image, probe=None):
    if probe == None:
        probe = ffprobe(input_file)
    Width, Height = probe.VidSize()
    # Get Relevant Information
    Duration = probe.GetDuration()
    # Generate Thumbnail from Video
    statement = ffmpegStatementFactory().GetStatement()
    statement.SetInputSeek(int(Duration / 2))
    statement.SetInputFile(input_file)
    statement.SetOutputFile(output_image)
    statement.SetVFramesOption(1)
    print(statement.GetCurrentCmd())
    statement.Run()
    return Width, Height


def AudioFromVideo(input_file, output_file, artist, title, faststart=False):
    statement = AudioStatementFactory.GetStatement()
    statement.SetInputFile(input_file)
    statement.SetOutputFile(output_file)
    statement.SetMetadata(flags.METADATA_ARTIST, artist)
    statement.SetMetadata(flags.METADATA_TITLE, title)
    if faststart:
        statement.SetMovFlags(flags.MOVFLAG_FASTSTART)
    print(statement.GetCurrentCmd())
    statement.Run()


def TagThumbnail(song: str, img):
    if song.endswith(".opus"):
        # .opus file
        audio = OggOpus(song)
        vcomment_value = ImageCommentValue(img)
        audio["METADATA_BLOCK_PICTURE"] = [vcomment_value]
        audio.save()
        remove(img)
    elif song.endswith((".m4a", ".mp4")):
        # .m4a/.mp4 file
        audio = MP4(song)
        with open(img, "rb") as img_:
            audio["covr"] = [MP4Cover(img_.read(), imageformat=MP4Cover.FORMAT_PNG)]
        audio.save()
        remove(img)