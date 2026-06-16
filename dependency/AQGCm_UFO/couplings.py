# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 13.1.0 for Microsoft Windows (64-bit) (June 16, 2022)
# Date: Mon 15 May 2023 18:54:25


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
                value = '-2*FM0*complex(0,1)',
                order = {'NP':1})

GC_7 = Coupling(name = 'GC_7',
                value = '2*ee*FM0*complex(0,1)',
                order = {'NP':1,'QED':1})

GC_8 = Coupling(name = 'GC_8',
                value = 'ee**2*FM0*complex(0,1)',
                order = {'NP':1,'QED':2})

GC_9 = Coupling(name = 'GC_9',
                value = '-0.5*(ee*FM1*complex(0,1))',
                order = {'NP':1,'QED':1})

GC_10 = Coupling(name = 'GC_10',
                 value = '(ee**2*FM1*complex(0,1))/4.',
                 order = {'NP':1,'QED':2})

GC_11 = Coupling(name = 'GC_11',
                 value = '2*ee**2*FM2*complex(0,1)',
                 order = {'NP':1,'QED':2})

GC_12 = Coupling(name = 'GC_12',
                 value = '-0.5*(ee**2*FM3*complex(0,1))',
                 order = {'NP':1,'QED':2})

GC_13 = Coupling(name = 'GC_13',
                 value = '-0.5*(ee*FM4*complex(0,1))',
                 order = {'NP':1,'QED':1})

GC_14 = Coupling(name = 'GC_14',
                 value = '-0.5*(ee**2*FM4*complex(0,1))',
                 order = {'NP':1,'QED':2})

GC_15 = Coupling(name = 'GC_15',
                 value = '(ee*FM5*complex(0,1))/4.',
                 order = {'NP':1,'QED':1})

GC_16 = Coupling(name = 'GC_16',
                 value = '(ee**2*FM5*complex(0,1))/4.',
                 order = {'NP':1,'QED':2})

GC_17 = Coupling(name = 'GC_17',
                 value = '-0.5*(ee**3*FM4*complex(0,1)) + (ee**3*FM5*complex(0,1))/2.',
                 order = {'NP':1,'QED':3})

GC_18 = Coupling(name = 'GC_18',
                 value = '-0.5*(FM1*complex(0,1)) + (FM7*complex(0,1))/4.',
                 order = {'NP':1})

GC_19 = Coupling(name = 'GC_19',
                 value = '-0.125*(ee*FM7*complex(0,1))',
                 order = {'NP':1,'QED':1})

GC_20 = Coupling(name = 'GC_20',
                 value = '-0.125*(ee**2*FM7*complex(0,1))',
                 order = {'NP':1,'QED':2})

GC_21 = Coupling(name = 'GC_21',
                 value = '-0.25*(ee**2*FM7*complex(0,1))',
                 order = {'NP':1,'QED':2})

GC_22 = Coupling(name = 'GC_22',
                 value = '-0.25*(ee**3*FM7*complex(0,1))',
                 order = {'NP':1,'QED':3})

GC_23 = Coupling(name = 'GC_23',
                 value = '-G',
                 order = {'QCD':1})

GC_24 = Coupling(name = 'GC_24',
                 value = 'complex(0,1)*G',
                 order = {'QCD':1})

GC_25 = Coupling(name = 'GC_25',
                 value = 'complex(0,1)*G**2',
                 order = {'QCD':2})

GC_26 = Coupling(name = 'GC_26',
                 value = '-6*complex(0,1)*lam',
                 order = {'QED':2})

GC_27 = Coupling(name = 'GC_27',
                 value = '(3*ee**4*FM0*complex(0,1))/sw**4 - (3*ee**4*FM1*complex(0,1))/(2.*sw**4) + (3*ee**4*FM7*complex(0,1))/(4.*sw**4)',
                 order = {'NP':1,'QED':4})

GC_28 = Coupling(name = 'GC_28',
                 value = '-0.5*(cw*ee**3*FM4*complex(0,1))/sw**3 - (cw*ee**3*FM5*complex(0,1))/(2.*sw**3)',
                 order = {'NP':1,'QED':3})

GC_29 = Coupling(name = 'GC_29',
                 value = '(ee**4*FM0*complex(0,1))/cw**2 + (2*ee**4*FM0*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':4})

GC_30 = Coupling(name = 'GC_30',
                 value = '(ee**4*FM1*complex(0,1))/(2.*cw**2) - (ee**4*FM7*complex(0,1))/(4.*cw**2) + (ee**4*FM1*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':4})

GC_31 = Coupling(name = 'GC_31',
                 value = '-0.5*(ee**3*FM4*complex(0,1)) - (cw**2*ee**3*FM4*complex(0,1))/(2.*sw**2)',
                 order = {'NP':1,'QED':3})

GC_32 = Coupling(name = 'GC_32',
                 value = '(ee**3*FM4*complex(0,1))/(2.*sw**2) + (ee**3*FM5*complex(0,1))/(2.*sw**2)',
                 order = {'NP':1,'QED':3})

GC_33 = Coupling(name = 'GC_33',
                 value = '(ee**3*FM5*complex(0,1))/4. + (cw**2*ee**3*FM5*complex(0,1))/(4.*sw**2)',
                 order = {'NP':1,'QED':3})

GC_34 = Coupling(name = 'GC_34',
                 value = '-(ee**4*FM0*complex(0,1)) + (ee**4*FM1*complex(0,1))/2. - (ee**4*FM7*complex(0,1))/4. - (cw**4*ee**4*FM0*complex(0,1))/sw**4 + (cw**4*ee**4*FM1*complex(0,1))/(2.*sw**4) - (cw**4*ee**4*FM7*complex(0,1))/(4.*sw**4) - (2*cw**2*ee**4*FM0*complex(0,1))/sw**2 + (cw**2*ee**4*FM1*complex(0,1))/sw**2 - (cw**2*ee**4*FM7*complex(0,1))/(2.*sw**2)',
                 order = {'NP':1,'QED':4})

GC_35 = Coupling(name = 'GC_35',
                 value = '-((cw**2*ee**4*FM0*complex(0,1))/sw**4)',
                 order = {'NP':1,'QED':4})

GC_36 = Coupling(name = 'GC_36',
                 value = '(3*cw**2*ee**4*FM1*complex(0,1))/(2.*sw**4)',
                 order = {'NP':1,'QED':4})

GC_37 = Coupling(name = 'GC_37',
                 value = '(-9*cw**2*ee**4*FM7*complex(0,1))/(4.*sw**4)',
                 order = {'NP':1,'QED':4})

GC_38 = Coupling(name = 'GC_38',
                 value = '-((cw*ee**3*FM0*complex(0,1))/sw**3)',
                 order = {'NP':1,'QED':3})

GC_39 = Coupling(name = 'GC_39',
                 value = '(4*cw*ee**4*FM0*complex(0,1))/sw**3',
                 order = {'NP':1,'QED':4})

GC_40 = Coupling(name = 'GC_40',
                 value = '(cw*ee**3*FM1*complex(0,1))/(4.*sw**3)',
                 order = {'NP':1,'QED':3})

GC_41 = Coupling(name = 'GC_41',
                 value = '-((cw*ee**4*FM1*complex(0,1))/sw**3)',
                 order = {'NP':1,'QED':4})

GC_42 = Coupling(name = 'GC_42',
                 value = '(cw**3*ee**3*FM4*complex(0,1))/(2.*sw**3)',
                 order = {'NP':1,'QED':3})

GC_43 = Coupling(name = 'GC_43',
                 value = '-0.25*(cw**3*ee**3*FM5*complex(0,1))/sw**3',
                 order = {'NP':1,'QED':3})

GC_44 = Coupling(name = 'GC_44',
                 value = '(cw*ee**3*FM7*complex(0,1))/(8.*sw**3)',
                 order = {'NP':1,'QED':3})

GC_45 = Coupling(name = 'GC_45',
                 value = '(3*cw**3*ee**3*FM7*complex(0,1))/(8.*sw**3)',
                 order = {'NP':1,'QED':3})

GC_46 = Coupling(name = 'GC_46',
                 value = '-0.5*(cw*ee**4*FM7*complex(0,1))/sw**3',
                 order = {'NP':1,'QED':4})

GC_47 = Coupling(name = 'GC_47',
                 value = '(ee**2*complex(0,1))/(2.*sw**2)',
                 order = {'QED':2})

GC_48 = Coupling(name = 'GC_48',
                 value = '-((ee**2*complex(0,1))/sw**2)',
                 order = {'QED':2})

GC_49 = Coupling(name = 'GC_49',
                 value = '(cw**2*ee**2*complex(0,1))/sw**2',
                 order = {'QED':2})

GC_50 = Coupling(name = 'GC_50',
                 value = '(ee**2*FM0*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':2})

GC_51 = Coupling(name = 'GC_51',
                 value = '(cw**2*ee**2*FM0*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':2})

GC_52 = Coupling(name = 'GC_52',
                 value = '-((ee**3*FM0*complex(0,1))/sw**2)',
                 order = {'NP':1,'QED':3})

GC_53 = Coupling(name = 'GC_53',
                 value = '-((ee**4*FM0*complex(0,1))/sw**2)',
                 order = {'NP':1,'QED':4})

GC_54 = Coupling(name = 'GC_54',
                 value = '-0.25*(ee**2*FM1*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':2})

GC_55 = Coupling(name = 'GC_55',
                 value = '(cw**2*ee**2*FM1*complex(0,1))/(4.*sw**2)',
                 order = {'NP':1,'QED':2})

GC_56 = Coupling(name = 'GC_56',
                 value = '-0.25*(ee**3*FM1*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':3})

GC_57 = Coupling(name = 'GC_57',
                 value = '(ee**4*FM1*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':4})

GC_58 = Coupling(name = 'GC_58',
                 value = '(2*cw**2*ee**2*FM2*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':2})

