# BioMarkerX — Authoritative Locked Test Benchmarks

**Policy Configuration**: Policy A (Dual-Tier Screening & Confirmation, Ungated)
- **Screening Threshold ($\tau_s$)**: `0.035`
- **Confirmation Threshold ($\tau_c$)**: `0.18`
- **Confirmation Persistence**: `2 consecutive 1-hour windows`
- **Trajectory Gate**: `OFF (Ungated)`
- **Onset Definition**: `first SepsisLabel == 1`
- **Locked Test Cohort**: `2,974 patients / 112,641 windows`

## 1. Discrimination & Accuracy Benchmarks
- **AUROC**: `0.7895` (95% CI: `[0.7657, 0.8109]`)
- **AUPRC**: `0.1241` (95% CI: `[0.1080, 0.1443]`)
- **Brier Score**: `0.02738`

## 2. Multi-Level Primary Operating Benchmarks

| Level | Metric | Observed Point Est | 95% Patient Bootstrap CI | Status / Target |
|---|---|---|---|---|
| **Patient-Level** | Patient Sensitivity | **82.44%** (230/279) | `[77.90%, 86.65%]` | ✅ **PASSED (Target >=80.0%)** |
| **Patient-Level** | Patient PPV | **15.04%** (230/1529) | `[13.36%, 16.84%]` | Informational |
| **Window-Level** | Screening PPV | **9.54%** (1968/20621) | `[8.57%, 10.51%]` | ❌ **FAIL (Target >=15.0%)** |
| **Window-Level** | Confirmation PPV | **18.60%** (436/2344) | `[14.56%, 23.34%]` | ❌ **FAIL (Target >=25.0%)** |
| **Window-Level** | Confirmation Sens | **12.94%** (436/3369) | `[9.83%, 15.96%]` | ❌ **FAIL (Target 20-30%)** |

## 3. Lead-Time Distribution (Hours Before SepsisLabel==1)
- **Median (P50)**: `33.5 hours` (IQR: `9.0`–`72.5` hours)
- **Mean**: `52.6 ± 58.4 hours`
- **Range**: `0.0` to `294.0 hours`

## 4. Hash-Verified Provenance
- **Master Model SHA-256**: `93ecdbc42f0fda19cbba15261c1545d653eeef54e343e44e5ddcfacaf83cccdd`
- **Calibrator SHA-256**: `b3faf071de7416a19da1189f12413bf15b6bd8212a74cf717f2ebc773cdee2bb`
- **Feature Matrix SHA-256**: `cafdc596c095c549d77c2b57058b253db292e3ba954a91aaa1ba4f8ce40601d9`
- **Predictions SHA-256**: `6d4f7d0463f14d33ba6c1ec090a2dab1c8e323b6245c84ac278f1eb13aedacee`
