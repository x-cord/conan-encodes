import locale
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

import vapoursynth as vs
from vapoursynth import core, YUV444P16, YUV444P10, YUV420P8, RGBS, YUV, GRAY
from vsengine.convert import to_rgb, yuv_heuristic
from vsmlrt import DPIR, DPIRModel, Backend, inference, Waifu2x, Waifu2xModel
import vs_colorfix
import kagefunc as kgf
import awsmfunc as awf
import havsfunc as haf

def bestframeselect(clips, ref, clips2=None, stat_func=core.std.PlaneStats, prop="PlaneStatsDiff", comp_func=min, merge_func=None, debug=False, log=False):
    """
    Picks the 'best' clip(s) for any given frame using stat functions.
    clips: list of clips for statistics
    ref: reference clip, e.g. core.average.Mean(clips) / core.median.Median(clips)
    clips2: list of clips for output, defaults to clips if unset
    stat_func: function that adds frame properties
    prop: property added by stat_func to compare
    comp_func: function to decide which clip to pick, e.g. min, max
    merge_func: function to merge clips if stat_func returned a list, e.g. core.average.Mean / core.median.Median
    debug: display values of prop for each clip, and which clip was picked, optionally specify alignment
    """
    from vstools import get_prop

    if not clips2:
        clips2 = clips

    diffs = [stat_func(clip, ref) for clip in clips]
    indices = list(range(len(diffs)))
    do_debug, alignment = debug if isinstance(debug, tuple) else (debug, 7)

    if log:
        print(f"frame,best,score{',score'.join(map(str, indices))}")

    def _select(n, f):
        scores = [
            get_prop(diff.props, prop, float) for diff in f
        ]

        best = comp_func(indices, key=lambda i: scores[i])

        if isinstance(best, list):
            nonlocal merge_func
            if not merge_func:
                if hasattr(ref, "average"):
                    merge_func = core.average.Mean
                else: # breaks with >31 clips
                    from functools import partial
                    merge_func = partial(core.std.AverageFrames, weights=[1] * len(best))
            best_clip = merge_func([clips2[b] for b in best])
            best = "/".join(map(str, best))
        else:
            best_clip = clips2[best]

        if log:
            print(f"{n},{best},{','.join(map(str, scores))}")

        if do_debug:
            return best_clip.text.Text(
                "\n".join([f"Prop: {prop}", *[f"{i}: {s}"for i, s in enumerate(scores)], f"Best: {best}"]), alignment
            )

        return best_clip

    return core.std.FrameEval(clips2[0], _select, diffs)

def gen_shifts(clip, n, forward=True, backward=True):
    shifts = [clip]
    for cur in range(1, n+1):
        if forward:
            shifts.append(clip[cur:]+clip[0]*cur)
        if backward:
            shifts.append(clip.std.DuplicateFrames([0]*cur)[:-1*cur])
    return shifts

oldflt = vs.core.lsmas.LWLibavSource("Detective Conan - Movie 09 Promo - Conan Kogoro on the Horizon [XC-Premux5].mkv")

aptx = vs.core.bs.VideoSource("[APTX4869][CONAN][M9_SP][水平线上的柯南小五郎][XVID_BF](D4CFE0AC).mkv").std.Limiter().std.AssumeFPS(oldflt)
conans = vs.core.bs.VideoSource("[conans][conan][movie9_sp][tvrip][xvid_mp3][big5].avi")[:43153].std.Limiter().std.AssumeFPS(oldflt)
aptxo = aptx
heuristic = yuv_heuristic(aptx.width, aptx.height)

aptx.set_output(0)

aptx = aptx.resize.Bicubic(format=RGBS, **heuristic)
conans = conans.resize.Bicubic(format=RGBS, **heuristic)

conans = core.std.MaskedMerge(conans, aptx, kgf.squaremask(aptx, 158, 30, 236, 438).std.BoxBlur(hradius=2, vradius=2))

out2 = vs_colorfix.wavelet(aptx, conans, wavelets=4, planes=[0, 1, 2], device="cuda")

out = core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 20, 0, 0).std.BoxBlur(hradius=0, vradius=10))

