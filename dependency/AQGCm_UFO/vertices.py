# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 13.1.0 for Microsoft Windows (64-bit) (June 16, 2022)
# Date: Mon 15 May 2023 18:54:25


from object_library import all_vertices, Vertex
import particles as P
import couplings as C
import lorentz as L


V_1 = Vertex(name = 'V_1',
             particles = [ P.H, P.H, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.SSSS1 ],
             couplings = {(0,0):C.GC_26})

V_2 = Vertex(name = 'V_2',
             particles = [ P.H, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.SSS1 ],
             couplings = {(0,0):C.GC_138})

V_3 = Vertex(name = 'V_3',
             particles = [ P.a, P.a, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVSS2, L.VVSS3 ],
             couplings = {(0,0):C.GC_118,(0,1):C.GC_110})

V_4 = Vertex(name = 'V_4',
             particles = [ P.W__minus__, P.W__plus__, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVSS1, L.VVSS2, L.VVSS3 ],
             couplings = {(0,0):C.GC_47,(0,1):C.GC_18,(0,2):C.GC_6})

V_5 = Vertex(name = 'V_5',
             particles = [ P.a, P.Z, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVSS2, L.VVSS3 ],
             couplings = {(0,0):C.GC_117,(0,1):C.GC_116})

V_6 = Vertex(name = 'V_6',
             particles = [ P.Z, P.Z, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVSS1, L.VVSS2, L.VVSS3 ],
             couplings = {(0,0):C.GC_109,(0,1):C.GC_115,(0,2):C.GC_114})

V_7 = Vertex(name = 'V_7',
             particles = [ P.ghG, P.ghG__tilde__, P.g ],
             color = [ 'f(1,2,3)' ],
             lorentz = [ L.UUV1 ],
             couplings = {(0,0):C.GC_23})

V_8 = Vertex(name = 'V_8',
             particles = [ P.g, P.g, P.g ],
             color = [ 'f(1,2,3)' ],
             lorentz = [ L.VVV1 ],
             couplings = {(0,0):C.GC_23})

V_9 = Vertex(name = 'V_9',
             particles = [ P.g, P.g, P.g, P.g ],
             color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
             lorentz = [ L.VVVV2, L.VVVV8, L.VVVV9 ],
             couplings = {(1,1):C.GC_25,(0,0):C.GC_25,(2,2):C.GC_25})

V_10 = Vertex(name = 'V_10',
              particles = [ P.s__tilde__, P.s, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_304})

V_11 = Vertex(name = 'V_11',
              particles = [ P.b__tilde__, P.b, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_301})

V_12 = Vertex(name = 'V_12',
              particles = [ P.mu__plus__, P.mu__minus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_303})

V_13 = Vertex(name = 'V_13',
              particles = [ P.ta__plus__, P.ta__minus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_306})

V_14 = Vertex(name = 'V_14',
              particles = [ P.c__tilde__, P.c, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_302})

V_15 = Vertex(name = 'V_15',
              particles = [ P.t__tilde__, P.t, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_305})

V_16 = Vertex(name = 'V_16',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVSS1, L.VVVSS3, L.VVVSS5, L.VVVSS6, L.VVVSS8 ],
              couplings = {(0,3):C.GC_19,(0,1):C.GC_85,(0,0):C.GC_81,(0,2):C.GC_9,(0,4):C.GC_7})

V_17 = Vertex(name = 'V_17',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVS1, L.VVVS4, L.VVVS5 ],
              couplings = {(0,1):C.GC_134,(0,2):C.GC_174,(0,0):C.GC_170})

V_18 = Vertex(name = 'V_18',
              particles = [ P.a, P.W__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVV1 ],
              couplings = {(0,0):C.GC_4})

V_19 = Vertex(name = 'V_19',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVSS2, L.VVVSS4, L.VVVSS5, L.VVVSS7, L.VVVSS8, L.VVVSS9 ],
              couplings = {(0,3):C.GC_89,(0,0):C.GC_100,(0,1):C.GC_15,(0,5):C.GC_13,(0,2):C.GC_77,(0,4):C.GC_75})

V_20 = Vertex(name = 'V_20',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVS2, L.VVVS3, L.VVVS6, L.VVVS7 ],
              couplings = {(0,2):C.GC_178,(0,1):C.GC_187,(0,3):C.GC_132,(0,0):C.GC_130})

