from vapoursynth import YUV, GRAY, core
import awsmfunc as awf
import kagefunc as kgf
import havsfunc as haf

# didn't bother fixing the logo fadeout at [967 996]
# still missing the half-frame at 26992, but TDecimate made it seamless (no stutter)

# bad mpeg2 12418

# this section is way too sharp [3944 3999]

# animation errors:
# [14408 14410] missing line

# need to qtgmc this half-frame 26153

conan = core.lsmas.LWLibavSource("ova02.y4m") # dump of ova02.py output

# fix chroma shift except during credits
flt = awf.ReplaceFrames(conan.resize.Bicubic(src_left=-0.6), conan, "[33695 35801]")

# slightly less fucked edgefixing
flt = awf.fb(flt, left=2)
flt = awf.bbmod(flt, left=3, thresh=20, blur=30)

flt = core.std.ShufflePlanes([conan, flt], [0, 1, 2], YUV)

# logo fade
flt = awf.ReplaceFrames(flt, flt[1:], "890 919") # freezing to next frame

flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.98), "918")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.96), "917")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.94), "916")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.86), "915")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.84), "914")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.80), "913")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.76), "912")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.72), "911")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.68), "910")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.65), "909")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.62), "908")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.58), "907")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.56), "906")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.52), "905")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.50), "904")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.45), "903")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.42), "902")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.38), "901")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.34), "900")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.30), "899")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.24), "898")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.21), "897")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.18), "896")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[891]*921, flt[925]*921, weight=0.14), "895")

flt = awf.ReplaceFrames(flt, core.std.Merge(flt[890]*891, flt[878]*891, weight=0.15), "889")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[890]*891, flt[878]*891, weight=0.22), "888")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[890]*891, flt[878]*891, weight=0.30), "887")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[890]*891, flt[878]*891, weight=0.37), "886")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[890]*891, flt[878]*891, weight=0.44), "885")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[890]*891, flt[878]*891, weight=0.50), "884")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[890]*891, flt[878]*891, weight=0.64), "883")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[890]*891, flt[878]*891, weight=0.78), "882")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[890]*891, flt[878]*891, weight=0.85), "881")
flt = awf.ReplaceFrames(flt, core.std.Merge(flt[890]*891, flt[878]*891, weight=0.92), "880")

flt = awf.ReplaceFrames(flt, flt[890]*895, "[892 894]")
flt = awf.ReplaceFrames(flt, flt[925]*954, "[921 953]")

# fix credits animation deinterlacing
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(flt, flt[1:], kgf.squaremask(flt, width=325, height=240, offset_x=350, offset_y=146)), "33749 33757 33772 33783 34001 34004 34012 34020 34024 34028 34031 34035 34039 34041 34046 34050 34054 34065 34119 34121 34125 34133 34136 34263 34280 34288 34291 34300 34302 34345 34347 34351 34358 34381 34396 34398 34413 34424 34628 34632 34636 35020 35024 35031 35035 35039 35043 35045 35049  35056 35059 35062 35070 35074 35078 35080 35090 35102 35228 35389 35427 35533 35537 35541 35545 35555 35611 35616 35618 35622 35675 35680 35683 35687 35776 35780 35783 35787") # freezing to next frame
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(flt, flt[0]+flt, kgf.squaremask(flt, width=325, height=240, offset_x=350, offset_y=146)), "35395") # freezing to previous frame
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(flt, flt[1:], core.std.Expr([kgf.squaremask(flt, width=325, height=240, offset_x=350, offset_y=146), core.std.Expr([flt.std.ShufflePlanes(planes=0, colorfamily=GRAY).std.Binarize(500), flt.std.ShufflePlanes(planes=1, colorfamily=GRAY).std.Binarize(500)], "x y min").std.BoxBlur(vradius=8).std.Maximum().std.Binarize(1).std.BoxBlur(hradius=2).std.Maximum().std.Binarize(1).std.BoxBlur(vradius=8).std.Binarize(1).std.Binarize().std.BoxBlur(vradius=8).std.Invert()], "x y min")), "34428 34432 34469 34473 34514 34518 34562 34566 34733 34738 34741 34743 34755 34766 34774 34775 34776 34782 34789 34792 34794 34797 34801 34914 34918 34921 34925 34929 34933 34936 34940 34944 34948 34951 34956 34959 34978 34980 34986 34990 34994 35356 35359") # freezing to next frame, avoiding white credits

# residual combing
flt = awf.ReplaceFrames(flt, haf.Vinverse(haf.Vinverse(flt)), "36300 36301")

# weirdest interlacing artifact I've seen --this probably doesn't have a name
flt = awf.ReplaceFrames(flt, flt[1:], "52 6435 6463 11996 12002 12042 12138 12281") # freezing to next frame
flt = awf.ReplaceFrames(flt, flt[0]+flt, "6425 12493 12305") # freezing to previous frame

flt.set_output()
