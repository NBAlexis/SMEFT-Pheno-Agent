# Significance and Constraint Roots

Use this reference as the single source of truth anywhere the workflow computes
a scan range, threshold criterion, or final coefficient constraint.

## Statistical Significance

Use the Asimov formula:

```text
S_stat = sqrt(2 * ((N_bg + N_sig) * log(1 + N_sig / N_bg) - N_sig))
```

with:

- `L` is the integrated luminosity converted to the inverse unit matching the
  cross-section unit used in the fit
- In this workflow, MG5/banner cross-sections are normally in pb and Phase 1
  collects luminosity in fb^-1, so `L = luminosity_fb * 1000` in pb^-1
- `N_bg = L * sigma0_after_cut`
- `N_sig = L * (sigma(c) - sigma0_after_cut)`
- `sigma(c) = sigma0_after_cut + c * sigma_int + c^2 * sigma_NP`
- `sigma0_after_cut` is the fixed selected cross-section at coefficient
  `c = 0` from the scan after all cuts/selection. It is not a fitted parameter.

The factor `1000` is only the unit conversion `fb^-1 -> pb^-1`. If a fit stores
cross-sections in another unit, convert luminosity to the corresponding inverse
unit instead of mechanically multiplying by `1000`.

When the fit is expressed in a normalized coefficient `f`, use:

```text
sigma(f) = sigma0_after_cut + f * sigma_int + f^2 * sigma_NP
N_sig(f) = L * (f * sigma_int + f^2 * sigma_NP)
```

For Phase 8/9 fits, obtain `sigma0_after_cut` from the `f = 0` scan point. With
the standard 11-point scan expression, this is label `f5`. Do not fit the
constant term.

Do not use `N_sig / sqrt(N_bg + N_sig)` or
`N_sig / sqrt(N_bg)` unless the user explicitly selects a standard
approximation. Phase 4, Phase 8, Phase 9, and the manuscript must all use the
same formula above by default.

## Solving Constraints

For each requested significance level `S`, solve:

```text
S_stat(x) = S
```

where `x` is the coefficient variable used by the fit. The coefficient
constraint is defined by the real roots of this equation. Polynomial or
symbolic solvers may also return extraneous complex roots.

The solver may return extra complex roots. Filter roots as follows:

1. Keep only roots with finite real and imaginary parts.
2. Treat a root as real only if `abs(imag(root)) < 1e-8 * max(1, abs(real(root)))`.
3. The upper bound is the smallest positive real root.
4. The lower bound is the largest negative real root.
5. If either side is missing, record `null` for that side and preserve the root list in diagnostics.

The interval is `[lower_bound, upper_bound]`. Do not force symmetry unless the
solver or physics approximation explicitly assumes a symmetric interval.

## Phase 4 Range Estimate

Phase 4 may have only the anchor default-point cross-section. In that case use
the available anchor approximation for `N_sig(c)` but still solve the Asimov
equation numerically. Archive the approximation used in `sm_baseline.json`.
