from vapoursynth import YUV444P10, YUV, core
import awsmfunc as awf
import kagefunc as kgf
import havsfunc as haf
import lvsfunc as lvf

conan = core.lsmas.LWLibavSource("ova01.y4m") # dump of ova01.py output

og = conan
credit = core.imwri.Read("fixup/ova01_33182.png").resize.Bicubic(format=YUV444P10, matrix_s="170m", dither_type="error_diffusion").resize.Bicubic(format=YUV444P10, matrix_s="170m", matrix_in_s="709", dither_type="error_diffusion")
credit = credit.std.AssumeFPS(conan).resize.Bicubic(src_left=-1)
conan = awf.ReplaceFrames(conan, credit*33183, "33182")

# slightly less fucked edgefixing
flt = awf.fb(conan, right=2)
flt = awf.bbmod(flt, right=3, thresh=20, blur=20)

flt = awf.FillBorders(flt, left=1, mode="fixborders")

flt = core.std.ShufflePlanes([conan, flt], [0, 1, 2], YUV)

flt = awf.FillBorders(flt, right=1, mode="fixborders")

# freeze framing
flt = awf.ReplaceFrames(flt, flt[1:], "134 316 1755 3947 5846 5855 6967 9721 10669 10672 10675 10678 10681 10684 10686 10689 10696 10699 10702 10705 10707 10710 10712 10714 10718 10720 10722 13961 13964 13966 13969 16776 16779 16783 16786 16789 16792 16795 16798 16953 16955 16957 16960 16963 16966 17157 17160 17162 23629 23654 23659 23670 25206 25208 25210 25214 25716 25718 25720 25788 25791 25794 25800 25797 25817 25819 25822 25824 25833 25836 25838 25841 25843 25845 25847 25850 25852 25854 25856 25860 25863 25866 25869 25878 25915 27806 27810 27813 27816 27820 28682 28686 28688 28692 28695 28698 28701 28704 28707 28710 28712 28715 27058 27061 27071 27074 27081 30551 30554 30558 32411 32436 33863 33865 33876 33878") # freezing to next frame
flt = awf.ReplaceFrames(flt, flt[2:], "133 315 1754 3946 5845 5854 10668 10671 10674 10677 10680 10683 10688 10695 10698 10701 10704 10709 10717 13960 13963 13968 16782 16785 16788 16791 16794 16797 16965 17156 17159 23653 23669 25213 25715 25787 25790 25793 25796 25799 25816 25821 25832 25835 25840 25849 25859 25862 25865 25868 25877 27809 27812 27815 27819 28685 28691 28694 28697 28700 28703 28706 28709 27060 27073 27080 30553 30557 33875") # freezing to frame +2
flt = awf.ReplaceFrames(flt, flt[3:], "27818") # freezing to frame +3
flt = awf.ReplaceFrames(flt, flt[:5]+flt, "3163 5853") # freezing to frame -5
flt = awf.ReplaceFrames(flt, flt[0]+flt, "130 314 1394 1752 1940 23278 4214 4355 3164 3512 5849 6965 9709 17055 17078 20006 23651 23657 23674 23675 25199 25227 25809 28287 27087 31457 33867") # freezing to previous frame
flt = awf.ReplaceFrames(flt, flt[:2]+flt, "131 1753 1941 4215 4356 3513 5850 6966 9710 23652 23658 31458") # freezing to frame -2
flt = awf.ReplaceFrames(flt, flt[:3]+flt, "132 4357 3514 5851 9711") # freezing to frame -3
flt = awf.ReplaceFrames(flt, flt[:4]+flt, "5852") # freezing to frame -4
flt = awf.ReplaceFrames(flt, flt[31418]*31418, "[31395 31417]")
flt = awf.ReplaceFrames(flt, flt[1706]*1728, "[1708 1727]")

# only affect right edge
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(conan, flt, kgf.squaremask(flt, width=6, height=540, offset_x=flt.width-6, offset_y=0)), "[130 134] [314 316] [1708 1727] [1752 1755] [1940 1941] [3512 3514] [3946 3947] [4214 4215] [4355 4357] [5845 5846] [5849 5855] [6965 6967]")
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(conan, flt, kgf.squaremask(flt, width=8, height=540, offset_x=flt.width-8, offset_y=0)), "[31395 31417]")
flt = awf.ReplaceFrames(flt, haf.Deblock_QED(flt, quant1=42, quant2=46), "[5851 5853]")
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(conan, flt, kgf.squaremask(flt, width=4, height=540, offset_x=flt.width-4, offset_y=0)), "[5851 5853] [9709 9711] 9721 23629 [23651 23659] [23669 23675]")
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(conan, flt, kgf.squaremask(flt, width=325, height=240, offset_x=360, offset_y=146)), "32411 32436 33863 33865 33867 [33875 33876] 33878")