out = awf.rfs(aptx, out, "[906 1026]")
out = awf.rfs(out, core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 22, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "953 [963 969]")
out = awf.rfs(out, core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 30, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "954")
out = awf.rfs(out, core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 44, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "955")
out = awf.rfs(out, core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 54, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "956")
out = awf.rfs(out, core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 68, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "957")
out = awf.rfs(out, core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 80, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "958")
out = awf.rfs(out, core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 94, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "959")
out = awf.rfs(out, core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 104, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "960")
out = awf.rfs(out, core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 118, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "961")
out = awf.rfs(out, core.std.MaskedMerge(out2, conans, kgf.squaremask(out2, out2.width, 128, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "962")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 74, 0, 70).std.BoxBlur(hradius=0, vradius=10)), "963")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 84, 0, 74).std.BoxBlur(hradius=0, vradius=10)), "964")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 100, 0, 74).std.BoxBlur(hradius=0, vradius=10)), "965")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 114, 0, 74).std.BoxBlur(hradius=0, vradius=10)), "970")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 128, 0, 74).std.BoxBlur(hradius=0, vradius=10)), "971")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 80, 0, 104).std.BoxBlur(hradius=0, vradius=10)), "[972 996]")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 90, 0, 94).std.BoxBlur(hradius=0, vradius=10)), "997")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 100, 0, 84).std.BoxBlur(hradius=0, vradius=10)), "[998 1000]")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 106, 0, 74).std.BoxBlur(hradius=0, vradius=10)), "1001")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 116, 0, 64).std.BoxBlur(hradius=0, vradius=10)), "1002")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 136, 0, 46).std.BoxBlur(hradius=0, vradius=10)), "1003")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 156, 0, 32).std.BoxBlur(hradius=0, vradius=10)), "1004")
out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out2, out2.width, 166, 0, 0).std.BoxBlur(hradius=0, vradius=10)), "[1005 1014]")

out = awf.rfs(out, core.std.MaskedMerge(out, conans, kgf.squaremask(out, out.width, 31, 0, 5).std.BoxBlur(hradius=0, vradius=2)), "[1215 2804]")

rgb = out


flt = inference([rgb], overlap=(16, 16), tilesize=(128, 128), network_path="/home/eva/Documents/neosr/experiments/conanm10sp_span/models/net_g_216000_fp32.onnx", backend=Backend.TRT(fp16=False, device_id=0, num_streams=2, use_cuda_graph=True))

flt = flt.resize.Bicubic(format=YUV444P16, **{key.replace("_in", ""): value for key, value in heuristic.items()})
flt = core.std.ShufflePlanes([rgb.resize.Bicubic(format=YUV444P16, **{key.replace("_in", ""): value for key, value in heuristic.items()}), flt], planes=[0, 1, 2], colorfamily=vs.YUV)


flt2z = vs_colorfix.wavelet(rgb, flt.resize.Bicubic(format=vs.RGBS, **heuristic, dither_type="error_diffusion").std.Limiter(), wavelets=4, planes=[0, 1, 2], device="cuda")
flt2z = flt2z.resize.Bicubic(format=YUV444P16, **{key.replace("_in", ""): value for key, value in heuristic.items()})


aptx = flt2z.resize.Bicubic(format=YUV444P16, **{key.replace("_in", ""): value for key, value in heuristic.items()})

flt5 = haf.QTGMC(aptx[::2], TFF=True, Preset="Very Slow", TR0=2, TR1=2, TR2=2, Sharpness=0.1)
flt6_ = haf.QTGMC(aptx[1::2], TFF=True, Preset="Very Slow", TR0=2, TR1=2, TR2=2, Sharpness=0.1).std.DuplicateFrames([0]).std.DuplicateFrames([aptx.num_frames-2])
flt6 = haf.QTGMC(aptx[1::2], TFF=False, Preset="Very Slow", TR0=2, TR1=2, TR2=2, Sharpness=0.1).std.DuplicateFrames([aptx.num_frames-3, aptx.num_frames-3])

flt5_2 = haf.QTGMC(aptx[::2], TFF=True, Preset="Very Slow", TR0=1, TR1=1, TR2=1, Sharpness=0.1)
flt6_2 = haf.QTGMC(aptx[1::2], TFF=True, Preset="Very Slow", TR0=1, TR1=1, TR2=1, Sharpness=0.1).std.DuplicateFrames([aptx.num_frames-3, aptx.num_frames-3])

