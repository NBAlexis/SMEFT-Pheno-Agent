# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 13.1.0 for Microsoft Windows (64-bit) (June 16, 2022)
# Date: Sat 27 May 2023 01:55:50


from object_library import all_vertices, Vertex
import particles as P
import couplings as C
import lorentz as L


V_1 = Vertex(name = 'V_1',
             particles = [ P.g, P.g, P.g ],
             color = [ 'f(1,2,3)' ],
             lorentz = [ L.VVV1 ],
             couplings = {(0,0):C.GC_17})

V_2 = Vertex(name = 'V_2',
             particles = [ P.g, P.g, P.g, P.g ],
             color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
             lorentz = [ L.VVVV2, L.VVVV6, L.VVVV7 ],
             couplings = {(1,1):C.GC_29,(0,0):C.GC_29,(2,2):C.GC_29})

V_3 = Vertex(name = 'V_3',
             particles = [ P.a, P.W__minus__, P.W__plus__ ],
             color = [ '1' ],
             lorentz = [ L.VVV1 ],
             couplings = {(0,0):C.GC_4})

V_4 = Vertex(name = 'V_4',
             particles = [ P.a, P.a, P.W__minus__, P.W__plus__ ],
             color = [ '1' ],
             lorentz = [ L.VVVV5 ],
             couplings = {(0,0):C.GC_5})

V_5 = Vertex(name = 'V_5',
             particles = [ P.W__minus__, P.W__plus__, P.Z ],
             color = [ '1' ],
             lorentz = [ L.VVV1 ],
             couplings = {(0,0):C.GC_76})

V_6 = Vertex(name = 'V_6',
             particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
             color = [ '1' ],
             lorentz = [ L.VVVV5 ],
             couplings = {(0,0):C.GC_55})

V_7 = Vertex(name = 'V_7',
             particles = [ P.a, P.W__minus__, P.W__plus__, P.Z ],
             color = [ '1' ],
             lorentz = [ L.VVVV8 ],
             couplings = {(0,0):C.GC_77})

V_8 = Vertex(name = 'V_8',
             particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z ],
             color = [ '1' ],
             lorentz = [ L.VVVV5 ],
             couplings = {(0,0):C.GC_56})

V_9 = Vertex(name = 'V_9',
             particles = [ P.H, P.H, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.SSSS1 ],
             couplings = {(0,0):C.GC_44})

V_10 = Vertex(name = 'V_10',
              particles = [ P.H, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.SSS1 ],
              couplings = {(0,0):C.GC_142})

V_11 = Vertex(name = 'V_11',
              particles = [ P.W__minus__, P.W__plus__, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVSS1 ],
              couplings = {(0,0):C.GC_54})

V_12 = Vertex(name = 'V_12',
              particles = [ P.W__minus__, P.W__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVS1 ],
              couplings = {(0,0):C.GC_143})

V_13 = Vertex(name = 'V_13',
              particles = [ P.Z, P.Z, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVSS1 ],
              couplings = {(0,0):C.GC_117})

V_14 = Vertex(name = 'V_14',
              particles = [ P.Z, P.Z, P.H ],
              color = [ '1' ],
              lorentz = [ L.VVS1 ],
              couplings = {(0,0):C.GC_144})

V_15 = Vertex(name = 'V_15',
              particles = [ P.e__plus__, P.e__minus__, P.a ],
              color = [ '1' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_3})

V_16 = Vertex(name = 'V_16',
              particles = [ P.mu__plus__, P.mu__minus__, P.a ],
              color = [ '1' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_3})

V_17 = Vertex(name = 'V_17',
              particles = [ P.ta__plus__, P.ta__minus__, P.a ],
              color = [ '1' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_3})

