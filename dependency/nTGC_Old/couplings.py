# This file was automatically created by FeynRules 2.3.35
# Mathematica version: 12.0.0 for Microsoft Windows (64-bit) (April 6, 2019)
# Date: Thu 21 Jan 2021 15:25:42


from object_library import all_couplings, Coupling

from function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot



GC_1 = Coupling(name = 'GC_1',
                value = '-(ee*complex(0,1))/3.',
                order = {'QED':1})

GC_2 = Coupling(name = 'GC_2',
                value = '(2*ee*complex(0,1))/3.',
                order = {'QED':1})

GC_3 = Coupling(name = 'GC_3',
                value = '-(ee*complex(0,1))',
                order = {'QED':1})

GC_4 = Coupling(name = 'GC_4',
                value = 'ee*complex(0,1)',
                order = {'QED':1})

GC_5 = Coupling(name = 'GC_5',
                value = 'ee**2*complex(0,1)',
                order = {'QED':2})

GC_6 = Coupling(name = 'GC_6',
                value = '-2*ee*FBW1',
                order = {'NP':1,'QED':1})

GC_7 = Coupling(name = 'GC_7',
                value = 'ee**2*FBW1',
                order = {'NP':1,'QED':2})

GC_8 = Coupling(name = 'GC_8',
                value = '-2*ee**3*FBW1',
                order = {'NP':1,'QED':3})

GC_9 = Coupling(name = 'GC_9',
                value = '-(ee**3*FBW1)',
                order = {'NP':1,'QED':3})

GC_10 = Coupling(name = 'GC_10',
                 value = '-(ee*FBW2)',
                 order = {'NP':1,'QED':1})

GC_11 = Coupling(name = 'GC_11',
                 value = '-(ee**2*FBW2)',
                 order = {'NP':1,'QED':2})

GC_12 = Coupling(name = 'GC_12',
                 value = '-FWW',
                 order = {'NP':1})

GC_13 = Coupling(name = 'GC_13',
                 value = '(ee*FWW)/2.',
                 order = {'NP':1,'QED':1})

GC_14 = Coupling(name = 'GC_14',
                 value = '-(ee**2*FWW)',
                 order = {'NP':1,'QED':2})

GC_15 = Coupling(name = 'GC_15',
                 value = '(ee**2*FWW)/2.',
                 order = {'NP':1,'QED':2})

GC_16 = Coupling(name = 'GC_16',
                 value = '-(ee**3*FWW)',
                 order = {'NP':1,'QED':3})

GC_17 = Coupling(name = 'GC_17',
                 value = '-G',
                 order = {'QCD':1})

GC_18 = Coupling(name = 'GC_18',
                 value = 'complex(0,1)*G',
                 order = {'QCD':1})

GC_19 = Coupling(name = 'GC_19',
                 value = 'complex(0,1)*G**2',
                 order = {'QCD':2})

GC_20 = Coupling(name = 'GC_20',
                 value = '-6*complex(0,1)*lam',
                 order = {'QED':2})

GC_21 = Coupling(name = 'GC_21',
                 value = '-(ee**3*FBW2) - (cw**2*ee**3*FBW2)/sw**2',
                 order = {'NP':1,'QED':3})

GC_22 = Coupling(name = 'GC_22',
                 value = 'ee**3*FWW - (2*cw*ee**3*FBW1)/sw',
                 order = {'NP':1,'QED':3})

GC_23 = Coupling(name = 'GC_23',
                 value = '(2*cw*ee**4*FWW)/sw**3 + (2*ee**4*FWW)/(cw*sw)',
                 order = {'NP':1,'QED':4})

GC_24 = Coupling(name = 'GC_24',
                 value = '(-3*cw*ee**3*FWW)/(2.*sw**3)',
                 order = {'NP':1,'QED':3})

GC_25 = Coupling(name = 'GC_25',
                 value = '(ee**2*complex(0,1))/(2.*sw**2)',
                 order = {'QED':2})

GC_26 = Coupling(name = 'GC_26',
                 value = '-((ee**2*complex(0,1))/sw**2)',
                 order = {'QED':2})

GC_27 = Coupling(name = 'GC_27',
                 value = '(cw**2*ee**2*complex(0,1))/sw**2',
                 order = {'QED':2})

