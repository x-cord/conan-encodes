import os
import time
import debandshit
import lvsfunc as lvf
import rvsfunc as rvf
import EoEfunc as eoe
import awsmfunc as awf
import havsfunc as haf
import vardefunc as vdf
from vsdpir import DPIR
from pathlib import Path
import vapoursynth as vs
from rekt import rektlvls
from lvsfunc.types import Range
from typing import Tuple, Union, List
from vardefunc.misc import merge_chroma
from vsutil import iterate, depth, get_y
from kagefunc import squaremask as kgf_squaremask

core = vs.core

conan = core.d2v.Source("sf-vol1/VTS_01_1.d2v")[43320:88220]

combed_frames = [
    2549, 4748, 6762, 10567, 13984, 15523,
    18453, 18551, 20459, 20809, 28045,
    30083, 34586, 35147, 36332, 39772
]

rvf_nnedi3 = rvf.NNEDI3.NNEDI3()


def Maximum(clip: vs.VideoNode, iterations: int) -> vs.VideoNode:
    return iterate(clip, core.std.Maximum, iterations)


def get_combmask(clip: vs.VideoNode) -> vs.VideoNode:
    return Maximum(clip.comb.CombMask(cthresh=20, mthresh=10), 6)


def squaremask(clip: vs.VideoNode, width: int, height: int, offset_x: int, offset_y: int, invert: bool = False) -> vs.VideoNode:
    mask = kgf_squaremask(clip, width, height, offset_x, offset_y)

    return mask.std.InvertMask() if invert else mask


def replace_squaremask(
    clipa: vs.VideoNode, clipb: vs.VideoNode, mask_params: Tuple[int, int, int, int],
    ranges: Union[Range, List[Range], None], invert: bool = False, first_plane: bool = True
) -> vs.VideoNode:
    mask = squaremask(clipb, *mask_params, invert=invert)

    return lvf.rfs(
        clipa, clipa.std.MaskedMerge(
            clipb, mask, first_plane=first_plane
        ), ranges
    )


def xymin(*clips: vs.VideoNode) -> vs.VideoNode:
    return core.std.Expr(clips, 'x y min')


def xymax(*clips: vs.VideoNode) -> vs.VideoNode:
    return core.std.Expr(clips, 'x y max')


