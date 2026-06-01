# This file was automatically created by FeynRules 2.3.35
# Mathematica version: 12.0.0 for Microsoft Windows (64-bit) (April 6, 2019)
# Date: Thu 21 Jan 2021 15:25:41


from object_library import all_vertices, Vertex
import particles as P
import couplings as C
import lorentz as L


V_1 = Vertex(name = 'V_1',
             particles = [ P.H, P.H, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.SSSS1 ],
             couplings = {(0,0):C.GC_20})

V_2 = Vertex(name = 'V_2',
             particles = [ P.H, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.SSS1 ],
             couplings = {(0,0):C.GC_84})

V_3 = Vertex(name = 'V_3',
             particles = [ P.W__minus__, P.W__plus__, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVSS1, L.VVSS2 ],
             couplings = {(0,0):C.GC_12,(0,1):C.GC_25})

V_4 = Vertex(name = 'V_4',
             particles = [ P.W__minus__, P.W__plus__, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVS1, L.VVS2 ],
             couplings = {(0,0):C.GC_79,(0,1):C.GC_86})

V_5 = Vertex(name = 'V_5',
             particles = [ P.a, P.W__minus__, P.W__plus__, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVVSS2, L.VVVSS5, L.VVVSS6 ],
             couplings = {(0,1):C.GC_13,(0,0):C.GC_44,(0,2):C.GC_40})

V_6 = Vertex(name = 'V_6',
             particles = [ P.a, P.W__minus__, P.W__plus__, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVVS2, L.VVVS5, L.VVVS6 ],
             couplings = {(0,1):C.GC_80,(0,0):C.GC_98,(0,2):C.GC_94})

V_7 = Vertex(name = 'V_7',
             particles = [ P.a, P.W__minus__, P.W__plus__ ],
             color = [ '1' ],
             lorentz = [ L.VVV2, L.VVV3, L.VVV5, L.VVV6 ],
             couplings = {(0,2):C.GC_119,(0,0):C.GC_135,(0,3):C.GC_131,(0,1):C.GC_4})

V_8 = Vertex(name = 'V_8',
             particles = [ P.W__minus__, P.W__plus__, P.Z, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVVSS1, L.VVVSS3, L.VVVSS7, L.VVVSS9 ],
             couplings = {(0,0):C.GC_6,(0,2):C.GC_46,(0,3):C.GC_10,(0,1):C.GC_56})

V_9 = Vertex(name = 'V_9',
             particles = [ P.W__minus__, P.W__plus__, P.Z, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVVS1, L.VVVS3, L.VVVS7, L.VVVS9 ],
             couplings = {(0,0):C.GC_73,(0,2):C.GC_100,(0,3):C.GC_77,(0,1):C.GC_108})

V_10 = Vertex(name = 'V_10',
              particles = [ P.W__minus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVV1, L.VVV3, L.VVV4, L.VVV7, L.VVV9 ],
              couplings = {(0,0):C.GC_113,(0,3):C.GC_137,(0,2):C.GC_117,(0,4):C.GC_145,(0,1):C.GC_38})

V_11 = Vertex(name = 'V_11',
              particles = [ P.a, P.a, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVSS3 ],
              couplings = {(0,0):C.GC_72})

V_12 = Vertex(name = 'V_12',
              particles = [ P.a, P.a, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVS3 ],
              couplings = {(0,0):C.GC_163})

V_13 = Vertex(name = 'V_13',
              particles = [ P.a, P.a, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVV9 ],
              couplings = {(0,0):C.GC_176})

V_14 = Vertex(name = 'V_14',
              particles = [ P.a, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVSS10, L.VVVSS2, L.VVVSS4, L.VVVSS6 ],
              couplings = {(0,0):C.GC_67,(0,1):C.GC_70,(0,2):C.GC_62,(0,3):C.GC_71})

V_15 = Vertex(name = 'V_15',
              particles = [ P.a, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVS10, L.VVVS2, L.VVVS4, L.VVVS6 ],
              couplings = {(0,0):C.GC_158,(0,1):C.GC_161,(0,2):C.GC_153,(0,3):C.GC_162})