V_21 = Vertex(name = 'V_21',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS2, L.VVVVSS22, L.VVVVSS24, L.VVVVSS31, L.VVVVSS5, L.VVVVSS7, L.VVVVSS8 ],
              couplings = {(0,4):C.GC_10,(0,1):C.GC_20,(0,0):C.GC_59,(0,2):C.GC_87,(0,5):C.GC_82,(0,3):C.GC_8,(0,6):C.GC_58})

V_22 = Vertex(name = 'V_22',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS2, L.VVVVS20, L.VVVVS22, L.VVVVS6, L.VVVVS7 ],
              couplings = {(0,0):C.GC_248,(0,1):C.GC_135,(0,2):C.GC_176,(0,3):C.GC_171,(0,4):C.GC_247})

V_23 = Vertex(name = 'V_23',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVV11, L.VVVV3, L.VVVV7 ],
              couplings = {(0,1):C.GC_284,(0,2):C.GC_5,(0,0):C.GC_283})

V_24 = Vertex(name = 'V_24',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS16, L.VVVVSS29, L.VVVVSS34 ],
              couplings = {(0,0):C.GC_54,(0,1):C.GC_64,(0,2):C.GC_50})

V_25 = Vertex(name = 'V_25',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS13, L.VVVVS27, L.VVVVS3 ],
              couplings = {(0,0):C.GC_156,(0,1):C.GC_164,(0,2):C.GC_152})

V_26 = Vertex(name = 'V_26',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVV19, L.VVVV20, L.VVVV4, L.VVVV7 ],
              couplings = {(0,1):C.GC_213,(0,0):C.GC_221,(0,2):C.GC_209,(0,3):C.GC_48})

V_27 = Vertex(name = 'V_27',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS1, L.VVVVSS10, L.VVVVSS11, L.VVVVSS12, L.VVVVSS13, L.VVVVSS21, L.VVVVSS23, L.VVVVSS28, L.VVVVSS30, L.VVVVSS33 ],
              couplings = {(0,8):C.GC_16,(0,5):C.GC_62,(0,7):C.GC_90,(0,6):C.GC_101,(0,4):C.GC_78,(0,3):C.GC_80,(0,1):C.GC_60,(0,2):C.GC_14,(0,9):C.GC_76,(0,0):C.GC_79})

V_28 = Vertex(name = 'V_28',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS1, L.VVVVS10, L.VVVVS11, L.VVVVS19, L.VVVVS21, L.VVVVS26, L.VVVVS28, L.VVVVS9 ],
              couplings = {(0,6):C.GC_133,(0,3):C.GC_162,(0,5):C.GC_179,(0,4):C.GC_188,(0,2):C.GC_254,(0,7):C.GC_160,(0,1):C.GC_131,(0,0):C.GC_253})

V_29 = Vertex(name = 'V_29',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV1, L.VVVV10, L.VVVV12, L.VVVV13, L.VVVV14, L.VVVV15, L.VVVV16, L.VVVV17, L.VVVV18 ],
              couplings = {(0,8):C.GC_194,(0,7):C.GC_219,(0,6):C.GC_231,(0,4):C.GC_239,(0,5):C.GC_282,(0,2):C.GC_193,(0,3):C.GC_217,(0,0):C.GC_281,(0,1):C.GC_74})

V_30 = Vertex(name = 'V_30',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS15, L.VVVVSS18, L.VVVVSS19, L.VVVVSS2, L.VVVVSS25, L.VVVVSS26, L.VVVVSS27, L.VVVVSS3, L.VVVVSS32, L.VVVVSS4, L.VVVVSS6, L.VVVVSS8 ],
              couplings = {(0,3):C.GC_119,(0,4):C.GC_21,(0,10):C.GC_55,(0,6):C.GC_65,(0,5):C.GC_86,(0,0):C.GC_98,(0,1):C.GC_11,(0,8):C.GC_51,(0,2):C.GC_83,(0,7):C.GC_96,(0,9):C.GC_12,(0,11):C.GC_111})

V_31 = Vertex(name = 'V_31',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS13, L.VVVVS15, L.VVVVS16, L.VVVVS17, L.VVVVS2, L.VVVVS23, L.VVVVS24, L.VVVVS25, L.VVVVS3, L.VVVVS4, L.VVVVS5, L.VVVVS7 ],
              couplings = {(0,4):C.GC_263,(0,5):C.GC_136,(0,10):C.GC_157,(0,7):C.GC_165,(0,6):C.GC_175,(0,0):C.GC_185,(0,1):C.GC_128,(0,3):C.GC_153,(0,2):C.GC_172,(0,8):C.GC_183,(0,9):C.GC_129,(0,11):C.GC_260})