GC_28 = Coupling(name = 'GC_28',
                 value = '-((cw**2*ee**2*FBW1)/sw**2)',
                 order = {'NP':1,'QED':2})

GC_29 = Coupling(name = 'GC_29',
                 value = '(cw**2*ee**3*FBW1)/sw**2',
                 order = {'NP':1,'QED':3})

GC_30 = Coupling(name = 'GC_30',
                 value = '-((cw**2*ee**2*FBW2)/sw**2)',
                 order = {'NP':1,'QED':2})

GC_31 = Coupling(name = 'GC_31',
                 value = '(ee**2*FWW)/sw**2',
                 order = {'NP':1,'QED':2})

GC_32 = Coupling(name = 'GC_32',
                 value = '-(cw**2*ee**2*FWW)/(2.*sw**2)',
                 order = {'NP':1,'QED':2})

GC_33 = Coupling(name = 'GC_33',
                 value = '(2*ee**3*FWW)/sw**2',
                 order = {'NP':1,'QED':3})

GC_34 = Coupling(name = 'GC_34',
                 value = '-(cw**2*ee**3*FWW)/(2.*sw**2)',
                 order = {'NP':1,'QED':3})

GC_35 = Coupling(name = 'GC_35',
                 value = '(ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_36 = Coupling(name = 'GC_36',
                 value = '-(cw*ee*complex(0,1))/(2.*sw)',
                 order = {'QED':1})

GC_37 = Coupling(name = 'GC_37',
                 value = '(cw*ee*complex(0,1))/(2.*sw)',
                 order = {'QED':1})

GC_38 = Coupling(name = 'GC_38',
                 value = '(cw*ee*complex(0,1))/sw',
                 order = {'QED':1})

GC_39 = Coupling(name = 'GC_39',
                 value = '(-2*cw*ee**2*complex(0,1))/sw',
                 order = {'QED':2})

GC_40 = Coupling(name = 'GC_40',
                 value = '(-2*cw*ee*FBW1)/sw',
                 order = {'NP':1,'QED':1})

GC_41 = Coupling(name = 'GC_41',
                 value = '-((cw*ee**2*FBW1)/sw)',
                 order = {'NP':1,'QED':2})

GC_42 = Coupling(name = 'GC_42',
                 value = '(2*cw*ee**2*FBW1)/sw',
                 order = {'NP':1,'QED':2})

GC_43 = Coupling(name = 'GC_43',
                 value = '(cw*ee**3*FBW1)/sw',
                 order = {'NP':1,'QED':3})

GC_44 = Coupling(name = 'GC_44',
                 value = '(cw*ee*FBW2)/sw',
                 order = {'NP':1,'QED':1})

GC_45 = Coupling(name = 'GC_45',
                 value = '(cw*ee**2*FBW2)/sw',
                 order = {'NP':1,'QED':2})

GC_46 = Coupling(name = 'GC_46',
                 value = '-((cw*ee*FWW)/sw)',
                 order = {'NP':1,'QED':1})

GC_47 = Coupling(name = 'GC_47',
                 value = '-(cw*ee**2*FWW)/(2.*sw)',
                 order = {'NP':1,'QED':2})

GC_48 = Coupling(name = 'GC_48',
                 value = '(ee**3*FWW)/(2.*cw*sw)',
                 order = {'NP':1,'QED':3})

GC_49 = Coupling(name = 'GC_49',
                 value = '-((cw*ee**3*FWW)/sw)',
                 order = {'NP':1,'QED':3})

GC_50 = Coupling(name = 'GC_50',
                 value = '-(cw*ee**3*FWW)/(2.*sw)',
                 order = {'NP':1,'QED':3})

GC_51 = Coupling(name = 'GC_51',
                 value = '-(ee*complex(0,1)*sw)/(6.*cw)',
                 order = {'QED':1})

GC_52 = Coupling(name = 'GC_52',
                 value = '(ee*complex(0,1)*sw)/(2.*cw)',
                 order = {'QED':1})

GC_53 = Coupling(name = 'GC_53',
                 value = '(ee**2*FBW1*sw)/cw',
                 order = {'NP':1,'QED':2})

