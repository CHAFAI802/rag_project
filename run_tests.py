#!/usr/bin/env python3
"""
Quick test runner - Tests RAG quality without requiring FastAPI server.
Perfect for CI/CD pipelines or manual verification.
"""

import sys
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from app.tests.test_quality import QualityTester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run quality tests and generate report."""
    try:
        logger.info("Starting RAG Quality Test Suite...")
        
        tester = QualityTester()
        report = tester.run_full_test_suite()
        
        # Print summary
        print("\n" + "="*80)
        print("QUALITY TEST SUMMARY")
        print("="*80)
        print(f"Total Tests:      {report.total_tests}")
        print(f"Passed:           {report.passed_tests}")
        print(f"Failed:           {report.total_tests - report.passed_tests}")
        print(f"Pass Rate:        {report.pass_rate:.1f}%")
        print(f"Avg Confidence:   {report.avg_confidence:.3f}")
        print("="*80 + "\n")
        
        # Detailed results
        print("\nDETAILED RESULTS:\n")
        for i, metric in enumerate(report.test_metrics, 1):
            status = "✅ PASS" if metric.passed else "❌ FAIL"
            print(f"{i:2d}. [{metric.test_category.upper():15s}] {status}")
            print(f"    Q: {metric.question}")
            print(f"    Confidence: {metric.confidence_score:.1%} | Sources: {metric.num_sources}")
            print()
        
        # Return appropriate exit code
        return 0 if report.pass_rate >= 80 else 1
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