V_32 = Vertex(name = 'V_32',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV11, L.VVVV20, L.VVVV21, L.VVVV22, L.VVVV23, L.VVVV25, L.VVVV26, L.VVVV27, L.VVVV3, L.VVVV4, L.VVVV5, L.VVVV6, L.VVVV7 ],
              couplings = {(0,8):C.GC_292,(0,4):C.GC_195,(0,11):C.GC_214,(0,2):C.GC_222,(0,3):C.GC_229,(0,1):C.GC_237,(0,5):C.GC_191,(0,7):C.GC_210,(0,6):C.GC_227,(0,9):C.GC_235,(0,10):C.GC_192,(0,12):C.GC_49,(0,0):C.GC_289})

V_33 = Vertex(name = 'V_33',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS1, L.VVVVVSS29, L.VVVVVSS3, L.VVVVVSS30 ],
              couplings = {(0,3):C.GC_56,(0,1):C.GC_66,(0,0):C.GC_28,(0,2):C.GC_52})

V_34 = Vertex(name = 'V_34',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS1, L.VVVVVS29, L.VVVVVS3, L.VVVVVS30 ],
              couplings = {(0,3):C.GC_158,(0,1):C.GC_166,(0,0):C.GC_244,(0,2):C.GC_154})

V_35 = Vertex(name = 'V_35',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVV1, L.VVVVV3, L.VVVVV30, L.VVVVV31 ],
              couplings = {(0,3):C.GC_215,(0,2):C.GC_223,(0,0):C.GC_274,(0,1):C.GC_211})

V_36 = Vertex(name = 'V_36',
              particles = [ P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS1, L.VVVVVVSS6, L.VVVVVVSS7 ],
              couplings = {(0,2):C.GC_57,(0,1):C.GC_68,(0,0):C.GC_53})

V_37 = Vertex(name = 'V_37',
              particles = [ P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS1, L.VVVVVVS6, L.VVVVVVS7 ],
              couplings = {(0,2):C.GC_159,(0,1):C.GC_168,(0,0):C.GC_155})

V_38 = Vertex(name = 'V_38',
              particles = [ P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV1, L.VVVVVV6, L.VVVVVV7 ],
              couplings = {(0,2):C.GC_216,(0,1):C.GC_225,(0,0):C.GC_212})

V_39 = Vertex(name = 'V_39',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS17, L.VVVVVSS18, L.VVVVVSS19, L.VVVVVSS20, L.VVVVVSS28 ],
              couplings = {(0,3):C.GC_38,(0,1):C.GC_40,(0,4):C.GC_44,(0,0):C.GC_91,(0,2):C.GC_32})

V_40 = Vertex(name = 'V_40',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS17, L.VVVVVS18, L.VVVVVS19, L.VVVVVS20, L.VVVVVS28 ],
              couplings = {(0,3):C.GC_142,(0,1):C.GC_144,(0,4):C.GC_148,(0,0):C.GC_180,(0,2):C.GC_250})

V_41 = Vertex(name = 'V_41',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV18, L.VVVVV19, L.VVVVV20, L.VVVVV21, L.VVVVV29 ],
              couplings = {(0,3):C.GC_200,(0,1):C.GC_202,(0,4):C.GC_206,(0,0):C.GC_232,(0,2):C.GC_278})

V_42 = Vertex(name = 'V_42',
              particles = [ P.W__minus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVS1 ],
              couplings = {(0,0):C.GC_151})

V_43 = Vertex(name = 'V_43',
              particles = [ P.W__minus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVV1 ],
              couplings = {(0,0):C.GC_73})

V_44 = Vertex(name = 'V_44',
              particles = [ P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS12 ],
              couplings = {(0,0):C.GC_27})

V_45 = Vertex(name = 'V_45',
              particles = [ P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS12 ],
              couplings = {(0,0):C.GC_243})

V_46 = Vertex(name = 'V_46',
              particles = [ P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV12 ],
              couplings = {(0,0):C.GC_273})

V_47 = Vertex(name = 'V_47',
              particles = [ P.a, P.a, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS2, L.VVVVSS8 ],
              couplings = {(0,0):C.GC_127,(0,1):C.GC_122})

V_48 = Vertex(name = 'V_48',
              particles = [ P.a, P.a, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS2, L.VVVVS7 ],
              couplings = {(0,0):C.GC_271,(0,1):C.GC_266})

