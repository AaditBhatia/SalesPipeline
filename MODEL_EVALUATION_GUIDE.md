# Model Evaluation Framework Guide

## Overview

The Model Evaluation Framework provides a comprehensive system for systematic prompt engineering and testing of Grok AI's performance across different AI features in the Sales Pipeline application.

## Features

### 1. **Systematic Prompt Engineering**
- Standardized test cases covering all AI features
- Reproducible evaluation methodology
- Version-controlled test scenarios

### 2. **Performance Testing Across AI Features**
The framework tests Grok's performance in these categories:
- **Lead Scoring**: Overall lead quality assessment (0-100 scale)
- **BANT Analysis**: Budget, Authority, Need, Timeline evaluation
- **Priority Classification**: Hot/Warm/Cold lead categorization
- **Deal Size Estimation**: Small/Medium/Large/Enterprise predictions
- **Insight Generation**: Actionable insights from lead data
- **Red Flag Detection**: Identification of problematic leads
- **Next Action Recommendations**: Suggested follow-up actions

### 3. **Qualitative Analysis**
- Pattern recognition in underperformance
- Root cause analysis for failures
- Specific case identification for debugging
- Confidence scoring for each category

### 4. **Actionable Recommendations**
- Prompt iteration plans based on results
- Priority-ranked improvement suggestions
- Category-specific optimization guidance
- Performance tracking over time

---

## Architecture

### Core Components

#### 1. **EvaluationService** (`backend/app/services/evaluation_service.py`)
Main service managing the evaluation framework.

**Key Classes:**
- `ModelEvaluationService`: Main service class
- `EvaluationTestCase`: Individual test case definition
- `EvaluationResult`: Results from a single test
- `QualitativeAnalysis`: Pattern analysis for underperformance
- `EvaluationReport`: Comprehensive evaluation report

**Key Methods:**
```python
# Run evaluation suite
await evaluation_service.run_evaluation_suite(
    grok_service=grok_service,
    test_ids=["enterprise_lead_001"],  # Optional: specific tests
    categories=[EvaluationCategory.LEAD_SCORING],  # Optional: filter by category
    tags=["baseline"]  # Optional: filter by tags
)

# Generate report
report = evaluation_service.generate_evaluation_report(results)

# Compare reports over time
comparison = evaluation_service.get_comparison_report(report1, report2)
```

#### 2. **API Endpoints** (`backend/app/api/leads.py`)

All evaluation endpoints are under `/api/leads/evaluation/`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/evaluation/run` | POST | Run evaluation suite |
| `/evaluation/test-cases` | GET | List all test cases |
| `/evaluation/reports` | GET | List recent reports |
| `/evaluation/reports/{report_id}` | GET | Get detailed report |
| `/evaluation/reports/{report_id}/export` | GET | Export report as JSON |
| `/evaluation/compare` | POST | Compare two reports |

---

## Usage Guide

### Quick Start

#### 1. **Run Basic Evaluation**

```bash
curl -X POST http://localhost:8000/api/leads/evaluation/run \
  -H "Content-Type: application/json" \
  -d '{
    "generate_report": true
  }'
```

This runs all test cases and generates a comprehensive report.

#### 2. **Run Specific Category Tests**

```bash
curl -X POST http://localhost:8000/api/leads/evaluation/run \
  -H "Content-Type: application/json" \
  -d '{
    "categories": ["lead_scoring", "bant_analysis"],
    "generate_report": true
  }'
```

#### 3. **Run Baseline Tests Only**

```bash
curl -X POST http://localhost:8000/api/leads/evaluation/run \
  -H "Content-Type: application/json" \
  -d '{
    "tags": ["baseline"],
    "generate_report": true
  }'
```

#### 4. **List Available Test Cases**

```bash
curl http://localhost:8000/api/leads/evaluation/test-cases
```

Filter by category:
```bash
curl http://localhost:8000/api/leads/evaluation/test-cases?category=lead_scoring
```

Filter by tags:
```bash
curl http://localhost:8000/api/leads/evaluation/test-cases?tags=enterprise,baseline
```

#### 5. **View Reports**

List recent reports:
```bash
curl http://localhost:8000/api/leads/evaluation/reports?limit=5
```

Get detailed report:
```bash
curl http://localhost:8000/api/leads/evaluation/reports/eval_report_20250101_120000
```

Export report as JSON:
```bash
curl http://localhost:8000/api/leads/evaluation/reports/eval_report_20250101_120000/export
```

#### 6. **Compare Reports Over Time**

```bash
curl -X POST http://localhost:8000/api/leads/evaluation/compare \
  -H "Content-Type: application/json" \
  -d '{
    "report1_id": "eval_report_20250101_120000",
    "report2_id": "eval_report_20250102_120000"
  }'
