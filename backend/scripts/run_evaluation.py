#!/usr/bin/env python3
"""
Script to run model evaluation and save results

Usage:
    python scripts/run_evaluation.py --all
    python scripts/run_evaluation.py --category lead_scoring
    python scripts/run_evaluation.py --tags baseline
    python scripts/run_evaluation.py --compare report1_id report2_id
"""

import argparse
import json
import sys
from datetime import datetime
import httpx


API_BASE_URL = "http://localhost:8000/api/leads"


def run_evaluation(test_ids=None, categories=None, tags=None, generate_report=True):
    """Run model evaluation"""

    payload = {
        "generate_report": generate_report
    }

    if test_ids:
        payload["test_ids"] = test_ids
    if categories:
        payload["categories"] = categories
    if tags:
        payload["tags"] = tags

    print("Running evaluation...")
    print(f"Filters: {payload}")
    print()

    try:
        response = httpx.post(
            f"{API_BASE_URL}/evaluation/run",
            json=payload,
            timeout=300.0  # 5 minute timeout for large test suites
        )
        response.raise_for_status()

        result = response.json()

        if generate_report:
            report = result["report"]
            print("=" * 80)
            print("EVALUATION REPORT")
            print("=" * 80)
            print(f"Report ID: {report['report_id']}")
            print(f"Timestamp: {report['timestamp']}")
            print()

            summary = report["summary"]
            print("SUMMARY")
            print("-" * 80)
            print(f"Total Tests:   {summary['total_tests']}")
            print(f"Passed:        {summary['passed_tests']}")
            print(f"Failed:        {summary['failed_tests']}")
            print(f"Overall Score: {summary['overall_score']:.2f}/100")
            print(f"Pass Rate:     {summary['pass_rate']:.1f}%")
            print()

            print("CATEGORY SCORES")
            print("-" * 80)
            for category, score in sorted(report["category_scores"].items(), key=lambda x: x[1]):
                status = "✓" if score >= 70 else "✗"
                print(f"{status} {category:30s} {score:6.2f}")
            print()

            print("PERFORMANCE BREAKDOWN")
            print("-" * 80)
            for level, count in report["performance_breakdown"].items():
                print(f"{level:15s} {count}")
            print()

            print("ACTIONABLE RECOMMENDATIONS")
            print("-" * 80)
            for i, rec in enumerate(report["actionable_recommendations"], 1):
                print(f"{i}. {rec}")
            print()

            print("PROMPT ITERATION PLAN")
            print("-" * 80)
            for item in report["prompt_iteration_plan"]:
                print(f"  {item}")
            print()

            # Save full report to file
            filename = f"evaluation_reports/{report['report_id']}.json"
            with open(filename, "w") as f:
                json.dump(result, f, indent=2)

            print(f"Full report saved to: {filename}")

            return report["report_id"]

        else:
            print(f"Evaluation completed: {len(result['results'])} tests run")
            return None

    except httpx.HTTPError as e:
        print(f"Error running evaluation: {e}")
        sys.exit(1)


def list_test_cases(category=None, tags=None):
    """List available test cases"""

    params = {}
    if category:
        params["category"] = category
    if tags:
        params["tags"] = tags

    try:
        response = httpx.get(
            f"{API_BASE_URL}/evaluation/test-cases",
            params=params
        )
        response.raise_for_status()

        result = response.json()

        print("=" * 80)
        print("AVAILABLE TEST CASES")
        print("=" * 80)
        print(f"Total: {result['total']}")
        print()

        for tc in result["test_cases"]:
            print(f"ID:          {tc['test_id']}")
            print(f"Category:    {tc['category']}")
            print(f"Description: {tc['description']}")
            print(f"Tags:        {', '.join(tc['tags'])}")
            print("-" * 80)

    except httpx.HTTPError as e:
        print(f"Error listing test cases: {e}")
        sys.exit(1)


def list_reports(limit=10):
    """List recent evaluation reports"""

    try:
        response = httpx.get(
            f"{API_BASE_URL}/evaluation/reports",
            params={"limit": limit}
        )
        response.raise_for_status()

        result = response.json()

        print("=" * 80)
        print("RECENT EVALUATION REPORTS")
        print("=" * 80)
        print(f"Total: {result['total']}")
        print()

        for report in result["reports"]:
            print(f"ID:        {report['report_id']}")
            print(f"Timestamp: {report['timestamp']}")
            print(f"Tests:     {report['total_tests']} ({report['passed_tests']} passed)")
            print(f"Score:     {report['overall_score']:.2f}/100")
            print(f"Pass Rate: {report['pass_rate']:.1f}%")
            print("-" * 80)

    except httpx.HTTPError as e:
        print(f"Error listing reports: {e}")
        sys.exit(1)