def effortfm(conan: vs.VideoNode) -> vs.VideoNode:
    fm = conan.vivtc.VFM(1)

    # we're missing a half-frame at the end of this panning shot 33741--not worth the effort

    combmask, combmask_r = get_combmask(fm), get_combmask(conan)

    blank_clip = combmask.std.BlankClip()

    combmask_5988 = core.std.MaskedMerge(
        blank_clip, combmask, squaremask(fm, 180, 140, 510, 190)
    )

    combmask_10833 = xymin(
        squaremask(fm, 46, 25, 210, 380, True),
        xymin(
            squaremask(fm, 100, 60, 140, 360, True),
            squaremask(fm, 220, 400, 500, 0, True)
        )
    )

    combmask_16301 = core.imwri.Read("masks/ova02_16301.png")
    combmask_21121 = core.imwri.Read("masks/ova02_21121.png")

    combmask_28471 = squaremask(fm, 290, 400, 280, 80).morpho.Dilate(size=12)

    combmask_23080 = core.std.MaskedMerge(
        blank_clip, combmask,
        squaremask(fm, 300, 290, 130, 25)
    )

    combmask_27795 = squaremask(fm, 332, 370, 100, 110)
    combmask_27795_nnedi = squaremask(fm, 30, 10, 230, 250)

    combmask_35803 = xymin(
        squaremask(fm, 230, 210, 340, 270),
        squaremask(fm, 65, 50, 340, 430, True)
    )

    qtgmc = haf.QTGMC(
        conan, TFF=True, Preset="Very Slow",
        SourceMatch=2, Lossless=1, MatchEnhance=0,
        TR0=0, TR1=2, TR2=3, FPSDivisor=2
    )

    qtgmc_vinv = qtgmc.vinverse.Vinverse()

    def _nnedi3rpow(clip: vs.VideoNode, tff: int = 0) -> vs.VideoNode:
        fields = fm.std.SeparateFields(tff=tff)

        rpow = rvf_nnedi3.rpow2(fields).std.SelectEvery(cycle=2, offsets=[1])

        return rpow.resize.Spline36(fm.width, fm.height)

    nnedi, nnedi_tff, nnedi_conan = _nnedi3rpow(fm, 0), _nnedi3rpow(conan, 1), _nnedi3rpow(conan, 0)

    nnedi_conan_vinv = nnedi_conan.vinverse.Vinverse()

    def _masked_qtmgc(frames: vs.VideoNode, mask: vs.VideoNode) -> vs.VideoNode:
        replace = core.std.MaskedMerge(fm, qtgmc_vinv, mask, first_plane=True)

        return lvf.rfs(fm, replace, frames)

    def _smasked_qtgmc(
        clip: vs.VideoNode, mask_params: Tuple[int, int, int, int],
        ranges: Union[Range, List[Range], None], invert: bool = False
    ) -> vs.VideoNode:
        return replace_squaremask(clip, qtgmc_vinv, mask_params, ranges, invert, True)

    fm = _masked_qtmgc(5988, combmask_5988)

    fm = lvf.rfs(
        fm, core.std.MaskedMerge(
            fm, nnedi_tff, xymin(
                squaremask(fm, 270, 380, 450, 100),
                Maximum(get_y(combmask_r), 6),
            )
        ), 7429
    )

    fm = _masked_qtmgc(10833, combmask_10833)
    fm = lvf.rfs(fm, core.std.MaskedMerge(fm, nnedi_tff, combmask_r, first_plane=True), 12945)
    fm = _masked_qtmgc(16301, combmask_16301)
    fm = _masked_qtmgc(21121, combmask_21121)
    fm = _masked_qtmgc(23080, combmask_23080.std.Maximum().std.Maximum())

    fm = lvf.rfs(
        fm, core.std.MaskedMerge(
            core.std.MaskedMerge(
                fm, qtgmc_vinv, combmask_27795, first_plane=True
            ), nnedi, combmask_27795_nnedi, first_plane=True
        ), 27795
    )

    fm = _masked_qtmgc(28471, combmask_28471)
    fm = _masked_qtmgc(35803, combmask_35803)

    fm = _smasked_qtgmc(fm, (130, 160, 560, 170), 26401, True)
    fm = _smasked_qtgmc(fm, (220, 190, 500, 290), 31566)
    fm = _smasked_qtgmc(fm, (160, 80, 140, 290), 32862, True)
    fm = _smasked_qtgmc(fm, (350, 480, 170, 0), 34895)
    fm = _smasked_qtgmc(fm, (450, 420, 270, 60), 35716)

    fm = lvf.rfs(
        conan.vinverse.Vinverse(),
        core.std.MaskedMerge(
            fm, nnedi_conan_vinv,
            combmask_r.morpho.Dilate(size=50),
            first_plane=True
        ), (42117, 42118)
    )

    pieceofshit_mask = core.std.Expr([
        squaremask(fm, width=400, height=480, offset_x=0, offset_y=0),
        get_y(conan.comb.CombMask(cthresh=20, mthresh=70, mi=60))
    ], "x y min")

    def pieceofshit(blur_iterations: int = 0, blur_hradius: int = 40) -> vs.VideoNode:
        mask = pieceofshit_mask

        if blur_iterations > 0:
            mask = Maximum(mask.std.BoxBlur(hradius=8), 5).std.Binarize(35).std.BoxBlur(hradius=8)

            for _ in blur_iterations:
                mask = mask.std.Binarize(5).std.BoxBlur(hradius=blur_hradius).std.Binarize(1).std.BoxBlur(hradius=8)

        return lvf.rfs(
            fm, core.std.MaskedMerge(
                conan, qtgmc, xymax(
                    squaremask(fm, 325, 215, 350, 130, True), mask
                ), first_plane=True
            ), (42137, 44217)
        )

    fm = lvf.rfs(
        lvf.rfs(pieceofshit(), pieceofshit(1, 40), (43243, 43312)),
        pieceofshit(1, 60), (43658, 43810)
    )

    fm = lvf.rfs(fm, qtgmc_vinv, combed_frames)
    fm = lvf.rfs(fm, nnedi_tff, 19016)
    fm = lvf.rfs(fm, fm.vinverse.Vinverse(), (549, 585))

    # freezing to previous frame
    fm = lvf.rfs(fm, fm[0] + fm, [24, 6288, 9618, 11890, 39913])

    # freezing to next frame
    fm = lvf.rfs(fm, fm[1:], [23901, 14218])

    fm = lvf.rfs(fm, nnedi_tff, 14219)

    return fm.std.SetFieldBased(0)


