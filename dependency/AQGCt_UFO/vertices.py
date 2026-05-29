# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 13.3.1 for Microsoft Windows (64-bit) (July 24, 2023)
# Date: Fri 29 May 2026 21:26:15


from object_library import all_vertices, Vertex
import particles as P
import couplings as C
import lorentz as L


V_1 = Vertex(name = 'V_1',
             particles = [ P.H, P.H, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.SSSS1 ],
             couplings = {(0,0):C.GC_44})

V_2 = Vertex(name = 'V_2',
             particles = [ P.H, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.SSS1 ],
             couplings = {(0,0):C.GC_203})

V_3 = Vertex(name = 'V_3',
             particles = [ P.a, P.a, P.a, P.a ],
             color = [ '1' ],
             lorentz = [ L.VVVV19, L.VVVV22 ],
             couplings = {(0,1):C.GC_192,(0,0):C.GC_193})

V_4 = Vertex(name = 'V_4',
             particles = [ P.a, P.a, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVSS2 ],
             couplings = {(0,0):C.GC_155})

V_5 = Vertex(name = 'V_5',
             particles = [ P.a, P.a, P.W__minus__, P.W__plus__ ],
             color = [ '1' ],
             lorentz = [ L.VVVV18, L.VVVV20, L.VVVV3, L.VVVV4, L.VVVV5 ],
             couplings = {(0,3):C.GC_179,(0,0):C.GC_158,(0,1):C.GC_176,(0,2):C.GC_226,(0,4):C.GC_5})

V_6 = Vertex(name = 'V_6',
             particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
             color = [ '1' ],
             lorentz = [ L.VVVV12, L.VVVV17, L.VVVV23, L.VVVV4, L.VVVV5 ],
             couplings = {(0,3):C.GC_13,(0,2):C.GC_20,(0,1):C.GC_27,(0,0):C.GC_235,(0,4):C.GC_73})

V_7 = Vertex(name = 'V_7',
             particles = [ P.W__minus__, P.W__plus__, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.VVSS1, L.VVSS2 ],
             couplings = {(0,0):C.GC_72,(0,1):C.GC_6})

V_8 = Vertex(name = 'V_8',
             particles = [ P.a, P.a, P.a, P.Z ],
             color = [ '1' ],
             lorentz = [ L.VVVV19, L.VVVV22 ],
             couplings = {(0,1):C.GC_188,(0,0):C.GC_187})

V_9 = Vertex(name = 'V_9',
             particles = [ P.a, P.W__minus__, P.W__plus__, P.Z ],
             color = [ '1' ],
             lorentz = [ L.VVVV1, L.VVVV10, L.VVVV16, L.VVVV21, L.VVVV8, L.VVVV9 ],
             couplings = {(0,0):C.GC_169,(0,2):C.GC_147,(0,3):C.GC_171,(0,1):C.GC_241,(0,5):C.GC_245,(0,4):C.GC_108})

V_10 = Vertex(name = 'V_10',
              particles = [ P.a, P.a, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV19, L.VVVV20, L.VVVV22, L.VVVV23, L.VVVV3, L.VVVV4 ],
              couplings = {(0,5):C.GC_195,(0,2):C.GC_184,(0,3):C.GC_163,(0,0):C.GC_185,(0,1):C.GC_194,(0,4):C.GC_263})

V_11 = Vertex(name = 'V_11',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV13, L.VVVV14, L.VVVV18, L.VVVV20, L.VVVV3, L.VVVV4, L.VVVV5 ],
              couplings = {(0,5):C.GC_183,(0,2):C.GC_28,(0,3):C.GC_182,(0,1):C.GC_227,(0,0):C.GC_236,(0,4):C.GC_247,(0,6):C.GC_74})

V_12 = Vertex(name = 'V_12',
              particles = [ P.a, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVSS2 ],
              couplings = {(0,0):C.GC_139})