V_49 = Vertex(name = 'V_49',
              particles = [ P.a, P.a, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV11, L.VVVV3 ],
              couplings = {(0,1):C.GC_300,(0,0):C.GC_295})

V_50 = Vertex(name = 'V_50',
              particles = [ P.a, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS14, L.VVVVSS9 ],
              couplings = {(0,0):C.GC_126,(0,1):C.GC_125})

V_51 = Vertex(name = 'V_51',
              particles = [ P.a, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS12, L.VVVVS8 ],
              couplings = {(0,0):C.GC_270,(0,1):C.GC_269})

V_52 = Vertex(name = 'V_52',
              particles = [ P.a, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV12, L.VVVV18 ],
              couplings = {(0,1):C.GC_299,(0,0):C.GC_298})

V_53 = Vertex(name = 'V_53',
              particles = [ P.Z, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS17, L.VVVVSS20 ],
              couplings = {(0,0):C.GC_124,(0,1):C.GC_123})

V_54 = Vertex(name = 'V_54',
              particles = [ P.Z, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS14, L.VVVVS18 ],
              couplings = {(0,0):C.GC_268,(0,1):C.GC_267})

V_55 = Vertex(name = 'V_55',
              particles = [ P.Z, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV24, L.VVVV28 ],
              couplings = {(0,0):C.GC_297,(0,1):C.GC_296})

V_56 = Vertex(name = 'V_56',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS10, L.VVVVVSS11, L.VVVVVSS15, L.VVVVVSS2, L.VVVVVSS4, L.VVVVVSS5, L.VVVVVSS6, L.VVVVVSS7, L.VVVVVSS8, L.VVVVVSS9 ],
              couplings = {(0,3):C.GC_120,(0,1):C.GC_22,(0,0):C.GC_67,(0,6):C.GC_42,(0,4):C.GC_43,(0,5):C.GC_84,(0,8):C.GC_88,(0,9):C.GC_99,(0,7):C.GC_97,(0,2):C.GC_112})

V_57 = Vertex(name = 'V_57',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS10, L.VVVVVS11, L.VVVVVS15, L.VVVVVS2, L.VVVVVS4, L.VVVVVS5, L.VVVVVS6, L.VVVVVS7, L.VVVVVS8, L.VVVVVS9 ],
              couplings = {(0,3):C.GC_264,(0,1):C.GC_137,(0,0):C.GC_167,(0,6):C.GC_146,(0,4):C.GC_147,(0,5):C.GC_173,(0,8):C.GC_177,(0,9):C.GC_186,(0,7):C.GC_184,(0,2):C.GC_261})

V_58 = Vertex(name = 'V_58',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV10, L.VVVVV11, L.VVVVV16, L.VVVVV2, L.VVVVV4, L.VVVVV5, L.VVVVV6, L.VVVVV7, L.VVVVV8, L.VVVVV9 ],
              couplings = {(0,3):C.GC_293,(0,9):C.GC_196,(0,8):C.GC_224,(0,6):C.GC_204,(0,4):C.GC_205,(0,5):C.GC_228,(0,0):C.GC_230,(0,1):C.GC_238,(0,7):C.GC_236,(0,2):C.GC_290})

V_59 = Vertex(name = 'V_59',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS2, L.VVVVVVSS5 ],
              couplings = {(0,0):C.GC_121,(0,1):C.GC_113})

V_60 = Vertex(name = 'V_60',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS2, L.VVVVVVS5 ],
              couplings = {(0,0):C.GC_265,(0,1):C.GC_262})

V_61 = Vertex(name = 'V_61',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV2, L.VVVVVV5 ],
              couplings = {(0,0):C.GC_294,(0,1):C.GC_291})

V_62 = Vertex(name = 'V_62',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS14, L.VVVVVSS16, L.VVVVVSS21, L.VVVVVSS22, L.VVVVVSS23, L.VVVVVSS24, L.VVVVVSS25, L.VVVVVSS26, L.VVVVVSS27 ],
              couplings = {(0,5):C.GC_17,(0,3):C.GC_107,(0,6):C.GC_45,(0,7):C.GC_61,(0,4):C.GC_63,(0,8):C.GC_92,(0,2):C.GC_103,(0,1):C.GC_105,(0,0):C.GC_102})

V_63 = Vertex(name = 'V_63',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS14, L.VVVVVS16, L.VVVVVS21, L.VVVVVS22, L.VVVVVS23, L.VVVVVS24, L.VVVVVS25, L.VVVVVS26, L.VVVVVS27 ],
              couplings = {(0,5):C.GC_242,(0,3):C.GC_257,(0,6):C.GC_149,(0,7):C.GC_161,(0,4):C.GC_163,(0,8):C.GC_181,(0,2):C.GC_190,(0,1):C.GC_255,(0,0):C.GC_189})

