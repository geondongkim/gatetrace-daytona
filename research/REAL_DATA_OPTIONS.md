# Real data options for the GateTrace failure-gating demo

Research date: 2026-09-19 (Asia/Seoul)

## Recommendation

Use **MetroPT-3** as the primary real-data demo. It is the best overall fit because it is operational railway equipment data (not a simulation or synthetic table), has a real `timestamp`, 15 compressor/APU signals, published air-leak intervals, an official UCI record, a peer-reviewed data paper, and an explicit **CC BY 4.0** dataset license. A chronological two-hour slice around the first reported failure can be extracted in minutes and can exercise GateTrace's missing-rate, ordering, and leakage-column gates without inventing sensor values.

Confidence: **high** for provenance, license, schema, size, missingness, and chronological order; **medium** for the demo label definition because `failure_within_1h` must be derived from the published failure interval rather than read from a native target column.

Important constraint: MetroPT-3 does **not** contain vibration or RPM. It must not be presented as satisfying the current fixed `vibration_mm_s` and `rpm` schema. For a source-faithful real-data demo, use a MetroPT-specific required-column profile (recommended below). If the current seven-column pump profile must remain unchanged, the UCI hydraulic dataset is closer—it has pressure, temperature, and vibration—but it still lacks native calendar timestamps and RPM. No candidate reviewed honestly supplies every current demo field.

## Candidate comparison

| Rank | Dataset | Why it is useful | Gate fit and limitations | License / download effort | Confidence |
|---|---|---|---|---|---|
| 1 | **MetroPT-3** | 1,516,948 observations from a compressor Air Production Unit on an operating Porto metro train; pressure, oil temperature, motor current, and digital control signals; reported air-leak intervals | Native timestamp and clean chronological stream; UCI says no missing values. `index` is an ID, not a model feature. No native vibration/RPM and no native target; derive the one-hour label only from the published event start. | CC BY 4.0. Official archive is directly downloadable and the CSV parses normally. A two-hour slice is small. | **High** |
| 2 | **Condition monitoring of hydraulic systems** | Real experimental hydraulic rig, specifically including internal pump leakage states; pressure, temperature, motor power, flow, and vibration in mm/s | Best physical match to the current pump story and `vibration_mm_s`; 2,205 ordered 60-second cycles and no missing values. However, it is a test rig, is stored as aligned tab-delimited matrices, has no calendar timestamp, no equipment ID, and no RPM. The `profile.txt` pump-leakage column is a target and must be excluded from features. | CC BY 4.0. Straightforward parsing but 20 files and mixed sampling rates require aggregation/alignment. | **High** |
| 3 | **AI4I 2020 Predictive Maintenance** | Tiny, ready-to-use CSV; temperature, rotational speed, torque, tool wear, aggregate failure and five failure-mode labels | Excellent fast fallback for schema/leakage demonstrations, but UCI explicitly calls it **synthetic**. It has no timestamp, pressure, or vibration, and the per-mode target columns (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) are leakage if `Machine failure` is the prediction target. | CC BY 4.0; one 518,125-byte CSV, so extraction is nearly instant. | **High** |

MetroPT-3 is stronger than the hydraulic rig for the main demo because GateTrace explicitly validates chronological order, and MetroPT provides genuine operational timestamps plus real failure reports. The hydraulic dataset is the best secondary example when the narrative must be specifically about a pump or vibration.

## 1. MetroPT-3 — recommended

### Primary sources and citations