V_13 = Vertex(name = 'V_13',
              particles = [ P.a, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV11, L.VVVV19, L.VVVV22 ],
              couplings = {(0,2):C.GC_189,(0,1):C.GC_190,(0,0):C.GC_262})

V_14 = Vertex(name = 'V_14',
              particles = [ P.Z, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVV15, L.VVVV19, L.VVVV22 ],
              couplings = {(0,2):C.GC_196,(0,1):C.GC_197,(0,0):C.GC_260})

V_15 = Vertex(name = 'V_15',
              particles = [ P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVSS1, L.VVSS2 ],
              couplings = {(0,0):C.GC_173,(0,1):C.GC_7})

V_16 = Vertex(name = 'V_16',
              particles = [ P.ghG, P.ghG__tilde__, P.g ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.UUV1 ],
              couplings = {(0,0):C.GC_41})

V_17 = Vertex(name = 'V_17',
              particles = [ P.g, P.g, P.g ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVV1 ],
              couplings = {(0,0):C.GC_41})

V_18 = Vertex(name = 'V_18',
              particles = [ P.g, P.g, P.g, P.g ],
              color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
              lorentz = [ L.VVVV2, L.VVVV6, L.VVVV7 ],
              couplings = {(1,1):C.GC_43,(0,0):C.GC_43,(2,2):C.GC_43})

V_19 = Vertex(name = 'V_19',
              particles = [ P.s__tilde__, P.s, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_267})

V_20 = Vertex(name = 'V_20',
              particles = [ P.b__tilde__, P.b, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_264})

V_21 = Vertex(name = 'V_21',
              particles = [ P.mu__plus__, P.mu__minus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_266})

V_22 = Vertex(name = 'V_22',
              particles = [ P.ta__plus__, P.ta__minus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_269})

V_23 = Vertex(name = 'V_23',
              particles = [ P.c__tilde__, P.c, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_265})

V_24 = Vertex(name = 'V_24',
              particles = [ P.t__tilde__, P.t, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_268})

V_25 = Vertex(name = 'V_25',
              particles = [ P.a, P.a, P.a, P.W__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVV22, L.VVVVV23, L.VVVVV5 ],
              couplings = {(0,1):C.GC_159,(0,2):C.GC_180,(0,0):C.GC_177})

V_26 = Vertex(name = 'V_26',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVV20, L.VVVVV27, L.VVVVV33, L.VVVVV7 ],
              couplings = {(0,1):C.GC_29,(0,3):C.GC_14,(0,2):C.GC_21,(0,0):C.GC_237})

V_27 = Vertex(name = 'V_27',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV1, L.VVVVV14, L.VVVVV2, L.VVVVV25, L.VVVVV29, L.VVVVV30, L.VVVVV8, L.VVVVV9 ],
              couplings = {(0,3):C.GC_148,(0,4):C.GC_145,(0,5):C.GC_153,(0,0):C.GC_134,(0,7):C.GC_143,(0,2):C.GC_150,(0,1):C.GC_258,(0,6):C.GC_130})

V_28 = Vertex(name = 'V_28',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV10, L.VVVVV11, L.VVVVV12, L.VVVVV13, L.VVVVV26, L.VVVVV3, L.VVVVV34, L.VVVVV35, L.VVVVV4, L.VVVVV6 ],
              couplings = {(0,4):C.GC_30,(0,3):C.GC_22,(0,2):C.GC_38,(0,7):C.GC_15,(0,6):C.GC_161,(0,9):C.GC_164,(0,5):C.GC_35,(0,1):C.GC_228,(0,0):C.GC_238,(0,8):C.GC_248})

V_29 = Vertex(name = 'V_29',
              particles = [ P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV1, L.VVVVVV21, L.VVVVVV30, L.VVVVVV31, L.VVVVVV40, L.VVVVVV51 ],
              couplings = {(0,3):C.GC_16,(0,5):C.GC_23,(0,4):C.GC_31,(0,0):C.GC_102,(0,1):C.GC_239,(0,2):C.GC_100})

