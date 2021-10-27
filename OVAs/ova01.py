import os
import time
from pathlib import Path

from vapoursynth import GRAY, RGBS, YUV, YUV444P10, YUV444P16, core
import awsmfunc as awf
import debandshit
import EoEfunc as eoe
import havsfunc as haf
import kagefunc as kgf
import lvsfunc as lvf
import vardefunc as vdf
from rekt import rektlvls
from vsdpir import DPIR

conan = core.d2v.Source("sf-vol1/VTS_01_1.d2v")
conan = conan[960:43320] # ova1

fm = conan.vivtc.VFM(1)

def effortfm(conan):
    fm = conan.vivtc.VFM(1)

    combed_frames = "42020 40227"

    qtgmc = haf.QTGMC(conan, TFF=True, Preset="Very Slow", SourceMatch=2, Lossless=1, MatchEnhance=0, TR0=0, TR1=2, TR2=3, FPSDivisor=2)

    def _masked_qtgmc(f, mask, vinverse=True, clip_vinverse=False, clip=fm):
        r = core.std.MaskedMerge(clip, qtgmc.vinverse.Vinverse(), mask, first_plane=True)
        if not vinverse:
            r = core.std.MaskedMerge(clip, qtgmc, mask, first_plane=True)
        return awf.ReplaceFrames(fm, r, f)

    fm = awf.ReplaceFrames(fm, qtgmc.vinverse.Vinverse(), combed_frames)

    combmask_10302_10319 = core.imwri.Read("masks/ova01_10302_10319.png")
    fm = awf.ReplaceFrames(fm, core.std.MaskedMerge(fm, fm[10301]*10320, combmask_10302_10319, first_plane=True), "[10302 10319]")

    fm1 = _masked_qtgmc("[39896 42000]", core.std.Expr([kgf.squaremask(fm, width=332, height=226, offset_x=330, offset_y=110).std.Invert(), conan.comb.CombMask(cthresh=26, mthresh=20, mi=20).std.ShufflePlanes(planes=0, colorfamily=GRAY).std.BoxBlur(hradius=8).std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Binarize(35).std.BoxBlur(hradius=8)], "x y max").std.Maximum().std.Maximum().std.Maximum(), vinverse=False, clip=fm)
    fm2 = awf.ReplaceFrames(fm1, core.std.MaskedMerge(fm1, qtgmc, core.std.MaskedMerge(fm.std.BlankClip().std.ShufflePlanes(planes=0, colorfamily=GRAY), fm1.comb.CombMask(cthresh=2, mthresh=10, mi=30).std.ShufflePlanes(planes=0, colorfamily=GRAY).std.BoxBlur(hradius=8).std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Binarize(35).std.BoxBlur(hradius=8), kgf.squaremask(fm, width=332, height=226, offset_x=330, offset_y=110), first_plane=True)), "39997 40069 40119 40137 40469 40531 40648 40687 40906 41173 41465 41508 41614 41618 41629 41632 41702 41806 41835 41963 41984 42000")
    fm = awf.ReplaceFrames(fm2, core.std.MaskedMerge(fm2, fm, kgf.squaremask(fm, width=332, height=226, offset_x=330, offset_y=110), first_plane=True), "[40156 40344] [41136 41172] [41174 41390] [41534 41613] [41615 41617] [41807 41631] [41633 41701] [41703 41805] [41807 41834] [41836 41962] [41964 41983] [41985 41999]")

    fm = awf.ReplaceFrames(fm, fm[0]+fm, "38968 25863 25453 25458 23968 23893 23888 23763 23448 21348 21313 21310 21199 20473 19673 19413 18882 18583 17948") # frame -1
    fm = awf.ReplaceFrames(fm, fm[:2]+fm, "18883") # frame -2
    fm = awf.ReplaceFrames(fm, fm[1:], "38960 38963 38966 21349 21311 5038") # frame +2
    fm = awf.ReplaceFrames(fm, fm[2:], "38959 38962 5037") # frame +3

    return fm.std.SetFieldBased(0)

