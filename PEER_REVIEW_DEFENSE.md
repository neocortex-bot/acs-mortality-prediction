# Peer Review Defense: Prediksi Mortalitas In-Hospital pada SKA dengan Random Forest

## Angka utama yang harus konsisten saat seminar

- N = 1.524 pasien; kematian = 115 (7,5%); hidup = 1.409.
- Mean AUC across 10 seeds = 0.8157, dibulatkan 0.816; SD = 0.0075; 95% CI = 0.8110 to 0.8204; range = 0.8024 to 0.8247.
- AUC of the averaged out-of-fold prediction vector = 0.8189, dibulatkan 0.819.
- Safety threshold = 0.018455: sensitivity 98.3%, specificity 26.2%, TP = 113, FN = 2, TN = 369, FP = 1.040, PPV = 9.8%, NPV = 99.5%.
- Youden threshold = 0.103981: sensitivity 71.3%, specificity 82.0%, TP = 82, FN = 33, TN = 1.155, FP = 254, PPV = 24.4%, NPV = 97.2%.
- Tiga strata internal: ward 371/2/0,5%; HCU 817/31/3,8%; ICU 336/82/24,4%.
- Head-to-head discrimination: RF AUC = 0.819; GRACE 2.0 AUC = 0.777; delta AUC = 0.042; bootstrap p = 0.029.
- Paired classification at the 20% risk threshold: McNemar p < 0.001. This is not the p-value for the AUC difference.

## Section A: Methodological Rigor

**Q: Why 13 features? Why not all 169 columns?**

**A:**

- The 169 columns include identifiers, administrative fields, outcomes or post-admission information, redundant measurements, and variables with limited availability. Using them all would increase leakage, missingness, and overfitting risk.
- The 13 predictors were restricted to clinically plausible variables available within the first 24 hours: age, ureum, eGFR, HR, Hb, Killip class, SBP, RR, LVEF, LVOT VTI, TAPSE, potassium, and APTT.
- With only 115 events, feature restriction is a form of complexity control. It does not prove that these are the optimal 13 features, and the selection process should be prospectively specified in external validation.
- Feature importance supports interpretation of the fitted model but does not establish causality or justify selecting variables after seeing the outcome.

**Q: Why Random Forest over XGBoost, LightGBM, or Deep Learning?**

**A:**

- Random Forest is a reasonable low-maintenance model for a moderately sized tabular dataset. It captures non-linearities and interactions without requiring their manual specification.
- Internal results favored RF over the implemented XGBoost comparator, with mean AUC 0.816 versus 0.789. This comparison depends on the tuning budget and does not establish universal algorithmic superiority.
- LightGBM was not required to answer the primary clinical question. Deep learning is poorly matched to 1,524 rows and 115 events unless additional structured or unstructured data are available.
- A stronger future benchmark should include penalized logistic regression and equally tuned boosting models under nested or external validation.

**Q: Why is AUC 0.816, and is that clinically useful?**

**A:**

- An AUC of 0.816 means that a randomly selected patient who died receives a higher risk score than a randomly selected survivor about 81.6% of the time.
- This is good internal discrimination, not proof of clinical benefit. AUC does not specify calibration, workload, bed capacity, false-negative harm, or whether decisions improve outcomes.
- Utility depends on the operating point: the safety threshold misses 2 deaths but flags 1,153 patients; the Youden threshold flags 336 patients and misses 33 deaths.
- The model should be described as promising for further validation, not ready for autonomous triage.

**Q: Why was nested CV not used for hyperparameter tuning?**

**A:**

- The final hyperparameters were fixed before the reported 10-seed evaluation, and all preprocessing was confined to training folds. This prevents preprocessing leakage.
- Because hyperparameter exploration was not enclosed in an outer CV loop, the reported performance can still contain tuning optimism. Repeated CV reduces split variance but does not remove this bias.
- The defensible claim is internal validation of a fixed pipeline, not an unbiased estimate after unrestricted model selection.
- External validation is the priority; if tuning continues on this cohort, nested CV should be used for the development-stage estimate.

**Q: Why per-fold median imputation rather than multiple imputation?**

**A:**

- Median imputation is deterministic, robust to skewed laboratory values, and computationally stable inside 50 train-validation cycles.
- The median was learned only from each training fold and then applied to its validation fold. This preserves the separation between development and assessment data.
- Median imputation ignores uncertainty and relationships among variables. It can attenuate associations and is not equivalent to multiple imputation.
- External validation should compare multiple imputation, missingness indicators, and complete-case sensitivity analysis, especially for echocardiographic variables.

**Q: How was class imbalance at 7.5% prevalence handled?**

**A:**

