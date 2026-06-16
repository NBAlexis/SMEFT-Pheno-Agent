# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 13.3.1 for Microsoft Windows (64-bit) (July 24, 2023)
# Date: Fri 29 May 2026 21:35:48


from object_library import all_lorentz, Lorentz

from function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot
try:
   import form_factors as ForFac 
except ImportError:
   pass


UUV2 = Lorentz(name = 'UUV2',
               spins = [ -1, -1, 3 ],
               structure = 'P(3,2) + P(3,3)')

SSS2 = Lorentz(name = 'SSS2',
               spins = [ 1, 1, 1 ],
               structure = '1')

FFS2 = Lorentz(name = 'FFS2',
               spins = [ 2, 2, 1 ],
               structure = 'ProjM(2,1) + ProjP(2,1)')

FFV6 = Lorentz(name = 'FFV6',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,1)')

FFV7 = Lorentz(name = 'FFV7',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,-1)*ProjM(-1,1)')

FFV8 = Lorentz(name = 'FFV8',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,-1)*ProjM(-1,1) - 2*Gamma(3,2,-1)*ProjP(-1,1)')

FFV9 = Lorentz(name = 'FFV9',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,-1)*ProjM(-1,1) + 2*Gamma(3,2,-1)*ProjP(-1,1)')

FFV10 = Lorentz(name = 'FFV10',
                spins = [ 2, 2, 3 ],
                structure = 'Gamma(3,2,-1)*ProjM(-1,1) + 4*Gamma(3,2,-1)*ProjP(-1,1)')

VVS2 = Lorentz(name = 'VVS2',
               spins = [ 3, 3, 1 ],
               structure = 'Metric(1,2)')

VVV2 = Lorentz(name = 'VVV2',
               spins = [ 3, 3, 3 ],
               structure = 'P(3,1)*Metric(1,2) - P(3,2)*Metric(1,2) - P(2,1)*Metric(1,3) + P(2,3)*Metric(1,3) + P(1,2)*Metric(2,3) - P(1,3)*Metric(2,3)')

SSSS2 = Lorentz(name = 'SSSS2',
                spins = [ 1, 1, 1, 1 ],
                structure = '1')

SSSS3 = Lorentz(name = 'SSSS3',
                spins = [ 1, 1, 1, 1 ],
                structure = 'P(-2,3)*P(-2,4)*P(-1,1)*P(-1,2) + P(-2,2)*P(-2,4)*P(-1,1)*P(-1,3) + P(-2,2)*P(-2,3)*P(-1,1)*P(-1,4)')

VVSS3 = Lorentz(name = 'VVSS3',
                spins = [ 3, 3, 1, 1 ],
                structure = 'P(1,4)*P(2,3) + P(1,3)*P(2,4)')

VVSS4 = Lorentz(name = 'VVSS4',
                spins = [ 3, 3, 1, 1 ],
                structure = 'Metric(1,2)')

VVSS5 = Lorentz(name = 'VVSS5',
                spins = [ 3, 3, 1, 1 ],
                structure = 'P(-1,3)*P(-1,4)*Metric(1,2)')

VVSS6 = Lorentz(name = 'VVSS6',
                spins = [ 3, 3, 1, 1 ],
                structure = 'P(1,4)*P(2,3) + P(1,3)*P(2,4) - P(-1,3)*P(-1,4)*Metric(1,2)')

VVVS4 = Lorentz(name = 'VVVS4',
                spins = [ 3, 3, 3, 1 ],
                structure = 'P(2,4)*Metric(1,3) - P(1,4)*Metric(2,3)')

VVVV24 = Lorentz(name = 'VVVV24',
                 spins = [ 3, 3, 3, 3 ],
                 structure = 'Metric(1,4)*Metric(2,3) - Metric(1,3)*Metric(2,4)')

VVVV25 = Lorentz(name = 'VVVV25',
                 spins = [ 3, 3, 3, 3 ],
                 structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4)')

VVVV26 = Lorentz(name = 'VVVV26',
                 spins = [ 3, 3, 3, 3 ],
                 structure = 'Metric(1,2)*Metric(3,4)')