GC_54 = Coupling(name = 'GC_54',
                 value = '-((ee**3*FBW1*sw)/cw)',
                 order = {'NP':1,'QED':3})

GC_55 = Coupling(name = 'GC_55',
                 value = '(ee**2*FBW2*sw)/cw',
                 order = {'NP':1,'QED':2})

GC_56 = Coupling(name = 'GC_56',
                 value = '-(ee*FWW*sw)/(2.*cw)',
                 order = {'NP':1,'QED':1})

GC_57 = Coupling(name = 'GC_57',
                 value = '-(ee**2*FWW*sw)/(2.*cw)',
                 order = {'NP':1,'QED':2})

GC_58 = Coupling(name = 'GC_58',
                 value = '-(ee**3*FWW*sw)/(2.*cw)',
                 order = {'NP':1,'QED':3})

GC_59 = Coupling(name = 'GC_59',
                 value = '-(ee**2*FWW*sw**2)/(2.*cw**2)',
                 order = {'NP':1,'QED':2})

GC_60 = Coupling(name = 'GC_60',
                 value = '-(ee**3*FWW*sw**2)/(2.*cw**2)',
                 order = {'NP':1,'QED':3})

GC_61 = Coupling(name = 'GC_61',
                 value = '(cw*ee*complex(0,1))/(2.*sw) + (ee*complex(0,1)*sw)/(2.*cw)',
                 order = {'QED':1})

GC_62 = Coupling(name = 'GC_62',
                 value = '-(cw*ee*FBW1*sw) + cw*ee*FBW2*sw',
                 order = {'NP':1,'QED':1})

GC_63 = Coupling(name = 'GC_63',
                 value = '(cw*ee**3*FBW2)/sw + (ee**3*FBW2*sw)/cw',
                 order = {'NP':1,'QED':3})

GC_64 = Coupling(name = 'GC_64',
                 value = '-((cw**3*ee**3*FWW)/sw**3) - (ee**3*FWW*sw)/cw',
                 order = {'NP':1,'QED':3})

GC_65 = Coupling(name = 'GC_65',
                 value = '(2*cw**3*ee**4*FWW)/sw**3 + (4*cw*ee**4*FWW)/sw + (2*ee**4*FWW*sw)/cw',
                 order = {'NP':1,'QED':4})

GC_66 = Coupling(name = 'GC_66',
                 value = 'ee**2*complex(0,1) + (cw**2*ee**2*complex(0,1))/(2.*sw**2) + (ee**2*complex(0,1)*sw**2)/(2.*cw**2)',
                 order = {'QED':2})

GC_67 = Coupling(name = 'GC_67',
                 value = '2*cw**2*ee*FBB - (cw**2*ee*FWW)/2. + 2*ee*FBB*sw**2 - (ee*FWW*sw**2)/2.',
                 order = {'NP':1,'QED':1})

GC_68 = Coupling(name = 'GC_68',
                 value = '2*ee**4*FWW + (cw**2*ee**4*FWW)/sw**2 + (ee**4*FWW*sw**2)/cw**2',
                 order = {'NP':1,'QED':4})

GC_69 = Coupling(name = 'GC_69',
                 value = '-2*cw**2*ee*FBW1 - 2*cw**2*ee*FBW2 - (cw**3*ee*FWW)/sw - 4*cw*ee*FBB*sw - cw*ee*FWW*sw - 2*ee*FBW1*sw**2 - 2*ee*FBW2*sw**2 - (4*ee*FBB*sw**3)/cw',
                 order = {'NP':1,'QED':1})

GC_70 = Coupling(name = 'GC_70',
                 value = '(cw**3*ee*FBW2)/sw - (ee*FBW1*sw**3)/cw',
                 order = {'NP':1,'QED':1})

GC_71 = Coupling(name = 'GC_71',
                 value = '(-2*cw**3*ee*FBW1)/sw + (2*ee*FBW2*sw**3)/cw',
                 order = {'NP':1,'QED':1})

GC_72 = Coupling(name = 'GC_72',
                 value = 'cw**2*ee*FBW1 + cw**2*ee*FBW2 - (2*cw**3*ee*FBB)/sw - 2*cw*ee*FBB*sw - (cw*ee*FWW*sw)/2. + ee*FBW1*sw**2 + ee*FBW2*sw**2 - (ee*FWW*sw**3)/(2.*cw)',
                 order = {'NP':1,'QED':1})