- StratifiedKFold preserved the event proportion in every fold. Performance was not judged by accuracy alone.
- AUC, AUPRC, Brier score, sensitivity, specificity, PPV, NPV, and confusion matrices were reported. AUPRC was 0.301 against a no-skill baseline prevalence of 0.075.
- Thresholds were selected for different clinical priorities. No synthetic observations were introduced, avoiding unrealistic SMOTE samples in a small clinical dataset.
- Class weighting or balanced forests remain legitimate sensitivity analyses, but they require probability recalibration and external assessment.

**Q: Why is there no external validation, and what is the plan?**

**A:**

- The available dataset is a single-center retrospective cohort; no independent center or later temporal cohort was available for this thesis.
- Repeated cross-validation quantifies internal split variability but cannot test transportability across hospitals, periods, workflows, or patient mix.
- The next step is locked-model temporal validation, followed by multicenter geographic validation with no refitting during the primary assessment.
- Evaluation should include discrimination, calibration intercept and slope, subgroup performance, decision curves, and recalibration only after reporting the original model's performance.

## Section B: Clinical Utility

**Q: The safety threshold has FN = 2. Is that stable across resamples?**

**A:**

- The threshold 0.018455 was derived from each patient's mean of ten out-of-fold predictions and was chosen as the highest cutoff with at most two false negatives in this cohort.
- The result FN = 2 is therefore an in-sample property of the pooled out-of-fold predictions, not a guaranteed future error count.
- AUC stability across seeds, SD 0.0075 and range 0.8024 to 0.8247, does not establish threshold stability. The distribution of sensitivity and cutoff values across seeds or bootstrap samples should be reported separately.
- Until externally validated with confidence intervals, the threshold is a candidate safety operating point and must not override clinical judgment.

**Q: How was the three-tier triage system validated?**

**A:**

- The tiers were applied to repeated out-of-fold predictions: ward below 0.018455, HCU from 0.018455 to below 0.103981, and ICU at or above 0.103981.
- Internal strata were ward 371 with 2 deaths, HCU 817 with 31 deaths, and ICU 336 with 82 deaths.
- Threshold derivation and tier evaluation used the same cohort. This is internal, apparent threshold validation and may be optimistic despite out-of-fold prediction.
- A prospective impact study must test bed demand, clinician adherence, override rates, time to treatment, adverse events, and patient outcomes before these labels guide placement.

**Q: What is the number needed to evaluate, or NNE?**

**A:**

- Define the denominator first. Here, NNE is the number flagged for enhanced evaluation divided by true deaths detected at that threshold.
- Safety threshold: 1,153 flagged / 113 true positives = 10.2 patients evaluated per death detected.
- Youden threshold: 336 flagged / 82 true positives = 4.1 patients evaluated per death detected.
- These are workload descriptors, not treatment NNTs. They do not show that evaluation prevents death, and they change with prevalence and referral setting.

**Q: How does the model compare with GRACE 2.0 in practice?**

**A:**

- On the same 1,524 patients, RF AUC was 0.819 and GRACE 2.0 AUC was 0.777; delta AUC was 0.042 with bootstrap p = 0.029.
- McNemar p < 0.001 refers to paired correctness at a common 20% risk threshold, not to AUC. At that threshold, RF was more specific but less sensitive than GRACE in this implementation.
- RF requires 13 variables, including LVOT VTI and TAPSE; GRACE uses fewer and more widely available inputs. Operational burden is part of the comparison.
- Incremental value should also be tested with calibration, net benefit, and prospective workflow outcomes. A higher AUC alone does not justify replacement of GRACE.

**Q: Can this model be deployed in a resource-limited emergency department?**

**A:**

- Not in its current form. LVOT VTI and TAPSE require timely echocardiography, trained operators, and consistent measurement.
- Median imputation permits a numerical output when values are missing, but systematic absence of echocardiography can shift predictions and degrade calibration.
- A reduced model using only routinely available clinical and laboratory variables should be developed and externally compared with the full model and GRACE.
- Any deployment needs a locked calculator, input-range checks, missing-data warnings, local calibration, clinical override, audit logs, and prospective silent-mode evaluation.

## Section C: Reproducibility

**Q: How can every reported number be reproduced?**

**A:**

- The source cohort is `thesis_complete_db.parquet`; the analytic filter is `pat_exclude=False` and Killip I to III.
- `thesis_main.py` executes cohort filtering, 10-seed 5-fold StratifiedKFold evaluation, fold-specific imputation, metrics, thresholds, triage counts, and artifact generation.
- `validation_results.json` is the machine-readable source of final counts, metrics, thresholds, feature importance, GRACE mapping, and dependency versions.
- `verify_artifacts.py` checks generated outputs against the locked results. The executed notebook provides an inspectable secondary record.

