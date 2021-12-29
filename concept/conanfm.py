from vapoursynth import core, GRAY, YUV
from functools import partial
from parsedvd import IsoFile

iso = IsoFile("[DVDISO][アニメ] 名探偵コナン 13-4")
conan = iso.get_title(0, (10, 14))

def magicscenechange(n, f, original_fields, fm50, fm51, fm50_sc, clip, next_stripes_a, next_stripes_b, prev_stripes_a, prev_stripes_b, fields_a, fields_b, fields_a_end, fields_b_end, next_fields_a_diff, next_fields_b_diff, prev_fields_a_diff, prev_fields_b_diff):
    sc_curr = f[0].props["_SceneChangePrev"] > 0
    sc_prev = f[1].props["_SceneChangePrev"] > 0
    sc_next = f[2].props["_SceneChangePrev"] > 0
    sc_next2 = f[3].props["_SceneChangePrev"] > 0
    sc_next3 = f[4].props["_SceneChangePrev"] > 0
    fm50_match = f[5].props["VFMMatch"]
    fm51_match = f[6].props["VFMMatch"]
    comb_a_next = f[7].props["PlaneStatsMax"] > 0
    comb_b_next = f[8].props["PlaneStatsMax"] > 0
    comb_a_prev = f[9].props["PlaneStatsMax"] > 0
    comb_b_prev = f[10].props["PlaneStatsMax"] > 0

    out = fm50

    if f[5].props["_Combed"] == 1:
        out = fm50_sc

    if sc_next or sc_next2 or sc_next3: # leave room for orphan field at scene end --bad hack that will probably break on some patterns, not sure
        out = fm50_sc
    elif (sc_curr != sc_prev) and not sc_next: # leave room for orphan field at scene start
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
        #print("orphan_start", n)
        comb_a = comb_a_next
        comb_b = comb_b_next
        fields_a_diff = next_fields_a_diff
        fields_b_diff = next_fields_b_diff
        stripes_a = next_stripes_a
        stripes_b = next_stripes_b
    else:
        #print("orphan_end", n)
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

    out = core.std.MaskedMerge(clip, fields, mask)

    return out

def conanfm(clip, postprocess_func=None, original_fields=False):
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

    super_clip = fm50_sc.mv.Super()
    vecs = super_clip.mv.Analyse()
    scenechange = fm50_sc.mv.SCDetection(vecs, thscd1=440, thscd2=150)
    scenechange_prev = scenechange[0]+scenechange
    scenechange_next = scenechange[1:]+scenechange[-1]
    scenechange_next2 = scenechange_next[1:]+scenechange_next[-1]
    scenechange_next3 = scenechange_next2[1:]+scenechange_next2[-1]

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

    nnedi_a = clip.eedi3m.EEDI3CL(field=0, sclip=clip.znedi3.nnedi3(False, nns=4, nsize=4, pscrn=0, qual=2), alpha=0.4, beta=0.55, gamma=80.0)
    nnedi_b = clip.eedi3m.EEDI3CL(field=1, sclip=clip.znedi3.nnedi3(True, nns=4, nsize=4, pscrn=0, qual=2), alpha=0.4, beta=0.55, gamma=80.0)
    nnedi_a_end = clip.std.SeparateFields(True)[1::2].eedi3m.EEDI3CL(field=0, dh=True, sclip=clip.znedi3.nnedi3(False, nns=4, nsize=4, pscrn=0, qual=2), alpha=0.4, beta=0.55, gamma=80.0)
    nnedi_b_end = clip.std.SeparateFields(True)[::2].eedi3m.EEDI3CL(field=1, dh=True, sclip=clip.znedi3.nnedi3(True, nns=4, nsize=4, pscrn=0, qual=2), alpha=0.4, beta=0.55, gamma=80.0)

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

    return core.std.FrameEval(clip, partial(magicscenechange, original_fields=original_fields, fm50=fm50, fm51=fm51, fm50_sc=fm50_sc, clip=clip, next_stripes_a=next_stripes_a, next_stripes_b=next_stripes_b, prev_stripes_a=prev_stripes_a, prev_stripes_b=prev_stripes_b, fields_a=nnedi_a, fields_b=nnedi_b, fields_a_end=nnedi_a_end, fields_b_end=nnedi_b_end, next_fields_a_diff=next_fields_a_diff, next_fields_b_diff=next_fields_b_diff, prev_fields_a_diff=prev_fields_a_diff, prev_fields_b_diff=prev_fields_b_diff), prop_src=[scenechange, scenechange_prev, scenechange_next, scenechange_next2, scenechange_next3, fm50, fm51, next_fields_a_stat, next_fields_b_stat, prev_fields_a_stat, prev_fields_b_stat])

conan.set_output(0)
conanfm(conan).set_output(1)