```

---

## Standard Test Cases

The framework includes 8 standard test cases covering key scenarios:

### 1. **enterprise_lead_001** (Lead Scoring - High Quality)
- **Scenario**: VP of Engineering at large enterprise with clear budget
- **Expected**: Score 80-100, Hot priority, Enterprise deal size
- **Tests**: Authority recognition, budget identification, urgency detection

### 2. **low_quality_lead_001** (Lead Scoring - Low Quality)
- **Scenario**: Intern at small startup, browsing only
- **Expected**: Score 0-40, Cold priority, Small deal size
- **Tests**: Low authority detection, weak engagement recognition

### 3. **midtier_lead_001** (Lead Scoring - Medium Quality)
- **Scenario**: Sales Manager at medium company
- **Expected**: Score 50-70, Warm priority, Medium deal size
- **Tests**: Balanced scoring, appropriate prioritization

### 4. **bant_authority_001** (BANT Analysis)
- **Scenario**: CTO with decision-making power
- **Expected**: High authority score (28+), C-level recognition
- **Tests**: Authority detection, decision-maker identification

### 5. **red_flag_001** (Red Flag Detection)
- **Scenario**: Potential competitor doing research
- **Expected**: Red flags detected, Cold priority
- **Tests**: Competitor risk detection, tire-kicker identification

### 6. **deal_size_001** (Deal Size Estimation)
- **Scenario**: Fortune 500 company with 500+ users
- **Expected**: Enterprise deal size, scale recognition
- **Tests**: Company size assessment, user volume consideration

### 7. **next_action_001** (Next Action Recommendations)
- **Scenario**: Urgent buyer with expiring contract
- **Expected**: Immediate action recommendations, Hot priority
- **Tests**: Urgency recognition, action prioritization

### 8. **insight_generation_001** (Insight Generation)
- **Scenario**: Lead with minimal information
- **Expected**: Insights generated, missing info identified
- **Tests**: Insight quality, limitation acknowledgment

---

## Understanding Evaluation Results

### Report Structure

```json
{
  "report_id": "eval_report_20250101_120000",
  "timestamp": "2025-01-01T12:00:00",
  "summary": {
    "total_tests": 8,
    "passed_tests": 6,
    "failed_tests": 2,
    "overall_score": 75.5,
    "pass_rate": 75.0
  },
  "category_scores": {
    "lead_scoring": 80.0,
    "bant_analysis": 75.0,
    "priority_classification": 70.0,
    "deal_size_estimation": 85.0,
    "insight_generation": 65.0,
    "red_flag_detection": 60.0,
    "next_action_recommendation": 78.0
  },
  "performance_breakdown": {
    "excellent": 2,
    "good": 3,
    "acceptable": 1,
    "poor": 1,
    "failing": 1
  },
  "actionable_recommendations": [
    "Priority: Improve Red Flag Detection (score: 60.0)",
    "Priority: Improve Insight Generation (score: 65.0)",
    "Testing: Run evaluations weekly to track prompt iteration effectiveness",
    "Data: Collect real-world lead scoring data for comparison and calibration"
  ],
  "prompt_iteration_plan": [
    "1. Iteratively refine prompts for lowest-scoring categories",
    "- Expand red flag examples in prompt: competitor signals, tire-kickers, invalid contacts",
    "- Encourage deeper analysis by asking model to consider multiple data points together",
    "2. Add specific examples for underperforming scenarios",
    "3. Test with edge cases and validate improvements",
    "4. Deploy updated prompt and monitor performance"
  ],
  "qualitative_analyses": [
    {
      "category": "red_flag_detection",
      "confidence_score": 60.0,
      "underperformance_patterns": [
        "Missing expected output (occurred 2 times)"
      ],
      "specific_failure_cases": [
        {
          "test_id": "red_flag_001",
          "score": 60.0,
          "discrepancies": ["Expected red flags but none were identified"]
        }
      ],
      "root_cause_analysis": [
        "Red flag detection sensitivity may be too low"
      ],
      "prompt_improvement_suggestions": [
        "Expand red flag examples in prompt: competitor signals, tire-kickers, invalid contacts"
      ]
    }
  ]
}
```

### Performance Levels

- **Excellent** (90-100): Outstanding performance, no changes needed
- **Good** (75-89): Solid performance, minor optimizations possible
- **Acceptable** (60-74): Meets minimum requirements, improvements recommended
- **Poor** (40-59): Below expectations, prompt revision needed
- **Failing** (0-39): Unacceptable performance, immediate action required

### Interpreting Scores

#### Overall Score
- **90-100**: Production-ready, excellent prompt engineering
- **75-89**: Production-ready with minor refinements
- **60-74**: Needs improvement before production deployment
- **Below 60**: Requires significant prompt engineering work

#### Category Scores
Focus on lowest-scoring categories first for maximum impact.

---

## Prompt Engineering Workflow

### 1. **Baseline Evaluation**
Run all baseline tests to establish current performance:

```bash
curl -X POST http://localhost:8000/api/leads/evaluation/run \
  -d '{"tags": ["baseline"], "generate_report": true}'
