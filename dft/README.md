# Quantum ESPRESSO labelling

The workflow uses periodic Quantum ESPRESSO single-point calculations to label sampled structures with reference energies and atomic forces.

Generate QE inputs from sampled XYZ structures:

```bash
python dft/generate_qe_inputs.py sampled_frames --output-dir qe_inputs
```

Parse completed QE outputs into an extended-XYZ dataset:

```bash
python dft/parse_qe_outputs.py qe_outputs \
    --temperatures 300 350 400 450 500 \
    --max-force 10.0 \
    --output dataset_all.xyz
```

Expected output layout:

```text
qe_outputs/
├── 300/*.out
├── 350/*.out
├── 400/*.out
├── 450/*.out
└── 500/*.out
```

The supplied research archive contained 931 QE output files. After parsing and filtering, the canonical dataset contains 875 configurations. Raw QE outputs and pseudopotentials are intentionally not redistributed.
