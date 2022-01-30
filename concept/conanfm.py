from vapoursynth import core, GRAY, YUV
from functools import partial
from parsedvd import IsoFile
from pathlib import Path
import time
import os

iso = IsoFile("[DVDISO][アニメ] 名探偵コナン 13-4")
conan = iso.get_title(0, (10, 14))

def magicscenechange(n, f, original_fields, fm50, fm51, clip, next_stripes_a, next_stripes_b, prev_stripes_a, prev_stripes_b, fields_a, fields_b, fields_a_end, fields_b_end, next_fields_a_diff, next_fields_b_diff, prev_fields_a_diff, prev_fields_b_diff):
    sc_curr = f[0].props["_SceneChangePrev"] > 0
    sc_prev = f[1].props["_SceneChangePrev"] > 0
    sc_next = f[2].props["_SceneChangePrev"] > 0
    fm50_match = f[3].props["VFMMatch"]
    fm51_match = f[4].props["VFMMatch"]
    comb_a_next = f[5].props["PlaneStatsMax"] > 0
    comb_b_next = f[6].props["PlaneStatsMax"] > 0
    comb_a_prev = f[7].props["PlaneStatsMax"] > 0
    comb_b_prev = f[8].props["PlaneStatsMax"] > 0

    out = fm50

    if (sc_curr != sc_prev) and not sc_next: # leave room for orphan field at scene start
        out = fm51
    elif fm50_match == 1 and fm51_match == 0: # either progressive frames where both clips are identical, or telecine'd frames where order=1 is better
        out = fm51

    orphan_start = sc_curr and (comb_a_next != comb_b_next) and (comb_a_prev == comb_b_prev)
    orphan_end = sc_next and (comb_a_prev != comb_b_prev) and (comb_a_next == comb_b_next)

    if sc_curr and sc_prev or sc_curr and sc_next or sc_prev and sc_next:
        orphan_start = False
        orphan_end = False

    if orphan_start == orphan_end:
        return out

    if orphan_start:
        comb_a = comb_a_next
        comb_b = comb_b_next
        fields_a_diff = next_fields_a_diff
        fields_b_diff = next_fields_b_diff
        stripes_a = next_stripes_a
        stripes_b = next_stripes_b
    else:
        comb_a = comb_a_prev
        comb_b = comb_b_prev
        fields_a = fields_a_end
        fields_b = fields_b_end
        fields_a_diff = prev_fields_a_diff
        fields_b_diff = prev_fields_b_diff
        stripes_a = prev_stripes_a
        stripes_b = prev_stripes_b

    if comb_a:
        fields = fields_a
        fields_diff = fields_a_diff
        stripes = stripes_a
    else:
        fields = fields_b
        fields_diff = fields_b_diff
        stripes = stripes_b

    if original_fields:
        mask = core.std.ShufflePlanes(clips=[stripes, fields_diff], planes=[0, 1, 2], colorfamily=YUV)
    else:
        mask = fields_diff

    if orphan_start:
        magicscenechange.orphans_start.append(n)
    else:
        magicscenechange.orphans_end.append(n)

    return core.std.MaskedMerge(clip, fields, mask)

