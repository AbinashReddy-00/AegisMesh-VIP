#!/usr/bin/env bash
# AegisMesh — Unified End-to-End Security Validation Suite (Bash)

set -e

echo "============================================================"
echo "  RUNNING AEGISMESH UNIFIED END-TO-END VALIDATION SUITE"
echo "============================================================"

python3 testing/end-to-end/run_e2e_tests.py