GC_59 = Coupling(name = 'GC_59',
                 value = '(cw**2*ee**2*FM3*complex(0,1))/(2.*sw**2)',
                 order = {'NP':1,'QED':2})

GC_60 = Coupling(name = 'GC_60',
                 value = '-0.5*(cw**2*ee**2*FM4*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':2})

GC_61 = Coupling(name = 'GC_61',
                 value = '-0.5*(cw**2*ee**3*FM4*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':3})

GC_62 = Coupling(name = 'GC_62',
                 value = '(cw**2*ee**2*FM5*complex(0,1))/(4.*sw**2)',
                 order = {'NP':1,'QED':2})

GC_63 = Coupling(name = 'GC_63',
                 value = '(cw**2*ee**3*FM5*complex(0,1))/(4.*sw**2)',
                 order = {'NP':1,'QED':3})

GC_64 = Coupling(name = 'GC_64',
                 value = '(ee**2*FM7*complex(0,1))/(4.*sw**2)',
                 order = {'NP':1,'QED':2})

GC_65 = Coupling(name = 'GC_65',
                 value = '-0.125*(cw**2*ee**2*FM7*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':2})

GC_66 = Coupling(name = 'GC_66',
                 value = '(ee**3*FM7*complex(0,1))/(4.*sw**2)',
                 order = {'NP':1,'QED':3})

GC_67 = Coupling(name = 'GC_67',
                 value = '-0.125*(cw**2*ee**3*FM7*complex(0,1))/sw**2',
                 order = {'NP':1,'QED':3})

GC_68 = Coupling(name = 'GC_68',
                 value = '-((ee**4*FM7*complex(0,1))/sw**2)',
                 order = {'NP':1,'QED':4})

GC_69 = Coupling(name = 'GC_69',
                 value = '(-3*ee**4*FM7*complex(0,1))/(2.*sw**2)',
                 order = {'NP':1,'QED':4})

GC_70 = Coupling(name = 'GC_70',
                 value = '(ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_71 = Coupling(name = 'GC_71',
                 value = '-0.5*(cw*ee*complex(0,1))/sw',
                 order = {'QED':1})

GC_72 = Coupling(name = 'GC_72',
                 value = '(cw*ee*complex(0,1))/(2.*sw)',
                 order = {'QED':1})

GC_73 = Coupling(name = 'GC_73',
                 value = '(cw*ee*complex(0,1))/sw',
                 order = {'QED':1})

GC_74 = Coupling(name = 'GC_74',
                 value = '(-2*cw*ee**2*complex(0,1))/sw',
                 order = {'QED':2})

GC_75 = Coupling(name = 'GC_75',
                 value = '(2*cw*ee*FM0*complex(0,1))/sw',
                 order = {'NP':1,'QED':1})

GC_76 = Coupling(name = 'GC_76',
                 value = '(cw*ee**2*FM0*complex(0,1))/sw',
                 order = {'NP':1,'QED':2})

GC_77 = Coupling(name = 'GC_77',
                 value = '-0.5*(cw*ee*FM1*complex(0,1))/sw',
                 order = {'NP':1,'QED':1})

GC_78 = Coupling(name = 'GC_78',
                 value = '-0.25*(cw*ee**2*FM1*complex(0,1))/sw',
                 order = {'NP':1,'QED':2})

GC_79 = Coupling(name = 'GC_79',
                 value = '(-2*cw*ee**2*FM2*complex(0,1))/sw',
                 order = {'NP':1,'QED':2})

GC_80 = Coupling(name = 'GC_80',
                 value = '(cw*ee**2*FM3*complex(0,1))/(2.*sw)',
                 order = {'NP':1,'QED':2})

GC_81 = Coupling(name = 'GC_81',
                 value = '(cw*ee*FM4*complex(0,1))/(2.*sw)',
                 order = {'NP':1,'QED':1})

GC_82 = Coupling(name = 'GC_82',
                 value = '(cw*ee**2*FM4*complex(0,1))/(2.*sw)',
                 order = {'NP':1,'QED':2})

GC_83 = Coupling(name = 'GC_83',
                 value = '-((cw*ee**2*FM4*complex(0,1))/sw)',
                 order = {'NP':1,'QED':2})

GC_84 = Coupling(name = 'GC_84',
                 value = '(cw*ee**3*FM4*complex(0,1))/(2.*sw)',
                 order = {'NP':1,'QED':3})

GC_85 = Coupling(name = 'GC_85',
                 value = '-0.25*(cw*ee*FM5*complex(0,1))/sw',
                 order = {'NP':1,'QED':1})

GC_86 = Coupling(name = 'GC_86',
                 value = '(cw*ee**2*FM5*complex(0,1))/(4.*sw)',
                 order = {'NP':1,'QED':2})

GC_87 = Coupling(name = 'GC_87',
                 value = '-0.5*(cw*ee**2*FM5*complex(0,1))/sw',
                 order = {'NP':1,'QED':2})

GC_88 = Coupling(name = 'GC_88',
                 value = '-0.5*(cw*ee**3*FM5*complex(0,1))/sw',
                 order = {'NP':1,'QED':3})

GC_89 = Coupling(name = 'GC_89',
                 value = '-0.125*(cw*ee*FM7*complex(0,1))/sw',
                 order = {'NP':1,'QED':1})

GC_90 = Coupling(name = 'GC_90',
                 value = '(cw*ee**2*FM7*complex(0,1))/(8.*sw)',
                 order = {'NP':1,'QED':2})

GC_91 = Coupling(name = 'GC_91',
                 value = '(ee**3*FM7*complex(0,1))/(8.*cw*sw)',
                 order = {'NP':1,'QED':3})

GC_92 = Coupling(name = 'GC_92',
                 value = '(cw*ee**3*FM7*complex(0,1))/(2.*sw)',
                 order = {'NP':1,'QED':3})

GC_93 = Coupling(name = 'GC_93',
                 value = '-0.5*(ee**4*FM7*complex(0,1))/(cw*sw)',
                 order = {'NP':1,'QED':4})

GC_94 = Coupling(name = 'GC_94',
                 value = '-0.16666666666666666*(ee*complex(0,1)*sw)/cw',
                 order = {'QED':1})

GC_95 = Coupling(name = 'GC_95',
                 value = '(ee*complex(0,1)*sw)/(2.*cw)',
                 order = {'QED':1})

GC_96 = Coupling(name = 'GC_96',
                 value = '(ee**2*FM4*complex(0,1)*sw)/(2.*cw)',
                 order = {'NP':1,'QED':2})

GC_97 = Coupling(name = 'GC_97',
                 value = '(ee**3*FM4*complex(0,1)*sw)/(2.*cw)',
                 order = {'NP':1,'QED':3})

GC_98 = Coupling(name = 'GC_98',
                 value = '(ee**2*FM5*complex(0,1)*sw)/(4.*cw)',
                 order = {'NP':1,'QED':2})

GC_99 = Coupling(name = 'GC_99',
                 value = '-0.25*(ee**3*FM5*complex(0,1)*sw)/cw',
                 order = {'NP':1,'QED':3})

GC_100 = Coupling(name = 'GC_100',
                  value = '-0.125*(ee*FM7*complex(0,1)*sw)/cw',
                  order = {'NP':1,'QED':1})

GC_101 = Coupling(name = 'GC_101',
                  value = '(ee**2*FM7*complex(0,1)*sw)/(8.*cw)',
                  order = {'NP':1,'QED':2})

GC_102 = Coupling(name = 'GC_102',
                  value = '-0.5*(ee**3*FM4*complex(0,1)*sw**2)/cw**2',
                  order = {'NP':1,'QED':3})

GC_103 = Coupling(name = 'GC_103',
                  value = '(ee**3*FM5*complex(0,1)*sw**2)/(4.*cw**2)',
                  order = {'NP':1,'QED':3})

GC_104 = Coupling(name = 'GC_104',
                  value = '(cw*ee*complex(0,1))/(2.*sw) + (ee*complex(0,1)*sw)/(2.*cw)',
                  order = {'QED':1})

GC_105 = Coupling(name = 'GC_105',
                  value = '-((cw**3*ee**3*FM0*complex(0,1))/sw**3) - (2*cw*ee**3*FM0*complex(0,1))/sw - (ee**3*FM0*complex(0,1)*sw)/cw',
                  order = {'NP':1,'QED':3})

GC_106 = Coupling(name = 'GC_106',
                  value = '(cw*ee**3*FM7*complex(0,1))/(8.*sw) + (ee**3*FM7*complex(0,1)*sw)/(8.*cw)',
                  order = {'NP':1,'QED':3})

GC_107 = Coupling(name = 'GC_107',
                  value = '-0.25*(cw**3*ee**3*FM1*complex(0,1))/sw**3 - (cw*ee**3*FM1*complex(0,1))/(2.*sw) - (ee**3*FM1*complex(0,1)*sw)/(4.*cw) + (ee**3*FM7*complex(0,1)*sw)/(8.*cw)',
                  order = {'NP':1,'QED':3})

GC_108 = Coupling(name = 'GC_108',
                  value = '(2*cw**3*ee**4*FM0*complex(0,1))/sw**3 - (cw**3*ee**4*FM1*complex(0,1))/sw**3 + (cw**3*ee**4*FM7*complex(0,1))/(2.*sw**3) + (4*cw*ee**4*FM0*complex(0,1))/sw - (2*cw*ee**4*FM1*complex(0,1))/sw + (cw*ee**4*FM7*complex(0,1))/sw + (2*ee**4*FM0*complex(0,1)*sw)/cw - (ee**4*FM1*complex(0,1)*sw)/cw + (ee**4*FM7*complex(0,1)*sw)/(2.*cw)',
                  order = {'NP':1,'QED':4})