V_64 = Vertex(name = 'V_64',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV15, L.VVVVV17, L.VVVVV22, L.VVVVV23, L.VVVVV24, L.VVVVV25, L.VVVVV26, L.VVVVV27, L.VVVVV28 ],
              couplings = {(0,5):C.GC_272,(0,3):C.GC_287,(0,6):C.GC_207,(0,7):C.GC_218,(0,4):C.GC_220,(0,8):C.GC_233,(0,2):C.GC_241,(0,1):C.GC_285,(0,0):C.GC_240})

V_65 = Vertex(name = 'V_65',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS10, L.VVVVVVSS16, L.VVVVVVSS2, L.VVVVVVSS5, L.VVVVVVSS8, L.VVVVVVSS9 ],
              couplings = {(0,2):C.GC_30,(0,5):C.GC_36,(0,4):C.GC_37,(0,0):C.GC_69,(0,1):C.GC_35,(0,3):C.GC_29})

V_66 = Vertex(name = 'V_66',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS10, L.VVVVVVS16, L.VVVVVVS2, L.VVVVVVS5, L.VVVVVVS8, L.VVVVVVS9 ],
              couplings = {(0,2):C.GC_246,(0,5):C.GC_140,(0,4):C.GC_141,(0,0):C.GC_169,(0,1):C.GC_139,(0,3):C.GC_245})

V_67 = Vertex(name = 'V_67',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV10, L.VVVVVV16, L.VVVVVV2, L.VVVVVV5, L.VVVVVV8, L.VVVVVV9 ],
              couplings = {(0,2):C.GC_276,(0,5):C.GC_198,(0,4):C.GC_199,(0,0):C.GC_226,(0,1):C.GC_197,(0,3):C.GC_275})

V_68 = Vertex(name = 'V_68',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS12, L.VVVVVSS13, L.VVVVVSS31 ],
              couplings = {(0,1):C.GC_33,(0,2):C.GC_106,(0,0):C.GC_31})

V_69 = Vertex(name = 'V_69',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS12, L.VVVVVS13, L.VVVVVS31 ],
              couplings = {(0,1):C.GC_251,(0,2):C.GC_256,(0,0):C.GC_249})

V_70 = Vertex(name = 'V_70',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS11, L.VVVVVVSS14, L.VVVVVVSS15, L.VVVVVVSS3 ],
              couplings = {(0,2):C.GC_39,(0,3):C.GC_41,(0,0):C.GC_46,(0,1):C.GC_93})

V_71 = Vertex(name = 'V_71',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS11, L.VVVVVVS14, L.VVVVVVS15, L.VVVVVVS3 ],
              couplings = {(0,2):C.GC_143,(0,3):C.GC_145,(0,0):C.GC_150,(0,1):C.GC_182})

V_72 = Vertex(name = 'V_72',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV11, L.VVVVVV14, L.VVVVVV15, L.VVVVVV3 ],
              couplings = {(0,2):C.GC_201,(0,3):C.GC_203,(0,0):C.GC_208,(0,1):C.GC_234})

V_73 = Vertex(name = 'V_73',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV12, L.VVVVV13, L.VVVVV14 ],
              couplings = {(0,2):C.GC_279,(0,0):C.GC_286,(0,1):C.GC_277})

V_74 = Vertex(name = 'V_74',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS13 ],
              couplings = {(0,0):C.GC_108})

V_75 = Vertex(name = 'V_75',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS13 ],
              couplings = {(0,0):C.GC_258})

V_76 = Vertex(name = 'V_76',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV13 ],
              couplings = {(0,0):C.GC_288})

V_77 = Vertex(name = 'V_77',
              particles = [ P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVS1 ],
              couplings = {(0,0):C.GC_259})

V_78 = Vertex(name = 'V_78',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS4 ],
              couplings = {(0,0):C.GC_34})

V_79 = Vertex(name = 'V_79',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS4 ],
              couplings = {(0,0):C.GC_252})

V_80 = Vertex(name = 'V_80',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV4 ],
              couplings = {(0,0):C.GC_280})

V_81 = Vertex(name = 'V_81',
              particles = [ P.e__plus__, P.e__minus__, P.a ],
              color = [ '1' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_3})

V_82 = Vertex(name = 'V_82',
              particles = [ P.mu__plus__, P.mu__minus__, P.a ],
              color = [ '1' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_3})