VVVV27 = Lorentz(name = 'VVVV27',
                 spins = [ 3, 3, 3, 3 ],
                 structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4) - 2*Metric(1,2)*Metric(3,4)')

VVVV28 = Lorentz(name = 'VVVV28',
                 spins = [ 3, 3, 3, 3 ],
                 structure = 'Metric(1,4)*Metric(2,3) - Metric(1,2)*Metric(3,4)')

VVVV29 = Lorentz(name = 'VVVV29',
                 spins = [ 3, 3, 3, 3 ],
                 structure = 'Metric(1,3)*Metric(2,4) - Metric(1,2)*Metric(3,4)')

VVVV30 = Lorentz(name = 'VVVV30',
                 spins = [ 3, 3, 3, 3 ],
                 structure = 'Metric(1,4)*Metric(2,3) - (Metric(1,3)*Metric(2,4))/2. - (Metric(1,2)*Metric(3,4))/2.')

VVVV31 = Lorentz(name = 'VVVV31',
                 spins = [ 3, 3, 3, 3 ],
                 structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4) + Metric(1,2)*Metric(3,4)')

VVSSS1 = Lorentz(name = 'VVSSS1',
                 spins = [ 3, 3, 1, 1, 1 ],
                 structure = 'P(1,4)*P(2,3) + P(1,5)*P(2,3) + P(1,3)*P(2,4) + P(1,5)*P(2,4) + P(1,3)*P(2,5) + P(1,4)*P(2,5)')

VVSSS2 = Lorentz(name = 'VVSSS2',
                 spins = [ 3, 3, 1, 1, 1 ],
                 structure = 'P(1,4)*P(2,3) + P(1,5)*P(2,3) + P(1,3)*P(2,4) + P(1,5)*P(2,4) + P(1,3)*P(2,5) + P(1,4)*P(2,5) - P(-1,3)*P(-1,4)*Metric(1,2) - P(-1,3)*P(-1,5)*Metric(1,2) - P(-1,4)*P(-1,5)*Metric(1,2)')

VVSSS3 = Lorentz(name = 'VVSSS3',
                 spins = [ 3, 3, 1, 1, 1 ],
                 structure = 'P(-1,3)*P(-1,4)*Metric(1,2) + P(-1,3)*P(-1,5)*Metric(1,2) + P(-1,4)*P(-1,5)*Metric(1,2)')

VVVSS4 = Lorentz(name = 'VVVSS4',
                 spins = [ 3, 3, 3, 1, 1 ],
                 structure = 'P(2,4)*Metric(1,3) + P(2,5)*Metric(1,3) - P(1,4)*Metric(2,3) - P(1,5)*Metric(2,3)')

VVVVS10 = Lorentz(name = 'VVVVS10',
                  spins = [ 3, 3, 3, 3, 1 ],
                  structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4)')

VVVVS11 = Lorentz(name = 'VVVVS11',
                  spins = [ 3, 3, 3, 3, 1 ],
                  structure = 'Metric(1,2)*Metric(3,4)')

VVVVS12 = Lorentz(name = 'VVVVS12',
                  spins = [ 3, 3, 3, 3, 1 ],
                  structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4) + Metric(1,2)*Metric(3,4)')

VVSSSS1 = Lorentz(name = 'VVSSSS1',
                  spins = [ 3, 3, 1, 1, 1, 1 ],
                  structure = 'P(1,4)*P(2,3) + P(1,5)*P(2,3) + P(1,6)*P(2,3) + P(1,3)*P(2,4) + P(1,5)*P(2,4) + P(1,6)*P(2,4) + P(1,3)*P(2,5) + P(1,4)*P(2,5) + P(1,6)*P(2,5) + P(1,3)*P(2,6) + P(1,4)*P(2,6) + P(1,5)*P(2,6)')