V_30 = Vertex(name = 'V_30',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVSS2 ],
              couplings = {(0,0):C.GC_8})

V_31 = Vertex(name = 'V_31',
              particles = [ P.a, P.W__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVV1 ],
              couplings = {(0,0):C.GC_4})

V_32 = Vertex(name = 'V_32',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVS2 ],
              couplings = {(0,0):C.GC_198})

V_33 = Vertex(name = 'V_33',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVSS1, L.VVVSS3 ],
              couplings = {(0,1):C.GC_109,(0,0):C.GC_140})

V_34 = Vertex(name = 'V_34',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVS1, L.VVVS3 ],
              couplings = {(0,1):C.GC_216,(0,0):C.GC_221})

V_35 = Vertex(name = 'V_35',
              particles = [ P.a, P.a, P.a, P.a, P.W__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV33, L.VVVVVV36, L.VVVVVV6 ],
              couplings = {(0,2):C.GC_181,(0,0):C.GC_160,(0,1):C.GC_178})

V_36 = Vertex(name = 'V_36',
              particles = [ P.a, P.a, P.a, P.W__minus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV14, L.VVVVVV15, L.VVVVVV2, L.VVVVVV28, L.VVVVVV29, L.VVVVVV38, L.VVVVVV4 ],
              couplings = {(0,2):C.GC_136,(0,0):C.GC_146,(0,5):C.GC_149,(0,1):C.GC_154,(0,3):C.GC_144,(0,6):C.GC_151,(0,4):C.GC_133})

V_37 = Vertex(name = 'V_37',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV1, L.VVVVVV12, L.VVVVVV13, L.VVVVVV30, L.VVVVVV37, L.VVVVVV47, L.VVVVVV49, L.VVVVVV5, L.VVVVVV7, L.VVVVVV8 ],
              couplings = {(0,1):C.GC_24,(0,0):C.GC_103,(0,4):C.GC_32,(0,6):C.GC_17,(0,5):C.GC_162,(0,2):C.GC_40,(0,8):C.GC_165,(0,7):C.GC_37,(0,9):C.GC_261,(0,3):C.GC_101})

V_38 = Vertex(name = 'V_38',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV15, L.VVVVV19, L.VVVVV21, L.VVVVV24, L.VVVVV31 ],
              couplings = {(0,3):C.GC_124,(0,4):C.GC_119,(0,2):C.GC_114,(0,1):C.GC_232,(0,0):C.GC_242})

V_39 = Vertex(name = 'V_39',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVV16, L.VVVVV17, L.VVVVV18, L.VVVVV28, L.VVVVV32, L.VVVVV36 ],
              couplings = {(0,5):C.GC_170,(0,3):C.GC_125,(0,4):C.GC_172,(0,1):C.GC_233,(0,2):C.GC_243,(0,0):C.GC_246})

V_40 = Vertex(name = 'V_40',
              particles = [ P.a, P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVV1, L.VVVVVVV11, L.VVVVVVV17 ],
              couplings = {(0,0):C.GC_18,(0,2):C.GC_33,(0,1):C.GC_25})

V_41 = Vertex(name = 'V_41',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV24, L.VVVVVV27, L.VVVVVV3, L.VVVVVV34, L.VVVVVV42, L.VVVVVV46, L.VVVVVV9 ],
              couplings = {(0,5):C.GC_120,(0,4):C.GC_126,(0,3):C.GC_115,(0,6):C.GC_135,(0,2):C.GC_131,(0,0):C.GC_234,(0,1):C.GC_244})

V_42 = Vertex(name = 'V_42',
              particles = [ P.a, P.a, P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVVV17, L.VVVVVVVV2, L.VVVVVVVV24 ],
              couplings = {(0,1):C.GC_19,(0,2):C.GC_26,(0,0):C.GC_34})