V_18 = Vertex(name = 'V_18',
              particles = [ P.u__tilde__, P.u, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_19 = Vertex(name = 'V_19',
              particles = [ P.c__tilde__, P.c, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_20 = Vertex(name = 'V_20',
              particles = [ P.t__tilde__, P.t, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_21 = Vertex(name = 'V_21',
              particles = [ P.d__tilde__, P.d, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_1})

V_22 = Vertex(name = 'V_22',
              particles = [ P.s__tilde__, P.s, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_1})

V_23 = Vertex(name = 'V_23',
              particles = [ P.b__tilde__, P.b, P.a ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_1})

V_24 = Vertex(name = 'V_24',
              particles = [ P.u__tilde__, P.u, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_25 = Vertex(name = 'V_25',
              particles = [ P.c__tilde__, P.c, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_26 = Vertex(name = 'V_26',
              particles = [ P.t__tilde__, P.t, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_27 = Vertex(name = 'V_27',
              particles = [ P.d__tilde__, P.d, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_28 = Vertex(name = 'V_28',
              particles = [ P.s__tilde__, P.s, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_29 = Vertex(name = 'V_29',
              particles = [ P.b__tilde__, P.b, P.g ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_18})

V_30 = Vertex(name = 'V_30',
              particles = [ P.d__tilde__, P.u, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_70})

V_31 = Vertex(name = 'V_31',
              particles = [ P.s__tilde__, P.u, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_71})

V_32 = Vertex(name = 'V_32',
              particles = [ P.d__tilde__, P.c, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_72})

V_33 = Vertex(name = 'V_33',
              particles = [ P.s__tilde__, P.c, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_73})

V_34 = Vertex(name = 'V_34',
              particles = [ P.b__tilde__, P.t, P.W__minus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_69})

V_35 = Vertex(name = 'V_35',
              particles = [ P.u__tilde__, P.d, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_148})

V_36 = Vertex(name = 'V_36',
              particles = [ P.c__tilde__, P.d, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_150})

V_37 = Vertex(name = 'V_37',
              particles = [ P.u__tilde__, P.s, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_149})

V_38 = Vertex(name = 'V_38',
              particles = [ P.c__tilde__, P.s, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_151})

V_39 = Vertex(name = 'V_39',
              particles = [ P.t__tilde__, P.b, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_69})

V_40 = Vertex(name = 'V_40',
              particles = [ P.e__plus__, P.ve, P.W__minus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_69})

V_41 = Vertex(name = 'V_41',
              particles = [ P.mu__plus__, P.vm, P.W__minus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_69})

V_42 = Vertex(name = 'V_42',
              particles = [ P.ta__plus__, P.vt, P.W__minus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_69})

V_43 = Vertex(name = 'V_43',
              particles = [ P.ve__tilde__, P.e__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_69})

V_44 = Vertex(name = 'V_44',
              particles = [ P.vm__tilde__, P.mu__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_69})

V_45 = Vertex(name = 'V_45',
              particles = [ P.vt__tilde__, P.ta__minus__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_69})

V_46 = Vertex(name = 'V_46',
              particles = [ P.u__tilde__, P.u, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2, L.FFV5 ],
              couplings = {(0,0):C.GC_75,(0,1):C.GC_98})

V_47 = Vertex(name = 'V_47',
              particles = [ P.c__tilde__, P.c, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2, L.FFV5 ],
              couplings = {(0,0):C.GC_75,(0,1):C.GC_98})

V_48 = Vertex(name = 'V_48',
              particles = [ P.t__tilde__, P.t, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2, L.FFV5 ],
              couplings = {(0,0):C.GC_75,(0,1):C.GC_98})

V_49 = Vertex(name = 'V_49',
              particles = [ P.d__tilde__, P.d, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2, L.FFV3 ],
              couplings = {(0,0):C.GC_102,(0,1):C.GC_99})

V_50 = Vertex(name = 'V_50',
              particles = [ P.s__tilde__, P.s, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2, L.FFV3 ],
              couplings = {(0,0):C.GC_102,(0,1):C.GC_99})

V_51 = Vertex(name = 'V_51',
              particles = [ P.b__tilde__, P.b, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFV2, L.FFV3 ],
              couplings = {(0,0):C.GC_102,(0,1):C.GC_99})

V_52 = Vertex(name = 'V_52',
              particles = [ P.ve__tilde__, P.ve, P.Z ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_104})

V_53 = Vertex(name = 'V_53',
              particles = [ P.vm__tilde__, P.vm, P.Z ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_104})

V_54 = Vertex(name = 'V_54',
              particles = [ P.vt__tilde__, P.vt, P.Z ],
              color = [ '1' ],
              lorentz = [ L.FFV2 ],
              couplings = {(0,0):C.GC_104})

V_55 = Vertex(name = 'V_55',
              particles = [ P.e__plus__, P.e__minus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.FFV2, L.FFV3 ],
              couplings = {(0,0):C.GC_103,(0,1):C.GC_101})

V_56 = Vertex(name = 'V_56',
              particles = [ P.mu__plus__, P.mu__minus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.FFV2, L.FFV3 ],
              couplings = {(0,0):C.GC_103,(0,1):C.GC_101})

V_57 = Vertex(name = 'V_57',
              particles = [ P.ta__plus__, P.ta__minus__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.FFV2, L.FFV4 ],
              couplings = {(0,0):C.GC_74,(0,1):C.GC_100})

V_58 = Vertex(name = 'V_58',
              particles = [ P.b__tilde__, P.b, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_145})

V_59 = Vertex(name = 'V_59',
              particles = [ P.ta__plus__, P.ta__minus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_147})

V_60 = Vertex(name = 'V_60',
              particles = [ P.t__tilde__, P.t, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_146})

V_61 = Vertex(name = 'V_61',
              particles = [ P.a, P.a, P.g, P.g ],
              color = [ 'Identity(3,4)' ],
              lorentz = [ L.VVVV11, L.VVVV12, L.VVVV3, L.VVVV4 ],
              couplings = {(0,3):C.GC_119,(0,2):C.GC_121,(0,0):C.GC_120,(0,1):C.GC_118})

V_62 = Vertex(name = 'V_62',
              particles = [ P.g, P.g, P.W__minus__, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.VVVV11, L.VVVV12, L.VVVV3, L.VVVV4 ],
              couplings = {(0,3):C.GC_9,(0,2):C.GC_14,(0,0):C.GC_11,(0,1):C.GC_6})

V_63 = Vertex(name = 'V_63',
              particles = [ P.a, P.g, P.g, P.Z ],
              color = [ 'Identity(2,3)' ],
              lorentz = [ L.VVVV1, L.VVVV10, L.VVVV13, L.VVVV9 ],
              couplings = {(0,0):C.GC_105,(0,3):C.GC_107,(0,2):C.GC_106,(0,1):C.GC_108})

V_64 = Vertex(name = 'V_64',
              particles = [ P.g, P.g, P.Z, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.VVVV11, L.VVVV12, L.VVVV3, L.VVVV4 ],
              couplings = {(0,3):C.GC_123,(0,2):C.GC_125,(0,0):C.GC_124,(0,1):C.GC_122})

V_65 = Vertex(name = 'V_65',
              particles = [ P.a, P.a, P.g, P.g, P.g ],
              color = [ 'f(3,4,5)' ],
              lorentz = [ L.VVVVV1, L.VVVVV12, L.VVVVV2, L.VVVVV8 ],
              couplings = {(0,1):C.GC_128,(0,0):C.GC_129,(0,2):C.GC_127,(0,3):C.GC_126})

V_66 = Vertex(name = 'V_66',
              particles = [ P.g, P.g, P.g, P.W__minus__, P.W__plus__ ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVVVV15, L.VVVVV16, L.VVVVV6, L.VVVVV7 ],
              couplings = {(0,0):C.GC_24,(0,1):C.GC_19,(0,2):C.GC_27,(0,3):C.GC_22})

V_67 = Vertex(name = 'V_67',
              particles = [ P.a, P.g, P.g, P.g, P.Z ],
              color = [ 'f(2,3,4)' ],
              lorentz = [ L.VVVVV10, L.VVVVV13, L.VVVVV3, L.VVVVV9 ],
              couplings = {(0,1):C.GC_111,(0,3):C.GC_112,(0,0):C.GC_110,(0,2):C.GC_109})

V_68 = Vertex(name = 'V_68',
              particles = [ P.g, P.g, P.g, P.Z, P.Z ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVVVV15, L.VVVVV16, L.VVVVV6, L.VVVVV7 ],
              couplings = {(0,0):C.GC_132,(0,1):C.GC_130,(0,2):C.GC_133,(0,3):C.GC_131})

V_69 = Vertex(name = 'V_69',
              particles = [ P.a, P.a, P.g, P.g, P.g, P.g ],
              color = [ 'f(-1,3,4)*f(5,6,-1)', 'f(-1,3,5)*f(4,6,-1)', 'f(-1,3,6)*f(4,5,-1)' ],
              lorentz = [ L.VVVVVV1, L.VVVVVV15, L.VVVVVV2, L.VVVVVV22, L.VVVVVV3, L.VVVVVV34, L.VVVVVV35, L.VVVVVV4, L.VVVVVV43, L.VVVVVV44, L.VVVVVV5, L.VVVVVV6 ],
              couplings = {(2,10):C.GC_137,(1,7):C.GC_135,(0,11):C.GC_137,(2,2):C.GC_135,(1,4):C.GC_137,(0,0):C.GC_135,(2,6):C.GC_136,(1,5):C.GC_136,(0,1):C.GC_136,(1,8):C.GC_134,(0,3):C.GC_134,(2,9):C.GC_134})

V_70 = Vertex(name = 'V_70',
              particles = [ P.g, P.g, P.g, P.g, P.W__minus__, P.W__plus__ ],
              color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
              lorentz = [ L.VVVVVV14, L.VVVVVV17, L.VVVVVV18, L.VVVVVV19, L.VVVVVV20, L.VVVVVV21, L.VVVVVV33, L.VVVVVV38, L.VVVVVV41, L.VVVVVV42, L.VVVVVV52, L.VVVVVV53 ],
              couplings = {(1,10):C.GC_30,(0,7):C.GC_30,(1,8):C.GC_36,(0,6):C.GC_36,(2,11):C.GC_30,(2,9):C.GC_36,(2,4):C.GC_39,(1,3):C.GC_33,(0,5):C.GC_39,(2,1):C.GC_33,(1,2):C.GC_39,(0,0):C.GC_33})

V_71 = Vertex(name = 'V_71',
              particles = [ P.a, P.g, P.g, P.g, P.g, P.Z ],
              color = [ 'f(-1,2,3)*f(4,5,-1)', 'f(-1,2,4)*f(3,5,-1)', 'f(-1,2,5)*f(3,4,-1)' ],
              lorentz = [ L.VVVVVV12, L.VVVVVV13, L.VVVVVV25, L.VVVVVV26, L.VVVVVV27, L.VVVVVV28, L.VVVVVV29, L.VVVVVV30, L.VVVVVV37, L.VVVVVV48, L.VVVVVV49, L.VVVVVV8 ],
              couplings = {(2,8):C.GC_115,(1,9):C.GC_115,(0,10):C.GC_115,(2,6):C.GC_116,(1,5):C.GC_114,(0,7):C.GC_116,(2,3):C.GC_114,(1,4):C.GC_116,(0,2):C.GC_114,(1,0):C.GC_113,(0,11):C.GC_113,(2,1):C.GC_113})

V_72 = Vertex(name = 'V_72',
              particles = [ P.g, P.g, P.g, P.g, P.Z, P.Z ],
              color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
              lorentz = [ L.VVVVVV14, L.VVVVVV17, L.VVVVVV18, L.VVVVVV19, L.VVVVVV20, L.VVVVVV21, L.VVVVVV33, L.VVVVVV38, L.VVVVVV41, L.VVVVVV42, L.VVVVVV52, L.VVVVVV53 ],
              couplings = {(1,10):C.GC_138,(0,7):C.GC_138,(1,8):C.GC_140,(0,6):C.GC_140,(2,11):C.GC_138,(2,9):C.GC_140,(2,4):C.GC_141,(1,3):C.GC_139,(0,5):C.GC_141,(2,1):C.GC_139,(1,2):C.GC_141,(0,0):C.GC_139})

V_73 = Vertex(name = 'V_73',
              particles = [ P.a, P.g, P.g, P.W__minus__, P.W__plus__ ],
              color = [ 'Identity(2,3)' ],
              lorentz = [ L.VVVVV11, L.VVVVV14, L.VVVVV4, L.VVVVV5 ],
              couplings = {(0,1):C.GC_12,(0,2):C.GC_15,(0,3):C.GC_10,(0,0):C.GC_7})

V_74 = Vertex(name = 'V_74',
              particles = [ P.a, P.g, P.g, P.g, P.W__minus__, P.W__plus__ ],
              color = [ 'f(2,3,4)' ],
              lorentz = [ L.VVVVVV23, L.VVVVVV24, L.VVVVVV40, L.VVVVVV51 ],
              couplings = {(0,3):C.GC_25,(0,2):C.GC_20,(0,1):C.GC_23,(0,0):C.GC_28})

V_75 = Vertex(name = 'V_75',
              particles = [ P.a, P.g, P.g, P.g, P.g, P.W__minus__, P.W__plus__ ],
              color = [ 'f(-1,2,3)*f(4,5,-1)', 'f(-1,2,4)*f(3,5,-1)', 'f(-1,2,5)*f(3,4,-1)' ],
              lorentz = [ L.VVVVVVV10, L.VVVVVVV11, L.VVVVVVV12, L.VVVVVVV13, L.VVVVVVV14, L.VVVVVVV20, L.VVVVVVV22, L.VVVVVVV25, L.VVVVVVV26, L.VVVVVVV30, L.VVVVVVV31, L.VVVVVVV9 ],
              couplings = {(1,9):C.GC_31,(0,6):C.GC_31,(1,7):C.GC_37,(0,5):C.GC_37,(2,10):C.GC_31,(2,8):C.GC_37,(2,1):C.GC_40,(1,3):C.GC_41,(0,11):C.GC_35,(1,0):C.GC_34,(0,4):C.GC_40,(2,2):C.GC_35})

V_76 = Vertex(name = 'V_76',
              particles = [ P.a, P.a, P.g, P.g, P.W__minus__, P.W__plus__ ],
              color = [ 'Identity(3,4)' ],
              lorentz = [ L.VVVVVV16, L.VVVVVV39, L.VVVVVV47 ],
              couplings = {(0,0):C.GC_16,(0,1):C.GC_13,(0,2):C.GC_8})

V_77 = Vertex(name = 'V_77',
              particles = [ P.a, P.a, P.g, P.g, P.g, P.W__minus__, P.W__plus__ ],
              color = [ 'f(3,4,5)' ],
              lorentz = [ L.VVVVVVV15, L.VVVVVVV23, L.VVVVVVV29 ],
              couplings = {(0,2):C.GC_26,(0,1):C.GC_21,(0,0):C.GC_42})

V_78 = Vertex(name = 'V_78',
              particles = [ P.a, P.a, P.g, P.g, P.g, P.g, P.W__minus__, P.W__plus__ ],
              color = [ 'f(-1,3,4)*f(5,6,-1)', 'f(-1,3,5)*f(4,6,-1)', 'f(-1,3,6)*f(4,5,-1)' ],
              lorentz = [ L.VVVVVVVV14, L.VVVVVVVV17, L.VVVVVVVV20, L.VVVVVVVV21, L.VVVVVVVV24, L.VVVVVVVV25, L.VVVVVVVV7, L.VVVVVVVV8, L.VVVVVVVV9 ],
              couplings = {(1,4):C.GC_32,(0,1):C.GC_32,(1,2):C.GC_38,(0,0):C.GC_38,(2,5):C.GC_32,(2,3):C.GC_38,(2,8):C.GC_43,(1,7):C.GC_43,(0,6):C.GC_43})

V_79 = Vertex(name = 'V_79',
              particles = [ P.g, P.g, P.W__minus__, P.W__plus__, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.VVVVV1, L.VVVVV12, L.VVVVV2, L.VVVVV8 ],
              couplings = {(0,1):C.GC_81,(0,0):C.GC_83,(0,2):C.GC_80,(0,3):C.GC_78})

V_80 = Vertex(name = 'V_80',
              particles = [ P.g, P.g, P.g, P.W__minus__, P.W__plus__, P.Z ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVVVVV10, L.VVVVVV11, L.VVVVVV31, L.VVVVVV50 ],
              couplings = {(0,3):C.GC_87,(0,1):C.GC_86,(0,0):C.GC_89,(0,2):C.GC_84})

V_81 = Vertex(name = 'V_81',
              particles = [ P.g, P.g, P.g, P.g, P.W__minus__, P.W__plus__, P.Z ],
              color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
              lorentz = [ L.VVVVVVV16, L.VVVVVVV17, L.VVVVVVV18, L.VVVVVVV24, L.VVVVVVV3, L.VVVVVVV32, L.VVVVVVV33, L.VVVVVVV4, L.VVVVVVV5, L.VVVVVVV6, L.VVVVVVV7, L.VVVVVVV8 ],
              couplings = {(2,3):C.GC_94,(1,5):C.GC_94,(0,6):C.GC_94,(2,8):C.GC_96,(1,10):C.GC_97,(0,4):C.GC_93,(1,7):C.GC_92,(0,11):C.GC_96,(2,9):C.GC_93,(1,1):C.GC_90,(0,0):C.GC_90,(2,2):C.GC_90})

V_82 = Vertex(name = 'V_82',
              particles = [ P.g, P.g, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.VVVVVV36, L.VVVVVV45, L.VVVVVV7 ],
              couplings = {(0,2):C.GC_45,(0,0):C.GC_59,(0,1):C.GC_57})

V_83 = Vertex(name = 'V_83',
              particles = [ P.g, P.g, P.g, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVVVVVV1, L.VVVVVVV21, L.VVVVVVV28 ],
              couplings = {(0,0):C.GC_47,(0,1):C.GC_63,(0,2):C.GC_61})

V_84 = Vertex(name = 'V_84',
              particles = [ P.g, P.g, P.g, P.g, P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
              color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
              lorentz = [ L.VVVVVVVV1, L.VVVVVVVV13, L.VVVVVVVV15, L.VVVVVVVV16, L.VVVVVVVV19, L.VVVVVVVV2, L.VVVVVVVV26, L.VVVVVVVV27, L.VVVVVVVV3 ],
              couplings = {(2,8):C.GC_49,(1,5):C.GC_49,(0,0):C.GC_49,(2,3):C.GC_67,(1,2):C.GC_67,(0,1):C.GC_67,(1,6):C.GC_65,(0,4):C.GC_65,(2,7):C.GC_65})

V_85 = Vertex(name = 'V_85',
              particles = [ P.a, P.g, P.g, P.W__minus__, P.W__plus__, P.Z ],
              color = [ 'Identity(2,3)' ],
              lorentz = [ L.VVVVVV32, L.VVVVVV46, L.VVVVVV9 ],
              couplings = {(0,1):C.GC_82,(0,2):C.GC_51,(0,0):C.GC_79})

V_86 = Vertex(name = 'V_86',
              particles = [ P.a, P.g, P.g, P.g, P.W__minus__, P.W__plus__, P.Z ],
              color = [ 'f(2,3,4)' ],
              lorentz = [ L.VVVVVVV19, L.VVVVVVV2, L.VVVVVVV27 ],
              couplings = {(0,2):C.GC_88,(0,1):C.GC_52,(0,0):C.GC_85})

V_87 = Vertex(name = 'V_87',
              particles = [ P.a, P.g, P.g, P.g, P.g, P.W__minus__, P.W__plus__, P.Z ],
              color = [ 'f(-1,2,3)*f(4,5,-1)', 'f(-1,2,4)*f(3,5,-1)', 'f(-1,2,5)*f(3,4,-1)' ],
              lorentz = [ L.VVVVVVVV10, L.VVVVVVVV11, L.VVVVVVVV12, L.VVVVVVVV18, L.VVVVVVVV22, L.VVVVVVVV23, L.VVVVVVVV4, L.VVVVVVVV5, L.VVVVVVVV6 ],
              couplings = {(2,3):C.GC_95,(1,4):C.GC_95,(0,5):C.GC_95,(1,7):C.GC_53,(0,8):C.GC_53,(2,6):C.GC_53,(1,1):C.GC_91,(0,0):C.GC_91,(2,2):C.GC_91})

V_88 = Vertex(name = 'V_88',
              particles = [ P.g, P.g, P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.VVVVVV36, L.VVVVVV45, L.VVVVVV7 ],
              couplings = {(0,2):C.GC_46,(0,0):C.GC_60,(0,1):C.GC_58})

V_89 = Vertex(name = 'V_89',
              particles = [ P.g, P.g, P.g, P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVVVVVV1, L.VVVVVVV21, L.VVVVVVV28 ],
              couplings = {(0,0):C.GC_48,(0,1):C.GC_64,(0,2):C.GC_62})

V_90 = Vertex(name = 'V_90',
              particles = [ P.g, P.g, P.g, P.g, P.W__minus__, P.W__plus__, P.Z, P.Z ],
              color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
              lorentz = [ L.VVVVVVVV1, L.VVVVVVVV13, L.VVVVVVVV15, L.VVVVVVVV16, L.VVVVVVVV19, L.VVVVVVVV2, L.VVVVVVVV26, L.VVVVVVVV27, L.VVVVVVVV3 ],
              couplings = {(2,8):C.GC_50,(1,5):C.GC_50,(0,0):C.GC_50,(2,3):C.GC_68,(1,2):C.GC_68,(0,1):C.GC_68,(1,6):C.GC_66,(0,4):C.GC_66,(2,7):C.GC_66})