# interlacing error
deint_24447 = core.imwri.Read("fixup/ova01_24447.png").resize.Bicubic(format=YUV444P10, matrix_s="170m", dither_type="error_diffusion").resize.Bicubic(format=YUV444P10, matrix_s="709", matrix_in_s="170m", dither_type="error_diffusion")
deint_24447 = deint_24447.std.AssumeFPS(flt)
deint_24447 = deint_24447*24448
mask_24447 = core.imwri.Read("masks/ova01_24447.png").resize.Bicubic(format=YUV444P10, matrix_s="170m", dither_type="error_diffusion").resize.Bicubic(format=YUV444P10, matrix_s="709", matrix_in_s="170m", dither_type="error_diffusion")
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(flt, deint_24447, mask_24447, first_plane=True), "24447")

# heiji shot edges
edges_27372 = core.imwri.Read("fixup/ova01_27372.png").resize.Bicubic(format=YUV444P10, matrix_s="170m", dither_type="error_diffusion").resize.Bicubic(format=YUV444P10, matrix_s="709", matrix_in_s="170m", dither_type="error_diffusion")
edges_27372 = edges_27372.std.AssumeFPS(flt)
edges_27372 = edges_27372*27373
mask_27372 = core.imwri.Read("masks/ova01_27372.png").resize.Bicubic(format=YUV444P10, matrix_s="170m", dither_type="error_diffusion").resize.Bicubic(format=YUV444P10, matrix_s="709", matrix_in_s="170m", dither_type="error_diffusion")
flt = awf.ReplaceFrames(flt, awf.bbmod(core.std.MaskedMerge(flt, edges_27372, mask_27372, first_plane=True), left=4, right=8, thresh=10, blur=20), "[27303 27372]")

# terrible hack, anti-aliasing the panning shot
mask_32096_32145 = core.imwri.Read("masks/ova01_32096_32145.png").resize.Bicubic(format=YUV444P10, matrix_s="170m", dither_type="error_diffusion").resize.Bicubic(format=YUV444P10, matrix_s="170m", matrix_in_s="709", dither_type="error_diffusion")
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(flt, lvf.aa.upscaled_sraa(flt, rfactor=1.6), mask_32096_32145, first_plane=True), "[32096 32145]")

# more deinterlacing
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(flt, haf.Vinverse(flt), kgf.squaremask(flt, width=325, height=240, offset_x=350, offset_y=146)), "32416")
flt = awf.ReplaceFrames(flt, core.std.MaskedMerge(og, flt, kgf.squaremask(flt, width=170, height=180, offset_x=430, offset_y=170).std.BoxBlur(hradius=4, vradius=4)), "33182")

# residual combing
flt = awf.ReplaceFrames(flt, haf.Vinverse(flt), "386 [34281 34283]")

# blend flickery credits
def gen_shifts(clip, n, shift, forward=True, backward=True):
    shifts = [clip]
    for cur in range(1, n+1):
        if forward:
            shifts.append(clip[1*cur:].resize.Bicubic(src_top=-shift*cur)+clip[0]*cur)
        if backward:
            shifts.append(clip[0]*cur+clip.resize.Bicubic(src_top=shift*cur)[:-1*cur])
    return shifts

flt2 = core.std.MaskedMerge(flt, core.average.Mean(gen_shifts(flt, 1, shift=3.3)), kgf.squaremask(flt, width=720, height=540-4*2, offset_x=0, offset_y=4))
flt2 = core.std.MaskedMerge(flt2, core.average.Mean(gen_shifts(flt, 2, shift=3.3)), kgf.squaremask(flt, width=720, height=540-7*2, offset_x=0, offset_y=7))

flt2 = core.std.MaskedMerge(flt2, flt, kgf.squaremask(flt, width=336, height=274, offset_x=325, offset_y=111).std.BoxBlur(hradius=2, vradius=2))

flt = awf.ReplaceFrames(flt, flt2, "[31924 34026]")

flt.set_output()