V_16 = Vertex(name = 'V_16',
              particles = [ P.a, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVV10, L.VVV2, L.VVV5, L.VVV6 ],
              couplings = {(0,0):C.GC_171,(0,1):C.GC_174,(0,2):C.GC_167,(0,3):C.GC_175})

V_17 = Vertex(name = 'V_17',
              particles = [ P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVSS8 ],
              couplings = {(0,0):C.GC_69})

V_18 = Vertex(name = 'V_18',
              particles = [ P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVS8 ],
              couplings = {(0,0):C.GC_160})

V_19 = Vertex(name = 'V_19',
              particles = [ P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVV8 ],
              couplings = {(0,0):C.GC_173})

V_20 = Vertex(name = 'V_20',
              particles = [ P.ghG, P.ghG__tilde__, P.g ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.UUV1 ],
              couplings = {(0,0):C.GC_17})

V_21 = Vertex(name = 'V_21',
              particles = [ P.g, P.g, P.g ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVV3 ],
              couplings = {(0,0):C.GC_17})

V_22 = Vertex(name = 'V_22',
              particles = [ P.g, P.g, P.g, P.g ],
              color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
              lorentz = [ L.VVVV20, L.VVVV21, L.VVVV8 ],
              couplings = {(1,0):C.GC_19,(0,2):C.GC_19,(2,1):C.GC_19})

V_23 = Vertex(name = 'V_23',
              particles = [ P.s__tilde__, P.s, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_180})

V_24 = Vertex(name = 'V_24',
              particles = [ P.b__tilde__, P.b, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_177})

V_25 = Vertex(name = 'V_25',
              particles = [ P.mu__plus__, P.mu__minus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_179})

V_26 = Vertex(name = 'V_26',
              particles = [ P.ta__plus__, P.ta__minus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_182})

V_27 = Vertex(name = 'V_27',
              particles = [ P.c__tilde__, P.c, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_178})

V_28 = Vertex(name = 'V_28',
              particles = [ P.t__tilde__, P.t, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_181})

V_29 = Vertex(name = 'V_29',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS4, L.VVVVSS5, L.VVVVSS6 ],
              couplings = {(0,2):C.GC_15,(0,1):C.GC_45,(0,0):C.GC_42})

V_30 = Vertex(name = 'V_30',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS4, L.VVVVS5, L.VVVVS6 ],
              couplings = {(0,2):C.GC_82,(0,1):C.GC_99,(0,0):C.GC_96})

V_31 = Vertex(name = 'V_31',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVV19, L.VVVV3, L.VVVV4, L.VVVV5 ],
              couplings = {(0,3):C.GC_121,(0,2):C.GC_136,(0,1):C.GC_133,(0,0):C.GC_5})

V_32 = Vertex(name = 'V_32',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS1, L.VVVVSS11, L.VVVVSS12, L.VVVVSS15, L.VVVVSS8, L.VVVVSS9 ],
              couplings = {(0,0):C.GC_30,(0,3):C.GC_47,(0,2):C.GC_11,(0,1):C.GC_57,(0,5):C.GC_7,(0,4):C.GC_28})

V_33 = Vertex(name = 'V_33',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS1, L.VVVVS11, L.VVVVS12, L.VVVVS15, L.VVVVS8, L.VVVVS9 ],
              couplings = {(0,0):C.GC_89,(0,3):C.GC_101,(0,2):C.GC_78,(0,1):C.GC_109,(0,5):C.GC_74,(0,4):C.GC_87})

V_34 = Vertex(name = 'V_34',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV1, L.VVVV10, L.VVVV11, L.VVVV13, L.VVVV14, L.VVVV22, L.VVVV9 ],
              couplings = {(0,0):C.GC_126,(0,3):C.GC_138,(0,2):C.GC_118,(0,4):C.GC_146,(0,6):C.GC_114,(0,1):C.GC_124,(0,5):C.GC_39})

