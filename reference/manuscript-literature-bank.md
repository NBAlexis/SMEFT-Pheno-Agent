# SMEFT and ML-in-HEP Literature Bank

Use this bank for two distinct tasks:

- build `reference_paper_plan.json` from the user-list comparison references
- build `literature_plan.json` from the foundational citation warehouse

Do not cite user-list entries automatically. They are comparison/style
references unless the manuscript directly compares with them or relies on a specific
claim.

## User-List Comparison Reference Map

| ID | Topic | Reference | arXiv | DOI | Use as comparison/reference object |
|---|---|---|---|---|---|
| P10 | LHC aQGC constraint baseline | Y.-C. Guo, Y.-Y. Wang, J.-C. Yang, C.-X. Yue, Chin. Phys. C 44, 123105 (2020) | 2002.03326 | 10.1088/1674-1137/abb4d2 | prior aQGC collider constraints |
| P12 | gamma gamma to WW aQGC | Y.-C. Guo, Y.-Y. Wang, J.-C. Yang, Nucl. Phys. B 961, 115222 (2020) | 1912.10686 | 10.1016/j.nuclphysb.2020.115222 | photon-induced aQGC/VBS context |
| P15 | Z gamma jj aQGC at LHC | J.-C. Yang, Y.-C. Guo, C.-X. Yue, Q. Fu, Phys. Rev. D 104, 035015 (2021) | 2107.01123 | 10.1103/PhysRevD.104.035015 | electroweak-boson plus jets aQGC context |
| P16 | Isolation Forest for aQGC | L. Jiang, Y.-C. Guo, J.-C. Yang, Phys. Rev. D 104, 035021 (2021) | 2103.03151 | 10.1103/PhysRevD.104.035021 | anomaly-detection motivation; few and kinematically different events |
| P17 | ANN for aQGC energy scale | J.-C. Yang, J.-H. Chen, Y.-C. Guo, JHEP 09, 085 (2021) | 2107.13624 | 10.1007/JHEP09(2021)085 | neural-network assisted aQGC phenomenology |
| P18 | nTGC e+e- with unitarity | Q. Fu, J.-C. Yang, C.-X. Yue, Y.-C. Guo, Nucl. Phys. B 972, 115543 (2021) | 2102.03623 | 10.1016/j.nuclphysb.2021.115543 | nTGC theory and e+e- collider context |
| P21 | Nested AD for nTGC | J.-C. Yang, Y.-C. Guo, L.-H. Cai, Nucl. Phys. B 977, 115735 (2022) | 2111.10543 | 10.1016/j.nuclphysb.2022.115735 | nested anomaly detection and nTGC ML context |
| P22 | tri-photon aQGC at muon collider | J.-C. Yang, Z.-B. Qin, X.-Y. Han, Y.-C. Guo, T. Li, JHEP 07, 053 (2022) | 2204.08195 | 10.1007/JHEP07(2022)053 | muon-collider tri-photon process motivation |
| P23 | ANN for WW scattering at muon collider | J.-C. Yang, X.-Y. Han, Z.-B. Qin, T. Li, Y.-C. Guo, JHEP 09, 074 (2022) | 2204.10034 | 10.1007/JHEP09(2022)074 | supervised ML for aQGC at muon colliders |
| P25 | magnetic monopoles at muon colliders | J.-C. Yang, Y.-C. Guo, B. Liu, T. Li, Nucl. Phys. B 987, 116097 (2023) | 2208.02188 | 10.1016/j.nuclphysb.2023.116097 | high-energy muon-collider BSM motivation |
| P26 | charged-current NSI at LHC/HL-LHC | C.-X. Yue, X.-J. Cheng, J.-C. Yang, Chin. Phys. C 47, 043111 (2023) | 2110.01204 | 10.1088/1674-1137/acb993 | non-SMEFT BSM collider comparison when relevant |
| P27 | PCA for aQGC at muon colliders | Y.-F. Dong, Y.-C. Mao, J.-C. Yang, Eur. Phys. J. C 83, 555 (2023) | 2304.01505 | 10.1140/epjc/s10052-023-11719-0 | PCA/anomaly detection; muon-collider aQGC paper structure |
| P28 | gQGC at muon colliders | J.-C. Yang, Y.-C. Guo, Y.-F. Dong, Commun. Theor. Phys. 75, 115201 (2023) | 2307.04207 | 10.1088/1572-9494/acfd14 | gluonic quartic gauge couplings context |
| P29 | MLAnalysis framework | Y.-C. Guo, F. Feng, A. Di, S.-Q. Lu, J.-C. Yang, Comput. Phys. Commun. 294, 108957 (2024) | 2305.00964 | 10.1016/j.cpc.2023.108957 | CutExperiment/MLAnalysis citation and feature extraction framework |
| P31 | k-means event selection | S. Zhang, J.-C. Yang, Y.-C. Guo, Eur. Phys. J. C 84, 142 (2024) | 2302.01274 | 10.1140/epjc/s10052-024-12494-2 | k-means assisted event selection; algorithm comparison context |
| P32 | Autoencoder for gQGC | Y.-T. Zhang, X.-T. Wang, J.-C. Yang, Phys. Rev. D 109, 095028 (2024) | 2311.16627 | 10.1103/PhysRevD.109.095028 | autoencoder/anomaly detection and gQGC context |
| P34 | SVM/QSVM event selection | S. Zhang, Y.-C. Guo, J.-C. Yang, Eur. Phys. J. C 84, 833 (2024) | 2311.15280 | 10.1140/epjc/s10052-024-13208-4 | supervised classifier and quantum-SVM event selection |
| P36 | quantum kernel k-means | S. Zhang, K.-X. Chen, J.-C. Yang, Eur. Phys. J. C 85, 378 (2025) | 2409.07010 | 10.1140/epjc/s10052-025-14069-1 | quantum-kernel k-means and quantum-accelerable ML |
| P37 | nTGC ZZ production at e+e- colliders | Y.-C. Guo, M.-Q. Ruan, J.-C. Yang, C.-J. Pan, Phys. Rev. D 112, 035033 (2025) | unavailable in List.txt | 10.1103/z1sc-f8m4 | nTGC collider baseline when the process is ZZ/e+e- related |
| P40 | NLOF for aQGC | K.-X. Chen, Y.-C. Guo, J.-C. Yang, SciPost Phys. Core 8, 091 (2025) | 2504.03145 | 10.21468/SciPostPhysCore.8.4.091 | nested LOF, unsupervised anomaly score with supervised EFT sensitivity optimization |
| P41 | nTGC at muon colliders | W. Xie, J.-C. Yang, JHEP 12, 127 (2025) | 2507.08681 | 10.1007/JHEP12(2025)127 | muon-collider nTGC process motivation |
| P42 | quantum ML classifier for NP | J.-C. Yang, S. Zhang, C.-X. Yue, JHEP 01, 023 (2026) | 2410.18847 | 10.1007/JHEP01(2026)023 | QML classifier and future ML-in-HEP discussion |