V_43 = Vertex(name = 'V_43',
              particles = [ P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV16, L.VVVVVV25, L.VVVVVV35, L.VVVVVV39 ],
              couplings = {(0,3):C.GC_93,(0,0):C.GC_87,(0,2):C.GC_81,(0,1):C.GC_230})

V_44 = Vertex(name = 'V_44',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV22, L.VVVVVV23, L.VVVVVV32, L.VVVVVV47, L.VVVVVV48, L.VVVVVV52, L.VVVVVV7, L.VVVVVV8 ],
              couplings = {(0,4):C.GC_82,(0,5):C.GC_88,(0,2):C.GC_94,(0,3):C.GC_36,(0,6):C.GC_39,(0,7):C.GC_229,(0,0):C.GC_231,(0,1):C.GC_240})

V_45 = Vertex(name = 'V_45',
              particles = [ P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVV12, L.VVVVVVV13, L.VVVVVVV6 ],
              couplings = {(0,0):C.GC_122,(0,1):C.GC_128,(0,2):C.GC_117})

V_46 = Vertex(name = 'V_46',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVV3, L.VVVVVVV4, L.VVVVVVV8 ],
              couplings = {(0,0):C.GC_89,(0,1):C.GC_96,(0,2):C.GC_83})

V_47 = Vertex(name = 'V_47',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS4 ],
              couplings = {(0,0):C.GC_9})

V_48 = Vertex(name = 'V_48',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS4 ],
              couplings = {(0,0):C.GC_199})

V_49 = Vertex(name = 'V_49',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS5, L.VVVVSS8 ],
              couplings = {(0,1):C.GC_110,(0,0):C.GC_141})

V_50 = Vertex(name = 'V_50',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS5, L.VVVVS8 ],
              couplings = {(0,1):C.GC_217,(0,0):C.GC_222})

V_51 = Vertex(name = 'V_51',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS9 ],
              couplings = {(0,0):C.GC_75})

V_52 = Vertex(name = 'V_52',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS9 ],
              couplings = {(0,0):C.GC_210})

V_53 = Vertex(name = 'V_53',
              particles = [ P.a, P.a, P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVVV16, L.VVVVVVVV22, L.VVVVVVVV4 ],
              couplings = {(0,2):C.GC_91,(0,0):C.GC_98,(0,1):C.GC_85})

V_54 = Vertex(name = 'V_54',
              particles = [ P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVV10, L.VVVVVVV16, L.VVVVVVV18 ],
              couplings = {(0,1):C.GC_60,(0,2):C.GC_68,(0,0):C.GC_64})

V_55 = Vertex(name = 'V_55',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS9 ],
              couplings = {(0,0):C.GC_77})

V_56 = Vertex(name = 'V_56',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS9 ],
              couplings = {(0,0):C.GC_212})

V_57 = Vertex(name = 'V_57',
              particles = [ P.W__minus__, P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVVV21 ],
              couplings = {(0,0):C.GC_45})

V_58 = Vertex(name = 'V_58',
              particles = [ P.W__minus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVS1 ],
              couplings = {(0,0):C.GC_209})

V_59 = Vertex(name = 'V_59',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS1, L.VVVVSS6, L.VVVVSS7 ],
              couplings = {(0,1):C.GC_10,(0,2):C.GC_76,(0,0):C.GC_156})

V_60 = Vertex(name = 'V_60',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS1, L.VVVVS6, L.VVVVS7 ],
              couplings = {(0,1):C.GC_200,(0,2):C.GC_211,(0,0):C.GC_224})

V_61 = Vertex(name = 'V_61',
              particles = [ P.W__minus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVV1 ],
              couplings = {(0,0):C.GC_107})

V_62 = Vertex(name = 'V_62',
              particles = [ P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS3 ],
              couplings = {(0,0):C.GC_79})

V_63 = Vertex(name = 'V_63',
              particles = [ P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS3 ],
              couplings = {(0,0):C.GC_214})

V_64 = Vertex(name = 'V_64',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS4, L.VVVVVSS8 ],
              couplings = {(0,1):C.GC_57,(0,0):C.GC_111})

