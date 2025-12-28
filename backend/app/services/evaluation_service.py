"""
Model Evaluation Service for Grok AI Performance Testing

This service provides a comprehensive evaluation framework for systematic prompt engineering,
including performance metrics, qualitative analysis, and actionable recommendations.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import statistics


class EvaluationCategory(str, Enum):
    """Categories of evaluation tests"""
    LEAD_SCORING = "lead_scoring"
    BANT_ANALYSIS = "bant_analysis"
    PRIORITY_CLASSIFICATION = "priority_classification"
    DEAL_SIZE_ESTIMATION = "deal_size_estimation"
    INSIGHT_GENERATION = "insight_generation"
    RED_FLAG_DETECTION = "red_flag_detection"
    NEXT_ACTION_RECOMMENDATION = "next_action_recommendation"


class PerformanceLevel(str, Enum):
    """Performance level classifications"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    FAILING = "failing"


@dataclass
class EvaluationTestCase:
    """Represents a single evaluation test case"""
    test_id: str
    category: EvaluationCategory
    description: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    evaluation_criteria: Dict[str, Any]
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class EvaluationResult:
    """Results from a single evaluation"""
    test_id: str
    category: EvaluationCategory
    actual_output: Dict[str, Any]
    expected_output: Dict[str, Any]
    score: float  # 0-100
    passed: bool
    performance_level: PerformanceLevel
    discrepancies: List[str]
    strengths: List[str]
    response_time_ms: float
    token_usage: Optional[int]
    timestamp: str
    error: Optional[str] = None


@dataclass
class QualitativeAnalysis:
    """Qualitative analysis of model performance"""
    category: EvaluationCategory
    underperformance_patterns: List[str]
    specific_failure_cases: List[Dict[str, Any]]
    root_cause_analysis: List[str]
    prompt_improvement_suggestions: List[str]
    confidence_score: float  # 0-100


@dataclass
class EvaluationReport:
    """Comprehensive evaluation report"""
    report_id: str
    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    overall_score: float
    category_scores: Dict[str, float]
    performance_breakdown: Dict[str, int]  # Count by performance level
    qualitative_analyses: List[QualitativeAnalysis]
    actionable_recommendations: List[str]
    prompt_iteration_plan: List[str]
    detailed_results: List[EvaluationResult]


