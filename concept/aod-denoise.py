from vapoursynth import core, GRAY, GRAY8, GRAYS, YUV, RGBS
from vsdpir import DPIR
import Oyster
import debandshit
import kagefunc as kgf

def aod_denoise(clip, frame):
    luma = clip.std.ShufflePlanes(planes=0, colorfamily=GRAY)

    # something I wish I could use but it didn't work well enough
    #stats = luma.std.PlaneStats().get_frame(frame)
    #bg = core.std.BlankClip(clip, color=stats.props["PlaneStatsAverage"], format=GRAYS, length=clip.num_frames).resize.Point(format=GRAY8)

    # color float needs to be tweaked based on how bright of a background the grain is against on the ref frame
    bg = core.std.BlankClip(clip, color=0.065, format=GRAYS, length=clip.num_frames).resize.Point(format=GRAY8)

    # alternatively something like this with a denoiser
    #bg = DPIR(luma[frame].resize.Bicubic(format=GRAYS), task="denoise", device_type="cpu").resize.Bicubic(format=GRAY8)*clip.num_frames

    diff = core.std.MakeDiff(bg, luma[frame], planes=0)*clip.num_frames
    merged = core.std.MergeDiff(luma, diff, planes=0)
    merged = core.std.ShufflePlanes([merged, clip], [0, 1, 2], YUV)
    return merged

aod = core.lsmas.LWLibavSource("Detektiv Conan 0001-0399 [0001-0433 INT] (AoD DE WEB-DL) [eva]/Detektiv Conan 0003 [0003 INT] (AoD WEB-DL 720p x264 AAC) [eva].mkv")

flt = aod_denoise(aod, 0)

lowpass = [0.0, 0.0, 0.12, 1024.0, 1.0, 1024.0]

oy = Oyster.get_core()

freq = oy.FreqMerge(denoise, aod, 9, lowpass)

den = DPIR(freq.resize.Bicubic(format=RGBS, matrix_in=1), strength=3, task="denoise", device_type="cpu").resize.Bicubic(format=freq.format, matrix=1)
den = oy.FreqMerge(freq, den, 9, lowpass)

flt = debandshit.dumb3kdb(den, radius=16, threshold=50, output_depth=10)
flt = kgf.adaptive_grain(flt)
flt = oy.FreqMerge(flt, den.resize.Bicubic(format=flt.format), 9, lowpass)

flt.set_output() # https://slow.pics/c/Emn0IULm