# mostly pasted from lvsfunc.deinterlace.TIVTC_VFR
def magicdecimate(fm, tdec_in="tdec_in.txt"):
    tdec_in = Path(tdec_in).resolve()

    # TIVTC can't write files into directories that don't exist
    if not tdec_in.parent.exists():
        tdec_in.parent.mkdir(parents=True)

    if not tdec_in.exists():
        ivtc_clip = fm.tivtc.TDecimate(mode=1, hint=True, output=str(tdec_in))

        with lvf.render.get_render_progress() as pr:
            task = pr.add_task("Analyzing frames...", total=ivtc_clip.num_frames)

            def _cb(n, total):
                pr.update(task, advance=1)

            with open(os.devnull, "wb") as dn:
                ivtc_clip.output(dn, progress_update=_cb)

        # Allow it to properly finish writing the logs
        time.sleep(0.5)
        del ivtc_clip # Releases the clip, and in turn the filter (prevents it from erroring out)

    return fm.tivtc.TDecimate(mode=1, hint=True, input=str(tdec_in))

fm = effortfm(conan)
conan = magicdecimate(fm[:39863], tdec_in=".ivtc/01_ep_tdec_in.txt") + fm[39863:42020] + magicdecimate(fm[42020:], tdec_in=".ivtc/01_ed_tdec_in.txt")

flt = rektlvls(conan, colnum=[1, 2], colval=[54, 16])
flt = flt.fb.FillBorders(left=1)

flt_prot = rektlvls(conan, colnum=[1, 2], colval=[54, 16], prot_val=[16, 40])
flt_prot = flt_prot.fb.FillBorders(left=1)

edgefix = core.std.ShufflePlanes([flt_prot, awf.fb(flt_prot, left=1)], [0, 1, 2], YUV)
flt = awf.ReplaceFrames(flt, awf.bbmod(edgefix, left=3, blur=20, thresh=30).std.Merge(edgefix, weight=[0.6, 0.4]), "[729 852]")

edgefix = awf.bbmod(flt, left=4, right=2, thresh=30, blur=90)
flt = core.std.ShufflePlanes([core.std.Expr([flt, edgefix], "x y min"), edgefix], planes=[0, 1, 2], colorfamily=YUV)

flt = flt.resize.Bicubic(format=YUV444P16, matrix_s="170m")

# magic filter
rgbs = core.resize.Bicubic(flt, format=RGBS, matrix_in_s="170m", range_in_s="limited")
flt = lvf.deblock.autodb_dpir(rgbs, strs=[10, 14, 18, 24], thrs=[(0.0, 0.0, 0.0), (0.8, 1.2, 1.2), (1.4, 1.8, 1.8), (3.0, 4.5, 4.5)], cuda=False).resize.Bicubic(format=YUV444P16, matrix_s="170m")

# stronger deblock around lineart to get rid of more halos
mask = lvf.mask.detail_mask(flt, brz_a=0.185, brz_b=0.260).std.Maximum()
strong = DPIR(rgbs, task="deblock", device_type="cpu", strength=45).resize.Bicubic(format=YUV444P16, matrix_s="170m")
dpirmin = core.std.MaskedMerge(flt, core.std.Expr([flt, strong], "x y min"), mask)
flt = core.std.ShufflePlanes([core.std.Expr([flt, dpirmin], "x y min"), flt], planes=[0, 1, 2], colorfamily=YUV)

# "strong" deband
deband = debandshit.dumb3kdb(flt, radius=16, threshold=20)

# trying to bring back fine lines
flt = core.std.Expr([flt, deband], "x y max")

# stretch for correct aspect ratio
flt = core.std.ShufflePlanes([vdf.scale.fsrcnnx_upscale(flt, width=720, height=540, shader_file="FSRCNNX_x2_56-16-4-1.glsl")] + vdf.scale.to_444(flt, width=720, height=540, join_planes=False), [0, 0, 0], YUV)
conan = core.std.ShufflePlanes([vdf.scale.fsrcnnx_upscale(conan, width=720, height=540, shader_file="FSRCNNX_x2_56-16-4-1.glsl")] + vdf.scale.to_444(conan, width=720, height=540, join_planes=False), [0, 0, 0], YUV)

# less strong deband that won't destroy fine lines + stronger deband on intro
flt = awf.ReplaceFrames(debandshit.dumb3kdb(flt, radius=12, threshold=10, output_depth=10), debandshit.dumb3kdb(flt, radius=22, threshold=34, output_depth=10), "[568 613]")

# contrasharpening
flt = core.std.Expr([flt, eoe.misc.ContraSharpening(flt, haf.FineDehalo(conan).resize.Bicubic(format=YUV444P10, matrix_s="170m"))], "x y min")

# fill 1px on each side instead of 2px on one side
flt = awf.ReplaceFrames(flt.resize.Bicubic(src_left=1).fb.FillBorders(right=1, mode="fixborders"), flt, "[400 852] [31890 34318]")

flt.set_output()