- Official dataset record: [UCI MetroPT-3](https://archive.ics.uci.edu/dataset/791/metropt+3+dataset), DOI [`10.24432/C5VW3R`](https://doi.org/10.24432/C5VW3R).
- Official direct download: [`metropt+3+dataset.zip`](https://archive.ics.uci.edu/static/public/791/metropt+3+dataset.zip).
- Supporting data paper: Bruno Veloso, Rita P. Ribeiro, João Gama, and Pedro Mota Pereira, “The MetroPT dataset for predictive maintenance,” *Scientific Data* 9, 764 (2022), DOI [`10.1038/s41597-022-01877-3`](https://doi.org/10.1038/s41597-022-01877-3); [open full text at PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9747912/).
- UCI also names the introductory DSAA paper: Narjes Davari et al., “Predictive maintenance based on anomaly detection using deep learning for air production unit in the railway industry,” DSAA 2021, [IEEE record](https://ieeexplore.ieee.org/document/9564181).
- License: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/), stated on the UCI record. Redistribution and adaptation are allowed with attribution.

### Verified facts

UCI describes 1,516,948 rows, 15 signals, no missing values, and failure prediction/anomaly detection/RUL uses. Its page reports four high-stress air-leak intervals, beginning with **2020-04-18 00:00 through 23:59**. It recommends using the first month for training and the rest for testing.

Local inspection of the official download on 2026-09-19 verified:

- Archive: **218,381,995 bytes**; it contains `MetroPT3(AirCompressor).csv` (**218,300,507 bytes**) and `Data Description_Metro.pdf` (**81,208 bytes**). UCI's UI rounds these to 208.2 MB for the CSV and 208.3 MB for the download.
- CSV: **1,516,948 data rows** and 17 headers when the unnamed exported index column is counted.
- Time range: `2020-02-01 00:00:00` through `2020-09-01 03:59:50`.
- Empty cells: **0 of 25,788,116 cells** (0.0%) in a streaming parse.
- Adjacent timestamp reversals: **0**. Most adjacent intervals are 10 seconds; 9-, 11-, 12-, and 13-second intervals also occur, so code must not assume a perfectly uniform cadence.

The UCI prose is internally inconsistent about cadence: one section says 1 Hz while its detailed attribute text says 0.1 Hz. The actual file advances mostly by 10 seconds, supporting 0.1 Hz. The data paper describes a larger 1 Hz collection, while the UCI MetroPT-3 file is a smaller derived dataset; cite the exact artifact being used.

### Native schema and honest GateTrace mapping

Recommended clean-demo columns:

| Demo column | Source / rule | Notes |
|---|---|---|
| `timestamp` | native `timestamp` | Preserve the source value; its timezone is not specified, so do not append `Z`. |
| `equipment_id` | constant `APU01` | The paper identifies the monitored APU; document that this is a dataset-level identifier added during extraction. |
| `oil_temperature_c` | native `Oil_temperature` | Temperature in °C. |
| `compressor_pressure_bar` | native `TP2` | Pressure on the compressor in bar. |
| `panel_pressure_bar` | native `TP3` | Pressure at the pneumatic panel in bar. |
| `motor_current_a` | native `Motor_current` | Motor current in amperes. |
| `failure_within_1h` | derived from the published event start | `1` only when `event_start - 1 hour <= timestamp < event_start`; otherwise `0`. This is the target, never an input feature. |

Preserve additional digital signals under their source names if useful. Drop the unnamed CSV index from features. Do not rename motor current to RPM or a pressure signal to vibration.

### Minimal clean/contaminated recipe

1. Stream the official CSV and select `2020-04-17 22:00:00 <= timestamp < 2020-04-18 00:00:00`, the two hours immediately before the first published air-leak interval. At the observed cadence this is roughly 720 rows; use the timestamps, not a fixed row count.
2. Sort ascending by `timestamp`, add `equipment_id = APU01`, map the four native measurements above, and derive `failure_within_1h`. This provides both `0` and `1` labels without putting the event time into the feature set.
3. The **clean** sample should require `timestamp`, `equipment_id`, `oil_temperature_c`, `compressor_pressure_bar`, `panel_pressure_bar`, `motor_current_a`, and `failure_within_1h`; check missingness over the four sensor columns; group chronological order by `equipment_id`; forbid `failure_timestamp`, `future_failure`, `future_failure_label`, and `time_to_failure_minutes`.
4. Clone it for the **contaminated** sample. Blank `oil_temperature_c` on every fourth row. Across four checked sensor columns this creates a 6.25% cell-missing rate, exceeding GateTrace's 5% limit. Swap one adjacent pair of rows to create a time-order violation. Add `time_to_failure_minutes` computed from the known event time to create an explicit leakage-column violation. Keep all required columns so exactly the three intended gates fail.
5. Record attribution and the extraction interval beside any redistributed sample. Keep the original filename/DOI in metadata and do not claim the derived one-hour target was supplied by UCI.

This recipe should complete well under 20 minutes after download. No sample is committed here because the requested output is research-only and the repository's `data/` directory is outside this task's allowed write scope.

## 2. UCI hydraulic system — pump-specific alternative

### Primary sources and citations

- Official dataset record: [UCI Condition monitoring of hydraulic systems](https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems), DOI [`10.24432/C5CW21`](https://doi.org/10.24432/C5CW21).
- Official direct download: [`condition+monitoring+of+hydraulic+systems.zip`](https://archive.ics.uci.edu/static/public/447/condition+monitoring+of+hydraulic+systems.zip).
- Supporting paper: Nikolai Helwig, Eliseo Pignanelli, and Andreas Schütze, “Condition Monitoring of a Complex Hydraulic System Using Multivariate Statistics,” IEEE I2MTC 2015, DOI [`10.1109/I2MTC.2015.7151267`](https://doi.org/10.1109/I2MTC.2015.7151267).
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), stated on the UCI record.

UCI reports 2,205 cycles of 60 seconds and no missing values. The files include six 100 Hz pressure matrices (`PS1`–`PS6`), motor power at 100 Hz, flow at 10 Hz, four temperatures at 1 Hz, and vibration `VS1` at 1 Hz in mm/s. `profile.txt` provides cycle-wise cooler, valve, internal pump leakage, accumulator, and stability targets. Internal pump leakage has 1,221 no-leak, 492 weak-leak, and 492 severe-leak cycles according to the included documentation.

Local archive inspection verified a **76,601,704-byte** ZIP expanding to **556,266,030 bytes** across 20 files. The files are tab-delimited matrices, not CSV. The minimal recipe is to read one row (one cycle) from `PS1.txt`, `TS1.txt`, and `VS1.txt`, aggregate each cycle (for example, mean plus standard deviation), use the row number as `cycle_id`, and join the third `profile.txt` column as the pump-leakage target. Treat `profile.txt` target columns and the stability flag as forbidden features. This is excellent for pump leakage and vibration, but a calendar `timestamp` or RPM would be fabricated; prefer a `cycle_id` order gate rather than pretending otherwise.

## 3. AI4I 2020 — tiny synthetic fallback

### Primary sources and citations

- Official dataset record: [UCI AI4I 2020 Predictive Maintenance](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset), DOI [`10.24432/C5HS5C`](https://doi.org/10.24432/C5HS5C).
- Official CSV: [`data.csv`](https://archive.ics.uci.edu/static/public/601/data.csv).
- Supporting paper: Stephan Matzka, “Explainable Artificial Intelligence for Predictive Maintenance Applications,” AI4I 2020, DOI [`10.1109/AI4I49448.2020.00023`](https://doi.org/10.1109/AI4I49448.2020.00023).
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), stated on the UCI record.

Local inspection verified **518,125 bytes**, 10,000 rows, 14 columns, and zero empty cells. The first header includes a UTF-8 byte-order mark, so read it with `utf-8-sig`. Native fields include air/process temperature, rotational speed in RPM, torque, tool wear, aggregate `Machine failure`, and five mode labels. For a failure classifier, retain `Machine failure` as the target and forbid `TWF`, `HDF`, `PWF`, `OSF`, and `RNF` as direct leakage. This is the fastest parsing option, but its synthetic provenance and lack of true timestamps make it a materially weaker main demo than MetroPT-3.

## Decision and stop conditions

## Roadmap: evidence-preserving augmentation

GateTrace can extend from validation to data-scarcity support without making synthetic data indistinguishable from observations. Nosana would return a constrained augmentation specification (allowed transforms, target count, random seed, feature bounds, and required post-checks); Daytona would execute only host-owned transform code in an isolated sandbox; GateTrace would then rerun schema, missingness, chronology, leakage, distribution-shift, and provenance gates before accepting an augmented bundle.

For sensor time series, start with bounded jitter, magnitude scaling, window slicing, and limited time warping. Apply augmentation only to the training partition after the chronological train/test split, never to validation or test data. Every generated row or window should retain a source-window identifier, transform name, parameters, seed, and `synthetic=true`. A failed distribution or leakage check must quarantine the whole augmented bundle. TimeGAN or diffusion-based generation can remain a later experiment because they require stronger fidelity, privacy, and mode-collapse evaluation than this hackathon MVP can demonstrate honestly.

- **Proceed with MetroPT-3** if the demo can use a dataset-specific schema and explicitly label the one-hour target as derived.
- **Use the hydraulic dataset** if a physical pump/vibration story is more important than calendar chronology and the order gate can accept `cycle_id`.
- **Use AI4I only as a fallback** when download/parsing time dominates authenticity.
- Stop and revisit the choice if the product requires all of `temperature_c`, `vibration_mm_s`, `pressure_bar`, and `rpm` to be native measurements in one dataset. None of the three authoritative candidates reviewed meets that requirement, and fabricating or semantically renaming measurements would undermine GateTrace's evidence-first claim.

## Source confidence and unresolved points

- UCI records and direct artifacts: **high confidence**; authoritative repository, explicit license, and locally inspected downloads.
- MetroPT data paper and hydraulic supporting paper: **high confidence**; publisher/DOI records match the dataset documentation.
- MetroPT failure-to-label transformation: **medium confidence**; deterministic and auditable, but it is a demo policy choice, not a source-provided label.
- MetroPT timezone: **unknown**; keep naive timestamps and disclose this.
- Claim that the sample predicts an actual failure within precisely one hour: **policy-defined**, not experimentally validated. The published interval supplies event timing, while the one-hour horizon is GateTrace's derived target definition.