V_83 = Vertex(name = 'V_83',
              particles = [ P.ta__plus__, P.ta__minus__, P.a ],
              color = [ '1' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_3})

V_84 = Vertex(name = 'V_84',
              particles = [ P.u__tilde__, P.u, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_85 = Vertex(name = 'V_85',
              particles = [ P.c__tilde__, P.c, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_86 = Vertex(name = 'V_86',
              particles = [ P.t__tilde__, P.t, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_87 = Vertex(name = 'V_87',
              particles = [ P.d__tilde__, P.d, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_1})

V_88 = Vertex(name = 'V_88',
              particles = [ P.s__tilde__, P.s, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_1})

V_89 = Vertex(name = 'V_89',
              particles = [ P.b__tilde__, P.b, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_1})

V_90 = Vertex(name = 'V_90',
              particles = [ P.u__tilde__, P.u, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_24})

V_91 = Vertex(name = 'V_91',
              particles = [ P.c__tilde__, P.c, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_24})

V_92 = Vertex(name = 'V_92',
              particles = [ P.t__tilde__, P.t, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_24})

V_93 = Vertex(name = 'V_93',
              particles = [ P.d__tilde__, P.d, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_24})

V_94 = Vertex(name = 'V_94',
              particles = [ P.s__tilde__, P.s, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_24})

V_95 = Vertex(name = 'V_95',
              particles = [ P.b__tilde__, P.b, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_24})

V_96 = Vertex(name = 'V_96',
              particles = [ P.d__tilde__, P.u, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_70})

V_97 = Vertex(name = 'V_97',
              particles = [ P.s__tilde__, P.c, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_70})

V_98 = Vertex(name = 'V_98',
              particles = [ P.b__tilde__, P.t, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_70})

V_99 = Vertex(name = 'V_99',
              particles = [ P.u__tilde__, P.d, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_70})

V_100 = Vertex(name = 'V_100',
               particles = [ P.c__tilde__, P.s, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_70})

V_101 = Vertex(name = 'V_101',
               particles = [ P.t__tilde__, P.b, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_70})

V_102 = Vertex(name = 'V_102',
               particles = [ P.e__plus__, P.ve, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_70})

V_103 = Vertex(name = 'V_103',
               particles = [ P.mu__plus__, P.vm, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_70})

V_104 = Vertex(name = 'V_104',
               particles = [ P.ta__plus__, P.vt, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_70})

V_105 = Vertex(name = 'V_105',
               particles = [ P.ve__tilde__, P.e__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_70})

V_106 = Vertex(name = 'V_106',
               particles = [ P.vm__tilde__, P.mu__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_70})

V_107 = Vertex(name = 'V_107',
               particles = [ P.vt__tilde__, P.ta__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_70})

V_108 = Vertex(name = 'V_108',
               particles = [ P.u__tilde__, P.u, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV5 ],
               couplings = {(0,0):C.GC_72,(0,1):C.GC_94})

V_109 = Vertex(name = 'V_109',
               particles = [ P.c__tilde__, P.c, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV5 ],
               couplings = {(0,0):C.GC_72,(0,1):C.GC_94})

V_110 = Vertex(name = 'V_110',
               particles = [ P.t__tilde__, P.t, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV5 ],
               couplings = {(0,0):C.GC_72,(0,1):C.GC_94})

V_111 = Vertex(name = 'V_111',
               particles = [ P.d__tilde__, P.d, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_71,(0,1):C.GC_94})

V_112 = Vertex(name = 'V_112',
               particles = [ P.s__tilde__, P.s, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_71,(0,1):C.GC_94})

V_113 = Vertex(name = 'V_113',
               particles = [ P.b__tilde__, P.b, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_71,(0,1):C.GC_94})

V_114 = Vertex(name = 'V_114',
               particles = [ P.ve__tilde__, P.ve, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_115 = Vertex(name = 'V_115',
               particles = [ P.vm__tilde__, P.vm, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_116 = Vertex(name = 'V_116',
               particles = [ P.vt__tilde__, P.vt, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_117 = Vertex(name = 'V_117',
               particles = [ P.e__plus__, P.e__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_71,(0,1):C.GC_95})

V_118 = Vertex(name = 'V_118',
               particles = [ P.mu__plus__, P.mu__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_71,(0,1):C.GC_95})

V_119 = Vertex(name = 'V_119',
               particles = [ P.ta__plus__, P.ta__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_71,(0,1):C.GC_95})

