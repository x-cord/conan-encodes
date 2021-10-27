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
import rvsfunc as rvf
import vardefunc as vdf
from rekt import rektlvls
from vsdpir import DPIR

conan = core.d2v.Source("sf-vol1/VTS_01_1.d2v")
conan = conan[43320:88220] # ova2

def effortfm(conan):
    fm = conan.vivtc.VFM(1)

    combed_frames = "2549 4748 6762 10567 13984 15523 18453 18551 20459 20809 28045 30083 34586 35147 36332 39772"

    # we're missing a half-frame at the end of this panning shot 33741 --not worth the effort

    combmask = fm.comb.CombMask(cthresh=20, mthresh=10).std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum()
    combmask_r = conan.comb.CombMask(cthresh=20, mthresh=10).std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum()
    combmask_5988 = core.std.MaskedMerge(combmask.std.BlankClip(), combmask, kgf.squaremask(fm, width=180, height=140, offset_x=510, offset_y=190))
    combmask_10833 = core.std.Expr([kgf.squaremask(fm, width=46, height=25, offset_x=210, offset_y=380).std.Invert(), core.std.Expr([kgf.squaremask(fm, width=100, height=60, offset_x=140, offset_y=360).std.Invert(), kgf.squaremask(fm, width=220, height=400, offset_x=500, offset_y=0).std.Invert()], "x y min")], "x y min")
    combmask_16301 = core.imwri.Read("masks/ova02_16301.png")
    combmask_21121 = core.imwri.Read("masks/ova02_21121.png")
    combmask_23080 = core.std.MaskedMerge(combmask.std.BlankClip(), combmask, kgf.squaremask(fm, width=300, height=290, offset_x=130, offset_y=25))
    combmask_26401 = kgf.squaremask(fm, width=130, height=160, offset_x=560, offset_y=170).std.Invert()
    combmask_27795 = kgf.squaremask(fm, width=332, height=370, offset_x=100, offset_y=110)
    combmask_27795_nnedi = kgf.squaremask(fm, width=30, height=10, offset_x=230, offset_y=250)
    combmask_28471 = kgf.squaremask(fm, width=290, height=400, offset_x=280, offset_y=80).morpho.Dilate(size=12)
    combmask_31566 = kgf.squaremask(fm, width=220, height=190, offset_x=500, offset_y=290)
    combmask_32862 = kgf.squaremask(fm, width=160, height=80, offset_x=140, offset_y=290).std.Invert()
    combmask_34895 = kgf.squaremask(fm, width=350, height=480, offset_x=170, offset_y=0)
    combmask_35716 = kgf.squaremask(fm, width=450, height=420, offset_x=270, offset_y=60)
    combmask_35803 = core.std.Expr([kgf.squaremask(fm, width=230, height=210, offset_x=340, offset_y=270), kgf.squaremask(fm, width=65, height=50, offset_x=340, offset_y=430).std.Invert()], "x y min")

    qtgmc = haf.QTGMC(conan, TFF=True, Preset="Very Slow", SourceMatch=2, Lossless=1, MatchEnhance=0, TR0=0, TR1=2, TR2=3, FPSDivisor=2)
    nnedi = rvf.NNEDI3.NNEDI3().rpow2(fm.std.SeparateFields(tff=0)).std.SelectEvery(cycle=2, offsets=[1]).resize.Spline36(width=fm.width, height=fm.height)
    nnedi_tff = rvf.NNEDI3.NNEDI3().rpow2(conan.std.SeparateFields(tff=1)).std.SelectEvery(cycle=2, offsets=[1]).resize.Spline36(width=fm.width, height=fm.height)
    nnedi_conan = rvf.NNEDI3.NNEDI3().rpow2(conan.std.SeparateFields(tff=0)).std.SelectEvery(cycle=2, offsets=[1]).resize.Spline36(width=fm.width, height=fm.height)

    def _masked_qtmgc(f, mask, vinverse=True, clip=fm):
        r = core.std.MaskedMerge(clip, qtgmc.vinverse.Vinverse(), mask, first_plane=True)
        if not vinverse:
            r = core.std.MaskedMerge(clip, qtgmc, mask, first_plane=True)
        return awf.ReplaceFrames(fm, r, f)

    def _masked_nnedi(clip, rclip, f, mask, vinverse=True):
        r = core.std.MaskedMerge(rclip, nnedi_conan.vinverse.Vinverse(), mask, first_plane=True)
        if not vinverse:
            r = core.std.MaskedMerge(rclip, nnedi_conan, mask, first_plane=True)
        return awf.ReplaceFrames(clip, r, f)

    fm = _masked_qtmgc("5988", combmask_5988)
    fm = awf.ReplaceFrames(fm, core.std.MaskedMerge(fm, nnedi_tff, core.std.Expr([kgf.squaremask(fm, width=270, height=380, offset_x=450, offset_y=100), combmask_r.std.ShufflePlanes(planes=0, colorfamily=GRAY).std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum()], "x y min")), "7429")
    fm = _masked_qtmgc("10833", combmask_10833)
    fm = awf.ReplaceFrames(fm, core.std.MaskedMerge(fm, nnedi_tff, combmask_r, first_plane=True), "12945")
    fm = _masked_qtmgc("16301", combmask_16301)
    fm = _masked_qtmgc("21121", combmask_21121)
    fm = _masked_qtmgc("23080", combmask_23080.std.Maximum().std.Maximum())
    fm = _masked_qtmgc("26401", combmask_26401)
    fm = awf.ReplaceFrames(fm, core.std.MaskedMerge(core.std.MaskedMerge(fm, qtgmc.vinverse.Vinverse(), combmask_27795, first_plane=True), nnedi, combmask_27795_nnedi, first_plane=True), "27795")
    fm = _masked_qtmgc("28471", combmask_28471)
    fm = _masked_qtmgc("31566", combmask_31566)
    fm = _masked_qtmgc("32862", combmask_32862)
    fm = _masked_qtmgc("34895", combmask_34895)
    fm = _masked_qtmgc("35716", combmask_35716)
    fm = _masked_qtmgc("35803", combmask_35803)
    fm = _masked_nnedi(fm, awf.ReplaceFrames(fm, conan.vinverse.Vinverse(), "42117 42118"), "42117 42118", combmask_r.morpho.Dilate(size=50))
    fm = awf.ReplaceFrames(awf.ReplaceFrames(_masked_qtmgc("[42137 44217]", core.std.Expr([kgf.squaremask(fm, width=325, height=215, offset_x=350, offset_y=130).std.Invert(), core.std.Expr([kgf.squaremask(fm, width=400, height=480, offset_x=0, offset_y=0), conan.comb.CombMask(cthresh=20, mthresh=70, mi=60).std.ShufflePlanes(planes=0, colorfamily=GRAY)], "x y min").std.BoxBlur(hradius=8).std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Binarize(35).std.BoxBlur(hradius=8)], "x y max"), vinverse=False, clip=conan), _masked_qtmgc("[42137 44217]", core.std.Expr([kgf.squaremask(fm, width=325, height=215, offset_x=350, offset_y=130).std.Invert(), core.std.Expr([kgf.squaremask(fm, width=400, height=480, offset_x=0, offset_y=0), conan.comb.CombMask(cthresh=20, mthresh=70, mi=60).std.ShufflePlanes(planes=0, colorfamily=GRAY)], "x y min").std.BoxBlur(hradius=8).std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Binarize(35).std.BoxBlur(hradius=8).std.Binarize(5).std.BoxBlur(hradius=40).std.Binarize(1).std.BoxBlur(hradius=8)], "x y max"), vinverse=False, clip=conan), "[43243 43312]"), _masked_qtmgc("[42137 44217]", core.std.Expr([kgf.squaremask(fm, width=325, height=215, offset_x=350, offset_y=130).std.Invert(), core.std.Expr([kgf.squaremask(fm, width=400, height=480, offset_x=0, offset_y=0), conan.comb.CombMask(cthresh=20, mthresh=70, mi=60).std.ShufflePlanes(planes=0, colorfamily=GRAY)], "x y min").std.BoxBlur(hradius=8).std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Binarize(35).std.BoxBlur(hradius=8).std.Binarize(5).std.BoxBlur(hradius=60).std.Binarize(1).std.BoxBlur(hradius=8)], "x y max"), vinverse=False, clip=conan), "[43658 43810]")

    fm = awf.ReplaceFrames(fm, qtgmc, "[413 456]")
    fm = awf.ReplaceFrames(fm, qtgmc.vinverse.Vinverse(), combed_frames)
    fm = awf.ReplaceFrames(fm, nnedi_tff, "19016")
    fm = awf.ReplaceFrames(fm, fm.vinverse.Vinverse(), "[549 585]")

    fm = awf.ReplaceFrames(fm, fm[0]+fm, "24 6288 9618 11890 39913") # freezing to previous frame
    fm = awf.ReplaceFrames(fm, fm[1:], "23901 14218") # freezing to next frame
    fm = awf.ReplaceFrames(fm, nnedi_tff, "14219")

    return fm.std.SetFieldBased(0)

