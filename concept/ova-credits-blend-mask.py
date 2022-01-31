from vapoursynth import core, GRAY
import havsfunc as haf
import kagefunc as kgf

conan = core.d2v.Source("sf-vol1/VTS_01_1.d2v")
conan = conan[88220:131732] # ova3

cr = conan[39399:41887]
qtgmc = haf.QTGMC(cr, TFF=True, Preset="Very Slow", SourceMatch=2, Lossless=1, MatchEnhance=0, TR0=0, TR1=2, TR2=3, FPSDivisor=2)
cr = qtgmc

def gen_shifts(clip, n, shift, forward=True, backward=True):
    shifts = [clip]
    for cur in range(1, n+1):
        if forward:
            shifts.append(clip[1*cur:].resize.Bicubic(src_top=-shift*cur)+clip[0]*cur)
        if backward:
            shifts.append(clip[0]*cur+clip.resize.Bicubic(src_top=shift*cur)[:-1*cur])
    return shifts

def shift_blend(clip, n, shift, forward=True, backward=True):
    return core.average.Mean(gen_shifts(clip, n, shift, forward, backward))

def shift_mask(mask, mask_height, shift, forward=True, backward=True, vertical=True):
    mask = mask.std.ShufflePlanes(planes=0, colorfamily=GRAY)
    return_mask = mask
    shifted = 0
    while shifted < mask.height:
        shifted += mask_height
        if forward:
            shift_frames = int(shifted/shift)
            shifted_mask = mask[0]*shift_frames+mask.resize.Bicubic(src_top=shift_frames*shift)[:-1*shift_frames]
            try:
                original_area = kgf.squaremask(mask, width=mask.width, height=shifted, offset_x=0, offset_y=mask.height-shifted).std.Invert()
            except:
                return return_mask
            shifted_mask = core.std.Expr([original_area, shifted_mask], "x y min")
            return_mask = core.std.Expr([return_mask, shifted_mask], "x y max")
    return return_mask

coolarea = kgf.squaremask(cr, width=720, height=290, offset_x=0, offset_y=95).std.Invert()

coolmask = core.std.Expr([cr.std.Binarize(30).std.ShufflePlanes(planes=0, colorfamily=GRAY), coolarea], "x y min")

coolmask2 = shift_mask(mask=coolmask, mask_height=92, shift=3, forward=True, backward=True)

flt = shift_blend(cr, 2, shift=3)

cr.set_output(0)
flt.set_output(1)
coolmask2.set_output(2)
cunkmask = core.std.Expr([core.std.Expr([coolarea, coolmask2], "x y max"), kgf.squaremask(cr, width=720, height=468, offset_x=0, offset_y=6)], "x y min").std.Minimum().std.BoxBlur(hradius=1, vradius=1)
core.std.MaskedMerge(cr, flt, cunkmask).set_output(3)
cunkmask.set_output(4)