GC_73 = Coupling(name = 'GC_73',
                 value = '-2*ee*FBW1*vev',
                 order = {'NP':1})

GC_74 = Coupling(name = 'GC_74',
                 value = 'ee**2*FBW1*vev',
                 order = {'NP':1,'QED':1})

GC_75 = Coupling(name = 'GC_75',
                 value = '-2*ee**3*FBW1*vev',
                 order = {'NP':1,'QED':2})

GC_76 = Coupling(name = 'GC_76',
                 value = '-(ee**3*FBW1*vev)',
                 order = {'NP':1,'QED':2})

GC_77 = Coupling(name = 'GC_77',
                 value = '-(ee*FBW2*vev)',
                 order = {'NP':1})

GC_78 = Coupling(name = 'GC_78',
                 value = '-(ee**2*FBW2*vev)',
                 order = {'NP':1,'QED':1})

GC_79 = Coupling(name = 'GC_79',
                 value = '-(FWW*vev)',
                 order = {'NP':1,'QED':-1})

GC_80 = Coupling(name = 'GC_80',
                 value = '(ee*FWW*vev)/2.',
                 order = {'NP':1})

GC_81 = Coupling(name = 'GC_81',
                 value = '-(ee**2*FWW*vev)',
                 order = {'NP':1,'QED':1})

GC_82 = Coupling(name = 'GC_82',
                 value = '(ee**2*FWW*vev)/2.',
                 order = {'NP':1,'QED':1})

GC_83 = Coupling(name = 'GC_83',
                 value = '-(ee**3*FWW*vev)',
                 order = {'NP':1,'QED':2})

GC_84 = Coupling(name = 'GC_84',
                 value = '-6*complex(0,1)*lam*vev',
                 order = {'QED':1})

GC_85 = Coupling(name = 'GC_85',
                 value = '(-3*cw*ee**3*FWW*vev)/(2.*sw**3)',
                 order = {'NP':1,'QED':2})

GC_86 = Coupling(name = 'GC_86',
                 value = '(ee**2*complex(0,1)*vev)/(2.*sw**2)',
                 order = {'QED':1})

GC_87 = Coupling(name = 'GC_87',
                 value = '-((cw**2*ee**2*FBW1*vev)/sw**2)',
                 order = {'NP':1,'QED':1})

GC_88 = Coupling(name = 'GC_88',
                 value = '(cw**2*ee**3*FBW1*vev)/sw**2',
                 order = {'NP':1,'QED':2})

GC_89 = Coupling(name = 'GC_89',
                 value = '-((cw**2*ee**2*FBW2*vev)/sw**2)',
                 order = {'NP':1,'QED':1})

GC_90 = Coupling(name = 'GC_90',
                 value = '(ee**2*FWW*vev)/sw**2',
                 order = {'NP':1,'QED':1})

GC_91 = Coupling(name = 'GC_91',
                 value = '-(cw**2*ee**2*FWW*vev)/(2.*sw**2)',
                 order = {'NP':1,'QED':1})

GC_92 = Coupling(name = 'GC_92',
                 value = '(2*ee**3*FWW*vev)/sw**2',
                 order = {'NP':1,'QED':2})

GC_93 = Coupling(name = 'GC_93',
                 value = '-(cw**2*ee**3*FWW*vev)/(2.*sw**2)',
                 order = {'NP':1,'QED':2})

GC_94 = Coupling(name = 'GC_94',
                 value = '(-2*cw*ee*FBW1*vev)/sw',
                 order = {'NP':1})

GC_95 = Coupling(name = 'GC_95',
                 value = '-((cw*ee**2*FBW1*vev)/sw)',
                 order = {'NP':1,'QED':1})

GC_96 = Coupling(name = 'GC_96',
                 value = '(2*cw*ee**2*FBW1*vev)/sw',
                 order = {'NP':1,'QED':1})

GC_97 = Coupling(name = 'GC_97',
                 value = '(cw*ee**3*FBW1*vev)/sw',
                 order = {'NP':1,'QED':2})

GC_98 = Coupling(name = 'GC_98',
                 value = '(cw*ee*FBW2*vev)/sw',
                 order = {'NP':1})

