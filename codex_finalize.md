# Finalize TESIS_FINAL.docx and notebook for seminar

Working directory: /home/linuxmint/thesis-clean

## Mission
Update TESIS_FINAL.docx and gm-acs-mortality-prediction-executed.ipynb with complete 3-outcomes analysis (mortality, de novo cardiogenic shock, composite). Must meet Kaggle Grandmaster quality — clean narrative, consistent numbers, professional formatting.

## Data source
- three_outcomes_results.json — contains AUC, CI, feature importance for all 3 outcomes
- validation_results.json — primary mortality metrics
- thesis_complete_db.parquet — raw data

## Current state
- run_three_outcomes.py already computes all 3 outcomes
- three_outcomes_results.json already saved with feature importance
- Notebook already has section 7 injected (3 outcomes) but needs verification
- DOCX already updated manually with:
  - TABLE 5: correct prevalence (7.5%, 11.2%, 12.9%)
  - P219: event counts
  - P268: shock feature importance
  - P271: composite feature importance
  - P264: updated comparison text

## Key numbers (ABSOLUTELY CORRECT — do not change)
| Metric | Value |
|--------|-------|
| N | 1.524 |
| Deaths | 115 (7,5%) |
| De novo shock | 171 (11,2%) |
| Composite | 197 (12,9%) |
| Mortality AUC | 0,819 ± 0,007 |
| Shock AUC | 0,747 ± 0,005 |
| Composite AUC | 0,769 ± 0,004 |
| Mortality top-3 FI | eGFR (0,152), ureum (0,131), LVOT VTI (0,098) |
| Shock top-3 FI | LVOT VTI (0,132), SBP (0,128), APTT (0,083) |
| Composite top-3 FI | LVOT VTI (0,134), SBP (0,117), eGFR (0,113) |

## Tasks

### 1. DOCX — verify and polish
- Verify all numbers in document match the table above
- Ensure feature importance is mentioned for ALL 3 outcomes in discussion section
- Ensure narrative flows naturally (not AI-generated, no clichés, no em dashes)
- Check TABLE 5 has correct prevalence values
- Add brief AUPRC context for shock (0,500) and composite (0,635) if missing
- Verify no orphaned figure references

### 2. DOCX — add secondary outcomes table
If not present, add a small table in section 4 comparing 3 outcomes:
| Outcome | AUC | ±SD | 95% CI | Feature importance (top 3) |
| Mortality | 0,819 | 0,007 | 0,805-0,833 | eGFR, ureum, LVOT VTI |
| De novo shock | 0,747 | 0,005 | 0,736-0,757 | LVOT VTI, SBP, APTT |
| Composite | 0,769 | 0,004 | 0,761-0,777 | LVOT VTI, SBP, eGFR |

### 3. Notebook — verify and fix
- Check that section 7 (secondary outcomes) code cell actually runs and displays correct numbers
- Fix any execution order issues
- Ensure all section numbers are consistent (7 → 10 → 11)

### 4. Cross-check
- Run `python3 verify_artifacts.py` if it exists
- Ensure no discrepancies between notebook and DOCX numbers

## Language
- DOCX: Indonesian, tesis style (formal akademik)
- Notebook: English (Kaggle standard)
- No em dashes in DOCX prose
- No "merupakan" overuse — prefer "adalah"