## Foundational SMEFT/ML-in-HEP Warehouse

Use these references for background claims that should not rely only on the
user's own papers.

| ID | Topic | Reference | arXiv/DOI | Use in manuscript |
|---|---|---|---|---|
| F-SMEFT-1 | SMEFT origin | S. Weinberg, Phys. Rev. Lett. 43, 1566 (1979) | DOI: 10.1103/PhysRevLett.43.1566 | effective-operator expansion motivation |
| F-SMEFT-2 | Warsaw basis | B. Grzadkowski et al., JHEP 10, 085 (2010) | arXiv:1008.4884; DOI: 10.1007/JHEP10(2010)085 | dimension-six SMEFT basis context |
| F-SMEFT-3 | SMEFT review | S. Willenbrock and C. Zhang, Ann. Rev. Nucl. Part. Sci. 64, 83 (2014) | arXiv:1401.0470; DOI: 10.1146/annurev-nucl-102313-025623 | concise SMEFT overview |
| F-DIM8-1 | dimension-eight counting | B. Henning et al., JHEP 08, 016 (2017) | arXiv:1512.03433; DOI: 10.1007/JHEP08(2017)016 | dimension-eight operator-count statements |
| F-AQGC-1 | aQGC operator basis | O. J. P. Eboli et al., Phys. Rev. D 74, 073005 (2006) | hep-ph/0606118; DOI: 10.1103/PhysRevD.74.073005 | classic aQGC operator definitions |
| F-AQGC-2 | dimension-eight aQGC basis | O. J. P. Eboli and M. C. Gonzalez-Garcia, Phys. Rev. D 93, 093013 (2016) | arXiv:1604.03555; DOI: 10.1103/PhysRevD.93.093013 | modern aQGC parameterization |
| F-AQGC-3 | aQGC model implementation | C. Degrande, JHEP 02, 101 (2014) | arXiv:1308.6323; DOI: 10.1007/JHEP02(2014)101 | UFO/aQGC implementation context |
| F-VBS-1 | VBS review | D. R. Green, P. Meade, M.-A. Pleier, Rev. Mod. Phys. 89, 035008 (2017) | arXiv:1610.07572; DOI: 10.1103/RevModPhys.89.035008 | vector-boson-scattering motivation |
| F-MLHEP-1 | ML in HEP overview | A. Radovic et al., Nature 560, 41 (2018) | DOI: 10.1038/s41586-018-0361-2 | broad ML-in-HEP motivation |
| F-MLHEP-2 | deep learning for HEP | P. Baldi, P. Sadowski, D. Whiteson, Nat. Commun. 5, 4308 (2014) | DOI: 10.1038/ncomms5308 | supervised classifier motivation |
| F-AD-1 | LHC Olympics anomaly benchmark | G. Kasieczka et al. (2021) | arXiv:2101.08320 | anomaly-detection benchmark context |
| F-IF-1 | isolation forest | F. T. Liu, K. M. Ting, Z.-H. Zhou, ICDM (2008) | DOI: 10.1109/ICDM.2008.17 | Isolation Forest algorithm source |
| F-AE-1 | autoencoder anomaly detection | M. Farina, Y. Nakai, D. Shih, Phys. Rev. D 101, 075021 (2020) | arXiv:1808.08992; DOI: 10.1103/PhysRevD.101.075021 | autoencoder/anomaly-search background |
| F-SKLEARN-1 | scikit-learn | F. Pedregosa et al., JMLR 12, 2825 (2011) | arXiv:1201.0490 | cite when sklearn algorithms are used |