GC_99 = Coupling(name = 'GC_99',
                 value = '(cw*ee**2*FBW2*vev)/sw',
                 order = {'NP':1,'QED':1})

GC_100 = Coupling(name = 'GC_100',
                  value = '-((cw*ee*FWW*vev)/sw)',
                  order = {'NP':1})

GC_101 = Coupling(name = 'GC_101',
                  value = '-(cw*ee**2*FWW*vev)/(2.*sw)',
                  order = {'NP':1,'QED':1})

GC_102 = Coupling(name = 'GC_102',
                  value = '(ee**3*FWW*vev)/(2.*cw*sw)',
                  order = {'NP':1,'QED':2})

GC_103 = Coupling(name = 'GC_103',
                  value = '-((cw*ee**3*FWW*vev)/sw)',
                  order = {'NP':1,'QED':2})

GC_104 = Coupling(name = 'GC_104',
                  value = '-(cw*ee**3*FWW*vev)/(2.*sw)',
                  order = {'NP':1,'QED':2})

GC_105 = Coupling(name = 'GC_105',
                  value = '(ee**2*FBW1*sw*vev)/cw',
                  order = {'NP':1,'QED':1})

GC_106 = Coupling(name = 'GC_106',
                  value = '-((ee**3*FBW1*sw*vev)/cw)',
                  order = {'NP':1,'QED':2})

GC_107 = Coupling(name = 'GC_107',
                  value = '(ee**2*FBW2*sw*vev)/cw',
                  order = {'NP':1,'QED':1})

GC_108 = Coupling(name = 'GC_108',
                  value = '-(ee*FWW*sw*vev)/(2.*cw)',
                  order = {'NP':1})

GC_109 = Coupling(name = 'GC_109',
                  value = '-(ee**2*FWW*sw*vev)/(2.*cw)',
                  order = {'NP':1,'QED':1})

GC_110 = Coupling(name = 'GC_110',
                  value = '-(ee**3*FWW*sw*vev)/(2.*cw)',
                  order = {'NP':1,'QED':2})

GC_111 = Coupling(name = 'GC_111',
                  value = '-(ee**2*FWW*sw**2*vev)/(2.*cw**2)',
                  order = {'NP':1,'QED':1})

GC_112 = Coupling(name = 'GC_112',
                  value = '-(ee**3*FWW*sw**2*vev)/(2.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_113 = Coupling(name = 'GC_113',
                  value = '-(ee*FBW1*vev**2)',
                  order = {'NP':1,'QED':-1})

GC_114 = Coupling(name = 'GC_114',
                  value = '(ee**2*FBW1*vev**2)/2.',
                  order = {'NP':1})

GC_115 = Coupling(name = 'GC_115',
                  value = '-(ee**3*FBW1*vev**2)',
                  order = {'NP':1,'QED':1})

GC_116 = Coupling(name = 'GC_116',
                  value = '-(ee**3*FBW1*vev**2)/2.',
                  order = {'NP':1,'QED':1})

GC_117 = Coupling(name = 'GC_117',
                  value = '-(ee*FBW2*vev**2)/2.',
                  order = {'NP':1,'QED':-1})

GC_118 = Coupling(name = 'GC_118',
                  value = '-(ee**2*FBW2*vev**2)/2.',
                  order = {'NP':1})

GC_119 = Coupling(name = 'GC_119',
                  value = '(ee*FWW*vev**2)/4.',
                  order = {'NP':1,'QED':-1})

GC_120 = Coupling(name = 'GC_120',
                  value = '-(ee**2*FWW*vev**2)/2.',
                  order = {'NP':1})

GC_121 = Coupling(name = 'GC_121',
                  value = '(ee**2*FWW*vev**2)/4.',
                  order = {'NP':1})

GC_122 = Coupling(name = 'GC_122',
                  value = '-(ee**3*FWW*vev**2)/2.',
                  order = {'NP':1,'QED':1})

GC_123 = Coupling(name = 'GC_123',
                  value = '(-3*cw*ee**3*FWW*vev**2)/(4.*sw**3)',
                  order = {'NP':1,'QED':1})

GC_124 = Coupling(name = 'GC_124',
                  value = '-(cw**2*ee**2*FBW1*vev**2)/(2.*sw**2)',
                  order = {'NP':1})

