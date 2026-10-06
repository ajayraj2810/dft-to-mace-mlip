# MACE validation

The final stage-two/SWA training run reported:

- Test energy RMSE: **0.6 meV/atom**
- Test force RMSE: **33.3 meV/Å**
- Relative force RMSE: **2.47%**

Use `scripts/evaluate_and_plot_mace.py` to evaluate a trained model directly with `MACECalculator`, or run `run_test_evaluation.sh` and then `scripts/plot_from_mace_eval.py`.

The plotting utilities generate energy/force parity plots and error distributions from the held-out test set. The full production model checkpoint is intentionally not redistributed here.