```

### 2. **Analyze Results**
Review the evaluation report, focusing on:
- Categories with scores < 70
- Common underperformance patterns
- Specific failure cases
- Root cause analyses

### 3. **Implement Prompt Changes**
Based on recommendations:
1. Update system prompt in `backend/app/services/grok_service.py`
2. Add examples for underperforming scenarios
3. Clarify scoring criteria and rubrics
4. Strengthen output format requirements

### 4. **Re-evaluate**
Run the same test suite again:

```bash
curl -X POST http://localhost:8000/api/leads/evaluation/run \
  -d '{"tags": ["baseline"], "generate_report": true}'
```

### 5. **Compare Results**
Track improvement over time:

```bash
curl -X POST http://localhost:8000/api/leads/evaluation/compare \
  -d '{
    "report1_id": "eval_report_before",
    "report2_id": "eval_report_after"
  }'
```

### 6. **Iterate**
Continue the cycle until all categories achieve acceptable scores (70+).

---

## Adding Custom Test Cases

### Via Code

```python
from app.services.evaluation_service import EvaluationTestCase, EvaluationCategory

# Create custom test case
custom_test = EvaluationTestCase(
    test_id="custom_test_001",
    category=EvaluationCategory.LEAD_SCORING,
    description="Custom test for specific edge case",
    input_data={
        "name": "Test Lead",
        "title": "CTO",
        "company": "TestCorp",
        "company_size": "500-1000 employees",
        "industry": "SaaS",
        "source": "Referral",
        "email": "test@testcorp.com",
        "phone": "+1-555-0100",
        "notes": "Specific scenario to test"
    },
    expected_output={
        "overall_score_range": (70, 90),
        "priority": "hot",
        "should_have_insights": True
    },
    evaluation_criteria={
        "score_accuracy_tolerance": 10,
        "priority_must_match": True,
        "must_generate_insights": True
    },
    tags=["custom", "edge_case"]
)