GC_125 = Coupling(name = 'GC_125',
                  value = '(cw**2*ee**3*FBW1*vev**2)/(2.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_126 = Coupling(name = 'GC_126',
                  value = '-(cw**2*ee**2*FBW2*vev**2)/(2.*sw**2)',
                  order = {'NP':1})

GC_127 = Coupling(name = 'GC_127',
                  value = '(ee**2*FWW*vev**2)/(2.*sw**2)',
                  order = {'NP':1})

GC_128 = Coupling(name = 'GC_128',
                  value = '-(cw**2*ee**2*FWW*vev**2)/(4.*sw**2)',
                  order = {'NP':1})

GC_129 = Coupling(name = 'GC_129',
                  value = '(ee**3*FWW*vev**2)/sw**2',
                  order = {'NP':1,'QED':1})

GC_130 = Coupling(name = 'GC_130',
                  value = '-(cw**2*ee**3*FWW*vev**2)/(4.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_131 = Coupling(name = 'GC_131',
                  value = '-((cw*ee*FBW1*vev**2)/sw)',
                  order = {'NP':1,'QED':-1})

GC_132 = Coupling(name = 'GC_132',
                  value = '-(cw*ee**2*FBW1*vev**2)/(2.*sw)',
                  order = {'NP':1})

GC_133 = Coupling(name = 'GC_133',
                  value = '(cw*ee**2*FBW1*vev**2)/sw',
                  order = {'NP':1})

GC_134 = Coupling(name = 'GC_134',
                  value = '(cw*ee**3*FBW1*vev**2)/(2.*sw)',
                  order = {'NP':1,'QED':1})

GC_135 = Coupling(name = 'GC_135',
                  value = '(cw*ee*FBW2*vev**2)/(2.*sw)',
                  order = {'NP':1,'QED':-1})

GC_136 = Coupling(name = 'GC_136',
                  value = '(cw*ee**2*FBW2*vev**2)/(2.*sw)',
                  order = {'NP':1})

GC_137 = Coupling(name = 'GC_137',
                  value = '-(cw*ee*FWW*vev**2)/(2.*sw)',
                  order = {'NP':1,'QED':-1})

GC_138 = Coupling(name = 'GC_138',
                  value = '-(cw*ee**2*FWW*vev**2)/(4.*sw)',
                  order = {'NP':1})

GC_139 = Coupling(name = 'GC_139',
                  value = '(ee**3*FWW*vev**2)/(4.*cw*sw)',
                  order = {'NP':1,'QED':1})

GC_140 = Coupling(name = 'GC_140',
                  value = '-(cw*ee**3*FWW*vev**2)/(2.*sw)',
                  order = {'NP':1,'QED':1})

GC_141 = Coupling(name = 'GC_141',
                  value = '-(cw*ee**3*FWW*vev**2)/(4.*sw)',
                  order = {'NP':1,'QED':1})

GC_142 = Coupling(name = 'GC_142',
                  value = '(ee**2*FBW1*sw*vev**2)/(2.*cw)',
                  order = {'NP':1})

GC_143 = Coupling(name = 'GC_143',
                  value = '-(ee**3*FBW1*sw*vev**2)/(2.*cw)',
                  order = {'NP':1,'QED':1})

GC_144 = Coupling(name = 'GC_144',
                  value = '(ee**2*FBW2*sw*vev**2)/(2.*cw)',
                  order = {'NP':1})

GC_145 = Coupling(name = 'GC_145',
                  value = '-(ee*FWW*sw*vev**2)/(4.*cw)',
                  order = {'NP':1,'QED':-1})

GC_146 = Coupling(name = 'GC_146',
                  value = '-(ee**2*FWW*sw*vev**2)/(4.*cw)',
                  order = {'NP':1})

GC_147 = Coupling(name = 'GC_147',
                  value = '-(ee**3*FWW*sw*vev**2)/(4.*cw)',
                  order = {'NP':1,'QED':1})

GC_148 = Coupling(name = 'GC_148',
                  value = '-(ee**2*FWW*sw**2*vev**2)/(4.*cw**2)',
                  order = {'NP':1})