## Selection Rules

- For aQGC processes, use P10, P12, or P15 as comparison references when relevant.
- For muon-collider aQGC studies, prefer P22 plus the algorithm-matched user-list paper as writing/comparison references.
- For nTGC processes, use P18, P21, and P41 as comparison references when relevant.
- For ML/anomaly-detection method comparison, prefer P16, P21, P27, P31, P32, P34, P36, or P40 based on the algorithm family.
- For CutExperiment/feature extraction, cite P29.
- For quantum or quantum-accelerable ML claims, cite P34, P36, or P42 only when the manuscript actually discusses those algorithms.
- For general SMEFT/aQGC definitions, include at least one foundational entry
  from F-SMEFT-* or F-AQGC-* unless the manuscript contains only UFO-parameter
  descriptions and no SMEFT/aQGC theory claims.
- For generic ML-in-HEP motivation, include F-MLHEP-1 or F-AD-1 in addition
  to any user-list method paper used for comparison.
- Use foundational entries to support broad textbook-style claims; use user-list
  entries to calibrate process-, collider-, and algorithm-specific comparison.

## Reusable Citation Claims

Use these as claim templates. Select foundational citations for broad SMEFT/ML claims. Use user-list comparison references only when they are cited through `comparison_citations` because the manuscript directly compares with them or relies on a specific claim.

- New-physics signals can be rare and kinematically different from SM backgrounds; anomaly-detection methods exploit this structure.
- Dimension-8 operators are important in aQGC phenomenology, especially in channels where lower-dimensional contributions are absent or suppressed.
- Muon colliders provide clean, high-energy environments for electroweak and gauge-coupling studies.
- ML-assisted event selection can exploit correlations in multidimensional kinematic observables beyond rectangular cuts.
- Algorithm performance for event selection is task-dependent; AUC is
  descriptive or diagnostic only, while final strategy comparison uses expected
  coefficient-constraint interval width from fitted selected cross-sections.