V_65 = Vertex(name = 'V_65',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS4, L.VVVVVS8 ],
              couplings = {(0,1):C.GC_206,(0,0):C.GC_218})

V_66 = Vertex(name = 'V_66',
              particles = [ P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS7 ],
              couplings = {(0,0):C.GC_49})

V_67 = Vertex(name = 'V_67',
              particles = [ P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS7 ],
              couplings = {(0,0):C.GC_204})

V_68 = Vertex(name = 'V_68',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV10, L.VVVVVV11, L.VVVVVV17, L.VVVVVV18, L.VVVVVV26, L.VVVVVV41, L.VVVVVV44, L.VVVVVV45 ],
              couplings = {(0,5):C.GC_127,(0,7):C.GC_116,(0,6):C.GC_152,(0,2):C.GC_121,(0,0):C.GC_136,(0,3):C.GC_154,(0,1):C.GC_132,(0,4):C.GC_259})

V_69 = Vertex(name = 'V_69',
              particles = [ P.a, P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVVV12, L.VVVVVVVV14, L.VVVVVVVV7 ],
              couplings = {(0,2):C.GC_123,(0,1):C.GC_129,(0,0):C.GC_118})

V_70 = Vertex(name = 'V_70',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVV2, L.VVVVVVV5, L.VVVVVVV7 ],
              couplings = {(0,0):C.GC_84,(0,1):C.GC_90,(0,2):C.GC_97})

V_71 = Vertex(name = 'V_71',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVVV10, L.VVVVVVVV18, L.VVVVVVVV6 ],
              couplings = {(0,2):C.GC_62,(0,0):C.GC_70,(0,1):C.GC_66})

V_72 = Vertex(name = 'V_72',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVV19, L.VVVVVV20, L.VVVVVV43, L.VVVVVV50 ],
              couplings = {(0,0):C.GC_48,(0,2):C.GC_95,(0,3):C.GC_47,(0,1):C.GC_257})

V_73 = Vertex(name = 'V_73',
              particles = [ P.a, P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVVV15, L.VVVVVVVV3, L.VVVVVVVV9 ],
              couplings = {(0,1):C.GC_86,(0,0):C.GC_92,(0,2):C.GC_99})

V_74 = Vertex(name = 'V_74',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVV14, L.VVVVVVV15, L.VVVVVVV9 ],
              couplings = {(0,0):C.GC_65,(0,1):C.GC_69,(0,2):C.GC_61})

V_75 = Vertex(name = 'V_75',
              particles = [ P.W__minus__, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.W__plus__, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVVV1, L.VVVVVVVV19, L.VVVVVVVV25 ],
              couplings = {(0,0):C.GC_53,(0,1):C.GC_55,(0,2):C.GC_51})

V_76 = Vertex(name = 'V_76',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS6, L.VVVVVVSS9 ],
              couplings = {(0,0):C.GC_59,(0,1):C.GC_113})

V_77 = Vertex(name = 'V_77',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS6, L.VVVVVVS9 ],
              couplings = {(0,0):C.GC_208,(0,1):C.GC_220})

V_78 = Vertex(name = 'V_78',
              particles = [ P.a, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVVV11, L.VVVVVVVV13, L.VVVVVVVV8 ],
              couplings = {(0,2):C.GC_67,(0,1):C.GC_71,(0,0):C.GC_63})

V_79 = Vertex(name = 'V_79',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS1, L.VVVVVVSS4, L.VVVVVVSS5 ],
              couplings = {(0,0):C.GC_12,(0,1):C.GC_50,(0,2):C.GC_80})

V_80 = Vertex(name = 'V_80',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS1, L.VVVVVVS4, L.VVVVVVS5 ],
              couplings = {(0,0):C.GC_202,(0,1):C.GC_205,(0,2):C.GC_215})