VVSSSS2 = Lorentz(name = 'VVSSSS2',
                  spins = [ 3, 3, 1, 1, 1, 1 ],
                  structure = 'P(1,4)*P(2,3) + P(1,5)*P(2,3) + P(1,6)*P(2,3) + P(1,3)*P(2,4) + P(1,5)*P(2,4) + P(1,6)*P(2,4) + P(1,3)*P(2,5) + P(1,4)*P(2,5) + P(1,6)*P(2,5) + P(1,3)*P(2,6) + P(1,4)*P(2,6) + P(1,5)*P(2,6) - P(-1,3)*P(-1,4)*Metric(1,2) - P(-1,3)*P(-1,5)*Metric(1,2) - P(-1,4)*P(-1,5)*Metric(1,2) - P(-1,3)*P(-1,6)*Metric(1,2) - P(-1,4)*P(-1,6)*Metric(1,2) - P(-1,5)*P(-1,6)*Metric(1,2)')

VVSSSS3 = Lorentz(name = 'VVSSSS3',
                  spins = [ 3, 3, 1, 1, 1, 1 ],
                  structure = 'P(-1,3)*P(-1,4)*Metric(1,2) + P(-1,3)*P(-1,5)*Metric(1,2) + P(-1,4)*P(-1,5)*Metric(1,2) + P(-1,3)*P(-1,6)*Metric(1,2) + P(-1,4)*P(-1,6)*Metric(1,2) + P(-1,5)*P(-1,6)*Metric(1,2)')

VVVSSS1 = Lorentz(name = 'VVVSSS1',
                  spins = [ 3, 3, 3, 1, 1, 1 ],
                  structure = 'P(2,4)*Metric(1,3) + P(2,5)*Metric(1,3) + P(2,6)*Metric(1,3) - P(1,4)*Metric(2,3) - P(1,5)*Metric(2,3) - P(1,6)*Metric(2,3)')

VVVVSS10 = Lorentz(name = 'VVVVSS10',
                   spins = [ 3, 3, 3, 3, 1, 1 ],
                   structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4)')

VVVVSS11 = Lorentz(name = 'VVVVSS11',
                   spins = [ 3, 3, 3, 3, 1, 1 ],
                   structure = 'Metric(1,2)*Metric(3,4)')

VVVVSS12 = Lorentz(name = 'VVVVSS12',
                   spins = [ 3, 3, 3, 3, 1, 1 ],
                   structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4) + Metric(1,2)*Metric(3,4)')

VVVSSSS1 = Lorentz(name = 'VVVSSSS1',
                   spins = [ 3, 3, 3, 1, 1, 1, 1 ],
                   structure = 'P(2,4)*Metric(1,3) + P(2,5)*Metric(1,3) + P(2,6)*Metric(1,3) + P(2,7)*Metric(1,3) - P(1,4)*Metric(2,3) - P(1,5)*Metric(2,3) - P(1,6)*Metric(2,3) - P(1,7)*Metric(2,3)')

VVVVSSS1 = Lorentz(name = 'VVVVSSS1',
                   spins = [ 3, 3, 3, 3, 1, 1, 1 ],
                   structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4)')

VVVVSSS2 = Lorentz(name = 'VVVVSSS2',
                   spins = [ 3, 3, 3, 3, 1, 1, 1 ],
                   structure = 'Metric(1,2)*Metric(3,4)')

VVVVSSS3 = Lorentz(name = 'VVVVSSS3',
                   spins = [ 3, 3, 3, 3, 1, 1, 1 ],
                   structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4) + Metric(1,2)*Metric(3,4)')

VVVVSSSS1 = Lorentz(name = 'VVVVSSSS1',
                    spins = [ 3, 3, 3, 3, 1, 1, 1, 1 ],
                    structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4)')

VVVVSSSS2 = Lorentz(name = 'VVVVSSSS2',
                    spins = [ 3, 3, 3, 3, 1, 1, 1, 1 ],
                    structure = 'Metric(1,2)*Metric(3,4)')

VVVVSSSS3 = Lorentz(name = 'VVVVSSSS3',
                    spins = [ 3, 3, 3, 3, 1, 1, 1, 1 ],
                    structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4) + Metric(1,2)*Metric(3,4)')

