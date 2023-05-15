#! python3.6
import subprocess
import re

class ffmpegFlags:

    CODEC_AUDIO = "a"
    CODEC_VIDEO = "v"
    CODEC_ALL = None
    CODEC_COPY = "copy"
    METADATA_ARTIST = "artist"
    METADATA_TITLE = "title"
    MOVFLAG_FASTSTART = "faststart"

class ffmpegStatementFactory:

    def __init__(self):
        self.YesFlag = False
        self.NoVideoFlag = False
        self.CodecOption = None

    def SetYesFlag(self):
        self.YesFlag = True

    def SetNoVideoFlag(self):
        self.NoVideoFlag = True

    def SetCodecOption(self, cType, cMode):
        self.CodecOption = [cType, cMode]

    def GetStatement(self):
        statement = ffmpegStatement()
        if self.YesFlag:
            statement.SetYesFlag()
        if self.NoVideoFlag:
            statement.SetNoVideoFlag()
        if self.CodecOption:
            statement.SetCodecOption(self.CodecOption[0], self.CodecOption[1])

        return statement
    


class ffmpegStatement:

    def __init__(self):
        self.progargs = []
        self.args = []

    def SetInputFile(self, InputFile):
        self.InputFile = InputFile

    def SetOutputFile(self, OutputFile):
        self.OutputFile = OutputFile

    def SetYesFlag(self):
        self.progargs.append("-y")

    def SetInputSeek(self, seconds):
        self.progargs.append("-ss " + str(seconds))

    def SetNoVideoFlag(self):
        self.args.append("-vn")

    def SetVFramesOption(self, numFrames):
        self.args.append("-vframes " + str(numFrames))

    def SetCodecOption(self, cType, cMode):
        BaseArg = "-c"
        if cType:
            BaseArg = BaseArg + ":" + cType
        BaseArg = BaseArg + " " + cMode
        self.args.append(BaseArg)

    def SetMovFlags(self, mFlag):
        BaseArg = "-movflags " + mFlag
        self.args.append(BaseArg)

    def SetMetadata(self, mType, mData):
        BaseArg = '-metadata ' + mType + '="' + mData + '"'
        self.args.append(BaseArg)

    def GetCurrentCmd(self):
        return 'ffmpeg ' + ' '.join(self.progargs) + ' -i "' + self.InputFile + '" ' + ' '.join(self.args) + ' "' + self.OutputFile + '"'

    def Run(self):
        subprocess.run(self.GetCurrentCmd())

class ffprobeResult():

    def __init__(self, result):
        exp = '(?:Stream #0:0)+.*'
        self.result = result.decode('UTF-8')
        match = re.findall(exp, self.result)
        self.stream0 = match[0]

    def AVType(self):
        return 'Audio' in self.stream0 and 'Audio' or 'Video'

    def VidSize(self):
        exp = r'(\d*)x(\d*)'
        match = re.findall(exp, self.stream0)
        if len(match) > 0:
            return int(match[0][0]), int(match[0][1])
        else:
            return None

    def GetDuration(self):
        exp = r'(?:Duration: )(\d{2})(?::)(\d{2})(?::)(\d{2})(?:.)(\d{2})'
        match = re.findall(exp, self.result)
        seconds = int(match[0][0])*3600 + int(match[0][1])*60 + int(match[0][2])
        return seconds

# ffmpeg -ss 80 -i f_000a31._1.webm -vframes 1 out2.jpg
def ffprobe(filename):
    fullcmd = 'ffprobe "' + filename + '"'
    output = subprocess.run(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = ffprobeResult(output.stdout)
    return result