# Add to evaluation service
evaluation_service.add_test_case(custom_test)
```

### Test Case Fields

- **test_id**: Unique identifier
- **category**: One of the EvaluationCategory enum values
- **description**: Human-readable description
- **input_data**: Lead data dictionary matching the schema
- **expected_output**: Expected results (scores, classifications, etc.)
- **evaluation_criteria**: Pass/fail criteria and tolerances
- **tags**: For filtering and organization

---

## Best Practices

### 1. **Run Evaluations Regularly**
- Weekly during active development
- Before deploying prompt changes
- After major feature additions

### 2. **Track Performance Over Time**
- Save all reports for historical analysis
- Use comparison endpoint to track trends
- Document prompt changes with report IDs

### 3. **Focus on Real-World Scenarios**
- Add test cases based on actual leads
- Include edge cases encountered in production
- Balance positive and negative examples

### 4. **Iterative Improvement**
- Make one change at a time
- Test after each change
- Keep a changelog of prompt modifications

### 5. **Category-Specific Optimization**
- Don't over-optimize one category at the expense of others
- Maintain balanced performance across all categories
- Consider trade-offs (e.g., precision vs. recall)

### 6. **Use Tags Effectively**
- `baseline`: Core functionality tests
- `edge_case`: Unusual scenarios
- `regression`: Previously failing cases
- `performance`: Speed/efficiency tests
- Custom tags for your specific needs

---

## Troubleshooting

### Low Overall Scores (<60)

**Possible Causes:**
- System prompt lacks clarity
- Insufficient examples in prompt
- Scoring rubric not well-defined
- Output format not properly specified

**Solutions:**
1. Review qualitative analysis for patterns
2. Add explicit examples to system prompt
3. Clarify BANT scoring criteria
4. Strengthen output format requirements

### Inconsistent Results

**Possible Causes:**
- Temperature too high (> 0.5)
- Prompt ambiguity
- Test case tolerances too strict

**Solutions:**
1. Lower temperature (currently 0.3 - good)
2. Add more structure to prompt
3. Adjust evaluation criteria tolerances

### Specific Category Underperformance

**Red Flag Detection:**
- Add explicit red flag examples
- Include competitor scenarios
- Specify what constitutes a red flag

**Deal Size Estimation:**
- Provide company size to deal size mapping
- Include revenue/user count indicators
- Add industry-specific considerations

**Insight Generation:**
- Ask model to consider data points holistically
- Require specific number of insights
- Provide examples of good vs. poor insights

**Next Action Recommendations:**
- Add urgency-based prioritization framework
- Include examples of immediate vs. delayed actions
- Specify action types (call, email, demo, etc.)

---

## API Reference

### POST /api/leads/evaluation/run

Run evaluation suite.

**Request Body:**
```json
{
  "test_ids": ["enterprise_lead_001"],  // Optional
  "categories": ["lead_scoring"],  // Optional
  "tags": ["baseline"],  // Optional
  "generate_report": true  // Optional, default: true
}
```

**Response:**
```json
{
  "message": "Evaluation completed successfully",
  "report": {
    "report_id": "eval_report_20250101_120000",
    "summary": { ... },
    "category_scores": { ... },
    "actionable_recommendations": [ ... ],
    "prompt_iteration_plan": [ ... ]
  }
}
```

### GET /api/leads/evaluation/test-cases

List all test cases.

**Query Parameters:**
- `category`: Filter by category (optional)
- `tags`: Comma-separated tags (optional)

**Response:**
```json
{
  "test_cases": [
    {
      "test_id": "enterprise_lead_001",
      "category": "lead_scoring",
      "description": "Enterprise VP with clear authority...",
      "tags": ["enterprise", "high_priority", "baseline"],
      "expected_output": { ... }
    }
  ],
  "total": 8
}
```

### GET /api/leads/evaluation/reports

List recent reports.

**Query Parameters:**
- `limit`: Number of reports (default: 10)

**Response:**
```json
{
  "reports": [
    {
      "report_id": "eval_report_20250101_120000",
      "timestamp": "2025-01-01T12:00:00",
      "total_tests": 8,
      "passed_tests": 6,
      "overall_score": 75.5,
      "pass_rate": 75.0
    }
  ],
  "total": 5
}
```

### GET /api/leads/evaluation/reports/{report_id}

Get detailed report.

**Response:**
Full report object with all details, qualitative analyses, and results.

### GET /api/leads/evaluation/reports/{report_id}/export

Export report as JSON.

**Response:**
```json
{
  "report_id": "eval_report_20250101_120000",
  "export": "{ ... full JSON export ... }",
  "message": "Report exported successfully"
}
```

### POST /api/leads/evaluation/compare

Compare two reports.

**Request Body:**
```json
{
  "report1_id": "eval_report_20250101_120000",
  "report2_id": "eval_report_20250102_120000"
}
```

**Response:**
```json
{
  "message": "Reports compared successfully",
  "comparison": {
    "report1": { ... },
    "report2": { ... },
    "overall_score_change": 5.5,
    "pass_rate_change": 12.5,
    "category_improvements": {
      "lead_scoring": 10.0,
      "red_flag_detection": 15.0
    },
    "category_regressions": {},
    "summary": "Significant improvement in model performance"
  }
}
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Model Evaluation

on:
  pull_request:
    paths:
      - 'backend/app/services/grok_service.py'
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Monday

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Start services
        run: docker-compose up -d

      - name: Wait for API
        run: sleep 10

      - name: Run evaluation
        run: |
          curl -X POST http://localhost:8000/api/leads/evaluation/run \
            -H "Content-Type: application/json" \
            -d '{"tags": ["baseline"], "generate_report": true}' \
            -o evaluation_report.json

      - name: Check performance
        run: |
          SCORE=$(jq '.report.summary.overall_score' evaluation_report.json)
          if (( $(echo "$SCORE < 70" | bc -l) )); then
            echo "Performance below threshold: $SCORE"
            exit 1
          fi

      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-report
          path: evaluation_report.json
```

---

## Conclusion

The Model Evaluation Framework provides a systematic approach to prompt engineering, enabling data-driven improvements to Grok AI's performance. By regularly running evaluations, analyzing results, and iterating on prompts, you can ensure consistent, high-quality AI-powered lead scoring and analysis.

For questions or issues, refer to the codebase or create an issue in the repository.
