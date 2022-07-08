import subprocess as sp


def get_devices():
    cmd = ['ffmpeg', '-list_devices',
           'true', '-f', 'dshow', '-i', 'dummy','-hide_banner']

    res = sp.getoutput(" ".join(cmd))
    print(res)
    if "Hauppauge Cx23100 Video Capture" in res:
        return ["Hauppauge Cx23100 Video Capture"]
    else:
        return [""]