def conanfm(clip, postprocess_func=None, original_fields=False, eedi={"alpha": 0.3, "beta": 0.15, "gamma": 80.0, "nrad": 2, "mdis": 20}, eedi2={"alpha": 0.3, "beta": 0.15, "gamma": 80.0, "nrad": 3, "mdis": 2}, nnedi={"nns": 4, "nsize": 4, "pscrn": 0, "qual": 2}):
    """
    Deinterlaces frames at scene boundaries that only have half of their fields.
    Also supports pattern changes.
    Meant for sources edited after telecine.

    clip: Telecined clip
    postprocess_func: Callable that does further filtering on deinterlaced frames
    original_fields: Only apply post-processing to interpolated fields
    """

    fm50 = clip.vivtc.VFM(mode=5, micmatch=1, order=0) # doesn't leave room for start orphan fields
    fm51 = clip.vivtc.VFM(mode=5, micmatch=1, order=1) # doesn't leave room for end orphan fields
    fm50_sc = clip.vivtc.VFM(mode=5, micmatch=1, order=0, field=0)

    magicscenechange.orphans_start = []
    magicscenechange.orphans_end = []

    super_clip = fm50_sc.mv.Super()
    vecs = super_clip.mv.Analyse()
    scenechange = fm50_sc.mv.SCDetection(vecs, thscd1=440, thscd2=150)
    scenechange_prev = scenechange[0]+scenechange
    scenechange_next = scenechange[1:]+scenechange[-1]

    next_diff = core.std.Expr([clip, fm51[1:]+fm51[-1]], "x y - abs").std.ShufflePlanes(planes=0, colorfamily=GRAY)
    next_fields_diff = next_diff.std.SeparateFields(True)
    next_fields_a = next_fields_diff[1::2]
    next_fields_b = next_fields_diff[::2]
    next_fields_a_diff = next_fields_a.resize.Spline36(height=clip.height, format=clip.format).std.Maximum().std.Binarize(10).std.Maximum().std.BoxBlur(vradius=2, hradius=2)
    next_fields_b_diff = next_fields_b.resize.Spline36(height=clip.height, format=clip.format).std.Maximum().std.Binarize(10).std.Maximum().std.BoxBlur(vradius=2, hradius=2)
    next_fields_a_stat = next_fields_a.std.Binarize(10).std.Minimum().std.PlaneStats()
    next_fields_b_stat = next_fields_b.std.Binarize(10).std.Minimum().std.PlaneStats()

    prev_diff = core.std.Expr([clip, fm50_sc[0]+fm50_sc], "x y - abs").std.ShufflePlanes(planes=0, colorfamily=GRAY)
    prev_fields_diff = prev_diff.std.SeparateFields(True)
    prev_fields_a = prev_fields_diff[1::2]
    prev_fields_b = prev_fields_diff[::2]
    prev_fields_a_diff = prev_fields_a.resize.Spline36(height=clip.height, format=clip.format).std.Maximum().std.Binarize(10).std.Maximum().std.BoxBlur(vradius=2, hradius=2)
    prev_fields_b_diff = prev_fields_b.resize.Spline36(height=clip.height, format=clip.format).std.Maximum().std.Binarize(10).std.Maximum().std.BoxBlur(vradius=2, hradius=2)
    prev_fields_a_stat = prev_fields_a.std.Binarize(10).std.Minimum().std.PlaneStats()
    prev_fields_b_stat = prev_fields_b.std.Binarize(10).std.Minimum().std.PlaneStats()

    pre_a = clip.znedi3.nnedi3(False, **nnedi)
    pre_b = clip.znedi3.nnedi3(True, **nnedi)
    nnedi_a = core.std.Expr([clip.eedi3m.EEDI3CL(field=0, sclip=pre_a, **eedi), clip.eedi3m.EEDI3CL(field=0, sclip=pre_a, **eedi2)], "x y min")
    nnedi_b = core.std.Expr([clip.eedi3m.EEDI3CL(field=1, sclip=pre_b, **eedi), clip.eedi3m.EEDI3CL(field=1, sclip=pre_b, **eedi2)], "x y min")
    nnedi_a_end = clip.std.SeparateFields(True)[1::2]
    nnedi_a_end = core.std.Expr([nnedi_a_end.eedi3m.EEDI3CL(field=0, dh=True, sclip=pre_a, **eedi), nnedi_a_end.eedi3m.EEDI3CL(field=0, dh=True, sclip=pre_a, **eedi2)], "x y min")
    nnedi_b_end = clip.std.SeparateFields(True)[::2]
    nnedi_b_end = core.std.Expr([nnedi_b_end.eedi3m.EEDI3CL(field=1, dh=True, sclip=pre_b, **eedi), nnedi_b_end.eedi3m.EEDI3CL(field=1, dh=True, sclip=pre_b, **eedi2)], "x y min")

    if postprocess_func:
        nnedi_a = postprocess_func(nnedi_a)
        nnedi_b = postprocess_func(nnedi_b)
        nnedi_a_end = postprocess_func(nnedi_a_end)
        nnedi_b_end = postprocess_func(nnedi_b_end)

    w = (1 << clip.format.bits_per_sample) - 1
    white = core.std.BlankClip(clip, height=clip.height // 2, color=[w, w, w])
    black = core.std.BlankClip(clip, height=clip.height // 2)

    stripes_a = core.std.Interleave([white, black]).std.DoubleWeave(tff=True)[::2]
    stripes_b = stripes_a.std.Invert()
    next_stripes_a = core.std.Expr([stripes_a, next_fields_a_diff], "x y min")
    next_stripes_b = core.std.Expr([stripes_b, next_fields_b_diff], "x y min")
    prev_stripes_a = core.std.Expr([stripes_a, prev_fields_a_diff], "x y min")
    prev_stripes_b = core.std.Expr([stripes_b, prev_fields_b_diff], "x y min")

    return core.std.FrameEval(clip, partial(magicscenechange, original_fields=original_fields, fm50=fm50, fm51=fm51, clip=clip, next_stripes_a=next_stripes_a, next_stripes_b=next_stripes_b, prev_stripes_a=prev_stripes_a, prev_stripes_b=prev_stripes_b, fields_a=nnedi_a, fields_b=nnedi_b, fields_a_end=nnedi_a_end, fields_b_end=nnedi_b_end, next_fields_a_diff=next_fields_a_diff, next_fields_b_diff=next_fields_b_diff, prev_fields_a_diff=prev_fields_a_diff, prev_fields_b_diff=prev_fields_b_diff), prop_src=[scenechange, scenechange_prev, scenechange_next, fm50, fm51, next_fields_a_stat, next_fields_b_stat, prev_fields_a_stat, prev_fields_b_stat])

def magicdecimate(fm, tdec_in="tdec_in.txt"):
    tdec_in = Path(tdec_in).resolve()

    # TIVTC can't write files into directories that don't exist
    if not tdec_in.parent.exists():
        tdec_in.parent.mkdir(parents=True)

    if not tdec_in.exists():
        ivtc_clip = fm.tivtc.TDecimate(mode=1, hint=True, output=str(tdec_in))

        with open(os.devnull, "wb") as dn:
            ivtc_clip.output(dn)

        # Allow it to properly finish writing the logs
        time.sleep(0.5)
        del ivtc_clip # Releases the clip, and in turn the filter (prevents it from erroring out)

    return fm.tivtc.TDecimate(mode=1, hint=True, input=str(tdec_in))

def orphandecimate(clip, tdec_in="tdec_in.txt", error=3):
    from bisect import bisect_left

    # first run through the clip to generate orphan list
    for f in clip.frames(): # clip.output() to os.devnull would be faster but could be inconsistent
        continue

    dec = clip.std.DeleteFrames(magicscenechange.orphans_start + magicscenechange.orphans_end)
    dec = magicdecimate(dec, tdec_in)

    super_clip = dec.mv.Super()
    vecs = super_clip.mv.Analyse()
    dec = dec.mv.SCDetection(vecs, thscd1=440, thscd2=150)

    i = 0

    orphans_dec = []
    decimation = 5 / 4
    remap_frames = ""

    orphans_start_count = len(magicscenechange.orphans_start)
    orphans_end_count = len(magicscenechange.orphans_end)

    for f in dec.frames():
        if f.props["_SceneChangePrev"] > 0:
            offset = len(orphans_dec)

            og_f = int((i-1)*decimation)
            closest_end = bisect_left(magicscenechange.orphans_end, og_f+offset-error)
            if og_f > 0 and closest_end < orphans_end_count and abs(magicscenechange.orphans_end[closest_end] - og_f - offset) <= error and i-1 not in orphans_dec:
                remap_frames += f"{i+offset} {magicscenechange.orphans_end[closest_end]}\n"
                orphans_dec.append(i-1)
                offset += 1

            og_f = int(i*decimation)
            closest_start = bisect_left(magicscenechange.orphans_start, og_f+offset-error)
            if og_f > 0 and closest_start < orphans_start_count and abs(magicscenechange.orphans_start[closest_start] - og_f - offset) <= error and i not in orphans_dec:
                remap_frames += f"{i+offset} {magicscenechange.orphans_start[closest_start]}\n"
                orphans_dec.append(i)
        i += 1

    splice = dec.std.DuplicateFrames(orphans_dec)
    splice_len = len(splice)

    splice = splice + splice.std.BlankClip(length=len(clip) - len(splice))

    splice = core.remap.RemapFrames(baseclip=splice, sourceclip=clip, mappings=remap_frames, mismatch=True)
    splice = splice[:splice_len]

    return splice

fm = conanfm(conan)
spliced = orphandecimate(conan, "366-dec.txt")
spliced = spliced.std.AssumeFPS(fm) # for vspreview

conan.set_output(0)
fm.set_output(1)
spliced.set_output(2)