GC_109 = Coupling(name = 'GC_109',
                  value = 'ee**2*complex(0,1) + (cw**2*ee**2*complex(0,1))/(2.*sw**2) + (ee**2*complex(0,1)*sw**2)/(2.*cw**2)',
                  order = {'QED':2})

GC_110 = Coupling(name = 'GC_110',
                  value = '-4*cw**2*FM2*complex(0,1) + 2*cw*FM4*complex(0,1)*sw - 2*FM0*complex(0,1)*sw**2',
                  order = {'NP':1})

GC_111 = Coupling(name = 'GC_111',
                  value = '2*ee**2*FM0*complex(0,1) + (ee**2*FM0*complex(0,1)*sw**2)/cw**2',
                  order = {'NP':1,'QED':2})

GC_112 = Coupling(name = 'GC_112',
                  value = '-2*ee**3*FM0*complex(0,1) - (cw**2*ee**3*FM0*complex(0,1))/sw**2 - (ee**3*FM0*complex(0,1)*sw**2)/cw**2',
                  order = {'NP':1,'QED':3})

GC_113 = Coupling(name = 'GC_113',
                  value = '-2*ee**4*FM0*complex(0,1) - (cw**2*ee**4*FM0*complex(0,1))/sw**2 - (ee**4*FM0*complex(0,1)*sw**2)/cw**2',
                  order = {'NP':1,'QED':4})

GC_114 = Coupling(name = 'GC_114',
                  value = '-2*cw**2*FM0*complex(0,1) - 2*cw*FM4*complex(0,1)*sw - 4*FM2*complex(0,1)*sw**2',
                  order = {'NP':1})

GC_115 = Coupling(name = 'GC_115',
                  value = '-0.5*(cw**2*FM1*complex(0,1)) + (cw**2*FM7*complex(0,1))/4. + cw*FM5*complex(0,1)*sw - FM3*complex(0,1)*sw**2',
                  order = {'NP':1})

GC_116 = Coupling(name = 'GC_116',
                  value = 'cw**2*FM4*complex(0,1) - 2*cw*FM0*complex(0,1)*sw + 4*cw*FM2*complex(0,1)*sw - FM4*complex(0,1)*sw**2',
                  order = {'NP':1})

GC_117 = Coupling(name = 'GC_117',
                  value = '-0.5*(cw**2*FM5*complex(0,1)) - (cw*FM1*complex(0,1)*sw)/2. + cw*FM3*complex(0,1)*sw + (cw*FM7*complex(0,1)*sw)/4. + (FM5*complex(0,1)*sw**2)/2.',
                  order = {'NP':1})

GC_118 = Coupling(name = 'GC_118',
                  value = '-(cw**2*FM3*complex(0,1)) - cw*FM5*complex(0,1)*sw - (FM1*complex(0,1)*sw**2)/2. + (FM7*complex(0,1)*sw**2)/4.',
                  order = {'NP':1})

GC_119 = Coupling(name = 'GC_119',
                  value = '(ee**2*FM1*complex(0,1))/2. + (ee**2*FM1*complex(0,1)*sw**2)/(4.*cw**2) - (ee**2*FM7*complex(0,1)*sw**2)/(8.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_120 = Coupling(name = 'GC_120',
                  value = '(ee**3*FM1*complex(0,1))/2. + (cw**2*ee**3*FM1*complex(0,1))/(4.*sw**2) + (ee**3*FM1*complex(0,1)*sw**2)/(4.*cw**2) - (ee**3*FM7*complex(0,1)*sw**2)/(8.*cw**2)',
                  order = {'NP':1,'QED':3})

GC_121 = Coupling(name = 'GC_121',
                  value = '-(ee**4*FM1*complex(0,1)) + (ee**4*FM7*complex(0,1))/2. - (cw**2*ee**4*FM1*complex(0,1))/(2.*sw**2) + (cw**2*ee**4*FM7*complex(0,1))/(4.*sw**2) - (ee**4*FM1*complex(0,1)*sw**2)/(2.*cw**2) + (ee**4*FM7*complex(0,1)*sw**2)/(4.*cw**2)',
                  order = {'NP':1,'QED':4})

GC_122 = Coupling(name = 'GC_122',
                  value = 'cw**2*ee**2*FM0*complex(0,1) + 4*cw**2*ee**2*FM2*complex(0,1) + (2*cw**4*ee**2*FM2*complex(0,1))/sw**2 - (cw**3*ee**2*FM4*complex(0,1))/sw - 2*cw*ee**2*FM4*complex(0,1)*sw + 2*ee**2*FM0*complex(0,1)*sw**2 + 2*ee**2*FM2*complex(0,1)*sw**2 - (ee**2*FM4*complex(0,1)*sw**3)/cw + (ee**2*FM0*complex(0,1)*sw**4)/cw**2',
                  order = {'NP':1,'QED':2})

GC_123 = Coupling(name = 'GC_123',
                  value = '2*cw**2*ee**2*FM0*complex(0,1) + 2*cw**2*ee**2*FM2*complex(0,1) + (cw**4*ee**2*FM0*complex(0,1))/sw**2 + (cw**3*ee**2*FM4*complex(0,1))/sw + 2*cw*ee**2*FM4*complex(0,1)*sw + ee**2*FM0*complex(0,1)*sw**2 + 4*ee**2*FM2*complex(0,1)*sw**2 + (ee**2*FM4*complex(0,1)*sw**3)/cw + (2*ee**2*FM2*complex(0,1)*sw**4)/cw**2',
                  order = {'NP':1,'QED':2})

GC_124 = Coupling(name = 'GC_124',
                  value = '(cw**2*ee**2*FM1*complex(0,1))/2. + (cw**2*ee**2*FM3*complex(0,1))/2. - (cw**2*ee**2*FM7*complex(0,1))/4. + (cw**4*ee**2*FM1*complex(0,1))/(4.*sw**2) - (cw**4*ee**2*FM7*complex(0,1))/(8.*sw**2) - (cw**3*ee**2*FM5*complex(0,1))/(2.*sw) - cw*ee**2*FM5*complex(0,1)*sw + (ee**2*FM1*complex(0,1)*sw**2)/4. + ee**2*FM3*complex(0,1)*sw**2 - (ee**2*FM7*complex(0,1)*sw**2)/8. - (ee**2*FM5*complex(0,1)*sw**3)/(2.*cw) + (ee**2*FM3*complex(0,1)*sw**4)/(2.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_125 = Coupling(name = 'GC_125',
                  value = '-0.5*(cw**2*ee**2*FM4*complex(0,1)) - (cw**4*ee**2*FM4*complex(0,1))/(2.*sw**2) + (cw**3*ee**2*FM0*complex(0,1))/sw - (2*cw**3*ee**2*FM2*complex(0,1))/sw + 2*cw*ee**2*FM0*complex(0,1)*sw - 4*cw*ee**2*FM2*complex(0,1)*sw + (ee**2*FM4*complex(0,1)*sw**2)/2. + (ee**2*FM0*complex(0,1)*sw**3)/cw - (2*ee**2*FM2*complex(0,1)*sw**3)/cw + (ee**2*FM4*complex(0,1)*sw**4)/(2.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_126 = Coupling(name = 'GC_126',
                  value = '(cw**2*ee**2*FM5*complex(0,1))/4. + (cw**4*ee**2*FM5*complex(0,1))/(4.*sw**2) + (cw**3*ee**2*FM1*complex(0,1))/(4.*sw) - (cw**3*ee**2*FM3*complex(0,1))/(2.*sw) - (cw**3*ee**2*FM7*complex(0,1))/(8.*sw) + (cw*ee**2*FM1*complex(0,1)*sw)/2. - cw*ee**2*FM3*complex(0,1)*sw - (cw*ee**2*FM7*complex(0,1)*sw)/4. - (ee**2*FM5*complex(0,1)*sw**2)/4. + (ee**2*FM1*complex(0,1)*sw**3)/(4.*cw) - (ee**2*FM3*complex(0,1)*sw**3)/(2.*cw) - (ee**2*FM7*complex(0,1)*sw**3)/(8.*cw) - (ee**2*FM5*complex(0,1)*sw**4)/(4.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_127 = Coupling(name = 'GC_127',
                  value = '(cw**2*ee**2*FM1*complex(0,1))/4. + cw**2*ee**2*FM3*complex(0,1) - (cw**2*ee**2*FM7*complex(0,1))/8. + (cw**4*ee**2*FM3*complex(0,1))/(2.*sw**2) + (cw**3*ee**2*FM5*complex(0,1))/(2.*sw) + cw*ee**2*FM5*complex(0,1)*sw + (ee**2*FM1*complex(0,1)*sw**2)/2. + (ee**2*FM3*complex(0,1)*sw**2)/2. - (ee**2*FM7*complex(0,1)*sw**2)/4. + (ee**2*FM5*complex(0,1)*sw**3)/(2.*cw) + (ee**2*FM1*complex(0,1)*sw**4)/(4.*cw**2) - (ee**2*FM7*complex(0,1)*sw**4)/(8.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_128 = Coupling(name = 'GC_128',
                  value = '2*ee**2*FM2*complex(0,1)*vev',
                  order = {'NP':1,'QED':1})

GC_129 = Coupling(name = 'GC_129',
                  value = '-0.5*(ee**2*FM3*complex(0,1)*vev)',
                  order = {'NP':1,'QED':1})

GC_130 = Coupling(name = 'GC_130',
                  value = '-0.5*(ee*FM4*complex(0,1)*vev)',
                  order = {'NP':1})

GC_131 = Coupling(name = 'GC_131',
                  value = '-0.5*(ee**2*FM4*complex(0,1)*vev)',
                  order = {'NP':1,'QED':1})

GC_132 = Coupling(name = 'GC_132',
                  value = '(ee*FM5*complex(0,1)*vev)/4.',
                  order = {'NP':1})

GC_133 = Coupling(name = 'GC_133',
                  value = '(ee**2*FM5*complex(0,1)*vev)/4.',
                  order = {'NP':1,'QED':1})

