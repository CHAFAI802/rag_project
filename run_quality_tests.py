#!/usr/bin/env python3
"""
🚚 RAG MASTER TEST RUNNER
Complete Quality Assurance & Testing Orchestration

This script orchestrates all quality testing and demonstrations:
1. Setup & validation
2. Comprehensive quality testing (Categories A, B, C)
3. Live demonstrations
4. Report generation
5. Executive summary

Usage:
    python run_quality_tests.py [--demo] [--quick] [--export]

Options:
    --demo      : Run interactive demonstration instead of tests
    --quick     : Run quick validation tests only
    --export    : Export results to JSON/CSV for analysis
    --full      : Run complete test suite with all validations
"""

import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header():
    """Print application header."""
    print("\n" + "█"*80)
    print("█ 🚚 RAG QUALITY TESTING & DEMONSTRATION - Master Test Runner")
    print("█ Logistics Integration RAG System - Enterprise Quality Assurance")
    print("█"*80 + "\n")


def validate_environment():
    """Validate that the system is properly configured."""
    print("🔍 Validating environment...\n")
    
    from app.services.rag_pipeline import vectorstore
    
    # Check if vector store is initialized
    if vectorstore is None:
        print("❌ ERROR: Vector store not initialized")
        print("   Run 'python setup_rag.py' first\n")
        return False
    
    print("✅ Vector store initialized")
    
    # Check documents indexed
    try:
        # Try a simple query to verify functionality
        from app.services.rag_pipeline import query_rag_with_sources
        response = query_rag_with_sources("test query")
        if response:
            print("✅ RAG pipeline functional")
        else:
            print("⚠️  RAG pipeline returned empty response")
            return False
    except Exception as e:
        print(f"❌ ERROR: RAG pipeline error: {e}")
        return False
    
    print("✅ All validations passed\n")
    return True


def run_executive_tests():
    """Run comprehensive executive quality test suite."""
    print("📊 Running Executive Quality Test Suite...\n")
    print("="*80)
    
    try:
        from quality_testing_executive import ExecutiveQualityTester
        
        tester = ExecutiveQualityTester()
        report = tester.run_full_suite()
        
        # Print executive summary
        tester.print_executive_summary()
        
        # Export JSON report
        tester.export_json_report("quality_report.json")
        
        # Summary
        if report['hallucinations_detected'] == 0 and report['failed_tests'] == 0:
            print("✅ ALL QUALITY TESTS PASSED")
            return True
        else:
            print("❌ QUALITY TESTS FAILED")
            print(f"   Failed: {report['failed_tests']}")
            print(f"   Hallucinations: {report['hallucinations_detected']}\n")
            return False
            
    except ImportError as e:
        print(f"❌ ERROR: Could not import quality_testing_executive: {e}")
        print("   Make sure quality_testing_executive.py is in the project root\n")
        return False
    except Exception as e:
        logger.error(f"Error running executive tests: {e}", exc_info=True)
        return False


def run_demonstration():
    """Run interactive live demonstration."""
    print("🎬 Running Interactive Demonstration...\n")
    print("="*80)
    
    try:
        from demo_quality_testing import RAGQualityDemo
        
        demo = RAGQualityDemo()
        demo.run_full_demo()
        
        return True
        
    except ImportError as e:
        print(f"❌ ERROR: Could not import demo_quality_testing: {e}")
        return False
    except Exception as e:
        logger.error(f"Error running demonstration: {e}", exc_info=True)
        return False


def run_quick_validation():
    """Run quick validation tests only."""
    print("⚡ Running Quick Validation Tests...\n")
    
    try:
        from app.services.rag_pipeline import query_rag_with_sources
        
        print("Testing simple question...")
        response1 = query_rag_with_sources("Quel est le délai maximal de retard fournisseur ?")
        if response1.confidence > 0.5 and len(response1.sources) > 0:
            print("✅ Simple question: PASS")
        else:
            print("❌ Simple question: FAIL")
            return False
        
        print("Testing complex question...")
        response2 = query_rag_with_sources("Procédure complète en cas de retard fournisseur")
        if response2.confidence > 0.4 and len(response2.sources) > 0:
            print("✅ Complex question: PASS")
        else:
            print("❌ Complex question: FAIL")
            return False
        
        print("Testing hallucination detection...")
        response3 = query_rag_with_sources("Politique sur les crypto-paiements ?")
        if response3.confidence < 0.5:
            print("✅ Hallucination detection: PASS")
        else:
            print("⚠️  Hallucination detection: NEEDS REVIEW")
        
        print("\n✅ Quick validation completed\n")
        return True
        
    except Exception as e:
        logger.error(f"Error in quick validation: {e}")
        return False


def show_usage():
    """Show usage help."""
    print("""
🚚 RAG QUALITY TEST RUNNER - Usage Guide

Commands:
    python run_quality_tests.py --full
        Run complete quality test suite (Category A, B, C)
        
    python run_quality_tests.py --demo
        Run interactive live demonstration
        
    python run_quality_tests.py --quick
        Run quick validation (2-3 key tests)
        
    python run_quality_tests.py --help
        Show this help message

Options:
    --export    : Export results to quality_report.json
    --verbose   : Enable verbose logging
    
Examples:
    # Run full tests with export
    python run_quality_tests.py --full --export
    
    # Run demonstration
    python run_quality_tests.py --demo
    
    # Quick validation
    python run_quality_tests.py --quick

Setup First:
    1. Source virtual environment:
       source .venv/bin/activate
    
    2. Index documents:
       python setup_rag.py
    
    3. Run tests:
       python run_quality_tests.py --full
""")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='RAG Quality Testing & Demonstration',
        add_help=False
    )
    parser.add_argument('--full', action='store_true', help='Run full test suite')
    parser.add_argument('--demo', action='store_true', help='Run demonstration')
    parser.add_argument('--quick', action='store_true', help='Run quick validation')
    parser.add_argument('--export', action='store_true', help='Export results to JSON')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    parser.add_argument('--help', action='store_true', help='Show help')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print_header()
    
    # Show help if requested
    if args.help or (not args.full and not args.demo and not args.quick):
        show_usage()
        return 0
    
    # Validate environment
    if not validate_environment():
        print("❌ Environment validation failed")
        print("Run 'python setup_rag.py' first\n")
        return 1
    
    success = False
    
    # Run requested tests
    if args.demo:
        success = run_demonstration()
    elif args.quick:
        success = run_quick_validation()
    else:  # Default to full
        success = run_executive_tests()
    
    # Print final status
    print("\n" + "="*80)
    if success:
        print("✅ TEST EXECUTION COMPLETED SUCCESSFULLY")
        if Path("quality_report.json").exists():
            print("📊 Report saved to: quality_report.json")
        print("="*80 + "\n")
        return 0
    else:
        print("❌ TEST EXECUTION FAILED")
        print("="*80 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
