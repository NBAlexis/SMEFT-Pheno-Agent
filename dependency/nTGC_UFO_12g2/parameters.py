# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 12.0.0 for Linux x86 (64-bit) (April 7, 2019)
# Date: Sat 29 Mar 2025 16:57:28



from object_library import all_parameters, Parameter


from function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# This is a default parameter object representing 0.
ZERO = Parameter(name = 'ZERO',
                 nature = 'internal',
                 type = 'real',
                 value = '0.0',
                 texname = '0')

# User-defined parameters.
C1 = Parameter(name = 'C1',
               nature = 'external',
               type = 'real',
               value = 1.e-12,
               texname = '\\frac{C_{\\text{wtw1}}}{\\Lambda ^4}',
               lhablock = 'DIM8',
               lhacode = [ 1 ])

C2 = Parameter(name = 'C2',
               nature = 'external',
               type = 'real',
               value = 1.e-12,
               texname = '\\frac{C_{\\text{wtw2}}}{\\Lambda ^4}',
               lhablock = 'DIM8',
               lhacode = [ 2 ])

C3 = Parameter(name = 'C3',
               nature = 'external',
               type = 'real',
               value = 1.e-12,
               texname = '\\frac{C_{\\text{btb1}}}{\\Lambda ^4}',
               lhablock = 'DIM8',
               lhacode = [ 3 ])

C4 = Parameter(name = 'C4',
               nature = 'external',
               type = 'real',
               value = 1.e-12,
               texname = '\\frac{C_{\\text{btb2}}}{\\Lambda ^4}',
               lhablock = 'DIM8',
               lhacode = [ 4 ])

C5 = Parameter(name = 'C5',
               nature = 'external',
               type = 'real',
               value = 1.e-12,
               texname = '\\frac{C_{\\text{btw1}}}{\\Lambda ^4}',
               lhablock = 'DIM8',
               lhacode = [ 5 ])

C6 = Parameter(name = 'C6',
               nature = 'external',
               type = 'real',
               value = 1.e-12,
               texname = '\\frac{C_{\\text{btw2}}}{\\Lambda ^4}',
               lhablock = 'DIM8',
               lhacode = [ 6 ])

C7 = Parameter(name = 'C7',
               nature = 'external',
               type = 'real',
               value = 1.e-12,
               texname = '\\frac{C_{\\text{wtb}}}{\\Lambda ^4}',
               lhablock = 'DIM8',
               lhacode = [ 7 ])

C8 = Parameter(name = 'C8',
               nature = 'external',
               type = 'real',
               value = 1.e-12,
               texname = '\\frac{C_{\\text{bw}}}{\\Lambda ^4}',
               lhablock = 'DIM8',
               lhacode = [ 8 ])

C9 = Parameter(name = 'C9',
               nature = 'external',
               type = 'real',
               value = 1.e-12,
               texname = '\\frac{C_{\\text{ww}}}{\\Lambda ^4}',
               lhablock = 'DIM8',
               lhacode = [ 9 ])

C10 = Parameter(name = 'C10',
                nature = 'external',
                type = 'real',
                value = 1.e-12,
                texname = '\\frac{C_{\\text{bb}}}{\\Lambda ^4}',
                lhablock = 'DIM8',
                lhacode = [ 10 ])

Cg1 = Parameter(name = 'Cg1',
                nature = 'external',
                type = 'real',
                value = 1.e-12,
                texname = '\\frac{C_{g_1}}{\\Lambda ^4}',
                lhablock = 'DIM8',
                lhacode = [ 11 ])

Cg2 = Parameter(name = 'Cg2',
                nature = 'external',
                type = 'real',
                value = 1.e-12,
                texname = '\\frac{C_{\\text{g2}}}{\\Lambda ^4}',
                lhablock = 'DIM8',
                lhacode = [ 12 ])

Cg3 = Parameter(name = 'Cg3',
                nature = 'external',
                type = 'real',
                value = 1.e-12,
                texname = '\\frac{C_{\\text{g3}}}{\\Lambda ^4}',
                lhablock = 'DIM8',
                lhacode = [ 13 ])

Cg4 = Parameter(name = 'Cg4',
                nature = 'external',
                type = 'real',
                value = 1.e-12,
                texname = '\\frac{C_{\\text{g4}}}{\\Lambda ^4}',
                lhablock = 'DIM8',
                lhacode = [ 14 ])

aEWM1 = Parameter(name = 'aEWM1',
                  nature = 'external',
                  type = 'real',
                  value = 127.9,
                  texname = '\\text{aEWM1}',
                  lhablock = 'SMINPUTS',
                  lhacode = [ 1 ])

Gf = Parameter(name = 'Gf',
               nature = 'external',
               type = 'real',
               value = 0.0000116637,
               texname = 'G_f',
               lhablock = 'SMINPUTS',
               lhacode = [ 2 ])

aS = Parameter(name = 'aS',
               nature = 'external',
               type = 'real',
               value = 0.1184,
               texname = '\\alpha _s',
               lhablock = 'SMINPUTS',
               lhacode = [ 3 ])