GC_134 = Coupling(name = 'GC_134',
                  value = '-0.125*(ee*FM7*complex(0,1)*vev)',
                  order = {'NP':1})

GC_135 = Coupling(name = 'GC_135',
                  value = '-0.125*(ee**2*FM7*complex(0,1)*vev)',
                  order = {'NP':1,'QED':1})

GC_136 = Coupling(name = 'GC_136',
                  value = '-0.25*(ee**2*FM7*complex(0,1)*vev)',
                  order = {'NP':1,'QED':1})

GC_137 = Coupling(name = 'GC_137',
                  value = '-0.25*(ee**3*FM7*complex(0,1)*vev)',
                  order = {'NP':1,'QED':2})

GC_138 = Coupling(name = 'GC_138',
                  value = '-6*complex(0,1)*lam*vev',
                  order = {'QED':1})

GC_139 = Coupling(name = 'GC_139',
                  value = '-((cw**2*ee**4*FM0*complex(0,1)*vev)/sw**4)',
                  order = {'NP':1,'QED':3})

GC_140 = Coupling(name = 'GC_140',
                  value = '(3*cw**2*ee**4*FM1*complex(0,1)*vev)/(2.*sw**4)',
                  order = {'NP':1,'QED':3})

GC_141 = Coupling(name = 'GC_141',
                  value = '(-9*cw**2*ee**4*FM7*complex(0,1)*vev)/(4.*sw**4)',
                  order = {'NP':1,'QED':3})

GC_142 = Coupling(name = 'GC_142',
                  value = '-((cw*ee**3*FM0*complex(0,1)*vev)/sw**3)',
                  order = {'NP':1,'QED':2})

GC_143 = Coupling(name = 'GC_143',
                  value = '(4*cw*ee**4*FM0*complex(0,1)*vev)/sw**3',
                  order = {'NP':1,'QED':3})

GC_144 = Coupling(name = 'GC_144',
                  value = '(cw*ee**3*FM1*complex(0,1)*vev)/(4.*sw**3)',
                  order = {'NP':1,'QED':2})

GC_145 = Coupling(name = 'GC_145',
                  value = '-((cw*ee**4*FM1*complex(0,1)*vev)/sw**3)',
                  order = {'NP':1,'QED':3})

GC_146 = Coupling(name = 'GC_146',
                  value = '(cw**3*ee**3*FM4*complex(0,1)*vev)/(2.*sw**3)',
                  order = {'NP':1,'QED':2})

GC_147 = Coupling(name = 'GC_147',
                  value = '-0.25*(cw**3*ee**3*FM5*complex(0,1)*vev)/sw**3',
                  order = {'NP':1,'QED':2})

GC_148 = Coupling(name = 'GC_148',
                  value = '(cw*ee**3*FM7*complex(0,1)*vev)/(8.*sw**3)',
                  order = {'NP':1,'QED':2})

GC_149 = Coupling(name = 'GC_149',
                  value = '(3*cw**3*ee**3*FM7*complex(0,1)*vev)/(8.*sw**3)',
                  order = {'NP':1,'QED':2})

GC_150 = Coupling(name = 'GC_150',
                  value = '-0.5*(cw*ee**4*FM7*complex(0,1)*vev)/sw**3',
                  order = {'NP':1,'QED':3})

GC_151 = Coupling(name = 'GC_151',
                  value = '(ee**2*complex(0,1)*vev)/(2.*sw**2)',
                  order = {'QED':1})

GC_152 = Coupling(name = 'GC_152',
                  value = '(ee**2*FM0*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':1})

GC_153 = Coupling(name = 'GC_153',
                  value = '(cw**2*ee**2*FM0*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':1})

GC_154 = Coupling(name = 'GC_154',
                  value = '-((ee**3*FM0*complex(0,1)*vev)/sw**2)',
                  order = {'NP':1,'QED':2})

GC_155 = Coupling(name = 'GC_155',
                  value = '-((ee**4*FM0*complex(0,1)*vev)/sw**2)',
                  order = {'NP':1,'QED':3})

GC_156 = Coupling(name = 'GC_156',
                  value = '-0.25*(ee**2*FM1*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':1})

GC_157 = Coupling(name = 'GC_157',
                  value = '(cw**2*ee**2*FM1*complex(0,1)*vev)/(4.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_158 = Coupling(name = 'GC_158',
                  value = '-0.25*(ee**3*FM1*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':2})

GC_159 = Coupling(name = 'GC_159',
                  value = '(ee**4*FM1*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':3})

GC_160 = Coupling(name = 'GC_160',
                  value = '-0.5*(cw**2*ee**2*FM4*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':1})

GC_161 = Coupling(name = 'GC_161',
                  value = '-0.5*(cw**2*ee**3*FM4*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':2})

GC_162 = Coupling(name = 'GC_162',
                  value = '(cw**2*ee**2*FM5*complex(0,1)*vev)/(4.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_163 = Coupling(name = 'GC_163',
                  value = '(cw**2*ee**3*FM5*complex(0,1)*vev)/(4.*sw**2)',
                  order = {'NP':1,'QED':2})

GC_164 = Coupling(name = 'GC_164',
                  value = '(ee**2*FM7*complex(0,1)*vev)/(4.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_165 = Coupling(name = 'GC_165',
                  value = '-0.125*(cw**2*ee**2*FM7*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':1})

GC_166 = Coupling(name = 'GC_166',
                  value = '(ee**3*FM7*complex(0,1)*vev)/(4.*sw**2)',
                  order = {'NP':1,'QED':2})

GC_167 = Coupling(name = 'GC_167',
                  value = '-0.125*(cw**2*ee**3*FM7*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':2})

GC_168 = Coupling(name = 'GC_168',
                  value = '-((ee**4*FM7*complex(0,1)*vev)/sw**2)',
                  order = {'NP':1,'QED':3})

GC_169 = Coupling(name = 'GC_169',
                  value = '(-3*ee**4*FM7*complex(0,1)*vev)/(2.*sw**2)',
                  order = {'NP':1,'QED':3})

GC_170 = Coupling(name = 'GC_170',
                  value = '(cw*ee*FM4*complex(0,1)*vev)/(2.*sw)',
                  order = {'NP':1})

GC_171 = Coupling(name = 'GC_171',
                  value = '(cw*ee**2*FM4*complex(0,1)*vev)/(2.*sw)',
                  order = {'NP':1,'QED':1})

GC_172 = Coupling(name = 'GC_172',
                  value = '-((cw*ee**2*FM4*complex(0,1)*vev)/sw)',
                  order = {'NP':1,'QED':1})

GC_173 = Coupling(name = 'GC_173',
                  value = '(cw*ee**3*FM4*complex(0,1)*vev)/(2.*sw)',
                  order = {'NP':1,'QED':2})

GC_174 = Coupling(name = 'GC_174',
                  value = '-0.25*(cw*ee*FM5*complex(0,1)*vev)/sw',
                  order = {'NP':1})

GC_175 = Coupling(name = 'GC_175',
                  value = '(cw*ee**2*FM5*complex(0,1)*vev)/(4.*sw)',
                  order = {'NP':1,'QED':1})

GC_176 = Coupling(name = 'GC_176',
                  value = '-0.5*(cw*ee**2*FM5*complex(0,1)*vev)/sw',
                  order = {'NP':1,'QED':1})

GC_177 = Coupling(name = 'GC_177',
                  value = '-0.5*(cw*ee**3*FM5*complex(0,1)*vev)/sw',
                  order = {'NP':1,'QED':2})

GC_178 = Coupling(name = 'GC_178',
                  value = '-0.125*(cw*ee*FM7*complex(0,1)*vev)/sw',
                  order = {'NP':1})

GC_179 = Coupling(name = 'GC_179',
                  value = '(cw*ee**2*FM7*complex(0,1)*vev)/(8.*sw)',
                  order = {'NP':1,'QED':1})

GC_180 = Coupling(name = 'GC_180',
                  value = '(ee**3*FM7*complex(0,1)*vev)/(8.*cw*sw)',
                  order = {'NP':1,'QED':2})

GC_181 = Coupling(name = 'GC_181',
                  value = '(cw*ee**3*FM7*complex(0,1)*vev)/(2.*sw)',
                  order = {'NP':1,'QED':2})

GC_182 = Coupling(name = 'GC_182',
                  value = '-0.5*(ee**4*FM7*complex(0,1)*vev)/(cw*sw)',
                  order = {'NP':1,'QED':3})

GC_183 = Coupling(name = 'GC_183',
                  value = '(ee**2*FM4*complex(0,1)*sw*vev)/(2.*cw)',
                  order = {'NP':1,'QED':1})

GC_184 = Coupling(name = 'GC_184',
                  value = '(ee**3*FM4*complex(0,1)*sw*vev)/(2.*cw)',
                  order = {'NP':1,'QED':2})

GC_185 = Coupling(name = 'GC_185',
                  value = '(ee**2*FM5*complex(0,1)*sw*vev)/(4.*cw)',
                  order = {'NP':1,'QED':1})

GC_186 = Coupling(name = 'GC_186',
                  value = '-0.25*(ee**3*FM5*complex(0,1)*sw*vev)/cw',
                  order = {'NP':1,'QED':2})

GC_187 = Coupling(name = 'GC_187',
                  value = '-0.125*(ee*FM7*complex(0,1)*sw*vev)/cw',
                  order = {'NP':1})

GC_188 = Coupling(name = 'GC_188',
                  value = '(ee**2*FM7*complex(0,1)*sw*vev)/(8.*cw)',
                  order = {'NP':1,'QED':1})

GC_189 = Coupling(name = 'GC_189',
                  value = '-0.5*(ee**3*FM4*complex(0,1)*sw**2*vev)/cw**2',
                  order = {'NP':1,'QED':2})

