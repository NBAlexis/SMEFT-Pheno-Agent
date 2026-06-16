# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 13.1.0 for Microsoft Windows (64-bit) (June 16, 2022)
# Date: Sat 27 May 2023 01:55:50


from object_library import all_couplings, Coupling

from function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot



GC_1 = Coupling(name = 'GC_1',
                value = '-0.3333333333333333*(ee*complex(0,1))',
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
                value = 'FgT0*complex(0,1)',
                order = {'NP':1})

GC_7 = Coupling(name = 'GC_7',
                value = '-(ee*FgT0*complex(0,1))',
                order = {'NP':1,'QED':1})

GC_8 = Coupling(name = 'GC_8',
                value = '-(ee**2*FgT0*complex(0,1))',
                order = {'NP':1,'QED':2})

GC_9 = Coupling(name = 'GC_9',
                value = '(FgT1*complex(0,1))/2.',
                order = {'NP':1})

GC_10 = Coupling(name = 'GC_10',
                 value = '(ee*FgT1*complex(0,1))/2.',
                 order = {'NP':1,'QED':1})

GC_11 = Coupling(name = 'GC_11',
                 value = '(FgT2*complex(0,1))/8.',
                 order = {'NP':1})

GC_12 = Coupling(name = 'GC_12',
                 value = '-0.125*(ee*FgT2*complex(0,1))',
                 order = {'NP':1,'QED':1})

GC_13 = Coupling(name = 'GC_13',
                 value = '-0.125*(ee**2*FgT2*complex(0,1))',
                 order = {'NP':1,'QED':2})

GC_14 = Coupling(name = 'GC_14',
                 value = '(FgT3*complex(0,1))/4.',
                 order = {'NP':1})

GC_15 = Coupling(name = 'GC_15',
                 value = '-0.25*(ee*FgT3*complex(0,1))',
                 order = {'NP':1,'QED':1})

GC_16 = Coupling(name = 'GC_16',
                 value = '-0.5*(ee**2*FgT1*complex(0,1)) - (ee**2*FgT3*complex(0,1))/4.',
                 order = {'NP':1,'QED':2})

GC_17 = Coupling(name = 'GC_17',
                 value = '-G',
                 order = {'QCD':1})

GC_18 = Coupling(name = 'GC_18',
                 value = 'complex(0,1)*G',
                 order = {'QCD':1})

GC_19 = Coupling(name = 'GC_19',
                 value = 'FgT0*G',
                 order = {'NP':1,'QCD':1})

GC_20 = Coupling(name = 'GC_20',
                 value = '-(ee*FgT0*G)',
                 order = {'NP':1,'QCD':1,'QED':1})

