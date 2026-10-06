#!/bin/bash
# Run inside the MACE environment used for training.
mace_eval_configs \
  --configs="test.xyz" \
  --model="mace_model_stagetwo.model" \
  --output="test_mace_predictions.xyz" \
  --device="cuda" \
  --default_dtype="float64" \
  --batch_size=8 \
  --info_prefix="MACE_"

python validation/scripts/plot_from_mace_eval.py test_mace_predictions.xyz \
  --output-dir validation_output
