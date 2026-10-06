# End-to-end workflow

1. Run classical MD and sample configurations across temperature and dynamical regimes.
2. Convert selected LAMMPS trajectory frames to XYZ while retaining periodic cell dimensions.
3. Build a structurally diverse set of equilibrated (EQ) and non-equilibrated (nEQ) structures.
4. Generate Quantum ESPRESSO single-point inputs for reference energies and forces.
5. Run QE labelling calculations on the sampled configurations.
6. Parse QE outputs with ASE, attach `REF_energy` and `REF_forces`, and reject pathological high-force structures.
7. Assemble the canonical 875-configuration extended-XYZ dataset.
8. Create a reproducible temperature-stratified split: 698 train / 85 validation / 92 test.
9. Train MACE on TACC Stampede3.
10. Apply stochastic weight averaging (SWA) during stage two.
11. Validate energy and force errors on train/validation/test sets.
12. Export the trained potential for downstream atomistic simulation.