V_35 = Vertex(name = 'V_35',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS10 ],
              couplings = {(0,0):C.GC_31})

V_36 = Vertex(name = 'V_36',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS10 ],
              couplings = {(0,0):C.GC_90})

V_37 = Vertex(name = 'V_37',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVV12, L.VVVV19 ],
              couplings = {(0,0):C.GC_127,(0,1):C.GC_26})

V_38 = Vertex(name = 'V_38',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS13, L.VVVVSS14, L.VVVVSS16, L.VVVVSS17, L.VVVVSS2, L.VVVVSS3, L.VVVVSS7 ],
              couplings = {(0,1):C.GC_14,(0,0):C.GC_32,(0,4):C.GC_59,(0,5):C.GC_41,(0,6):C.GC_53,(0,2):C.GC_45,(0,3):C.GC_55})

V_39 = Vertex(name = 'V_39',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS13, L.VVVVS14, L.VVVVS16, L.VVVVS17, L.VVVVS2, L.VVVVS3, L.VVVVS7 ],
              couplings = {(0,1):C.GC_81,(0,0):C.GC_91,(0,4):C.GC_111,(0,5):C.GC_95,(0,6):C.GC_105,(0,2):C.GC_99,(0,3):C.GC_107})

V_40 = Vertex(name = 'V_40',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV15, L.VVVV16, L.VVVV17, L.VVVV18, L.VVVV19, L.VVVV2, L.VVVV6, L.VVVV7 ],
              couplings = {(0,1):C.GC_120,(0,0):C.GC_128,(0,5):C.GC_148,(0,7):C.GC_132,(0,6):C.GC_142,(0,2):C.GC_136,(0,3):C.GC_144,(0,4):C.GC_27})

V_41 = Vertex(name = 'V_41',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS1, L.VVVVVSS11, L.VVVVVSS15, L.VVVVVSS16, L.VVVVVSS17 ],
              couplings = {(0,0):C.GC_21,(0,3):C.GC_50,(0,1):C.GC_58,(0,4):C.GC_9,(0,2):C.GC_29})

V_42 = Vertex(name = 'V_42',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS1, L.VVVVVS11, L.VVVVVS15, L.VVVVVS16, L.VVVVVS17 ],
              couplings = {(0,0):C.GC_150,(0,3):C.GC_104,(0,1):C.GC_110,(0,4):C.GC_76,(0,2):C.GC_88})

V_43 = Vertex(name = 'V_43',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV1, L.VVVVV11, L.VVVVV15, L.VVVVV16, L.VVVVV17 ],
              couplings = {(0,0):C.GC_164,(0,3):C.GC_141,(0,1):C.GC_147,(0,4):C.GC_116,(0,2):C.GC_125})

V_44 = Vertex(name = 'V_44',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS18 ],
              couplings = {(0,0):C.GC_33})

V_45 = Vertex(name = 'V_45',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS18 ],
              couplings = {(0,0):C.GC_92})

V_46 = Vertex(name = 'V_46',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVV18 ],
              couplings = {(0,0):C.GC_129})

V_47 = Vertex(name = 'V_47',
              particles = [ P.a, P.a, P.a, P.W__minus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS3 ],
              couplings = {(0,0):C.GC_22})

V_48 = Vertex(name = 'V_48',
              particles = [ P.a, P.a, P.a, P.W__minus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS3 ],
              couplings = {(0,0):C.GC_151})

V_49 = Vertex(name = 'V_49',
              particles = [ P.a, P.a, P.a, P.W__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVV3 ],
              couplings = {(0,0):C.GC_165})

V_50 = Vertex(name = 'V_50',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS12, L.VVVVVSS14 ],
              couplings = {(0,1):C.GC_24,(0,0):C.GC_48})

V_51 = Vertex(name = 'V_51',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS12, L.VVVVVS14 ],
              couplings = {(0,1):C.GC_85,(0,0):C.GC_102})