# mostly pasted from lvsfunc.deinterlace.TIVTC_VFR
def magicdecimate(clip, fm, tdec_in="tdec_in.txt"):
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

# field matching and decimation
fm = effortfm(conan)
conan = magicdecimate(conan[:42119], fm[:42119], tdec_in=".ivtc/02_ep_tdec_in.txt") + fm[42119:44226] + magicdecimate(conan[44226:], fm[44226:], tdec_in=".ivtc/02_ed_tdec_in.txt")

flt = conan

# edgefixing
flt = rektlvls(flt, colnum=[5, 6, 7, 8, 715], colval=[46, -4, -4, 4, 40]).std.Crop(left=4, right=4)
flt = flt.fb.FillBorders(left=1, mode="fixborders")
flt = awf.bbmod(flt, left=4, right=4, thresh=1, blur=30)
flt = awf.bbmod(flt, left=4, right=4, thresh=30, blur=50)
flt = flt.resize.Bicubic(format=YUV444P16, matrix_s="170m")

# magic filter
rgbs = core.resize.Bicubic(flt, format=RGBS, matrix_in_s="170m", range_in_s="limited")
flt = lvf.deblock.autodb_dpir(rgbs, strs=[10, 14, 18, 24], thrs=[(0.0, 0.0, 0.0), (0.8, 1.2, 1.2), (1.4, 1.8, 1.8), (3.0, 4.5, 4.5)], cuda=True).resize.Bicubic(format=YUV444P16, matrix_s="170m")

