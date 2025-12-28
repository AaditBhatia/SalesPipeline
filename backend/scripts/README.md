# Evaluation Scripts

This directory contains utility scripts for model evaluation.

## run_evaluation.py

Command-line tool for running evaluations and analyzing results.

### Prerequisites

```bash
pip install httpx
```

### Usage Examples

#### Run all tests
```bash
python scripts/run_evaluation.py --all
```

#### Run specific category
```bash
python scripts/run_evaluation.py --category lead_scoring
```

#### Run baseline tests only
```bash
python scripts/run_evaluation.py --tags baseline
```

#### Run specific tests
```bash
python scripts/run_evaluation.py --test-ids enterprise_lead_001,low_quality_lead_001
```

#### List available test cases
```bash
python scripts/run_evaluation.py --list-tests
python scripts/run_evaluation.py --list-tests --category lead_scoring
python scripts/run_evaluation.py --list-tests --tags baseline
```

#### List recent reports
```bash
python scripts/run_evaluation.py --list-reports
```

#### Get detailed report
```bash
python scripts/run_evaluation.py --get-report eval_report_20250101_120000
```

#### Compare two reports
```bash
python scripts/run_evaluation.py --compare report1_id report2_id
```

### Output

Reports are automatically saved to `evaluation_reports/` directory with the format:
```
evaluation_reports/eval_report_YYYYMMDD_HHMMSS.json
```

## Creating the evaluation_reports directory

```bash
mkdir -p backend/evaluation_reports
```