**Q: What random seeds and dependency versions were used?**

**A:**

- Seeds: 42, 123, 456, 789, 111, 222, 333, 444, 555, and 666; five stratified folds per seed.
- Recorded environment: Python 3.11.11, pandas 3.0.3, NumPy 2.4.6, scikit-learn 1.9.0, and SciPy 1.17.1.
- The exact versions in `validation_results.json` take precedence over the minimum versions listed in `requirements.txt`.
- Reproduction should occur in a clean environment with pinned exact versions and a recorded hash of the analytic dataset and final script.

**Q: Is there a single end-to-end script?**

**A:**

- Yes. `thesis_main.py` is the primary end-to-end analysis script for the final RF results.
- `compute_grace_v2.py` and related comparison artifacts document the GRACE analysis; this separation should be disclosed rather than implying that one command currently generates every comparison.
- `gm-acs-mortality-prediction-executed.ipynb` is useful for inspection but should not replace the script as the canonical pipeline.
- A release-quality package should add a single entry command, exact environment lockfile, dataset checksum, and automated tests for all headline numbers.

**Q: Is the patient-level data publicly accessible?**

**A:**

- No. The dataset contains sensitive clinical information and cannot be made public without ethics approval, data-use controls, and de-identification review.
- Reproducibility does not require unrestricted disclosure of protected data. Code, data dictionary, cohort rules, synthetic test data, and aggregate outputs can be shared.
- Qualified researchers may request controlled access from the data custodian and ethics authority, subject to institutional approval.
- The thesis should state the access process and restrictions explicitly rather than promising open data.

## Section D: Limitations and Future Work

**Q: How does the single-center retrospective design affect the conclusions?**

**A:**

- Clinical practice, referral patterns, measurement timing, and case mix at one tertiary cardiac center may differ from other hospitals.
- Retrospective records can contain misclassification, informative missingness, and variation in measurement quality that the model may learn.
- The study supports model development and internal validation only. It does not establish transportability or clinical effectiveness.

**Q: What is the consequence of having no external validation?**

**A:**

- The observed AUC, calibration, thresholds, and triage event rates may be optimistic or poorly transported to a new population.
- No claim of deployment readiness, safety, or superiority over GRACE outside this cohort is justified.
- The model and thresholds should be locked before temporal and geographic validation, with original performance reported before any recalibration.

**Q: Could excluding Killip IV patients and requiring echocardiographic data cause selection bias?**

**A:**

- Excluding Killip IV intentionally changes the target population to patients without manifest cardiogenic shock at presentation. Predictions must not be generalized to Killip IV.
- Availability of LVEF, LVOT VTI, and TAPSE may depend on severity, staffing, timing, and survivorship long enough to undergo echocardiography.
- Per-fold imputation addresses missing values computationally but does not remove selection bias or missing-not-at-random mechanisms.
- External validation should record reasons and timing for missing echocardiography and evaluate a model that does not require echo variables.

**Q: Are 115 deaths enough for a 13-feature Random Forest?**

**A:**

- The event count limits effective complexity, precision of subgroup estimates, and confidence in threshold tails despite the total N of 1,524.
- The informal events-per-variable ratio is about 8.8 and is not a sufficient sample-size justification for a non-linear ensemble.
- Depth 6 and minimum leaf size 5 constrain the trees, while repeated CV measures split variability. Neither eliminates overfitting.
- Larger external cohorts and formal prediction-model sample-size calculations are needed before updating or expanding the model.

**Q: Was calibration-in-the-large assessed?**

**A:**

- No explicit calibration intercept or observed-to-expected ratio was reported. Brier score 0.061 and a calibration plot do not replace those quantities.
- Calibration slope should also be reported to detect overly extreme or overly compressed predictions.
- Future validation should report intercept, slope, observed-to-expected ratio, calibration plot with uncertainty, and Brier score.
- Thresholds should be reassessed only after external calibration is characterized; local recalibration may be needed.

**Q: What are the concrete next studies?**

**A:**

- Lock the 13-feature model, preprocessing, and thresholds; conduct temporal validation on a later cohort from the same center.
- Conduct multicenter geographic validation, including secondary and resource-limited hospitals, and compare the full and no-echo models with GRACE 2.0.
- Run a prospective silent-mode study to measure data availability, latency, calibration drift, alert volume, and clinician-model disagreement without changing care.
- Proceed to an implementation or impact study only if external discrimination, calibration, and decision-curve net benefit are acceptable; measure patient outcomes, resource use, equity, and unintended harm.