GC_190 = Coupling(name = 'GC_190',
                  value = '(ee**3*FM5*complex(0,1)*sw**2*vev)/(4.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_191 = Coupling(name = 'GC_191',
                  value = 'ee**2*FM2*complex(0,1)*vev**2',
                  order = {'NP':1})

GC_192 = Coupling(name = 'GC_192',
                  value = '-0.25*(ee**2*FM3*complex(0,1)*vev**2)',
                  order = {'NP':1})

GC_193 = Coupling(name = 'GC_193',
                  value = '-0.25*(ee**2*FM4*complex(0,1)*vev**2)',
                  order = {'NP':1})

GC_194 = Coupling(name = 'GC_194',
                  value = '(ee**2*FM5*complex(0,1)*vev**2)/8.',
                  order = {'NP':1})

GC_195 = Coupling(name = 'GC_195',
                  value = '-0.125*(ee**2*FM7*complex(0,1)*vev**2)',
                  order = {'NP':1})

GC_196 = Coupling(name = 'GC_196',
                  value = '-0.125*(ee**3*FM7*complex(0,1)*vev**2)',
                  order = {'NP':1,'QED':1})

GC_197 = Coupling(name = 'GC_197',
                  value = '-0.5*(cw**2*ee**4*FM0*complex(0,1)*vev**2)/sw**4',
                  order = {'NP':1,'QED':2})

GC_198 = Coupling(name = 'GC_198',
                  value = '(3*cw**2*ee**4*FM1*complex(0,1)*vev**2)/(4.*sw**4)',
                  order = {'NP':1,'QED':2})

GC_199 = Coupling(name = 'GC_199',
                  value = '(-9*cw**2*ee**4*FM7*complex(0,1)*vev**2)/(8.*sw**4)',
                  order = {'NP':1,'QED':2})

GC_200 = Coupling(name = 'GC_200',
                  value = '-0.5*(cw*ee**3*FM0*complex(0,1)*vev**2)/sw**3',
                  order = {'NP':1,'QED':1})

GC_201 = Coupling(name = 'GC_201',
                  value = '(2*cw*ee**4*FM0*complex(0,1)*vev**2)/sw**3',
                  order = {'NP':1,'QED':2})

GC_202 = Coupling(name = 'GC_202',
                  value = '(cw*ee**3*FM1*complex(0,1)*vev**2)/(8.*sw**3)',
                  order = {'NP':1,'QED':1})

GC_203 = Coupling(name = 'GC_203',
                  value = '-0.5*(cw*ee**4*FM1*complex(0,1)*vev**2)/sw**3',
                  order = {'NP':1,'QED':2})

GC_204 = Coupling(name = 'GC_204',
                  value = '(cw**3*ee**3*FM4*complex(0,1)*vev**2)/(4.*sw**3)',
                  order = {'NP':1,'QED':1})

GC_205 = Coupling(name = 'GC_205',
                  value = '-0.125*(cw**3*ee**3*FM5*complex(0,1)*vev**2)/sw**3',
                  order = {'NP':1,'QED':1})

GC_206 = Coupling(name = 'GC_206',
                  value = '(cw*ee**3*FM7*complex(0,1)*vev**2)/(16.*sw**3)',
                  order = {'NP':1,'QED':1})

GC_207 = Coupling(name = 'GC_207',
                  value = '(3*cw**3*ee**3*FM7*complex(0,1)*vev**2)/(16.*sw**3)',
                  order = {'NP':1,'QED':1})

GC_208 = Coupling(name = 'GC_208',
                  value = '-0.25*(cw*ee**4*FM7*complex(0,1)*vev**2)/sw**3',
                  order = {'NP':1,'QED':2})

GC_209 = Coupling(name = 'GC_209',
                  value = '(ee**2*FM0*complex(0,1)*vev**2)/(2.*sw**2)',
                  order = {'NP':1})

GC_210 = Coupling(name = 'GC_210',
                  value = '(cw**2*ee**2*FM0*complex(0,1)*vev**2)/(2.*sw**2)',
                  order = {'NP':1})

GC_211 = Coupling(name = 'GC_211',
                  value = '-0.5*(ee**3*FM0*complex(0,1)*vev**2)/sw**2',
                  order = {'NP':1,'QED':1})

GC_212 = Coupling(name = 'GC_212',
                  value = '-0.5*(ee**4*FM0*complex(0,1)*vev**2)/sw**2',
                  order = {'NP':1,'QED':2})

GC_213 = Coupling(name = 'GC_213',
                  value = '-0.125*(ee**2*FM1*complex(0,1)*vev**2)/sw**2',
                  order = {'NP':1})

GC_214 = Coupling(name = 'GC_214',
                  value = '(cw**2*ee**2*FM1*complex(0,1)*vev**2)/(8.*sw**2)',
                  order = {'NP':1})

GC_215 = Coupling(name = 'GC_215',
                  value = '-0.125*(ee**3*FM1*complex(0,1)*vev**2)/sw**2',
                  order = {'NP':1,'QED':1})

GC_216 = Coupling(name = 'GC_216',
                  value = '(ee**4*FM1*complex(0,1)*vev**2)/(2.*sw**2)',
                  order = {'NP':1,'QED':2})

GC_217 = Coupling(name = 'GC_217',
                  value = '(cw**2*ee**2*FM4*complex(0,1)*vev**2)/(4.*sw**2)',
                  order = {'NP':1})

GC_218 = Coupling(name = 'GC_218',
                  value = '-0.25*(cw**2*ee**3*FM4*complex(0,1)*vev**2)/sw**2',
                  order = {'NP':1,'QED':1})

GC_219 = Coupling(name = 'GC_219',
                  value = '(cw**2*ee**2*FM5*complex(0,1)*vev**2)/(8.*sw**2)',
                  order = {'NP':1})

GC_220 = Coupling(name = 'GC_220',
                  value = '(cw**2*ee**3*FM5*complex(0,1)*vev**2)/(8.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_221 = Coupling(name = 'GC_221',
                  value = '(ee**2*FM7*complex(0,1)*vev**2)/(8.*sw**2)',
                  order = {'NP':1})

GC_222 = Coupling(name = 'GC_222',
                  value = '-0.0625*(cw**2*ee**2*FM7*complex(0,1)*vev**2)/sw**2',
                  order = {'NP':1})

GC_223 = Coupling(name = 'GC_223',
                  value = '(ee**3*FM7*complex(0,1)*vev**2)/(8.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_224 = Coupling(name = 'GC_224',
                  value = '-0.0625*(cw**2*ee**3*FM7*complex(0,1)*vev**2)/sw**2',
                  order = {'NP':1,'QED':1})

GC_225 = Coupling(name = 'GC_225',
                  value = '-0.5*(ee**4*FM7*complex(0,1)*vev**2)/sw**2',
                  order = {'NP':1,'QED':2})

GC_226 = Coupling(name = 'GC_226',
                  value = '(-3*ee**4*FM7*complex(0,1)*vev**2)/(4.*sw**2)',
                  order = {'NP':1,'QED':2})

GC_227 = Coupling(name = 'GC_227',
                  value = '-0.5*(cw*ee**2*FM4*complex(0,1)*vev**2)/sw',
                  order = {'NP':1})

GC_228 = Coupling(name = 'GC_228',
                  value = '(cw*ee**3*FM4*complex(0,1)*vev**2)/(4.*sw)',
                  order = {'NP':1,'QED':1})

GC_229 = Coupling(name = 'GC_229',
                  value = '(cw*ee**2*FM5*complex(0,1)*vev**2)/(8.*sw)',
                  order = {'NP':1})

GC_230 = Coupling(name = 'GC_230',
                  value = '-0.25*(cw*ee**3*FM5*complex(0,1)*vev**2)/sw',
                  order = {'NP':1,'QED':1})

GC_231 = Coupling(name = 'GC_231',
                  value = '(cw*ee**2*FM7*complex(0,1)*vev**2)/(16.*sw)',
                  order = {'NP':1})

GC_232 = Coupling(name = 'GC_232',
                  value = '(ee**3*FM7*complex(0,1)*vev**2)/(16.*cw*sw)',
                  order = {'NP':1,'QED':1})

GC_233 = Coupling(name = 'GC_233',
                  value = '(cw*ee**3*FM7*complex(0,1)*vev**2)/(4.*sw)',
                  order = {'NP':1,'QED':1})

GC_234 = Coupling(name = 'GC_234',
                  value = '-0.25*(ee**4*FM7*complex(0,1)*vev**2)/(cw*sw)',
                  order = {'NP':1,'QED':2})

GC_235 = Coupling(name = 'GC_235',
                  value = '(ee**2*FM4*complex(0,1)*sw*vev**2)/(4.*cw)',
                  order = {'NP':1})

GC_236 = Coupling(name = 'GC_236',
                  value = '(ee**3*FM4*complex(0,1)*sw*vev**2)/(4.*cw)',
                  order = {'NP':1,'QED':1})

GC_237 = Coupling(name = 'GC_237',
                  value = '(ee**2*FM5*complex(0,1)*sw*vev**2)/(8.*cw)',
                  order = {'NP':1})

GC_238 = Coupling(name = 'GC_238',
                  value = '-0.125*(ee**3*FM5*complex(0,1)*sw*vev**2)/cw',
                  order = {'NP':1,'QED':1})

GC_239 = Coupling(name = 'GC_239',
                  value = '(ee**2*FM7*complex(0,1)*sw*vev**2)/(16.*cw)',
                  order = {'NP':1})

GC_240 = Coupling(name = 'GC_240',
                  value = '-0.25*(ee**3*FM4*complex(0,1)*sw**2*vev**2)/cw**2',
                  order = {'NP':1,'QED':1})

GC_241 = Coupling(name = 'GC_241',
                  value = '(ee**3*FM5*complex(0,1)*sw**2*vev**2)/(8.*cw**2)',
                  order = {'NP':1,'QED':1})