flt5 = bestframeselect(gen_shifts(flt5, 1) + [flt6], aptx)
flt5_2 = bestframeselect(gen_shifts(flt5_2, 1) + [flt6_2], aptx)
flt6 = bestframeselect(gen_shifts(flt6, 1) + gen_shifts(flt6_, 1) + [flt5], aptx)

flt7 = core.average.Mean([flt5, flt6])

flt4 = haf.QTGMC(flt7, TFF=True, Preset="Very Slow", InputType=2)

flt7 = flt7.resize.Bicubic(format=RGBS, **heuristic)
flt4 = flt4.resize.Bicubic(format=RGBS, **heuristic)

rep = flt2z.resize.Bicubic(format=vs.RGBS, **heuristic, dither_type="error_diffusion").std.Limiter()

rep = awf.rfs(rep, flt7, "[4228 4229] [5384 5489]")
rep = awf.rfs(rep, flt4, "[4171 4227] [14172 14260]")

mask_bluelogo_a = kgf.squaremask(rep, 326, 54, 62, 354).std.BoxBlur(hradius=3, vradius=3)
mask_bluelogo_b = kgf.squaremask(rep, 140, 58, 236, 388).std.BoxBlur(hradius=3, vradius=3)
mask_bluelogo_text = kgf.squaremask(rep, 112, 28, 60, 326).std.BoxBlur(hradius=3, vradius=3)
mask_bluelogo = core.std.Expr([mask_bluelogo_a, mask_bluelogo_b, mask_bluelogo_text], "x y max z max")
mask_topright = kgf.squaremask(rep, 72, 30, 500, 40).std.BoxBlur(hradius=3, vradius=3)
mask_bluelogo_topright = core.std.Expr([mask_bluelogo, mask_topright], "x y max")

mask_topedge = kgf.squaremask(rep, 640, 58, 0, 0).std.BoxBlur(hradius=1, vradius=1)
mask_bottomedge = kgf.squaremask(rep, 640, 60, 0, 420)#.std.BoxBlur(hradius=1, vradius=1)

mask_topedge2 = kgf.squaremask(rep, 304, 30, 294, 38).std.BoxBlur(hradius=1, vradius=1)

mask_topright2 = kgf.squaremask(rep, 354, 30, 244, 38).std.BoxBlur(hradius=1, vradius=1)

mask_topedge3 = kgf.squaremask(rep, 640, 12, 0, 0).std.BoxBlur(hradius=2, vradius=2)
mask_topedge4 = kgf.squaremask(rep, 640, 4, 0, 0).std.BoxBlur(hradius=1, vradius=1)

mask_edges = core.std.Expr([mask_topedge, mask_bottomedge], "x y max")

mask_brickedges = kgf.squaremask(rep, 640, 336, 0, 68).std.Invert().std.BoxBlur(hradius=3, vradius=3)

mask_topright3 = kgf.squaremask(rep, 468, 30, 128, 38).std.BoxBlur(hradius=2, vradius=2)

rep = awf.rfs(rep, core.std.MaskedMerge(flt4, rep, core.std.Expr([mask_bluelogo_topright, mask_edges], "x y max")), "[3147 3189] [39158 39183] [40125 40150]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt7, rep, core.std.Expr([mask_bluelogo_topright, mask_edges], "x y max")), "[3190 3191] [41590 41610]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt7, rep, mask_topedge2), "[4679 4719] [4767 4810]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt7, rep, mask_topright2), "[6486 6521] [6522 6556] 6681")
rep = awf.rfs(rep, core.std.MaskedMerge(flt4, rep, core.std.Expr([mask_topright2, mask_topedge3], "x y max")), "[6682 6791] [23920 23978]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt7, rep, mask_topedge4), "[13546 13681] [17920 18009]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt7, rep, core.std.Expr([mask_topright2, mask_topedge3], "x y max")), "[22889 23025]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt4, rep, core.std.Expr([mask_topright2, mask_topedge4], "x y max")), "[24164 24296]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt4, rep, mask_topedge4), "[26961 27123] [21632 21706] [21707 22431]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt7, rep, mask_topedge4), "27124 [22432 22458]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt4, rep, mask_brickedges), "[38093 38167]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt7, rep, mask_brickedges), "[38393 38467]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt4, rep, core.std.Expr([mask_topright3, mask_topedge4], "x y max")), "[19543 19657]")
rep = awf.rfs(rep, core.std.MaskedMerge(flt5_2.resize.Bicubic(format=RGBS, **heuristic), rep, core.std.Expr([mask_topright3, mask_topedge4], "x y max")), "[19698 19762]")