class ModelEvaluationService:
    """Service for evaluating Grok AI model performance"""

    def __init__(self):
        self.test_cases: Dict[str, EvaluationTestCase] = {}
        self.results: List[EvaluationResult] = []
        self.reports: List[EvaluationReport] = []
        self._initialize_standard_test_cases()

    def _initialize_standard_test_cases(self):
        """Initialize standard test cases for comprehensive evaluation"""

        # Enterprise Lead - Should score high
        self.add_test_case(EvaluationTestCase(
            test_id="enterprise_lead_001",
            category=EvaluationCategory.LEAD_SCORING,
            description="Enterprise VP with clear authority and budget - should score 80+",
            input_data={
                "name": "Sarah Chen",
                "title": "VP of Engineering",
                "company": "TechCorp Inc",
                "company_size": "1000+ employees",
                "industry": "Enterprise Software",
                "source": "Direct Website Inquiry",
                "email": "sarah.chen@techcorp.com",
                "phone": "+1-555-0123",
                "notes": "Looking to replace current CRM. Budget approved for Q1. Needs demo ASAP."
            },
            expected_output={
                "overall_score_range": (80, 100),
                "priority": "hot",
                "deal_size": "enterprise",
                "should_have_strengths": True,
                "should_have_next_actions": True,
                "authority_score_min": 25,
                "company_fit_score_min": 25
            },
            evaluation_criteria={
                "score_accuracy_tolerance": 10,
                "priority_must_match": True,
                "deal_size_must_match": True,
                "must_identify_budget_mention": True,
                "must_identify_urgency": True
            },
            tags=["enterprise", "high_priority", "baseline"]
        ))

        # Low Quality Lead - Should score low
        self.add_test_case(EvaluationTestCase(
            test_id="low_quality_lead_001",
            category=EvaluationCategory.LEAD_SCORING,
            description="Student intern with no authority - should score below 40",
            input_data={
                "name": "John Doe",
                "title": "Intern",
                "company": "Small Startup",
                "company_size": "1-10 employees",
                "industry": "Unknown",
                "source": "Cold Email",
                "email": "john@startup.com",
                "phone": "",
                "notes": "Just browsing options"
            },
            expected_output={
                "overall_score_range": (0, 40),
                "priority": "cold",
                "deal_size": "small",
                "should_have_red_flags": True
            },
            evaluation_criteria={
                "score_accuracy_tolerance": 10,
                "priority_must_match": True,
                "must_identify_low_authority": True,
                "must_identify_weak_engagement": True
            },
            tags=["low_quality", "baseline"]
        ))

        # Mid-tier Lead - Should score medium
        self.add_test_case(EvaluationTestCase(
            test_id="midtier_lead_001",
            category=EvaluationCategory.LEAD_SCORING,
            description="Manager at medium company - should score 50-70",
            input_data={
                "name": "Alice Johnson",
                "title": "Sales Manager",
                "company": "MidSize Corp",
                "company_size": "100-500 employees",
                "industry": "B2B Services",
                "source": "LinkedIn",
                "email": "alice.j@midsizecorp.com",
                "phone": "+1-555-0199",
                "notes": "Interested in learning more about pricing"
            },
            expected_output={
                "overall_score_range": (50, 70),
                "priority": "warm",
                "deal_size": "medium",
            },
            evaluation_criteria={
                "score_accuracy_tolerance": 15,
                "priority_must_match": True
            },
            tags=["midtier", "baseline"]
        ))

        # BANT Analysis - Authority Detection
        self.add_test_case(EvaluationTestCase(
            test_id="bant_authority_001",
            category=EvaluationCategory.BANT_ANALYSIS,
            description="Test accurate authority detection with C-level executive",
            input_data={
                "name": "Michael Roberts",
                "title": "CTO",
                "company": "Innovation Labs",
                "company_size": "500-1000 employees",
                "industry": "Technology",
                "source": "Referral",
                "email": "michael.roberts@innovationlabs.com",
                "phone": "+1-555-0150",
                "notes": "Decision maker for all tech purchases. Direct access to CEO."
            },
            expected_output={
                "authority_score_min": 28,
                "should_mention_decision_maker": True,
                "should_identify_c_level": True
            },
            evaluation_criteria={
                "must_score_high_authority": True,
                "must_mention_in_reasoning": "decision maker"
            },
            tags=["bant", "authority", "c_level"]
        ))

        # Red Flag Detection
        self.add_test_case(EvaluationTestCase(
            test_id="red_flag_001",
            category=EvaluationCategory.RED_FLAG_DETECTION,
            description="Should detect competitor and potential tire-kicker",
            input_data={
                "name": "Competitor Research",
                "title": "Market Analyst",
                "company": "CompetitorCorp",
                "company_size": "Unknown",
                "industry": "Same as ours",
                "source": "Unknown",
                "email": "research@competitor.com",
                "phone": "",
                "notes": "Asking lots of questions about pricing and features. No mention of actual need."
            },
            expected_output={
                "should_have_red_flags": True,
                "should_identify_competitor_risk": True,
                "priority": "cold"
            },
            evaluation_criteria={
                "must_detect_red_flags": True,
                "must_mention_competitor_or_research": True
            },
            tags=["red_flags", "edge_case"]
        ))

        # Deal Size Estimation
        self.add_test_case(EvaluationTestCase(
            test_id="deal_size_001",
            category=EvaluationCategory.DEAL_SIZE_ESTIMATION,
            description="Large company should be estimated as enterprise deal",
            input_data={
                "name": "Enterprise Buyer",
                "title": "Director of Sales Operations",
                "company": "Fortune 500 Company",
                "company_size": "10000+ employees",
                "industry": "Financial Services",
                "source": "Direct Inquiry",
                "email": "buyer@fortune500.com",
                "phone": "+1-555-0200",
                "notes": "Need solution for entire sales org, 500+ users"
            },
            expected_output={
                "deal_size": "enterprise",
                "should_mention_scale": True
            },
            evaluation_criteria={
                "deal_size_must_match": True,
                "must_recognize_scale": True
            },
            tags=["deal_size", "enterprise"]
        ))

        # Next Action Recommendation
        self.add_test_case(EvaluationTestCase(
            test_id="next_action_001",
            category=EvaluationCategory.NEXT_ACTION_RECOMMENDATION,
            description="Hot lead should get immediate action recommendations",
            input_data={
                "name": "Urgent Buyer",
                "title": "VP Sales",
                "company": "GrowthCo",
                "company_size": "500+ employees",
                "industry": "SaaS",
                "source": "Direct Inquiry",
                "email": "urgent@growthco.com",
                "phone": "+1-555-0300",
                "notes": "Current CRM contract expires in 2 weeks. Need replacement urgently."
            },
            expected_output={
                "should_have_next_actions": True,
                "should_recommend_urgency": True,
                "priority": "hot"
            },
            evaluation_criteria={
                "must_have_immediate_action": True,
                "must_identify_urgency": True
            },
            tags=["next_action", "urgency"]
        ))

        # Insight Generation - Complex case
        self.add_test_case(EvaluationTestCase(
            test_id="insight_generation_001",
            category=EvaluationCategory.INSIGHT_GENERATION,
            description="Should generate meaningful insights from limited information",
            input_data={
                "name": "Minimal Info Lead",
                "title": "Manager",
                "company": "Some Company",
                "company_size": "Unknown",
                "industry": "Technology",
                "source": "Web Form",
                "email": "contact@somecompany.com",
                "phone": "",
                "notes": "Interested in demo"
            },
            expected_output={
                "should_have_insights": True,
                "should_identify_missing_info": True,
                "should_suggest_qualification": True
            },
            evaluation_criteria={
                "must_generate_insights": True,
                "must_acknowledge_limitations": True
            },
            tags=["insight", "edge_case", "incomplete_data"]
        ))

    def add_test_case(self, test_case: EvaluationTestCase) -> None:
        """Add a test case to the evaluation suite"""
        self.test_cases[test_case.test_id] = test_case

    def evaluate_response(
        self,
        test_case: EvaluationTestCase,
        actual_response: Dict[str, Any],
        response_time_ms: float,
        token_usage: Optional[int] = None
    ) -> EvaluationResult:
        """Evaluate a single response against expected output"""

        discrepancies = []
        strengths = []
        score = 100.0
        passed = True

        expected = test_case.expected_output
        criteria = test_case.evaluation_criteria

        # Score range validation
        if "overall_score_range" in expected:
            min_score, max_score = expected["overall_score_range"]
            actual_score = actual_response.get("overall_score", 0)
            if not (min_score <= actual_score <= max_score):
                discrepancies.append(
                    f"Score {actual_score} outside expected range [{min_score}, {max_score}]"
                )
                score -= 25
                passed = False
            else:
                strengths.append(f"Score {actual_score} within expected range")

        # Priority classification
        if "priority" in expected:
            expected_priority = expected["priority"]
            actual_priority = actual_response.get("priority", "").lower()

            if criteria.get("priority_must_match", False):
                if actual_priority != expected_priority:
                    discrepancies.append(
                        f"Priority mismatch: expected '{expected_priority}', got '{actual_priority}'"
                    )
                    score -= 20
                    passed = False
                else:
                    strengths.append(f"Priority correctly classified as '{expected_priority}'")

        # Deal size estimation
        if "deal_size" in expected:
            expected_size = expected["deal_size"]
            actual_size = actual_response.get("estimated_deal_size", "").lower()

            if criteria.get("deal_size_must_match", False):
                if actual_size != expected_size:
                    discrepancies.append(
                        f"Deal size mismatch: expected '{expected_size}', got '{actual_size}'"
                    )
                    score -= 15
                    passed = False
                else:
                    strengths.append(f"Deal size correctly estimated as '{expected_size}'")

        # BANT Authority Score
        if "authority_score_min" in expected:
            min_authority = expected["authority_score_min"]
            actual_authority = actual_response.get("score_breakdown", {}).get("authority", 0)

            if actual_authority < min_authority:
                discrepancies.append(
                    f"Authority score {actual_authority} below minimum {min_authority}"
                )
                score -= 15
            else:
                strengths.append(f"Authority score {actual_authority} meets minimum")

        # Company Fit Score
        if "company_fit_score_min" in expected:
            min_fit = expected["company_fit_score_min"]
            actual_fit = actual_response.get("score_breakdown", {}).get("company_fit", 0)

            if actual_fit < min_fit:
                discrepancies.append(
                    f"Company fit score {actual_fit} below minimum {min_fit}"
                )
                score -= 15
            else:
                strengths.append(f"Company fit score {actual_fit} meets minimum")

        # Red flags detection
        if expected.get("should_have_red_flags", False):
            red_flags = actual_response.get("red_flags", [])
            if not red_flags or len(red_flags) == 0:
                discrepancies.append("Expected red flags but none were identified")
                score -= 20
                if criteria.get("must_detect_red_flags", False):
                    passed = False
            else:
                strengths.append(f"Identified {len(red_flags)} red flags")

        # Strengths identification
        if expected.get("should_have_strengths", False):
            actual_strengths = actual_response.get("strengths", [])
            if not actual_strengths or len(actual_strengths) == 0:
                discrepancies.append("Expected strengths but none were identified")
                score -= 10
            else:
                strengths.append(f"Identified {len(actual_strengths)} strengths")

        # Next actions
        if expected.get("should_have_next_actions", False):
            next_actions = actual_response.get("next_actions", [])
            if not next_actions or len(next_actions) == 0:
                discrepancies.append("Expected next actions but none were provided")
                score -= 15
                if criteria.get("must_have_immediate_action", False):
                    passed = False
            else:
                strengths.append(f"Provided {len(next_actions)} next actions")

        # Insights generation
        if expected.get("should_have_insights", False):
            insights = actual_response.get("key_insights", [])
            if not insights or len(insights) == 0:
                discrepancies.append("Expected insights but none were generated")
                score -= 15
                if criteria.get("must_generate_insights", False):
                    passed = False
            else:
                strengths.append(f"Generated {len(insights)} insights")

        # Keyword/phrase detection in reasoning
        if "must_mention_in_reasoning" in criteria:
            required_phrase = criteria["must_mention_in_reasoning"].lower()
            reasoning = actual_response.get("reasoning", "").lower()

            if required_phrase not in reasoning:
                discrepancies.append(
                    f"Reasoning does not mention expected keyword: '{required_phrase}'"
                )
                score -= 10
            else:
                strengths.append(f"Reasoning appropriately mentions '{required_phrase}'")

        # Response time evaluation (bonus/penalty)
        if response_time_ms < 2000:
            strengths.append(f"Fast response time: {response_time_ms:.0f}ms")
        elif response_time_ms > 10000:
            discrepancies.append(f"Slow response time: {response_time_ms:.0f}ms")
            score -= 5

        # Cap score at 0-100
        score = max(0, min(100, score))

        # Determine performance level
        if score >= 90:
            performance_level = PerformanceLevel.EXCELLENT
        elif score >= 75:
            performance_level = PerformanceLevel.GOOD
        elif score >= 60:
            performance_level = PerformanceLevel.ACCEPTABLE
        elif score >= 40:
            performance_level = PerformanceLevel.POOR
        else:
            performance_level = PerformanceLevel.FAILING

        return EvaluationResult(
            test_id=test_case.test_id,
            category=test_case.category,
            actual_output=actual_response,
            expected_output=expected,
            score=score,
            passed=passed,
            performance_level=performance_level,
            discrepancies=discrepancies,
            strengths=strengths,
            response_time_ms=response_time_ms,
            token_usage=token_usage,
            timestamp=datetime.utcnow().isoformat()
        )

    async def run_evaluation_suite(
        self,
        grok_service,
        test_ids: Optional[List[str]] = None,
        categories: Optional[List[EvaluationCategory]] = None,
        tags: Optional[List[str]] = None
    ) -> List[EvaluationResult]:
        """
        Run a suite of evaluation tests

        Args:
            grok_service: Instance of GrokService to test
            test_ids: Specific test IDs to run (None = all)
            categories: Filter by categories (None = all)
            tags: Filter by tags (None = all)

        Returns:
            List of evaluation results
        """
        results = []

        # Filter test cases
        test_cases_to_run = []
        for test_case in self.test_cases.values():
            # Filter by test_ids
            if test_ids and test_case.test_id not in test_ids:
                continue

            # Filter by categories
            if categories and test_case.category not in categories:
                continue

            # Filter by tags
            if tags and not any(tag in test_case.tags for tag in tags):
                continue

            test_cases_to_run.append(test_case)

        # Run each test case
        for test_case in test_cases_to_run:
            try:
                # Measure response time
                start_time = time.time()

                # Call Grok service with test data
                response = await grok_service.score_lead(test_case.input_data)

                response_time_ms = (time.time() - start_time) * 1000

                # Evaluate the response
                result = self.evaluate_response(
                    test_case=test_case,
                    actual_response=response,
                    response_time_ms=response_time_ms,
                    token_usage=None  # Could extract from response if available
                )

                results.append(result)

            except Exception as e:
                # Record error result
                error_result = EvaluationResult(
                    test_id=test_case.test_id,
                    category=test_case.category,
                    actual_output={},
                    expected_output=test_case.expected_output,
                    score=0.0,
                    passed=False,
                    performance_level=PerformanceLevel.FAILING,
                    discrepancies=[f"Exception occurred: {str(e)}"],
                    strengths=[],
                    response_time_ms=0.0,
                    token_usage=None,
                    timestamp=datetime.utcnow().isoformat(),
                    error=str(e)
                )
                results.append(error_result)

        self.results.extend(results)
        return results

    def perform_qualitative_analysis(
        self,
        results: List[EvaluationResult]
    ) -> List[QualitativeAnalysis]:
        """
        Perform qualitative analysis on evaluation results to identify patterns
        and root causes of underperformance
        """
        analyses = []

        # Group results by category
        category_results = {}
        for result in results:
            if result.category not in category_results:
                category_results[result.category] = []
            category_results[result.category].append(result)

        # Analyze each category
        for category, cat_results in category_results.items():
            underperformance_patterns = []
            failure_cases = []
            root_causes = []
            prompt_suggestions = []

            # Calculate category metrics
            failed_results = [r for r in cat_results if not r.passed]
            poor_results = [r for r in cat_results if r.performance_level in [
                PerformanceLevel.POOR, PerformanceLevel.FAILING
            ]]

            avg_score = statistics.mean([r.score for r in cat_results]) if cat_results else 0

            # Identify patterns in discrepancies
            all_discrepancies = []
            for result in failed_results:
                all_discrepancies.extend(result.discrepancies)

            # Common discrepancy patterns
            discrepancy_counts = {}
            for disc in all_discrepancies:
                # Extract pattern (first part before specific values)
                if "mismatch" in disc:
                    pattern = "Classification mismatch"
                elif "below minimum" in disc:
                    pattern = "Insufficient scoring"
                elif "Expected" in disc and "but" in disc:
                    pattern = "Missing expected output"
                elif "outside expected range" in disc:
                    pattern = "Score calibration issue"
                else:
                    pattern = disc

                discrepancy_counts[pattern] = discrepancy_counts.get(pattern, 0) + 1

            # Report top patterns
            for pattern, count in sorted(discrepancy_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                underperformance_patterns.append(f"{pattern} (occurred {count} times)")

            # Capture specific failure cases
            for result in poor_results[:3]:  # Top 3 worst cases
                failure_cases.append({
                    "test_id": result.test_id,
                    "score": result.score,
                    "discrepancies": result.discrepancies[:2],  # Top 2 issues
                    "input_sample": result.actual_output.get("lead_name", "N/A")
                })

            # Root cause analysis
            if "Classification mismatch" in [p for p in underperformance_patterns]:
                root_causes.append(
                    "Priority/deal size classification criteria may be too strict or unclear in prompt"
                )
                prompt_suggestions.append(
                    "Add more explicit examples of hot/warm/cold leads in system prompt with score ranges"
                )

            if "Insufficient scoring" in [p for p in underperformance_patterns]:
                root_causes.append(
                    "BANT component scoring may be under-weighting certain factors"
                )
                prompt_suggestions.append(
                    "Clarify BANT scoring rubric with specific point allocations for each factor"
                )

            if "Missing expected output" in [p for p in underperformance_patterns]:
                root_causes.append(
                    "Model may not consistently generate all required output fields"
                )
                prompt_suggestions.append(
                    "Strengthen output format instructions and add JSON schema validation requirement"
                )

            if "Score calibration issue" in [p for p in underperformance_patterns]:
                root_causes.append(
                    "Score ranges may not align with lead quality expectations"
                )
                prompt_suggestions.append(
                    "Recalibrate scoring thresholds based on actual lead conversion data"
                )

            # Category-specific analysis
            if category == EvaluationCategory.RED_FLAG_DETECTION:
                if avg_score < 70:
                    root_causes.append(
                        "Red flag detection sensitivity may be too low"
                    )
                    prompt_suggestions.append(
                        "Expand red flag examples in prompt: competitor signals, tire-kickers, invalid contacts"
                    )

            if category == EvaluationCategory.NEXT_ACTION_RECOMMENDATION:
                if avg_score < 70:
                    root_causes.append(
                        "Next action recommendations may lack specificity or urgency awareness"
                    )
                    prompt_suggestions.append(
                        "Add framework for urgency-based action prioritization in prompt"
                    )

            if category == EvaluationCategory.INSIGHT_GENERATION:
                if avg_score < 70:
                    root_causes.append(
                        "Insight generation may be superficial or template-based"
                    )
                    prompt_suggestions.append(
                        "Encourage deeper analysis by asking model to consider multiple data points together"
                    )

            # Default suggestions if none found
            if not prompt_suggestions:
                prompt_suggestions.append(
                    "Review and refine prompt with additional context and examples"
                )

            analysis = QualitativeAnalysis(
                category=category,
                underperformance_patterns=underperformance_patterns,
                specific_failure_cases=failure_cases,
                root_cause_analysis=root_causes,
                prompt_improvement_suggestions=prompt_suggestions,
                confidence_score=avg_score
            )

            analyses.append(analysis)

        return analyses

    def generate_evaluation_report(
        self,
        results: List[EvaluationResult],
        report_id: Optional[str] = None
    ) -> EvaluationReport:
        """Generate comprehensive evaluation report with recommendations"""

        if report_id is None:
            report_id = f"eval_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Calculate overall metrics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        overall_score = statistics.mean([r.score for r in results]) if results else 0

        # Category scores
        category_scores = {}
        category_results = {}
        for result in results:
            cat = result.category.value
            if cat not in category_results:
                category_results[cat] = []
            category_results[cat].append(result)

        for cat, cat_results in category_results.items():
            category_scores[cat] = statistics.mean([r.score for r in cat_results])

        # Performance breakdown
        performance_breakdown = {
            PerformanceLevel.EXCELLENT.value: 0,
            PerformanceLevel.GOOD.value: 0,
            PerformanceLevel.ACCEPTABLE.value: 0,
            PerformanceLevel.POOR.value: 0,
            PerformanceLevel.FAILING.value: 0
        }

        for result in results:
            performance_breakdown[result.performance_level.value] += 1

        # Qualitative analyses
        qualitative_analyses = self.perform_qualitative_analysis(results)

        # Generate actionable recommendations
        actionable_recommendations = []
        prompt_iteration_plan = []

        # Based on overall score
        if overall_score < 60:
            actionable_recommendations.append(
                "CRITICAL: Overall model performance is below acceptable threshold. Immediate prompt revision required."
            )
            prompt_iteration_plan.append(
                "1. Conduct prompt engineering workshop to redesign system prompt from scratch"
            )
        elif overall_score < 75:
            actionable_recommendations.append(
                "Model performance needs improvement. Focus on specific underperforming categories."
            )
            prompt_iteration_plan.append(
                "1. Iteratively refine prompts for lowest-scoring categories"
            )
        else:
            actionable_recommendations.append(
                "Model performance is acceptable. Focus on optimization and edge cases."
            )
            prompt_iteration_plan.append(
                "1. Fine-tune prompts for edge cases and complex scenarios"
            )

        # Category-specific recommendations
        for cat, score in sorted(category_scores.items(), key=lambda x: x[1]):
            if score < 70:
                actionable_recommendations.append(
                    f"Priority: Improve {cat.replace('_', ' ').title()} (score: {score:.1f})"
                )

        # Add suggestions from qualitative analysis
        for analysis in qualitative_analyses:
            if analysis.confidence_score < 70:
                for suggestion in analysis.prompt_improvement_suggestions[:2]:
                    if suggestion not in prompt_iteration_plan:
                        prompt_iteration_plan.append(f"- {suggestion}")

        # Response time recommendations
        slow_responses = [r for r in results if r.response_time_ms > 5000]
        if len(slow_responses) > total_tests * 0.2:  # More than 20% slow
            actionable_recommendations.append(
                "Performance: Consider reducing max_tokens or optimizing prompt length for faster responses"
            )

        # Add testing recommendations
        actionable_recommendations.append(
            "Testing: Run evaluations weekly to track prompt iteration effectiveness"
        )
        actionable_recommendations.append(
            "Data: Collect real-world lead scoring data for comparison and calibration"
        )

        # Finalize iteration plan
        if len(prompt_iteration_plan) == 1:  # Only has the initial step
            prompt_iteration_plan.append("2. Add specific examples for underperforming scenarios")
            prompt_iteration_plan.append("3. Test with edge cases and validate improvements")
            prompt_iteration_plan.append("4. Deploy updated prompt and monitor performance")

        report = EvaluationReport(
            report_id=report_id,
            timestamp=datetime.utcnow().isoformat(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            overall_score=overall_score,
            category_scores=category_scores,
            performance_breakdown=performance_breakdown,
            qualitative_analyses=qualitative_analyses,
            actionable_recommendations=actionable_recommendations,
            prompt_iteration_plan=prompt_iteration_plan,
            detailed_results=results
        )

        self.reports.append(report)
        return report

    def export_report_to_json(self, report: EvaluationReport) -> str:
        """Export evaluation report to JSON string"""

        # Convert dataclasses to dicts
        report_dict = {
            "report_id": report.report_id,
            "timestamp": report.timestamp,
            "summary": {
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "overall_score": report.overall_score,
                "pass_rate": (report.passed_tests / report.total_tests * 100) if report.total_tests > 0 else 0
            },
            "category_scores": report.category_scores,
            "performance_breakdown": report.performance_breakdown,
            "qualitative_analyses": [asdict(qa) for qa in report.qualitative_analyses],
            "actionable_recommendations": report.actionable_recommendations,
            "prompt_iteration_plan": report.prompt_iteration_plan,
            "detailed_results": [asdict(r) for r in report.detailed_results]
        }

        return json.dumps(report_dict, indent=2)

    def get_comparison_report(
        self,
        report1: EvaluationReport,
        report2: EvaluationReport
    ) -> Dict[str, Any]:
        """Compare two evaluation reports to track improvement"""

        comparison = {
            "report1_id": report1.report_id,
            "report2_id": report2.report_id,
            "overall_score_change": report2.overall_score - report1.overall_score,
            "pass_rate_change": (
                (report2.passed_tests / report2.total_tests) -
                (report1.passed_tests / report1.total_tests)
            ) * 100 if report1.total_tests > 0 and report2.total_tests > 0 else 0,
            "category_improvements": {},
            "category_regressions": {},
            "summary": ""
        }

        # Compare category scores
        for category in set(list(report1.category_scores.keys()) + list(report2.category_scores.keys())):
            score1 = report1.category_scores.get(category, 0)
            score2 = report2.category_scores.get(category, 0)
            change = score2 - score1

            if change > 0:
                comparison["category_improvements"][category] = change
            elif change < 0:
                comparison["category_regressions"][category] = change

        # Generate summary
        if comparison["overall_score_change"] > 5:
            comparison["summary"] = "Significant improvement in model performance"
        elif comparison["overall_score_change"] > 0:
            comparison["summary"] = "Slight improvement in model performance"
        elif comparison["overall_score_change"] > -5:
            comparison["summary"] = "Minimal change in model performance"
        else:
            comparison["summary"] = "Performance regression detected"

        return comparison