GC_242 = Coupling(name = 'GC_242',
                  value = '-0.5*(ee**3*FM4*complex(0,1)*vev) + (ee**3*FM5*complex(0,1)*vev)/2.',
                  order = {'NP':1,'QED':2})

GC_243 = Coupling(name = 'GC_243',
                  value = '(3*ee**4*FM0*complex(0,1)*vev)/sw**4 - (3*ee**4*FM1*complex(0,1)*vev)/(2.*sw**4) + (3*ee**4*FM7*complex(0,1)*vev)/(4.*sw**4)',
                  order = {'NP':1,'QED':3})

GC_244 = Coupling(name = 'GC_244',
                  value = '-0.5*(cw*ee**3*FM4*complex(0,1)*vev)/sw**3 - (cw*ee**3*FM5*complex(0,1)*vev)/(2.*sw**3)',
                  order = {'NP':1,'QED':2})

GC_245 = Coupling(name = 'GC_245',
                  value = '(ee**4*FM0*complex(0,1)*vev)/cw**2 + (2*ee**4*FM0*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':3})

GC_246 = Coupling(name = 'GC_246',
                  value = '(ee**4*FM1*complex(0,1)*vev)/(2.*cw**2) - (ee**4*FM7*complex(0,1)*vev)/(4.*cw**2) + (ee**4*FM1*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':3})

GC_247 = Coupling(name = 'GC_247',
                  value = 'ee**2*FM0*complex(0,1)*vev + (2*cw**2*ee**2*FM2*complex(0,1)*vev)/sw**2',
                  order = {'NP':1,'QED':1})

GC_248 = Coupling(name = 'GC_248',
                  value = '(ee**2*FM1*complex(0,1)*vev)/4. + (cw**2*ee**2*FM3*complex(0,1)*vev)/(2.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_249 = Coupling(name = 'GC_249',
                  value = '-0.5*(ee**3*FM4*complex(0,1)*vev) - (cw**2*ee**3*FM4*complex(0,1)*vev)/(2.*sw**2)',
                  order = {'NP':1,'QED':2})

GC_250 = Coupling(name = 'GC_250',
                  value = '(ee**3*FM4*complex(0,1)*vev)/(2.*sw**2) + (ee**3*FM5*complex(0,1)*vev)/(2.*sw**2)',
                  order = {'NP':1,'QED':2})

GC_251 = Coupling(name = 'GC_251',
                  value = '(ee**3*FM5*complex(0,1)*vev)/4. + (cw**2*ee**3*FM5*complex(0,1)*vev)/(4.*sw**2)',
                  order = {'NP':1,'QED':2})

GC_252 = Coupling(name = 'GC_252',
                  value = '-(ee**4*FM0*complex(0,1)*vev) + (ee**4*FM1*complex(0,1)*vev)/2. - (ee**4*FM7*complex(0,1)*vev)/4. - (cw**4*ee**4*FM0*complex(0,1)*vev)/sw**4 + (cw**4*ee**4*FM1*complex(0,1)*vev)/(2.*sw**4) - (cw**4*ee**4*FM7*complex(0,1)*vev)/(4.*sw**4) - (2*cw**2*ee**4*FM0*complex(0,1)*vev)/sw**2 + (cw**2*ee**4*FM1*complex(0,1)*vev)/sw**2 - (cw**2*ee**4*FM7*complex(0,1)*vev)/(2.*sw**2)',
                  order = {'NP':1,'QED':3})

GC_253 = Coupling(name = 'GC_253',
                  value = '(cw*ee**2*FM0*complex(0,1)*vev)/sw - (2*cw*ee**2*FM2*complex(0,1)*vev)/sw',
                  order = {'NP':1,'QED':1})

GC_254 = Coupling(name = 'GC_254',
                  value = '-0.25*(cw*ee**2*FM1*complex(0,1)*vev)/sw + (cw*ee**2*FM3*complex(0,1)*vev)/(2.*sw)',
                  order = {'NP':1,'QED':1})

GC_255 = Coupling(name = 'GC_255',
                  value = '-((cw**3*ee**3*FM0*complex(0,1)*vev)/sw**3) - (2*cw*ee**3*FM0*complex(0,1)*vev)/sw - (ee**3*FM0*complex(0,1)*sw*vev)/cw',
                  order = {'NP':1,'QED':2})

GC_256 = Coupling(name = 'GC_256',
                  value = '(cw*ee**3*FM7*complex(0,1)*vev)/(8.*sw) + (ee**3*FM7*complex(0,1)*sw*vev)/(8.*cw)',
                  order = {'NP':1,'QED':2})

GC_257 = Coupling(name = 'GC_257',
                  value = '-0.25*(cw**3*ee**3*FM1*complex(0,1)*vev)/sw**3 - (cw*ee**3*FM1*complex(0,1)*vev)/(2.*sw) - (ee**3*FM1*complex(0,1)*sw*vev)/(4.*cw) + (ee**3*FM7*complex(0,1)*sw*vev)/(8.*cw)',
                  order = {'NP':1,'QED':2})

GC_258 = Coupling(name = 'GC_258',
                  value = '(2*cw**3*ee**4*FM0*complex(0,1)*vev)/sw**3 - (cw**3*ee**4*FM1*complex(0,1)*vev)/sw**3 + (cw**3*ee**4*FM7*complex(0,1)*vev)/(2.*sw**3) + (4*cw*ee**4*FM0*complex(0,1)*vev)/sw - (2*cw*ee**4*FM1*complex(0,1)*vev)/sw + (cw*ee**4*FM7*complex(0,1)*vev)/sw + (2*ee**4*FM0*complex(0,1)*sw*vev)/cw - (ee**4*FM1*complex(0,1)*sw*vev)/cw + (ee**4*FM7*complex(0,1)*sw*vev)/(2.*cw)',
                  order = {'NP':1,'QED':3})

GC_259 = Coupling(name = 'GC_259',
                  value = 'ee**2*complex(0,1)*vev + (cw**2*ee**2*complex(0,1)*vev)/(2.*sw**2) + (ee**2*complex(0,1)*sw**2*vev)/(2.*cw**2)',
                  order = {'QED':1})

GC_260 = Coupling(name = 'GC_260',
                  value = '2*ee**2*FM0*complex(0,1)*vev + (ee**2*FM0*complex(0,1)*sw**2*vev)/cw**2',
                  order = {'NP':1,'QED':1})

GC_261 = Coupling(name = 'GC_261',
                  value = '-2*ee**3*FM0*complex(0,1)*vev - (cw**2*ee**3*FM0*complex(0,1)*vev)/sw**2 - (ee**3*FM0*complex(0,1)*sw**2*vev)/cw**2',
                  order = {'NP':1,'QED':2})

GC_262 = Coupling(name = 'GC_262',
                  value = '-2*ee**4*FM0*complex(0,1)*vev - (cw**2*ee**4*FM0*complex(0,1)*vev)/sw**2 - (ee**4*FM0*complex(0,1)*sw**2*vev)/cw**2',
                  order = {'NP':1,'QED':3})

GC_263 = Coupling(name = 'GC_263',
                  value = '(ee**2*FM1*complex(0,1)*vev)/2. + (ee**2*FM1*complex(0,1)*sw**2*vev)/(4.*cw**2) - (ee**2*FM7*complex(0,1)*sw**2*vev)/(8.*cw**2)',
                  order = {'NP':1,'QED':1})

GC_264 = Coupling(name = 'GC_264',
                  value = '(ee**3*FM1*complex(0,1)*vev)/2. + (cw**2*ee**3*FM1*complex(0,1)*vev)/(4.*sw**2) + (ee**3*FM1*complex(0,1)*sw**2*vev)/(4.*cw**2) - (ee**3*FM7*complex(0,1)*sw**2*vev)/(8.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_265 = Coupling(name = 'GC_265',
                  value = '-(ee**4*FM1*complex(0,1)*vev) + (ee**4*FM7*complex(0,1)*vev)/2. - (cw**2*ee**4*FM1*complex(0,1)*vev)/(2.*sw**2) + (cw**2*ee**4*FM7*complex(0,1)*vev)/(4.*sw**2) - (ee**4*FM1*complex(0,1)*sw**2*vev)/(2.*cw**2) + (ee**4*FM7*complex(0,1)*sw**2*vev)/(4.*cw**2)',
                  order = {'NP':1,'QED':3})

GC_266 = Coupling(name = 'GC_266',
                  value = 'cw**2*ee**2*FM0*complex(0,1)*vev + 4*cw**2*ee**2*FM2*complex(0,1)*vev + (2*cw**4*ee**2*FM2*complex(0,1)*vev)/sw**2 - (cw**3*ee**2*FM4*complex(0,1)*vev)/sw - 2*cw*ee**2*FM4*complex(0,1)*sw*vev + 2*ee**2*FM0*complex(0,1)*sw**2*vev + 2*ee**2*FM2*complex(0,1)*sw**2*vev - (ee**2*FM4*complex(0,1)*sw**3*vev)/cw + (ee**2*FM0*complex(0,1)*sw**4*vev)/cw**2',
                  order = {'NP':1,'QED':1})

GC_267 = Coupling(name = 'GC_267',
                  value = '2*cw**2*ee**2*FM0*complex(0,1)*vev + 2*cw**2*ee**2*FM2*complex(0,1)*vev + (cw**4*ee**2*FM0*complex(0,1)*vev)/sw**2 + (cw**3*ee**2*FM4*complex(0,1)*vev)/sw + 2*cw*ee**2*FM4*complex(0,1)*sw*vev + ee**2*FM0*complex(0,1)*sw**2*vev + 4*ee**2*FM2*complex(0,1)*sw**2*vev + (ee**2*FM4*complex(0,1)*sw**3*vev)/cw + (2*ee**2*FM2*complex(0,1)*sw**4*vev)/cw**2',
                  order = {'NP':1,'QED':1})