rgb = rep




rgb = inference([rgb], overlap=(16, 16), tilesize=(128, 128), network_path="1x-AnimeUndeint-Compact.onnx", backend=Backend.TRT(fp16=False, device_id=0, num_streams=2, use_cuda_graph=True))
rgb = rgb.resize.Bicubic(src_top=0.25, src_left=0)

out3 = rgb

rgbbleed = inference([rgb], overlap=(16, 16), tilesize=(128, 128), network_path="1x-BleedOut-Compact.onnx", backend=Backend.TRT(fp16=False, device_id=0, num_streams=2, use_cuda_graph=True))

real = vs_colorfix.wavelet(rgbbleed, rgb, wavelets=4, planes=[0, 1, 2], device="cuda")
real2 = inference([real], overlap=(16, 16), tilesize=(128, 128), network_path="1x-Dotzilla-Compact.onnx", backend=Backend.TRT(fp16=False, device_id=0, num_streams=2, use_cuda_graph=True))

dpir = DPIR(real2, strength=120, model=DPIRModel.drunet_deblocking_color, backend=Backend.TRT(fp16=True, device_id=0, num_streams=2))
dpir = dpir.resize.Bicubic(format=YUV444P16, **{key.replace("_in", ""): value for key, value in heuristic.items()})

real2 = real2.resize.Bicubic(format=YUV444P16, **{key.replace("_in", ""): value for key, value in heuristic.items()})

flt2 = core.std.ShufflePlanes([real2, dpir], planes=[0, 1, 2], colorfamily=YUV)
flt2 = awf.ReplaceFrames(flt2, dpir, "19698 [19702 19705]")


flt2 = awf.rfs(flt2, real2, "[4171 4227] [4228 4229] [14172 14260]")

# freeze framing
flt2 = awf.ReplaceFrames(flt2, flt2[0]+flt2, "6687 6692 6697 6702 6707 6712 6717 6722 22894 22904 22914 22924 22934 22944 40153") # freezing to previous frame
flt2 = awf.ReplaceFrames(flt2, flt2[1:], "4232 11017 14898 18320 22469 22898 22908 22918 22928 22938 25684 26871 28296 33118") # freezing to next frame
flt2 = awf.ReplaceFrames(flt2, flt2[2:], "4231 11016 14897 18319 22468 25683 26870 28295 33117") # freezing to frame +2
flt2 = awf.ReplaceFrames(flt2, flt2[3:], "4230 11015 14896 18318 22467 25682 26869 28294 33116") # freezing to frame +3

rgb2 = flt2.resize.Bicubic(format=RGBS, **heuristic)
ldanime = inference([rgb2], overlap=(16, 16), tilesize=(128, 128), network_path="2x-LD-Anime-Compact.onnx", backend=Backend.TRT(fp16=False, device_id=0, num_streams=2, use_cuda_graph=True))
ldanime = ldanime.resize.Bicubic(width=rgb2.width, height=rgb2.height, format=YUV444P16, **{key.replace("_in", ""): value for key, value in heuristic.items()})

redering = flt2.rgvs.Repair(ldanime, 13)
redering = core.std.Expr([flt2, redering], ["x y min", ""])


out.set_output(1)
#flt2z.set_output(2)
oldflt.set_output(2)
rep.set_output(3)
mask_bluelogo_topright.set_output(4)
out3.set_output(4)
dpir.set_output(5)
rgbbleed.set_output(6)
#real.set_output(7)
real2.set_output(7)
flt2.set_output(8)
redering.resize.Bicubic(format=YUV444P10).set_output(9)
