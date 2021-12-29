from vapoursynth import core, YUV444P8, GRAY, RGBS, YUV
import havsfunc as haf
import kagefunc as kgf
from vsdpir import DPIR
import notvlc
import muvsfunc as muvf

def ReplaceEvery(a, b, cycle=5, offsets=[0, 1, 2, 3, 4]):
    """
    Replace a clip with another at a given interval.

    :param a:               Original clip
    :param b:               Replacement clip
    :param cycle:           Cycle length in frames
    :param offsets:         Frames in cycle to replace (see std.SelectEvery)
    """
    offsets_a = set(list(range(cycle))) - set(offsets)
    offsets_a = [x*2 for x in offsets_a]
    offsets_b = [x*2+1 for x in offsets]
    offsets = sorted(offsets_a + offsets_b)
    return core.std.Interleave([a, b]).std.SelectEvery(cycle=cycle*2, offsets=offsets)

conan = core.d2v.Source("[DVDISO][アニメ] 名探偵コナン 10-9/VTS_01_1.d2v")
conan = notvlc.dvd_titles("[DVDISO][アニメ] 名探偵コナン 10-9", conan, title=1)[:4]
conan = core.std.Splice([conan[0], conan[1], conan[2], conan[3]])
vfm = conan.vivtc.VFM(order=1, field=3, cthresh=3)
flt = ReplaceEvery(vfm, conan.vivtc.VFM(order=1, field=1, cthresh=3), offsets=[4])
comb = flt.comb.CombMask().std.BoxBlur(hradius=2, vradius=2)
flt = core.std.MaskedMerge(flt, haf.QTGMC(flt, TFF=True, SourceMatch=3, Lossless=2, TR0=1, TR1=2, TR2=3, FPSDivisor=2), comb)
flt = flt.vinverse.Vinverse()

conan = conan.std.SelectEvery(cycle=5, offsets=[0, 1, 2, 4])
flt = flt.std.SelectEvery(cycle=5, offsets=[0, 1, 2, 4])

dot = core.std.ShufflePlanes([core.std.Expr([flt.dotkill.DotKillS(2), flt], "x y min"), flt], [0, 1, 2], YUV)
dot = dot.resize.Bicubic(format=YUV444P8, matrix_s="170m", matrix_in_s="170m")
adb = fvf.AutoDeblock(dot)

mask_dot = dot.std.Binarize(50).std.Maximum().std.Maximum()
mask_dot = core.std.MaskedMerge(core.std.MaskedMerge(kgf.retinex_edgemask(dot), core.std.ShufflePlanes(mask_dot.std.BlankClip(), 0, colorfamily=GRAY), core.std.ShufflePlanes(mask_dot, 0, colorfamily=GRAY)).std.Maximum().std.Binarize(48).std.Maximum().morpho.Dilate().std.BoxBlur(hradius=2, vradius=2).std.Maximum(), core.std.ShufflePlanes(mask_dot.std.BlankClip(), 0, colorfamily=GRAY), core.std.ShufflePlanes(mask_dot, 0, colorfamily=GRAY))

rgbs = core.resize.Bicubic(dot, format=RGBS, matrix_in_s="170m")
rgbs = DPIR(rgbs, task="deblock", device_type="cpu", strength=20)
weak = rgbs.resize.Bicubic(format=YUV444P8, matrix_s="170m")
weak = core.std.MaskedMerge(weak, dot, weak.std.Binarize(threshold=20, v0=255, v1=0, planes=0).std.Maximum())
weak = core.std.ShufflePlanes([core.std.MaskedMerge(weak, core.std.Expr([dot, weak], "x y min"), mask_dot), weak], [0, 1, 2], YUV)

rgbs = core.resize.Bicubic(weak, format=RGBS, matrix_in_s="170m")
mask = vdf.mask.FDOG().get_mask(weak)
dn = core.std.MaskedMerge(weak, DPIR(rgbs, task="denoise", device_type="cpu", strength=8).resize.Bicubic(format=YUV444P8, matrix_s="170m"), mask)
dn = core.std.MaskedMerge(kgf.adaptive_grain(dn.placebo.Deband(radius=4, threshold=2, grain=2), luma_scaling=18, strength=0.12), dn, mask)

dnm = core.std.ShufflePlanes([core.std.MaskedMerge(dn, core.std.Expr([adb, dn], "x y min"), mask), dn], [0, 1, 2], YUV)

conan.set_output(0)
dnm.set_output(1)