V_81 = Vertex(name = 'V_81',
              particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__, P.Z, P.Z, P.Z, P.Z ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVVV20, L.VVVVVVVV23, L.VVVVVVVV5 ],
              couplings = {(0,2):C.GC_52,(0,1):C.GC_54,(0,0):C.GC_56})

V_82 = Vertex(name = 'V_82',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS10 ],
              couplings = {(0,0):C.GC_167})

V_83 = Vertex(name = 'V_83',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS10 ],
              couplings = {(0,0):C.GC_250})

V_84 = Vertex(name = 'V_84',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS1, L.VVVVVSS2, L.VVVVVSS3 ],
              couplings = {(0,2):C.GC_11,(0,1):C.GC_78,(0,0):C.GC_157})

V_85 = Vertex(name = 'V_85',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS1, L.VVVVVS2, L.VVVVVS3 ],
              couplings = {(0,2):C.GC_201,(0,1):C.GC_213,(0,0):C.GC_225})

V_86 = Vertex(name = 'V_86',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVSS5, L.VVVVVSS6, L.VVVVVSS7 ],
              couplings = {(0,1):C.GC_58,(0,2):C.GC_112,(0,0):C.GC_142})

V_87 = Vertex(name = 'V_87',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVS5, L.VVVVVS6, L.VVVVVS7 ],
              couplings = {(0,1):C.GC_207,(0,2):C.GC_219,(0,0):C.GC_223})

V_88 = Vertex(name = 'V_88',
              particles = [ P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVS1 ],
              couplings = {(0,0):C.GC_252})

V_89 = Vertex(name = 'V_89',
              particles = [ P.a, P.a, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS1 ],
              couplings = {(0,0):C.GC_191})

V_90 = Vertex(name = 'V_90',
              particles = [ P.a, P.a, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS1 ],
              couplings = {(0,0):C.GC_256})

V_91 = Vertex(name = 'V_91',
              particles = [ P.a, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS2 ],
              couplings = {(0,0):C.GC_186})

V_92 = Vertex(name = 'V_92',
              particles = [ P.a, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS2 ],
              couplings = {(0,0):C.GC_255})

V_93 = Vertex(name = 'V_93',
              particles = [ P.Z, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVSS3 ],
              couplings = {(0,0):C.GC_174})

V_94 = Vertex(name = 'V_94',
              particles = [ P.Z, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVS3 ],
              couplings = {(0,0):C.GC_253})

V_95 = Vertex(name = 'V_95',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS1 ],
              couplings = {(0,0):C.GC_175})

V_96 = Vertex(name = 'V_96',
              particles = [ P.a, P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS1 ],
              couplings = {(0,0):C.GC_254})

V_97 = Vertex(name = 'V_97',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS8 ],
              couplings = {(0,0):C.GC_168})

V_98 = Vertex(name = 'V_98',
              particles = [ P.a, P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVS8 ],
              couplings = {(0,0):C.GC_251})

V_99 = Vertex(name = 'V_99',
              particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVVVVVSS2 ],
              couplings = {(0,0):C.GC_46})

V_100 = Vertex(name = 'V_100',
               particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z, P.Z, P.Z, P.H ],
               color = [ '1' ],
               lorentz = [ L.VVVVVVS2 ],
               couplings = {(0,0):C.GC_249})

V_101 = Vertex(name = 'V_101',
               particles = [ P.e__plus__, P.e__minus__, P.a ],
               color = [ '1' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_3})

V_102 = Vertex(name = 'V_102',
               particles = [ P.mu__plus__, P.mu__minus__, P.a ],
               color = [ '1' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_3})

V_103 = Vertex(name = 'V_103',
               particles = [ P.ta__plus__, P.ta__minus__, P.a ],
               color = [ '1' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_3})

V_104 = Vertex(name = 'V_104',
               particles = [ P.u__tilde__, P.u, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_2})

V_105 = Vertex(name = 'V_105',
               particles = [ P.c__tilde__, P.c, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_2})

V_106 = Vertex(name = 'V_106',
               particles = [ P.t__tilde__, P.t, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_2})