GC_21 = Coupling(name = 'GC_21',
                 value = '-(ee**2*FgT0*G)',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_22 = Coupling(name = 'GC_22',
                 value = '-0.5*(FgT1*G)',
                 order = {'NP':1,'QCD':1})

GC_23 = Coupling(name = 'GC_23',
                 value = '-0.5*(ee*FgT1*G)',
                 order = {'NP':1,'QCD':1,'QED':1})

GC_24 = Coupling(name = 'GC_24',
                 value = '(FgT2*G)/8.',
                 order = {'NP':1,'QCD':1})

GC_25 = Coupling(name = 'GC_25',
                 value = '-0.125*(ee*FgT2*G)',
                 order = {'NP':1,'QCD':1,'QED':1})

GC_26 = Coupling(name = 'GC_26',
                 value = '-0.125*(ee**2*FgT2*G)',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_27 = Coupling(name = 'GC_27',
                 value = '(FgT3*G)/4.',
                 order = {'NP':1,'QCD':1})

GC_28 = Coupling(name = 'GC_28',
                 value = '(ee*FgT3*G)/4.',
                 order = {'NP':1,'QCD':1,'QED':1})

GC_29 = Coupling(name = 'GC_29',
                 value = 'complex(0,1)*G**2',
                 order = {'QCD':2})

GC_30 = Coupling(name = 'GC_30',
                 value = '-(FgT0*complex(0,1)*G**2)',
                 order = {'NP':1,'QCD':2})

GC_31 = Coupling(name = 'GC_31',
                 value = 'ee*FgT0*complex(0,1)*G**2',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_32 = Coupling(name = 'GC_32',
                 value = 'ee**2*FgT0*complex(0,1)*G**2',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_33 = Coupling(name = 'GC_33',
                 value = '-0.5*(FgT1*complex(0,1)*G**2)',
                 order = {'NP':1,'QCD':2})

GC_34 = Coupling(name = 'GC_34',
                 value = '-0.5*(ee*FgT1*complex(0,1)*G**2)',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_35 = Coupling(name = 'GC_35',
                 value = '(ee*FgT1*complex(0,1)*G**2)/2.',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_36 = Coupling(name = 'GC_36',
                 value = '-0.125*(FgT2*complex(0,1)*G**2)',
                 order = {'NP':1,'QCD':2})

GC_37 = Coupling(name = 'GC_37',
                 value = '(ee*FgT2*complex(0,1)*G**2)/8.',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_38 = Coupling(name = 'GC_38',
                 value = '(ee**2*FgT2*complex(0,1)*G**2)/8.',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_39 = Coupling(name = 'GC_39',
                 value = '-0.25*(FgT3*complex(0,1)*G**2)',
                 order = {'NP':1,'QCD':2})

GC_40 = Coupling(name = 'GC_40',
                 value = '-0.25*(ee*FgT3*complex(0,1)*G**2)',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_41 = Coupling(name = 'GC_41',
                 value = '(ee*FgT3*complex(0,1)*G**2)/4.',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_42 = Coupling(name = 'GC_42',
                 value = '(ee**2*FgT1*G)/2. + (ee**2*FgT3*G)/4.',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_43 = Coupling(name = 'GC_43',
                 value = '(ee**2*FgT1*complex(0,1)*G**2)/2. + (ee**2*FgT3*complex(0,1)*G**2)/4.',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_44 = Coupling(name = 'GC_44',
                 value = '-6*complex(0,1)*lam',
                 order = {'QED':2})

GC_45 = Coupling(name = 'GC_45',
                 value = '(ee**2*FgT1*complex(0,1))/(2.*sw**2) + (ee**2*FgT3*complex(0,1))/(4.*sw**2)',
                 order = {'NP':1,'QED':2})

GC_46 = Coupling(name = 'GC_46',
                 value = '-0.5*(cw**2*ee**2*FgT1*complex(0,1))/sw**2 - (cw**2*ee**2*FgT3*complex(0,1))/(4.*sw**2)',
                 order = {'NP':1,'QED':2})

GC_47 = Coupling(name = 'GC_47',
                 value = '-0.5*(ee**2*FgT1*G)/sw**2 - (ee**2*FgT3*G)/(4.*sw**2)',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_48 = Coupling(name = 'GC_48',
                 value = '(cw**2*ee**2*FgT1*G)/(2.*sw**2) + (cw**2*ee**2*FgT3*G)/(4.*sw**2)',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_49 = Coupling(name = 'GC_49',
                 value = '-0.5*(ee**2*FgT1*complex(0,1)*G**2)/sw**2 - (ee**2*FgT3*complex(0,1)*G**2)/(4.*sw**2)',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_50 = Coupling(name = 'GC_50',
                 value = '(cw**2*ee**2*FgT1*complex(0,1)*G**2)/(2.*sw**2) + (cw**2*ee**2*FgT3*complex(0,1)*G**2)/(4.*sw**2)',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_51 = Coupling(name = 'GC_51',
                 value = '(cw*ee**2*FgT1*complex(0,1))/(2.*sw) + (cw*ee**2*FgT3*complex(0,1))/(4.*sw)',
                 order = {'NP':1,'QED':2})

GC_52 = Coupling(name = 'GC_52',
                 value = '(cw*ee**2*FgT1*G)/(2.*sw) + (cw*ee**2*FgT3*G)/(4.*sw)',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_53 = Coupling(name = 'GC_53',
                 value = '-0.5*(cw*ee**2*FgT1*complex(0,1)*G**2)/sw - (cw*ee**2*FgT3*complex(0,1)*G**2)/(4.*sw)',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_54 = Coupling(name = 'GC_54',
                 value = '(ee**2*complex(0,1))/(2.*sw**2)',
                 order = {'QED':2})

GC_55 = Coupling(name = 'GC_55',
                 value = '-((ee**2*complex(0,1))/sw**2)',
                 order = {'QED':2})

GC_56 = Coupling(name = 'GC_56',
                 value = '(cw**2*ee**2*complex(0,1))/sw**2',
                 order = {'QED':2})

GC_57 = Coupling(name = 'GC_57',
                 value = '(ee**2*FgT0*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':2})

GC_58 = Coupling(name = 'GC_58',
                 value = '-((cw**2*ee**2*FgT0*complex(0,1))/sw**2)',
                 order = {'NP':1,'QED':2})

GC_59 = Coupling(name = 'GC_59',
                 value = '(ee**2*FgT2*complex(0,1))/(4.*sw**2)',
                 order = {'NP':1,'QED':2})

GC_60 = Coupling(name = 'GC_60',
                 value = '-0.25*(cw**2*ee**2*FgT2*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':2})

GC_61 = Coupling(name = 'GC_61',
                 value = '(ee**2*FgT0*G)/sw**2',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_62 = Coupling(name = 'GC_62',
                 value = '-((cw**2*ee**2*FgT0*G)/sw**2)',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_63 = Coupling(name = 'GC_63',
                 value = '-0.25*(ee**2*FgT2*G)/sw**2',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_64 = Coupling(name = 'GC_64',
                 value = '(cw**2*ee**2*FgT2*G)/(4.*sw**2)',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_65 = Coupling(name = 'GC_65',
                 value = '-((ee**2*FgT0*complex(0,1)*G**2)/sw**2)',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_66 = Coupling(name = 'GC_66',
                 value = '(cw**2*ee**2*FgT0*complex(0,1)*G**2)/sw**2',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_67 = Coupling(name = 'GC_67',
                 value = '-0.25*(ee**2*FgT2*complex(0,1)*G**2)/sw**2',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_68 = Coupling(name = 'GC_68',
                 value = '(cw**2*ee**2*FgT2*complex(0,1)*G**2)/(4.*sw**2)',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_69 = Coupling(name = 'GC_69',
                 value = '(ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_70 = Coupling(name = 'GC_70',
                 value = '(CKM1x1*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_71 = Coupling(name = 'GC_71',
                 value = '(CKM1x2*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_72 = Coupling(name = 'GC_72',
                 value = '(CKM2x1*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_73 = Coupling(name = 'GC_73',
                 value = '(CKM2x2*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_74 = Coupling(name = 'GC_74',
                 value = '-0.5*(cw*ee*complex(0,1))/sw',
                 order = {'QED':1})

GC_75 = Coupling(name = 'GC_75',
                 value = '(cw*ee*complex(0,1))/(2.*sw)',
                 order = {'QED':1})

GC_76 = Coupling(name = 'GC_76',
                 value = '(cw*ee*complex(0,1))/sw',
                 order = {'QED':1})

GC_77 = Coupling(name = 'GC_77',
                 value = '(-2*cw*ee**2*complex(0,1))/sw',
                 order = {'QED':2})

GC_78 = Coupling(name = 'GC_78',
                 value = '-((cw*ee*FgT0*complex(0,1))/sw)',
                 order = {'NP':1,'QED':1})

GC_79 = Coupling(name = 'GC_79',
                 value = '(2*cw*ee**2*FgT0*complex(0,1))/sw',
                 order = {'NP':1,'QED':2})

GC_80 = Coupling(name = 'GC_80',
                 value = '(cw*ee*FgT1*complex(0,1))/(2.*sw)',
                 order = {'NP':1,'QED':1})

GC_81 = Coupling(name = 'GC_81',
                 value = '-0.125*(cw*ee*FgT2*complex(0,1))/sw',
                 order = {'NP':1,'QED':1})

GC_82 = Coupling(name = 'GC_82',
                 value = '(cw*ee**2*FgT2*complex(0,1))/(8.*sw)',
                 order = {'NP':1,'QED':2})

GC_83 = Coupling(name = 'GC_83',
                 value = '-0.25*(cw*ee*FgT3*complex(0,1))/sw',
                 order = {'NP':1,'QED':1})

GC_84 = Coupling(name = 'GC_84',
                 value = '-((cw*ee*FgT0*G)/sw)',
                 order = {'NP':1,'QCD':1,'QED':1})

GC_85 = Coupling(name = 'GC_85',
                 value = '(2*cw*ee**2*FgT0*G)/sw',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_86 = Coupling(name = 'GC_86',
                 value = '-0.5*(cw*ee*FgT1*G)/sw',
                 order = {'NP':1,'QCD':1,'QED':1})

GC_87 = Coupling(name = 'GC_87',
                 value = '(cw*ee*FgT2*G)/(8.*sw)',
                 order = {'NP':1,'QCD':1,'QED':1})

GC_88 = Coupling(name = 'GC_88',
                 value = '-0.125*(cw*ee**2*FgT2*G)/sw',
                 order = {'NP':1,'QCD':1,'QED':2})

GC_89 = Coupling(name = 'GC_89',
                 value = '(cw*ee*FgT3*G)/(4.*sw)',
                 order = {'NP':1,'QCD':1,'QED':1})

GC_90 = Coupling(name = 'GC_90',
                 value = '(cw*ee*FgT0*complex(0,1)*G**2)/sw',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_91 = Coupling(name = 'GC_91',
                 value = '(-2*cw*ee**2*FgT0*complex(0,1)*G**2)/sw',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_92 = Coupling(name = 'GC_92',
                 value = '-0.5*(cw*ee*FgT1*complex(0,1)*G**2)/sw',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_93 = Coupling(name = 'GC_93',
                 value = '(cw*ee*FgT1*complex(0,1)*G**2)/(2.*sw)',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_94 = Coupling(name = 'GC_94',
                 value = '-0.125*(cw*ee*FgT2*complex(0,1)*G**2)/sw',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_95 = Coupling(name = 'GC_95',
                 value = '(cw*ee**2*FgT2*complex(0,1)*G**2)/(4.*sw)',
                 order = {'NP':1,'QCD':2,'QED':2})

GC_96 = Coupling(name = 'GC_96',
                 value = '-0.25*(cw*ee*FgT3*complex(0,1)*G**2)/sw',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_97 = Coupling(name = 'GC_97',
                 value = '(cw*ee*FgT3*complex(0,1)*G**2)/(4.*sw)',
                 order = {'NP':1,'QCD':2,'QED':1})

GC_98 = Coupling(name = 'GC_98',
                 value = '-0.16666666666666666*(ee*complex(0,1)*sw)/cw',
                 order = {'QED':1})

GC_99 = Coupling(name = 'GC_99',
                 value = '(ee*complex(0,1)*sw)/(3.*cw)',
                 order = {'QED':1})

GC_100 = Coupling(name = 'GC_100',
                  value = '(ee*complex(0,1)*sw)/(2.*cw)',
                  order = {'QED':1})

GC_101 = Coupling(name = 'GC_101',
                  value = '(ee*complex(0,1)*sw)/cw',
                  order = {'QED':1})

GC_102 = Coupling(name = 'GC_102',
                  value = '-0.5*(cw*ee*complex(0,1))/sw - (ee*complex(0,1)*sw)/(6.*cw)',
                  order = {'QED':1})

GC_103 = Coupling(name = 'GC_103',
                  value = '-0.5*(cw*ee*complex(0,1))/sw + (ee*complex(0,1)*sw)/(2.*cw)',
                  order = {'QED':1})

GC_104 = Coupling(name = 'GC_104',
                  value = '(cw*ee*complex(0,1))/(2.*sw) + (ee*complex(0,1)*sw)/(2.*cw)',
                  order = {'QED':1})

GC_105 = Coupling(name = 'GC_105',
                  value = 'cw*FgT0*complex(0,1)*sw - cw*FgT4*complex(0,1)*sw',
                  order = {'NP':1})

GC_106 = Coupling(name = 'GC_106',
                  value = '(cw*FgT1*complex(0,1)*sw)/2. - (cw*FgT5*complex(0,1)*sw)/2.',
                  order = {'NP':1})

GC_107 = Coupling(name = 'GC_107',
                  value = '(cw*FgT2*complex(0,1)*sw)/8. - (cw*FgT6*complex(0,1)*sw)/8.',
                  order = {'NP':1})

GC_108 = Coupling(name = 'GC_108',
                  value = '(cw*FgT3*complex(0,1)*sw)/4. - (cw*FgT7*complex(0,1)*sw)/4.',
                  order = {'NP':1})

GC_109 = Coupling(name = 'GC_109',
                  value = 'cw*FgT0*G*sw - cw*FgT4*G*sw',
                  order = {'NP':1,'QCD':1})

GC_110 = Coupling(name = 'GC_110',
                  value = '-0.5*(cw*FgT1*G*sw) + (cw*FgT5*G*sw)/2.',
                  order = {'NP':1,'QCD':1})

GC_111 = Coupling(name = 'GC_111',
                  value = '(cw*FgT2*G*sw)/8. - (cw*FgT6*G*sw)/8.',
                  order = {'NP':1,'QCD':1})

GC_112 = Coupling(name = 'GC_112',
                  value = '(cw*FgT3*G*sw)/4. - (cw*FgT7*G*sw)/4.',
                  order = {'NP':1,'QCD':1})

GC_113 = Coupling(name = 'GC_113',
                  value = '-(cw*FgT0*complex(0,1)*G**2*sw) + cw*FgT4*complex(0,1)*G**2*sw',
                  order = {'NP':1,'QCD':2})

GC_114 = Coupling(name = 'GC_114',
                  value = '-0.5*(cw*FgT1*complex(0,1)*G**2*sw) + (cw*FgT5*complex(0,1)*G**2*sw)/2.',
                  order = {'NP':1,'QCD':2})

GC_115 = Coupling(name = 'GC_115',
                  value = '(cw*FgT2*complex(0,1)*G**2*sw)/8. - (cw*FgT6*complex(0,1)*G**2*sw)/8.',
                  order = {'NP':1,'QCD':2})

GC_116 = Coupling(name = 'GC_116',
                  value = '-0.25*(cw*FgT3*complex(0,1)*G**2*sw) + (cw*FgT7*complex(0,1)*G**2*sw)/4.',
                  order = {'NP':1,'QCD':2})

GC_117 = Coupling(name = 'GC_117',
                  value = 'ee**2*complex(0,1) + (cw**2*ee**2*complex(0,1))/(2.*sw**2) + (ee**2*complex(0,1)*sw**2)/(2.*cw**2)',
                  order = {'QED':2})

GC_118 = Coupling(name = 'GC_118',
                  value = 'cw**2*FgT4*complex(0,1) + FgT0*complex(0,1)*sw**2',
                  order = {'NP':1})

GC_119 = Coupling(name = 'GC_119',
                  value = '(cw**2*FgT5*complex(0,1))/2. + (FgT1*complex(0,1)*sw**2)/2.',
                  order = {'NP':1})

GC_120 = Coupling(name = 'GC_120',
                  value = '(cw**2*FgT6*complex(0,1))/8. + (FgT2*complex(0,1)*sw**2)/8.',
                  order = {'NP':1})

GC_121 = Coupling(name = 'GC_121',
                  value = '(cw**2*FgT7*complex(0,1))/4. + (FgT3*complex(0,1)*sw**2)/4.',
                  order = {'NP':1})

GC_122 = Coupling(name = 'GC_122',
                  value = 'cw**2*FgT0*complex(0,1) + FgT4*complex(0,1)*sw**2',
                  order = {'NP':1})

GC_123 = Coupling(name = 'GC_123',
                  value = '(cw**2*FgT1*complex(0,1))/2. + (FgT5*complex(0,1)*sw**2)/2.',
                  order = {'NP':1})

GC_124 = Coupling(name = 'GC_124',
                  value = '(cw**2*FgT2*complex(0,1))/8. + (FgT6*complex(0,1)*sw**2)/8.',
                  order = {'NP':1})

GC_125 = Coupling(name = 'GC_125',
                  value = '(cw**2*FgT3*complex(0,1))/4. + (FgT7*complex(0,1)*sw**2)/4.',
                  order = {'NP':1})

GC_126 = Coupling(name = 'GC_126',
                  value = 'cw**2*FgT4*G + FgT0*G*sw**2',
                  order = {'NP':1,'QCD':1})

GC_127 = Coupling(name = 'GC_127',
                  value = '-0.5*(cw**2*FgT5*G) - (FgT1*G*sw**2)/2.',
                  order = {'NP':1,'QCD':1})

GC_128 = Coupling(name = 'GC_128',
                  value = '(cw**2*FgT6*G)/8. + (FgT2*G*sw**2)/8.',
                  order = {'NP':1,'QCD':1})

GC_129 = Coupling(name = 'GC_129',
                  value = '(cw**2*FgT7*G)/4. + (FgT3*G*sw**2)/4.',
                  order = {'NP':1,'QCD':1})

GC_130 = Coupling(name = 'GC_130',
                  value = 'cw**2*FgT0*G + FgT4*G*sw**2',
                  order = {'NP':1,'QCD':1})

GC_131 = Coupling(name = 'GC_131',
                  value = '-0.5*(cw**2*FgT1*G) - (FgT5*G*sw**2)/2.',
                  order = {'NP':1,'QCD':1})

GC_132 = Coupling(name = 'GC_132',
                  value = '(cw**2*FgT2*G)/8. + (FgT6*G*sw**2)/8.',
                  order = {'NP':1,'QCD':1})

GC_133 = Coupling(name = 'GC_133',
                  value = '(cw**2*FgT3*G)/4. + (FgT7*G*sw**2)/4.',
                  order = {'NP':1,'QCD':1})

GC_134 = Coupling(name = 'GC_134',
                  value = '-(cw**2*FgT4*complex(0,1)*G**2) - FgT0*complex(0,1)*G**2*sw**2',
                  order = {'NP':1,'QCD':2})

GC_135 = Coupling(name = 'GC_135',
                  value = '-0.5*(cw**2*FgT5*complex(0,1)*G**2) - (FgT1*complex(0,1)*G**2*sw**2)/2.',
                  order = {'NP':1,'QCD':2})

GC_136 = Coupling(name = 'GC_136',
                  value = '-0.125*(cw**2*FgT6*complex(0,1)*G**2) - (FgT2*complex(0,1)*G**2*sw**2)/8.',
                  order = {'NP':1,'QCD':2})

GC_137 = Coupling(name = 'GC_137',
                  value = '-0.25*(cw**2*FgT7*complex(0,1)*G**2) - (FgT3*complex(0,1)*G**2*sw**2)/4.',
                  order = {'NP':1,'QCD':2})

GC_138 = Coupling(name = 'GC_138',
                  value = '-(cw**2*FgT0*complex(0,1)*G**2) - FgT4*complex(0,1)*G**2*sw**2',
                  order = {'NP':1,'QCD':2})

GC_139 = Coupling(name = 'GC_139',
                  value = '-0.5*(cw**2*FgT1*complex(0,1)*G**2) - (FgT5*complex(0,1)*G**2*sw**2)/2.',
                  order = {'NP':1,'QCD':2})

GC_140 = Coupling(name = 'GC_140',
                  value = '-0.125*(cw**2*FgT2*complex(0,1)*G**2) - (FgT6*complex(0,1)*G**2*sw**2)/8.',
                  order = {'NP':1,'QCD':2})

GC_141 = Coupling(name = 'GC_141',
                  value = '-0.25*(cw**2*FgT3*complex(0,1)*G**2) - (FgT7*complex(0,1)*G**2*sw**2)/4.',
                  order = {'NP':1,'QCD':2})

GC_142 = Coupling(name = 'GC_142',
                  value = '-6*complex(0,1)*lam*vev',
                  order = {'QED':1})

GC_143 = Coupling(name = 'GC_143',
                  value = '(ee**2*complex(0,1)*vev)/(2.*sw**2)',
                  order = {'QED':1})

GC_144 = Coupling(name = 'GC_144',
                  value = 'ee**2*complex(0,1)*vev + (cw**2*ee**2*complex(0,1)*vev)/(2.*sw**2) + (ee**2*complex(0,1)*sw**2*vev)/(2.*cw**2)',
                  order = {'QED':1})

GC_145 = Coupling(name = 'GC_145',
                  value = '-((complex(0,1)*yb)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_146 = Coupling(name = 'GC_146',
                  value = '-((complex(0,1)*yt)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_147 = Coupling(name = 'GC_147',
                  value = '-((complex(0,1)*ytau)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_148 = Coupling(name = 'GC_148',
                  value = '(ee*complex(0,1)*complexconjugate(CKM1x1))/(sw*cmath.sqrt(2))',
                  order = {'QED':1})

GC_149 = Coupling(name = 'GC_149',
                  value = '(ee*complex(0,1)*complexconjugate(CKM1x2))/(sw*cmath.sqrt(2))',
                  order = {'QED':1})

GC_150 = Coupling(name = 'GC_150',
                  value = '(ee*complex(0,1)*complexconjugate(CKM2x1))/(sw*cmath.sqrt(2))',
                  order = {'QED':1})

GC_151 = Coupling(name = 'GC_151',
                  value = '(ee*complex(0,1)*complexconjugate(CKM2x2))/(sw*cmath.sqrt(2))',
                  order = {'QED':1})