def magicdecimate(clip: vs.VideoNode, fm: vs.VideoNode, tdec_in: Path = "tdec_in.txt") -> vs.VideoNode:
    tdec_in = Path(tdec_in).resolve()

    # TIVTC can't write files into directories that don't exist
    if not tdec_in.parent.exists():
        tdec_in.parent.mkdir(parents=True)

    if not tdec_in.exists():
        ivtc_clip = fm.tivtc.TDecimate(mode=1, hint=True, output=str(tdec_in))

        with lvf.render.get_render_progress() as pr:
            task = pr.add_task("Analyzing frames...", total=ivtc_clip.num_frames)

            def _cb(n: int, total: int) -> None:
                pr.update(task, advance=1)

            with open(os.devnull, "wb") as dn:
                ivtc_clip.output(dn, progress_update=_cb)

        # Allow it to properly finish writing the logs
        time.sleep(0.5)
        del ivtc_clip  # Releases the clip, and in turn the filter (prevents it from erroring out)

    return fm.tivtc.TDecimate(mode=1, hint=True, input=str(tdec_in))


# field matching and decimation
fm = effortfm(conan)

conan = magicdecimate(conan[:42119], fm[:42119], tdec_in=".ivtc/02_ep_tdec_in.txt")
conan += fm[42119:44226] + magicdecimate(conan[44226:], fm[44226:], tdec_in=".ivtc/02_ed_tdec_in.txt")

# edgefixing
flt = rektlvls(conan, colnum=[5, 6, 7, 8, 715], colval=[46, -4, -4, 4, 40]).std.Crop(left=4, right=4)
flt = flt.fb.FillBorders(left=1, mode="fixborders")
flt = awf.bbmod(flt, left=4, right=4, thresh=1, blur=30)
flt = awf.bbmod(flt, left=4, right=4, thresh=30, blur=50)
flt = flt.resize.Bicubic(format=vs.YUV444P16, matrix_s="170m")

# magic filter
rgbs = core.resize.Bicubic(flt, format=vs.RGBS, matrix_in_s="170m", range_in_s="limited")

flt = lvf.deblock.autodb_dpir(
    rgbs,
    strs=[10, 14, 18, 24],
    thrs=[
        (0.0, 0.0, 0.0),
        (0.8, 1.2, 1.2),
        (1.4, 1.8, 1.8),
        (3.0, 4.5, 4.5)
    ],
    cuda=True
).resize.Bicubic(format=vs.YUV444P16, matrix_s="170m")

# stronger deblock around lineart to get rid of more halos
mask = lvf.mask.detail_mask(flt, brz_a=0.185, brz_b=0.260).std.Maximum()

strong = DPIR(rgbs, task="deblock", device_type="cuda", strength=45)
strong = strong.resize.Bicubic(format=vs.YUV444P16, matrix_s="170m")

dpirmin = core.std.MaskedMerge(flt, core.std.Expr([flt, strong], "x y min"), mask)

flt = merge_chroma(xymin(flt, dpirmin), flt)

# "strong" deband
deband = debandshit.dumb3kdb(flt, 16, 20)

# trying to bring back fine lines
flt = core.std.Expr([flt, deband], "x y max")

flt = flt.std.Crop(left=1, right=1)


def stretch(clip: vs.VideoNode, width: int) -> vs.VideoNode:
    """Stretch video for correct aspect ratio"""
    return merge_chroma(
        vdf.scale.fsrcnnx_upscale(conan, width, 540, "FSRCNNX_x2_56-16-4-1.glsl"),
        vdf.scale.to_444(conan, width, 540, False)
    )


flt = stretch(flt, 710)
conan = stretch(conan, 710)

# less strong deband that won't destroy fine lines
flt = debandshit.dumb3kdb(flt, 12, 10)

dehalo = haf.FineDehalo(conan).resize.Bicubic(format=vs.YUV444P16, matrix_s="170m").std.Crop(5, 5)

flt = core.std.Expr([
    flt,
    eoe.misc.ContraSharpening(flt, dehalo)
], "x y min")

flt = depth(flt, 10)

flt.set_output()