V_107 = Vertex(name = 'V_107',
               particles = [ P.d__tilde__, P.d, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_1})

V_108 = Vertex(name = 'V_108',
               particles = [ P.s__tilde__, P.s, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_1})

V_109 = Vertex(name = 'V_109',
               particles = [ P.b__tilde__, P.b, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_1})

V_110 = Vertex(name = 'V_110',
               particles = [ P.u__tilde__, P.u, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_42})

V_111 = Vertex(name = 'V_111',
               particles = [ P.c__tilde__, P.c, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_42})

V_112 = Vertex(name = 'V_112',
               particles = [ P.t__tilde__, P.t, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_42})

V_113 = Vertex(name = 'V_113',
               particles = [ P.d__tilde__, P.d, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_42})

V_114 = Vertex(name = 'V_114',
               particles = [ P.s__tilde__, P.s, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_42})

V_115 = Vertex(name = 'V_115',
               particles = [ P.b__tilde__, P.b, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_42})

V_116 = Vertex(name = 'V_116',
               particles = [ P.d__tilde__, P.u, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_117 = Vertex(name = 'V_117',
               particles = [ P.s__tilde__, P.c, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_118 = Vertex(name = 'V_118',
               particles = [ P.b__tilde__, P.t, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_119 = Vertex(name = 'V_119',
               particles = [ P.u__tilde__, P.d, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_120 = Vertex(name = 'V_120',
               particles = [ P.c__tilde__, P.s, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_121 = Vertex(name = 'V_121',
               particles = [ P.t__tilde__, P.b, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_122 = Vertex(name = 'V_122',
               particles = [ P.e__plus__, P.ve, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_123 = Vertex(name = 'V_123',
               particles = [ P.mu__plus__, P.vm, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_124 = Vertex(name = 'V_124',
               particles = [ P.ta__plus__, P.vt, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_125 = Vertex(name = 'V_125',
               particles = [ P.ve__tilde__, P.e__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_126 = Vertex(name = 'V_126',
               particles = [ P.vm__tilde__, P.mu__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_127 = Vertex(name = 'V_127',
               particles = [ P.vt__tilde__, P.ta__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_104})

V_128 = Vertex(name = 'V_128',
               particles = [ P.u__tilde__, P.u, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV5 ],
               couplings = {(0,0):C.GC_106,(0,1):C.GC_137})

V_129 = Vertex(name = 'V_129',
               particles = [ P.c__tilde__, P.c, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV5 ],
               couplings = {(0,0):C.GC_106,(0,1):C.GC_137})

V_130 = Vertex(name = 'V_130',
               particles = [ P.t__tilde__, P.t, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV5 ],
               couplings = {(0,0):C.GC_106,(0,1):C.GC_137})

V_131 = Vertex(name = 'V_131',
               particles = [ P.d__tilde__, P.d, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_105,(0,1):C.GC_137})

V_132 = Vertex(name = 'V_132',
               particles = [ P.s__tilde__, P.s, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_105,(0,1):C.GC_137})

V_133 = Vertex(name = 'V_133',
               particles = [ P.b__tilde__, P.b, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_105,(0,1):C.GC_137})

V_134 = Vertex(name = 'V_134',
               particles = [ P.ve__tilde__, P.ve, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_166})

V_135 = Vertex(name = 'V_135',
               particles = [ P.vm__tilde__, P.vm, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_166})

V_136 = Vertex(name = 'V_136',
               particles = [ P.vt__tilde__, P.vt, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_166})

V_137 = Vertex(name = 'V_137',
               particles = [ P.e__plus__, P.e__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_105,(0,1):C.GC_138})

V_138 = Vertex(name = 'V_138',
               particles = [ P.mu__plus__, P.mu__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_105,(0,1):C.GC_138})

V_139 = Vertex(name = 'V_139',
               particles = [ P.ta__plus__, P.ta__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_105,(0,1):C.GC_138})