GC_149 = Coupling(name = 'GC_149',
                  value = '-(ee**3*FWW*sw**2*vev**2)/(4.*cw**2)',
                  order = {'NP':1,'QED':1})

GC_150 = Coupling(name = 'GC_150',
                  value = '-(ee**3*FBW2*vev) - (cw**2*ee**3*FBW2*vev)/sw**2',
                  order = {'NP':1,'QED':2})

GC_151 = Coupling(name = 'GC_151',
                  value = 'ee**3*FWW*vev - (2*cw*ee**3*FBW1*vev)/sw',
                  order = {'NP':1,'QED':2})

GC_152 = Coupling(name = 'GC_152',
                  value = '(2*cw*ee**4*FWW*vev)/sw**3 + (2*ee**4*FWW*vev)/(cw*sw)',
                  order = {'NP':1,'QED':3})

GC_153 = Coupling(name = 'GC_153',
                  value = '-(cw*ee*FBW1*sw*vev) + cw*ee*FBW2*sw*vev',
                  order = {'NP':1})

GC_154 = Coupling(name = 'GC_154',
                  value = '(cw*ee**3*FBW2*vev)/sw + (ee**3*FBW2*sw*vev)/cw',
                  order = {'NP':1,'QED':2})

GC_155 = Coupling(name = 'GC_155',
                  value = '-((cw**3*ee**3*FWW*vev)/sw**3) - (ee**3*FWW*sw*vev)/cw',
                  order = {'NP':1,'QED':2})

GC_156 = Coupling(name = 'GC_156',
                  value = '(2*cw**3*ee**4*FWW*vev)/sw**3 + (4*cw*ee**4*FWW*vev)/sw + (2*ee**4*FWW*sw*vev)/cw',
                  order = {'NP':1,'QED':3})

GC_157 = Coupling(name = 'GC_157',
                  value = 'ee**2*complex(0,1)*vev + (cw**2*ee**2*complex(0,1)*vev)/(2.*sw**2) + (ee**2*complex(0,1)*sw**2*vev)/(2.*cw**2)',
                  order = {'QED':1})

GC_158 = Coupling(name = 'GC_158',
                  value = '2*cw**2*ee*FBB*vev - (cw**2*ee*FWW*vev)/2. + 2*ee*FBB*sw**2*vev - (ee*FWW*sw**2*vev)/2.',
                  order = {'NP':1})

GC_159 = Coupling(name = 'GC_159',
                  value = '2*ee**4*FWW*vev + (cw**2*ee**4*FWW*vev)/sw**2 + (ee**4*FWW*sw**2*vev)/cw**2',
                  order = {'NP':1,'QED':3})

GC_160 = Coupling(name = 'GC_160',
                  value = '-2*cw**2*ee*FBW1*vev - 2*cw**2*ee*FBW2*vev - (cw**3*ee*FWW*vev)/sw - 4*cw*ee*FBB*sw*vev - cw*ee*FWW*sw*vev - 2*ee*FBW1*sw**2*vev - 2*ee*FBW2*sw**2*vev - (4*ee*FBB*sw**3*vev)/cw',
                  order = {'NP':1})

GC_161 = Coupling(name = 'GC_161',
                  value = '(cw**3*ee*FBW2*vev)/sw - (ee*FBW1*sw**3*vev)/cw',
                  order = {'NP':1})

GC_162 = Coupling(name = 'GC_162',
                  value = '(-2*cw**3*ee*FBW1*vev)/sw + (2*ee*FBW2*sw**3*vev)/cw',
                  order = {'NP':1})

GC_163 = Coupling(name = 'GC_163',
                  value = 'cw**2*ee*FBW1*vev + cw**2*ee*FBW2*vev - (2*cw**3*ee*FBB*vev)/sw - 2*cw*ee*FBB*sw*vev - (cw*ee*FWW*sw*vev)/2. + ee*FBW1*sw**2*vev + ee*FBW2*sw**2*vev - (ee*FWW*sw**3*vev)/(2.*cw)',
                  order = {'NP':1})

GC_164 = Coupling(name = 'GC_164',
                  value = '-(ee**3*FBW2*vev**2)/2. - (cw**2*ee**3*FBW2*vev**2)/(2.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_165 = Coupling(name = 'GC_165',
                  value = '(ee**3*FWW*vev**2)/2. - (cw*ee**3*FBW1*vev**2)/sw',
                  order = {'NP':1,'QED':1})