V_52 = Vertex(name = 'V_52',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV12, L.VVVVV14 ],
              couplings = {(0,1):C.GC_123,(0,0):C.GC_139})

V_53 = Vertex(name = 'V_53',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS4, L.VVVVVSS5, L.VVVVVSS6, L.VVVVVSS7, L.VVVVVSS8, L.VVVVVSS9 ],
              couplings = {(0,5):C.GC_16,(0,4):C.GC_34,(0,0):C.GC_60,(0,3):C.GC_63,(0,2):C.GC_43,(0,1):C.GC_54})

V_54 = Vertex(name = 'V_54',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS4, L.VVVVVS5, L.VVVVVS6, L.VVVVVS7, L.VVVVVS8, L.VVVVVS9 ],
              couplings = {(0,5):C.GC_83,(0,4):C.GC_93,(0,0):C.GC_112,(0,3):C.GC_154,(0,2):C.GC_97,(0,1):C.GC_106})

V_55 = Vertex(name = 'V_55',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV4, L.VVVVV5, L.VVVVV6, L.VVVVV7, L.VVVVV8, L.VVVVV9 ],
              couplings = {(0,5):C.GC_122,(0,4):C.GC_130,(0,0):C.GC_149,(0,3):C.GC_168,(0,2):C.GC_134,(0,1):C.GC_143})

V_56 = Vertex(name = 'V_56',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS2 ],
              couplings = {(0,0):C.GC_23})

V_57 = Vertex(name = 'V_57',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS2 ],
              couplings = {(0,0):C.GC_152})

V_58 = Vertex(name = 'V_58',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV2 ],
              couplings = {(0,0):C.GC_166})

V_59 = Vertex(name = 'V_59',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS10, L.VVVVVSS13, L.VVVVVSS2 ],
              couplings = {(0,2):C.GC_8,(0,0):C.GC_49,(0,1):C.GC_64})

V_60 = Vertex(name = 'V_60',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS10, L.VVVVVS13, L.VVVVVS2 ],
              couplings = {(0,2):C.GC_75,(0,0):C.GC_103,(0,1):C.GC_155})

V_61 = Vertex(name = 'V_61',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV10, L.VVVVV13, L.VVVVV2 ],
              couplings = {(0,2):C.GC_115,(0,0):C.GC_140,(0,1):C.GC_169})

V_62 = Vertex(name = 'V_62',
              particles = [ P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVSS2 ],
              couplings = {(0,0):C.GC_66})

V_63 = Vertex(name = 'V_63',
              particles = [ P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVS2 ],
              couplings = {(0,0):C.GC_157})

V_64 = Vertex(name = 'V_64',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS1 ],
              couplings = {(0,0):C.GC_68})

V_65 = Vertex(name = 'V_65',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS1 ],
              couplings = {(0,0):C.GC_159})

V_66 = Vertex(name = 'V_66',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV1 ],
              couplings = {(0,0):C.GC_172})

V_67 = Vertex(name = 'V_67',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS3 ],
              couplings = {(0,0):C.GC_65})

V_68 = Vertex(name = 'V_68',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS3 ],
              couplings = {(0,0):C.GC_156})

V_69 = Vertex(name = 'V_69',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV3 ],
              couplings = {(0,0):C.GC_170})

V_70 = Vertex(name = 'V_70',
              particles = [ P.e__plus__, P.e__minus__, P.a ],
              color = [ '1' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_3})

V_71 = Vertex(name = 'V_71',
              particles = [ P.mu__plus__, P.mu__minus__, P.a ],
              color = [ '1' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_3})

V_72 = Vertex(name = 'V_72',
              particles = [ P.ta__plus__, P.ta__minus__, P.a ],
              color = [ '1' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_3})