GC_268 = Coupling(name = 'GC_268',
                  value = '(cw**2*ee**2*FM1*complex(0,1)*vev)/2. + (cw**2*ee**2*FM3*complex(0,1)*vev)/2. - (cw**2*ee**2*FM7*complex(0,1)*vev)/4. + (cw**4*ee**2*FM1*complex(0,1)*vev)/(4.*sw**2) - (cw**4*ee**2*FM7*complex(0,1)*vev)/(8.*sw**2) - (cw**3*ee**2*FM5*complex(0,1)*vev)/(2.*sw) - cw*ee**2*FM5*complex(0,1)*sw*vev + (ee**2*FM1*complex(0,1)*sw**2*vev)/4. + ee**2*FM3*complex(0,1)*sw**2*vev - (ee**2*FM7*complex(0,1)*sw**2*vev)/8. - (ee**2*FM5*complex(0,1)*sw**3*vev)/(2.*cw) + (ee**2*FM3*complex(0,1)*sw**4*vev)/(2.*cw**2)',
                  order = {'NP':1,'QED':1})

GC_269 = Coupling(name = 'GC_269',
                  value = '-0.5*(cw**2*ee**2*FM4*complex(0,1)*vev) - (cw**4*ee**2*FM4*complex(0,1)*vev)/(2.*sw**2) + (cw**3*ee**2*FM0*complex(0,1)*vev)/sw - (2*cw**3*ee**2*FM2*complex(0,1)*vev)/sw + 2*cw*ee**2*FM0*complex(0,1)*sw*vev - 4*cw*ee**2*FM2*complex(0,1)*sw*vev + (ee**2*FM4*complex(0,1)*sw**2*vev)/2. + (ee**2*FM0*complex(0,1)*sw**3*vev)/cw - (2*ee**2*FM2*complex(0,1)*sw**3*vev)/cw + (ee**2*FM4*complex(0,1)*sw**4*vev)/(2.*cw**2)',
                  order = {'NP':1,'QED':1})

GC_270 = Coupling(name = 'GC_270',
                  value = '(cw**2*ee**2*FM5*complex(0,1)*vev)/4. + (cw**4*ee**2*FM5*complex(0,1)*vev)/(4.*sw**2) + (cw**3*ee**2*FM1*complex(0,1)*vev)/(4.*sw) - (cw**3*ee**2*FM3*complex(0,1)*vev)/(2.*sw) - (cw**3*ee**2*FM7*complex(0,1)*vev)/(8.*sw) + (cw*ee**2*FM1*complex(0,1)*sw*vev)/2. - cw*ee**2*FM3*complex(0,1)*sw*vev - (cw*ee**2*FM7*complex(0,1)*sw*vev)/4. - (ee**2*FM5*complex(0,1)*sw**2*vev)/4. + (ee**2*FM1*complex(0,1)*sw**3*vev)/(4.*cw) - (ee**2*FM3*complex(0,1)*sw**3*vev)/(2.*cw) - (ee**2*FM7*complex(0,1)*sw**3*vev)/(8.*cw) - (ee**2*FM5*complex(0,1)*sw**4*vev)/(4.*cw**2)',
                  order = {'NP':1,'QED':1})

GC_271 = Coupling(name = 'GC_271',
                  value = '(cw**2*ee**2*FM1*complex(0,1)*vev)/4. + cw**2*ee**2*FM3*complex(0,1)*vev - (cw**2*ee**2*FM7*complex(0,1)*vev)/8. + (cw**4*ee**2*FM3*complex(0,1)*vev)/(2.*sw**2) + (cw**3*ee**2*FM5*complex(0,1)*vev)/(2.*sw) + cw*ee**2*FM5*complex(0,1)*sw*vev + (ee**2*FM1*complex(0,1)*sw**2*vev)/2. + (ee**2*FM3*complex(0,1)*sw**2*vev)/2. - (ee**2*FM7*complex(0,1)*sw**2*vev)/4. + (ee**2*FM5*complex(0,1)*sw**3*vev)/(2.*cw) + (ee**2*FM1*complex(0,1)*sw**4*vev)/(4.*cw**2) - (ee**2*FM7*complex(0,1)*sw**4*vev)/(8.*cw**2)',
                  order = {'NP':1,'QED':1})

GC_272 = Coupling(name = 'GC_272',
                  value = '-0.25*(ee**3*FM4*complex(0,1)*vev**2) + (ee**3*FM5*complex(0,1)*vev**2)/4.',
                  order = {'NP':1,'QED':1})

GC_273 = Coupling(name = 'GC_273',
                  value = '(3*ee**4*FM0*complex(0,1)*vev**2)/(2.*sw**4) - (3*ee**4*FM1*complex(0,1)*vev**2)/(4.*sw**4) + (3*ee**4*FM7*complex(0,1)*vev**2)/(8.*sw**4)',
                  order = {'NP':1,'QED':2})

GC_274 = Coupling(name = 'GC_274',
                  value = '-0.25*(cw*ee**3*FM4*complex(0,1)*vev**2)/sw**3 - (cw*ee**3*FM5*complex(0,1)*vev**2)/(4.*sw**3)',
                  order = {'NP':1,'QED':1})

GC_275 = Coupling(name = 'GC_275',
                  value = '(ee**4*FM0*complex(0,1)*vev**2)/(2.*cw**2) + (ee**4*FM0*complex(0,1)*vev**2)/sw**2',
                  order = {'NP':1,'QED':2})

GC_276 = Coupling(name = 'GC_276',
                  value = '(ee**4*FM1*complex(0,1)*vev**2)/(4.*cw**2) - (ee**4*FM7*complex(0,1)*vev**2)/(8.*cw**2) + (ee**4*FM1*complex(0,1)*vev**2)/(2.*sw**2)',
                  order = {'NP':1,'QED':2})

GC_277 = Coupling(name = 'GC_277',
                  value = '-0.25*(ee**3*FM4*complex(0,1)*vev**2) - (cw**2*ee**3*FM4*complex(0,1)*vev**2)/(4.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_278 = Coupling(name = 'GC_278',
                  value = '(ee**3*FM4*complex(0,1)*vev**2)/(4.*sw**2) + (ee**3*FM5*complex(0,1)*vev**2)/(4.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_279 = Coupling(name = 'GC_279',
                  value = '(ee**3*FM5*complex(0,1)*vev**2)/8. + (cw**2*ee**3*FM5*complex(0,1)*vev**2)/(8.*sw**2)',
                  order = {'NP':1,'QED':1})

GC_280 = Coupling(name = 'GC_280',
                  value = '-0.5*(ee**4*FM0*complex(0,1)*vev**2) + (ee**4*FM1*complex(0,1)*vev**2)/4. - (ee**4*FM7*complex(0,1)*vev**2)/8. - (cw**4*ee**4*FM0*complex(0,1)*vev**2)/(2.*sw**4) + (cw**4*ee**4*FM1*complex(0,1)*vev**2)/(4.*sw**4) - (cw**4*ee**4*FM7*complex(0,1)*vev**2)/(8.*sw**4) - (cw**2*ee**4*FM0*complex(0,1)*vev**2)/sw**2 + (cw**2*ee**4*FM1*complex(0,1)*vev**2)/(2.*sw**2) - (cw**2*ee**4*FM7*complex(0,1)*vev**2)/(4.*sw**2)',
                  order = {'NP':1,'QED':2})

GC_281 = Coupling(name = 'GC_281',
                  value = '(cw*ee**2*FM0*complex(0,1)*vev**2)/(2.*sw) - (cw*ee**2*FM2*complex(0,1)*vev**2)/sw',
                  order = {'NP':1})

GC_282 = Coupling(name = 'GC_282',
                  value = '-0.125*(cw*ee**2*FM1*complex(0,1)*vev**2)/sw + (cw*ee**2*FM3*complex(0,1)*vev**2)/(4.*sw)',
                  order = {'NP':1})

GC_283 = Coupling(name = 'GC_283',
                  value = '(ee**2*FM0*complex(0,1)*vev**2)/2. + (cw**2*ee**2*FM2*complex(0,1)*vev**2)/sw**2 + (cw*ee**2*FM4*complex(0,1)*vev**2)/(2.*sw)',
                  order = {'NP':1})

GC_284 = Coupling(name = 'GC_284',
                  value = '(ee**2*FM1*complex(0,1)*vev**2)/8. - (ee**2*FM7*complex(0,1)*vev**2)/16. + (cw**2*ee**2*FM3*complex(0,1)*vev**2)/(4.*sw**2) - (cw*ee**2*FM5*complex(0,1)*vev**2)/(4.*sw)',
                  order = {'NP':1})

GC_285 = Coupling(name = 'GC_285',
                  value = '-0.5*(cw**3*ee**3*FM0*complex(0,1)*vev**2)/sw**3 - (cw*ee**3*FM0*complex(0,1)*vev**2)/sw - (ee**3*FM0*complex(0,1)*sw*vev**2)/(2.*cw)',
                  order = {'NP':1,'QED':1})

GC_286 = Coupling(name = 'GC_286',
                  value = '(cw*ee**3*FM7*complex(0,1)*vev**2)/(16.*sw) + (ee**3*FM7*complex(0,1)*sw*vev**2)/(16.*cw)',
                  order = {'NP':1,'QED':1})

GC_287 = Coupling(name = 'GC_287',
                  value = '-0.125*(cw**3*ee**3*FM1*complex(0,1)*vev**2)/sw**3 - (cw*ee**3*FM1*complex(0,1)*vev**2)/(4.*sw) - (ee**3*FM1*complex(0,1)*sw*vev**2)/(8.*cw) + (ee**3*FM7*complex(0,1)*sw*vev**2)/(16.*cw)',
                  order = {'NP':1,'QED':1})