GC_166 = Coupling(name = 'GC_166',
                  value = '(cw*ee**4*FWW*vev**2)/sw**3 + (ee**4*FWW*vev**2)/(cw*sw)',
                  order = {'NP':1,'QED':2})

GC_167 = Coupling(name = 'GC_167',
                  value = '-(cw*ee*FBW1*sw*vev**2)/2. + (cw*ee*FBW2*sw*vev**2)/2.',
                  order = {'NP':1,'QED':-1})

GC_168 = Coupling(name = 'GC_168',
                  value = '(cw*ee**3*FBW2*vev**2)/(2.*sw) + (ee**3*FBW2*sw*vev**2)/(2.*cw)',
                  order = {'NP':1,'QED':1})

GC_169 = Coupling(name = 'GC_169',
                  value = '-(cw**3*ee**3*FWW*vev**2)/(2.*sw**3) - (ee**3*FWW*sw*vev**2)/(2.*cw)',
                  order = {'NP':1,'QED':1})

GC_170 = Coupling(name = 'GC_170',
                  value = '(cw**3*ee**4*FWW*vev**2)/sw**3 + (2*cw*ee**4*FWW*vev**2)/sw + (ee**4*FWW*sw*vev**2)/cw',
                  order = {'NP':1,'QED':2})

GC_171 = Coupling(name = 'GC_171',
                  value = 'cw**2*ee*FBB*vev**2 - (cw**2*ee*FWW*vev**2)/4. + ee*FBB*sw**2*vev**2 - (ee*FWW*sw**2*vev**2)/4.',
                  order = {'NP':1,'QED':-1})

GC_172 = Coupling(name = 'GC_172',
                  value = 'ee**4*FWW*vev**2 + (cw**2*ee**4*FWW*vev**2)/(2.*sw**2) + (ee**4*FWW*sw**2*vev**2)/(2.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_173 = Coupling(name = 'GC_173',
                  value = '-(cw**2*ee*FBW1*vev**2) - cw**2*ee*FBW2*vev**2 - (cw**3*ee*FWW*vev**2)/(2.*sw) - 2*cw*ee*FBB*sw*vev**2 - (cw*ee*FWW*sw*vev**2)/2. - ee*FBW1*sw**2*vev**2 - ee*FBW2*sw**2*vev**2 - (2*ee*FBB*sw**3*vev**2)/cw',
                  order = {'NP':1,'QED':-1})

GC_174 = Coupling(name = 'GC_174',
                  value = '(cw**3*ee*FBW2*vev**2)/(2.*sw) - (ee*FBW1*sw**3*vev**2)/(2.*cw)',
                  order = {'NP':1,'QED':-1})

GC_175 = Coupling(name = 'GC_175',
                  value = '-((cw**3*ee*FBW1*vev**2)/sw) + (ee*FBW2*sw**3*vev**2)/cw',
                  order = {'NP':1,'QED':-1})

GC_176 = Coupling(name = 'GC_176',
                  value = '(cw**2*ee*FBW1*vev**2)/2. + (cw**2*ee*FBW2*vev**2)/2. - (cw**3*ee*FBB*vev**2)/sw - cw*ee*FBB*sw*vev**2 - (cw*ee*FWW*sw*vev**2)/4. + (ee*FBW1*sw**2*vev**2)/2. + (ee*FBW2*sw**2*vev**2)/2. - (ee*FWW*sw**3*vev**2)/(4.*cw)',
                  order = {'NP':1,'QED':-1})

GC_177 = Coupling(name = 'GC_177',
                  value = '-((complex(0,1)*yb)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_178 = Coupling(name = 'GC_178',
                  value = '-((complex(0,1)*yc)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_179 = Coupling(name = 'GC_179',
                  value = '-((complex(0,1)*ym)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_180 = Coupling(name = 'GC_180',
                  value = '-((complex(0,1)*ys)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_181 = Coupling(name = 'GC_181',
                  value = '-((complex(0,1)*yt)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_182 = Coupling(name = 'GC_182',
                  value = '-((complex(0,1)*ytau)/cmath.sqrt(2))',
                  order = {'QED':1})