# stronger deblock around lineart to get rid of more halos
mask = lvf.mask.detail_mask(flt, brz_a=0.185, brz_b=0.260).std.Maximum()
strong = DPIR(rgbs, task="deblock", device_type="cuda", strength=45).resize.Bicubic(format=YUV444P16, matrix_s="170m")
dpirmin = core.std.MaskedMerge(flt, core.std.Expr([flt, strong], "x y min"), mask)
flt = core.std.ShufflePlanes([core.std.Expr([flt, dpirmin], "x y min"), flt], planes=[0, 1, 2], colorfamily=YUV)

# "strong" deband
deband = debandshit.dumb3kdb(flt, radius=16, threshold=20)

# trying to bring back fine lines
flt = core.std.Expr([flt, deband], "x y max")

flt = flt.std.Crop(left=1, right=1)

# stretch for correct aspect ratio
flt = core.std.ShufflePlanes([vdf.scale.fsrcnnx_upscale(flt, width=710, height=540, shader_file="FSRCNNX_x2_56-16-4-1.glsl")] + vdf.scale.to_444(flt, width=710, height=540, join_planes=False), [0, 0, 0], YUV)
conan = core.std.ShufflePlanes([vdf.scale.fsrcnnx_upscale(conan, width=720, height=540, shader_file="FSRCNNX_x2_56-16-4-1.glsl")] + vdf.scale.to_444(conan, width=720, height=540, join_planes=False), [0, 0, 0], YUV)

# less strong deband that won't destroy fine lines
flt = debandshit.dumb3kdb(flt, radius=12, threshold=10, output_depth=10)

# contrasharpening
flt = core.std.Expr([flt, eoe.misc.ContraSharpening(flt, haf.FineDehalo(conan).resize.Bicubic(format=YUV444P10, matrix_s="170m").std.Crop(left=5, right=5))], "x y min")

flt.set_output()
