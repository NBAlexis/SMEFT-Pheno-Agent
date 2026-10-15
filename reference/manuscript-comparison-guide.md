# Manuscript Comparison Guide

Use this guide before drafting Phase 10 when the user has provided `List.txt` or
reference-paper PDFs. These papers are writing and comparison references, not
default citation targets.

The skill does not bundle these papers. If paper-specific details are needed,
retrieve the paper from arXiv/DOI or use files explicitly provided by the user in
the active workspace.

## Output

Build:

```
results/data/phase10/reference_paper_plan.json
```

The plan records which papers were used as structural, methodological, or result
comparison references.

```json
{
  "style_references": ["P27"],
  "method_references": ["P16", "P34"],
  "result_comparison_references": [],
  "papers_to_cite": [],
  "quality_dimensions": {
    "analysis_context": "P27",
    "dataset_and_sample_detail": "P27",
    "algorithm_explanation": ["P16", "P34"],
    "fit_and_constraint_presentation": "P27",
    "discussion_and_limitations": "P32"
  },
  "notes": {
    "P27": "Use section organization and dataset-detail level as a writing reference."
  }
}
```

`papers_to_cite` must stay empty unless the manuscript directly compares with,
quotes, or relies on a specific paper. If a paper is added to `papers_to_cite`,
also add it to `literature_plan.json` under `comparison_citations`.

## Reference Paper Map

| ID | Use as comparison/reference object | arXiv | Paper title |
|---|---|---|---|
| P16 | anomaly-detection method reference | 2103.03151 | Detecting anomalous quartic gauge couplings using the isolation forest machine learning algorithm |
| P27 | muon-collider aQGC paper structure and PCA-style anomaly-detection reference | 2304.01505 | Searching for anomalous quartic gauge couplings at muon colliders using principal component analysis |
| P31 | k-means event-selection workflow reference | 2302.01274 | Using k-means assistant event selection strategy to study anomalous quartic gauge couplings at muon colliders |
| P32 | autoencoder/gQGC workflow reference | 2311.16627 | Searching for gluon quartic gauge couplings at muon colliders using the autoencoder |
| P34 | SVM/QSVM event-selection workflow reference | 2311.15280 | Optimize the event selection strategy to study the anomalous quartic gauge couplings at muon colliders using the support vector machine and quantum support vector machine |
| P40 | nested local outlier factor workflow reference | 2504.03145 | Search for anomalous quartic gauge couplings in the process mu+mu- to nu nubar gamma gamma with a nested local outlier factor |

## Use Rules

- Use reference papers to calibrate scientific completeness: section structure,
  dataset tables, feature definitions, algorithm descriptions, fit tables, and
  constraint presentation, result interpretation, and limitations.
- Before drafting, record in `quality_dimensions` which structural lesson from a
  reference paper is being adopted. This is a writing-quality aid, not a request
  to copy that paper's physics or to cite it automatically.
- Do not cite a reference paper merely because it was used as a style reference.
- Cite a reference paper only for an explicit scientific comparison, prior result,
  or method claim in the final text.
- If the current process, collider, or algorithm does not match any listed paper,
  use the closest paper only for format/style expectations, not for physics claims.

The comparison plan may also record **quality dimensions**, meaning the aspects
of article presentation used to calibrate depth: analysis context, dataset
detail, algorithm explanation, fit/constraint presentation, and
discussion/limitations. These are writing dimensions, not additional scientific
deliverables and not automatic citation requirements.
