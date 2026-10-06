# Dataset

Reference structures were sampled across 300, 350, 400, 450, and 500 K, labelled with Quantum ESPRESSO energies and forces, and stored as extended XYZ for MACE.

## Canonical dataset statistics

| Temperature (K) | Accepted | Train | Validation | Test |
|---:|---:|---:|---:|---:|
| 300 | 126 | 100 | 12 | 14 |
| 350 | 192 | 153 | 19 | 20 |
| 400 | 188 | 150 | 18 | 20 |
| 450 | 189 | 151 | 18 | 20 |
| 500 | 180 | 144 | 18 | 18 |
| **Total** | **875** | **698** | **85** | **92** |

The split is temperature-stratified and reproducible with a fixed random seed:

```bash
python data/split_dataset.py dataset_all.xyz --seed 42
```

The complete production dataset is intentionally omitted from this portfolio repository.