ymb = Parameter(name = 'ymb',
                nature = 'external',
                type = 'real',
                value = 4.7,
                texname = '\\text{ymb}',
                lhablock = 'YUKAWA',
                lhacode = [ 5 ])

ymt = Parameter(name = 'ymt',
                nature = 'external',
                type = 'real',
                value = 172,
                texname = '\\text{ymt}',
                lhablock = 'YUKAWA',
                lhacode = [ 6 ])

ymtau = Parameter(name = 'ymtau',
                  nature = 'external',
                  type = 'real',
                  value = 1.777,
                  texname = '\\text{ymtau}',
                  lhablock = 'YUKAWA',
                  lhacode = [ 15 ])

MZ = Parameter(name = 'MZ',
               nature = 'external',
               type = 'real',
               value = 91.1876,
               texname = '\\text{MZ}',
               lhablock = 'MASS',
               lhacode = [ 23 ])

MTA = Parameter(name = 'MTA',
                nature = 'external',
                type = 'real',
                value = 1.777,
                texname = '\\text{MTA}',
                lhablock = 'MASS',
                lhacode = [ 15 ])

MT = Parameter(name = 'MT',
               nature = 'external',
               type = 'real',
               value = 172,
               texname = '\\text{MT}',
               lhablock = 'MASS',
               lhacode = [ 6 ])

MB = Parameter(name = 'MB',
               nature = 'external',
               type = 'real',
               value = 4.7,
               texname = '\\text{MB}',
               lhablock = 'MASS',
               lhacode = [ 5 ])

MH = Parameter(name = 'MH',
               nature = 'external',
               type = 'real',
               value = 125,
               texname = '\\text{MH}',
               lhablock = 'MASS',
               lhacode = [ 25 ])

WZ = Parameter(name = 'WZ',
               nature = 'external',
               type = 'real',
               value = 2.4952,
               texname = '\\text{WZ}',
               lhablock = 'DECAY',
               lhacode = [ 23 ])

WW = Parameter(name = 'WW',
               nature = 'external',
               type = 'real',
               value = 2.085,
               texname = '\\text{WW}',
               lhablock = 'DECAY',
               lhacode = [ 24 ])

WT = Parameter(name = 'WT',
               nature = 'external',
               type = 'real',
               value = 1.50833649,
               texname = '\\text{WT}',
               lhablock = 'DECAY',
               lhacode = [ 6 ])

WH = Parameter(name = 'WH',
               nature = 'external',
               type = 'real',
               value = 0.00407,
               texname = '\\text{WH}',
               lhablock = 'DECAY',
               lhacode = [ 25 ])

aEW = Parameter(name = 'aEW',
                nature = 'internal',
                type = 'real',
                value = '1/aEWM1',
                texname = '\\alpha _{\\text{EW}}')

G = Parameter(name = 'G',
              nature = 'internal',
              type = 'real',
              value = '2*cmath.sqrt(aS)*cmath.sqrt(cmath.pi)',
              texname = 'G')

MW = Parameter(name = 'MW',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(MZ**2/2. + cmath.sqrt(MZ**4/4. - (aEW*cmath.pi*MZ**2)/(Gf*cmath.sqrt(2))))',
               texname = 'M_W')

ee = Parameter(name = 'ee',
               nature = 'internal',
               type = 'real',
               value = '2*cmath.sqrt(aEW)*cmath.sqrt(cmath.pi)',
               texname = 'e')

sw2 = Parameter(name = 'sw2',
                nature = 'internal',
                type = 'real',
                value = '1 - MW**2/MZ**2',
                texname = '\\text{sw2}')

cw = Parameter(name = 'cw',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(1 - sw2)',
               texname = 'c_w')

sw = Parameter(name = 'sw',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(sw2)',
               texname = 's_w')

g1 = Parameter(name = 'g1',
               nature = 'internal',
               type = 'real',
               value = 'ee/cw',
               texname = 'g_1')

gw = Parameter(name = 'gw',
               nature = 'internal',
               type = 'real',
               value = 'ee/sw',
               texname = 'g_w')

vev = Parameter(name = 'vev',
                nature = 'internal',
                type = 'real',
                value = '(2*MW*sw)/ee',
                texname = '\\text{vev}')

lam = Parameter(name = 'lam',
                nature = 'internal',
                type = 'real',
                value = 'MH**2/(2.*vev**2)',
                texname = '\\text{lam}')

yb = Parameter(name = 'yb',
               nature = 'internal',
               type = 'real',
               value = '(ymb*cmath.sqrt(2))/vev',
               texname = '\\text{yb}')

yt = Parameter(name = 'yt',
               nature = 'internal',
               type = 'real',
               value = '(ymt*cmath.sqrt(2))/vev',
               texname = '\\text{yt}')

ytau = Parameter(name = 'ytau',
                 nature = 'internal',
                 type = 'real',
                 value = '(ymtau*cmath.sqrt(2))/vev',
                 texname = '\\text{ytau}')

muH = Parameter(name = 'muH',
                nature = 'internal',
                type = 'real',
                value = 'cmath.sqrt(lam*vev**2)',
                texname = '\\mu')

