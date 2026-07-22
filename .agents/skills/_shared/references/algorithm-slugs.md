# Algorithm slugs (ALGORITHM_MAP reference)

Valid slugs for `biolm_web/scripts/generate_jupyter_migration.py` `ALGORITHM_MAP` values.
Used by create-guide (draft validation) and review-guides (missing-map detection).

If `BIOLM_WEB_ROOT` is set, `list_algorithm_slugs.py` merges slugs from that repo's `ALGORITHM_MAP`.

## Known slugs (from biolm_web ALGORITHM_MAP)

| Slug | Used in guides |
|------|------------------|
| `esmfold` | 1.0, 1.1, 9.2 |
| `esm2-150m` | 2.0, 2.1, 2.2, 2.3, 9.3 |
| `esm2-35m` | 2.0, 2.1, 2.2, 2.3 |
| `esm2-650m` | 2.0 |
| `esm2-8m` | 2.0 |
| `esm1v-all` | 3.0, 3.1 |
| `esm-if1` | 4.0 |
| `progen2` | 6.0 |
| `biolmtox-v1` | 8.0, 8.1 |
| `antifold` | 9.0, 9.3 |
| `ablang2` | 9.1 |
| `igbert-paired` | 9.1 |
| `igbert-unpaired` | 9.1 |
| `immunefold-antibody` | 9.2 |

## Current ALGORITHM_MAP stems (biolm_web)

```
0_Introduction → []
1.0_ESMFold → [esmfold]
1.1_ESMFold_PDB_Generation → [esmfold]
2.0_ESM2 → [esm2-150m, esm2-35m, esm2-650m, esm2-8m]
2.1_ESM2_Attention_Map → [esm2-150m, esm2-35m]
2.2_ESM2_Protein_Contact_Map → [esm2-150m, esm2-35m]
2.3_ESM2_Embeddings_XGBoost → [esm2-150m, esm2-35m]
3.0_ESM_1v → [esm1v-all]
3.1_ESM-1v_Deep_Mutational_Scan_Protein → [esm1v-all]
4.0_ESM-IF1 → [esm-if1]
6.0_ProGen2 → [progen2]
8.0_BioLMTox_Toxin_Classification → [biolmtox-v1]
8.1_BioLMTox_Toxin_Similarity → [biolmtox-v1]
9.0_Generation_for_Antibody_Engineering → [antifold]
9.1_Intrinsic_Scoring_for_Antibody_Engineering → [ablang2, igbert-paired, igbert-unpaired]
9.2_Structural_Scoring_for_Antibody_Engineering → [esmfold, immunefold-antibody]
9.3_Downstream_for_Antibody_Engineering → [antifold, esm2-150m]
```

**Note:** 10.x pipeline guides (10.0–10.6) are synced to the site but have **empty** `algorithms` arrays until `ALGORITHM_MAP` is updated in biolm_web.

## Draft format for new guides

```python
# Add to biolm_web/scripts/generate_jupyter_migration.py ALGORITHM_MAP
"10.7_My_New_Guide": ["esm2-650m"],
```

Validate slugs: `python .agents/skills/_shared/scripts/list_algorithm_slugs.py --validate esm2-650m`