GC_288 = Coupling(name = 'GC_288',
                  value = '(cw**3*ee**4*FM0*complex(0,1)*vev**2)/sw**3 - (cw**3*ee**4*FM1*complex(0,1)*vev**2)/(2.*sw**3) + (cw**3*ee**4*FM7*complex(0,1)*vev**2)/(4.*sw**3) + (2*cw*ee**4*FM0*complex(0,1)*vev**2)/sw - (cw*ee**4*FM1*complex(0,1)*vev**2)/sw + (cw*ee**4*FM7*complex(0,1)*vev**2)/(2.*sw) + (ee**4*FM0*complex(0,1)*sw*vev**2)/cw - (ee**4*FM1*complex(0,1)*sw*vev**2)/(2.*cw) + (ee**4*FM7*complex(0,1)*sw*vev**2)/(4.*cw)',
                  order = {'NP':1,'QED':2})

GC_289 = Coupling(name = 'GC_289',
                  value = 'ee**2*FM0*complex(0,1)*vev**2 + (ee**2*FM0*complex(0,1)*sw**2*vev**2)/(2.*cw**2)',
                  order = {'NP':1})

GC_290 = Coupling(name = 'GC_290',
                  value = '-(ee**3*FM0*complex(0,1)*vev**2) - (cw**2*ee**3*FM0*complex(0,1)*vev**2)/(2.*sw**2) - (ee**3*FM0*complex(0,1)*sw**2*vev**2)/(2.*cw**2)',
                  order = {'NP':1,'QED':1})

GC_291 = Coupling(name = 'GC_291',
                  value = '-(ee**4*FM0*complex(0,1)*vev**2) - (cw**2*ee**4*FM0*complex(0,1)*vev**2)/(2.*sw**2) - (ee**4*FM0*complex(0,1)*sw**2*vev**2)/(2.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_292 = Coupling(name = 'GC_292',
                  value = '(ee**2*FM1*complex(0,1)*vev**2)/4. + (ee**2*FM1*complex(0,1)*sw**2*vev**2)/(8.*cw**2) - (ee**2*FM7*complex(0,1)*sw**2*vev**2)/(16.*cw**2)',
                  order = {'NP':1})

GC_293 = Coupling(name = 'GC_293',
                  value = '(ee**3*FM1*complex(0,1)*vev**2)/4. + (cw**2*ee**3*FM1*complex(0,1)*vev**2)/(8.*sw**2) + (ee**3*FM1*complex(0,1)*sw**2*vev**2)/(8.*cw**2) - (ee**3*FM7*complex(0,1)*sw**2*vev**2)/(16.*cw**2)',
                  order = {'NP':1,'QED':1})

GC_294 = Coupling(name = 'GC_294',
                  value = '-0.5*(ee**4*FM1*complex(0,1)*vev**2) + (ee**4*FM7*complex(0,1)*vev**2)/4. - (cw**2*ee**4*FM1*complex(0,1)*vev**2)/(4.*sw**2) + (cw**2*ee**4*FM7*complex(0,1)*vev**2)/(8.*sw**2) - (ee**4*FM1*complex(0,1)*sw**2*vev**2)/(4.*cw**2) + (ee**4*FM7*complex(0,1)*sw**2*vev**2)/(8.*cw**2)',
                  order = {'NP':1,'QED':2})

GC_295 = Coupling(name = 'GC_295',
                  value = '(cw**2*ee**2*FM0*complex(0,1)*vev**2)/2. + 2*cw**2*ee**2*FM2*complex(0,1)*vev**2 + (cw**4*ee**2*FM2*complex(0,1)*vev**2)/sw**2 - (cw**3*ee**2*FM4*complex(0,1)*vev**2)/(2.*sw) - cw*ee**2*FM4*complex(0,1)*sw*vev**2 + ee**2*FM0*complex(0,1)*sw**2*vev**2 + ee**2*FM2*complex(0,1)*sw**2*vev**2 - (ee**2*FM4*complex(0,1)*sw**3*vev**2)/(2.*cw) + (ee**2*FM0*complex(0,1)*sw**4*vev**2)/(2.*cw**2)',
                  order = {'NP':1})

GC_296 = Coupling(name = 'GC_296',
                  value = 'cw**2*ee**2*FM0*complex(0,1)*vev**2 + cw**2*ee**2*FM2*complex(0,1)*vev**2 + (cw**4*ee**2*FM0*complex(0,1)*vev**2)/(2.*sw**2) + (cw**3*ee**2*FM4*complex(0,1)*vev**2)/(2.*sw) + cw*ee**2*FM4*complex(0,1)*sw*vev**2 + (ee**2*FM0*complex(0,1)*sw**2*vev**2)/2. + 2*ee**2*FM2*complex(0,1)*sw**2*vev**2 + (ee**2*FM4*complex(0,1)*sw**3*vev**2)/(2.*cw) + (ee**2*FM2*complex(0,1)*sw**4*vev**2)/cw**2',
                  order = {'NP':1})

GC_297 = Coupling(name = 'GC_297',
                  value = '(cw**2*ee**2*FM1*complex(0,1)*vev**2)/4. + (cw**2*ee**2*FM3*complex(0,1)*vev**2)/4. - (cw**2*ee**2*FM7*complex(0,1)*vev**2)/8. + (cw**4*ee**2*FM1*complex(0,1)*vev**2)/(8.*sw**2) - (cw**4*ee**2*FM7*complex(0,1)*vev**2)/(16.*sw**2) - (cw**3*ee**2*FM5*complex(0,1)*vev**2)/(4.*sw) - (cw*ee**2*FM5*complex(0,1)*sw*vev**2)/2. + (ee**2*FM1*complex(0,1)*sw**2*vev**2)/8. + (ee**2*FM3*complex(0,1)*sw**2*vev**2)/2. - (ee**2*FM7*complex(0,1)*sw**2*vev**2)/16. - (ee**2*FM5*complex(0,1)*sw**3*vev**2)/(4.*cw) + (ee**2*FM3*complex(0,1)*sw**4*vev**2)/(4.*cw**2)',
                  order = {'NP':1})

GC_298 = Coupling(name = 'GC_298',
                  value = '-0.25*(cw**2*ee**2*FM4*complex(0,1)*vev**2) - (cw**4*ee**2*FM4*complex(0,1)*vev**2)/(4.*sw**2) + (cw**3*ee**2*FM0*complex(0,1)*vev**2)/(2.*sw) - (cw**3*ee**2*FM2*complex(0,1)*vev**2)/sw + cw*ee**2*FM0*complex(0,1)*sw*vev**2 - 2*cw*ee**2*FM2*complex(0,1)*sw*vev**2 + (ee**2*FM4*complex(0,1)*sw**2*vev**2)/4. + (ee**2*FM0*complex(0,1)*sw**3*vev**2)/(2.*cw) - (ee**2*FM2*complex(0,1)*sw**3*vev**2)/cw + (ee**2*FM4*complex(0,1)*sw**4*vev**2)/(4.*cw**2)',
                  order = {'NP':1})

GC_299 = Coupling(name = 'GC_299',
                  value = '(cw**2*ee**2*FM5*complex(0,1)*vev**2)/8. + (cw**4*ee**2*FM5*complex(0,1)*vev**2)/(8.*sw**2) + (cw**3*ee**2*FM1*complex(0,1)*vev**2)/(8.*sw) - (cw**3*ee**2*FM3*complex(0,1)*vev**2)/(4.*sw) - (cw**3*ee**2*FM7*complex(0,1)*vev**2)/(16.*sw) + (cw*ee**2*FM1*complex(0,1)*sw*vev**2)/4. - (cw*ee**2*FM3*complex(0,1)*sw*vev**2)/2. - (cw*ee**2*FM7*complex(0,1)*sw*vev**2)/8. - (ee**2*FM5*complex(0,1)*sw**2*vev**2)/8. + (ee**2*FM1*complex(0,1)*sw**3*vev**2)/(8.*cw) - (ee**2*FM3*complex(0,1)*sw**3*vev**2)/(4.*cw) - (ee**2*FM7*complex(0,1)*sw**3*vev**2)/(16.*cw) - (ee**2*FM5*complex(0,1)*sw**4*vev**2)/(8.*cw**2)',
                  order = {'NP':1})

GC_300 = Coupling(name = 'GC_300',
                  value = '(cw**2*ee**2*FM1*complex(0,1)*vev**2)/8. + (cw**2*ee**2*FM3*complex(0,1)*vev**2)/2. - (cw**2*ee**2*FM7*complex(0,1)*vev**2)/16. + (cw**4*ee**2*FM3*complex(0,1)*vev**2)/(4.*sw**2) + (cw**3*ee**2*FM5*complex(0,1)*vev**2)/(4.*sw) + (cw*ee**2*FM5*complex(0,1)*sw*vev**2)/2. + (ee**2*FM1*complex(0,1)*sw**2*vev**2)/4. + (ee**2*FM3*complex(0,1)*sw**2*vev**2)/4. - (ee**2*FM7*complex(0,1)*sw**2*vev**2)/8. + (ee**2*FM5*complex(0,1)*sw**3*vev**2)/(4.*cw) + (ee**2*FM1*complex(0,1)*sw**4*vev**2)/(8.*cw**2) - (ee**2*FM7*complex(0,1)*sw**4*vev**2)/(16.*cw**2)',
                  order = {'NP':1})

GC_301 = Coupling(name = 'GC_301',
                  value = '-((complex(0,1)*yb)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_302 = Coupling(name = 'GC_302',
                  value = '-((complex(0,1)*yc)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_303 = Coupling(name = 'GC_303',
                  value = '-((complex(0,1)*ym)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_304 = Coupling(name = 'GC_304',
                  value = '-((complex(0,1)*ys)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_305 = Coupling(name = 'GC_305',
                  value = '-((complex(0,1)*yt)/cmath.sqrt(2))',
                  order = {'QED':1})

GC_306 = Coupling(name = 'GC_306',
                  value = '-((complex(0,1)*ytau)/cmath.sqrt(2))',
                  order = {'QED':1})