def get_report(report_id):
    """Get detailed report"""

    try:
        response = httpx.get(
            f"{API_BASE_URL}/evaluation/reports/{report_id}"
        )
        response.raise_for_status()

        result = response.json()

        print("=" * 80)
        print(f"EVALUATION REPORT: {result['report_id']}")
        print("=" * 80)
        print(json.dumps(result, indent=2))

    except httpx.HTTPError as e:
        print(f"Error getting report: {e}")
        sys.exit(1)


def compare_reports(report1_id, report2_id):
    """Compare two evaluation reports"""

    try:
        response = httpx.post(
            f"{API_BASE_URL}/evaluation/compare",
            json={
                "report1_id": report1_id,
                "report2_id": report2_id
            }
        )
        response.raise_for_status()

        result = response.json()
        comparison = result["comparison"]

        print("=" * 80)
        print("REPORT COMPARISON")
        print("=" * 80)
        print()

        print("REPORT 1")
        print("-" * 80)
        print(f"ID:        {comparison['report1']['id']}")
        print(f"Timestamp: {comparison['report1']['timestamp']}")
        print(f"Score:     {comparison['report1']['overall_score']:.2f}")
        print()

        print("REPORT 2")
        print("-" * 80)
        print(f"ID:        {comparison['report2']['id']}")
        print(f"Timestamp: {comparison['report2']['timestamp']}")
        print(f"Score:     {comparison['report2']['overall_score']:.2f}")
        print()

        print("CHANGES")
        print("-" * 80)
        score_change = comparison["overall_score_change"]
        score_symbol = "↑" if score_change > 0 else "↓" if score_change < 0 else "="
        print(f"Overall Score:  {score_symbol} {abs(score_change):.2f}")

        pass_change = comparison["pass_rate_change"]
        pass_symbol = "↑" if pass_change > 0 else "↓" if pass_change < 0 else "="
        print(f"Pass Rate:      {pass_symbol} {abs(pass_change):.2f}%")
        print()

        if comparison["category_improvements"]:
            print("IMPROVEMENTS:")
            for cat, change in comparison["category_improvements"].items():
                print(f"  ↑ {cat:30s} +{change:.2f}")
            print()

        if comparison["category_regressions"]:
            print("REGRESSIONS:")
            for cat, change in comparison["category_regressions"].items():
                print(f"  ↓ {cat:30s} {change:.2f}")
            print()

        print(f"Summary: {comparison['summary']}")

    except httpx.HTTPError as e:
        print(f"Error comparing reports: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run model evaluation")

    parser.add_argument("--all", action="store_true", help="Run all test cases")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--tags", help="Filter by tags (comma-separated)")
    parser.add_argument("--test-ids", help="Specific test IDs (comma-separated)")

    parser.add_argument("--list-tests", action="store_true", help="List available test cases")
    parser.add_argument("--list-reports", action="store_true", help="List recent reports")
    parser.add_argument("--get-report", help="Get detailed report by ID")
    parser.add_argument("--compare", nargs=2, metavar=("REPORT1", "REPORT2"), help="Compare two reports")

    parser.add_argument("--no-report", action="store_true", help="Don't generate full report")

    args = parser.parse_args()

    # List operations
    if args.list_tests:
        list_test_cases(category=args.category, tags=args.tags)
        return

    if args.list_reports:
        list_reports()
        return

    if args.get_report:
        get_report(args.get_report)
        return

    if args.compare:
        compare_reports(args.compare[0], args.compare[1])
        return

    # Run evaluation
    test_ids = args.test_ids.split(",") if args.test_ids else None
    categories = [args.category] if args.category else None
    tags = args.tags.split(",") if args.tags else None
    generate_report = not args.no_report

    if not args.all and not test_ids and not categories and not tags:
        print("Error: Must specify --all, --test-ids, --category, or --tags")
        print()
        parser.print_help()
        sys.exit(1)

    run_evaluation(
        test_ids=test_ids,
        categories=categories,
        tags=tags,
        generate_report=generate_report
    )


if __name__ == "__main__":
    main()
