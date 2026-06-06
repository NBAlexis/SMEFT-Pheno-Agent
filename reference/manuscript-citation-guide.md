# Manuscript Citation Guide

Build `results/data/phase10/literature_plan.json` before drafting citations and
bibliography entries. The plan records which citation objects are used in which
section and why.

Read [`manuscript-literature-bank.md`](manuscript-literature-bank.md) before selecting
domain citations. It contains:

- a reusable SMEFT/aQGC/nTGC/ML-in-HEP citation warehouse
- user-list paper metadata only when a paper is actually cited because the
  manuscript directly compares with it or relies on a method from it

Do not treat the user's `List.txt` papers as default bibliography entries. Those
papers are primarily writing/comparison references; use
[`manuscript-comparison-guide.md`](manuscript-comparison-guide.md) for that role.

## Mandatory Toolchain References

Always cite tools that were actually used:

| Tool | Reference | DOI | arXiv |
|---|---|---|---|
| MadGraph5_aMC@NLO | J. Alwall et al., JHEP 07, 079 (2014) | 10.1007/JHEP07(2014)079 | 1405.0301 |
| FeynRules | N. D. Christensen and C. Duhr, Comput. Phys. Commun. 180, 1614 (2009) | 10.1016/j.cpc.2009.02.018 | 0806.4194 |
| UFO | C. Degrande et al., Comput. Phys. Commun. 183, 1201 (2012) | 10.1016/j.cpc.2012.01.022 | 1108.2040 |
| Delphes | J. de Favereau et al., JHEP 02, 057 (2014) | 10.1007/JHEP02(2014)057 | 1307.6346 |
| Pythia 8 | T. Sjostrand et al., Comput. Phys. Commun. 191, 159 (2015) | 10.1016/j.cpc.2015.01.024 | 1410.3012 |
| LHAPDF | A. Buckley et al., Eur. Phys. J. C 75, 132 (2015) | 10.1140/epjc/s10052-015-3318-8 | 1412.7420 |
| MLAnalysis / CutExperiment | Y.-C. Guo et al., Comput. Phys. Commun. 294, 108957 (2024) | 10.1016/j.cpc.2023.108957 | 2305.00964 |

CutExperiment is the development branch of MLAnalysis and shares the MLAnalysis
citation.

## Literature Plan Structure

`literature_plan.json` must separate actual citations by role:

```json
{
  "toolchain": ["MadGraph5_aMC@NLO", "FeynRules", "UFO"],
  "foundational": ["F-SMEFT-1", "F-AQGC-2", "F-MLHEP-1"],
  "comparison_citations": [],
  "section_usage": {
    "Introduction": ["F-SMEFT-3"],
    "Machine Learning Methodology": ["F-MLHEP-1"],
    "Numerical Results": []
  }
}
```

`comparison_citations` is normally empty. Add a user-list paper there only when
the final manuscript explicitly compares with that paper's result or describes that
paper's method as part of the study's motivation.

Do not invent arXiv identifiers. Use the identifiers in
[`manuscript-literature-bank.md`](manuscript-literature-bank.md) or explicit user input.

## Citation Density

Minimum citation expectations:

- Introduction: use enough domain citations to support SMEFT/aQGC/ML motivation, typically up to three when those claims require them.
- Event generation: all actually used toolchain references.
- ML methodology: at least one reference for each nontrivial algorithm family when available.
- Results comparison: cite prior constraints only when the paper makes an explicit comparison.

Do not pad references with unrelated papers.
