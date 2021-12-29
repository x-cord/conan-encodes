from vapoursynth import core

tv1 = core.lsmas.LWLibavSource("303/325-326.mkv")
tv1_p = tv1[8775:8775+2603]
tv1 = tv1[11379:]
tv1 = tv1[:18489] + tv1[18488:]
tv2 = core.lsmas.LWLibavSource("303/324_325.mkv")
tv2 = tv2[55155:]
tv3 = core.lsmas.LWLibavSource("303/C325JP.mkv")
tv3_p = tv3[315:315+2603]
tv3 = tv3[2919:]
tv3 = tv3[:3077] + tv3[3076:]
tv3 = tv3[:12972] + tv3[12972]*11 + tv3[12972:]
tv3 = tv3[:15206] + tv3[15206]*3 + tv3[15206:]

tv4 = core.ffms2.Source("303/324_325_R.mkv")
tv4 = tv4[40417:]

tv1 = tv1[:32260]
tv2 = tv2[:32260]
tv3 = tv3[:32260]
tv4 = tv4[:32260]

# filtering here

tv1.set_output(0)
tv2.set_output(1)
tv3.set_output(2)
tv4.set_output(3)
