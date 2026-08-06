# Ensemble Evidence

A sum `W = Σxᵢ` does not automatically measure wisdom. It can amplify bias, duplicated sources, correlated errors, majority error, model collapse and contamination.

A safer starting model is `W = Σ(wᵢxᵢ) / Σwᵢ`, with documented weights for source independence, calibration, evidence quality, recency, expertise, uncertainty and duplication penalty. Weighting assumptions, correlations and sensitivity analyses must remain visible.