V_73 = Vertex(name = 'V_73',
              particles = [ P.u__tilde__, P.u, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_74 = Vertex(name = 'V_74',
              particles = [ P.c__tilde__, P.c, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_75 = Vertex(name = 'V_75',
              particles = [ P.t__tilde__, P.t, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_76 = Vertex(name = 'V_76',
              particles = [ P.d__tilde__, P.d, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_1})

V_77 = Vertex(name = 'V_77',
              particles = [ P.s__tilde__, P.s, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_1})

V_78 = Vertex(name = 'V_78',
              particles = [ P.b__tilde__, P.b, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_1})

V_79 = Vertex(name = 'V_79',
              particles = [ P.u__tilde__, P.u, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_80 = Vertex(name = 'V_80',
              particles = [ P.c__tilde__, P.c, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_81 = Vertex(name = 'V_81',
              particles = [ P.t__tilde__, P.t, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_82 = Vertex(name = 'V_82',
              particles = [ P.d__tilde__, P.d, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_83 = Vertex(name = 'V_83',
              particles = [ P.s__tilde__, P.s, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_84 = Vertex(name = 'V_84',
              particles = [ P.b__tilde__, P.b, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_85 = Vertex(name = 'V_85',
              particles = [ P.d__tilde__, P.u, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_86 = Vertex(name = 'V_86',
              particles = [ P.s__tilde__, P.c, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_87 = Vertex(name = 'V_87',
              particles = [ P.b__tilde__, P.t, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_88 = Vertex(name = 'V_88',
              particles = [ P.u__tilde__, P.d, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_89 = Vertex(name = 'V_89',
              particles = [ P.c__tilde__, P.s, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_90 = Vertex(name = 'V_90',
              particles = [ P.t__tilde__, P.b, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_91 = Vertex(name = 'V_91',
              particles = [ P.e__plus__, P.ve, P.W__minus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_92 = Vertex(name = 'V_92',
              particles = [ P.mu__plus__, P.vm, P.W__minus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_93 = Vertex(name = 'V_93',
              particles = [ P.ta__plus__, P.vt, P.W__minus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_94 = Vertex(name = 'V_94',
              particles = [ P.ve__tilde__, P.e__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_95 = Vertex(name = 'V_95',
              particles = [ P.vm__tilde__, P.mu__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_96 = Vertex(name = 'V_96',
              particles = [ P.vt__tilde__, P.ta__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_35})

V_97 = Vertex(name = 'V_97',
              particles = [ P.u__tilde__, P.u, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2, L.FFV5 ],
              couplings = {(0,0):C.GC_37,(0,1):C.GC_51})

V_98 = Vertex(name = 'V_98',
              particles = [ P.c__tilde__, P.c, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2, L.FFV5 ],
              couplings = {(0,0):C.GC_37,(0,1):C.GC_51})

V_99 = Vertex(name = 'V_99',
              particles = [ P.t__tilde__, P.t, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2, L.FFV5 ],
              couplings = {(0,0):C.GC_37,(0,1):C.GC_51})

V_100 = Vertex(name = 'V_100',
               particles = [ P.d__tilde__, P.d, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_36,(0,1):C.GC_51})

V_101 = Vertex(name = 'V_101',
               particles = [ P.s__tilde__, P.s, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_36,(0,1):C.GC_51})

V_102 = Vertex(name = 'V_102',
               particles = [ P.b__tilde__, P.b, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_36,(0,1):C.GC_51})

V_103 = Vertex(name = 'V_103',
               particles = [ P.ve__tilde__, P.ve, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_61})

V_104 = Vertex(name = 'V_104',
               particles = [ P.vm__tilde__, P.vm, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_61})

V_105 = Vertex(name = 'V_105',
               particles = [ P.vt__tilde__, P.vt, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_61})

V_106 = Vertex(name = 'V_106',
               particles = [ P.e__plus__, P.e__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_36,(0,1):C.GC_52})

V_107 = Vertex(name = 'V_107',
               particles = [ P.mu__plus__, P.mu__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_36,(0,1):C.GC_52})

V_108 = Vertex(name = 'V_108',
               particles = [ P.ta__plus__, P.ta__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_36,(0,1):C.GC_52})

