#!/usr/bin/env python3
"""
🚚 RAG QUALITY TESTING & EXECUTIVE DEMONSTRATION
Logistics Integration RAG - Enterprise-Grade Quality Assurance

This script implements comprehensive quality testing aligned with:
1. Simple questions (1 doc, 1 chunk)
2. Complex questions (multi-docs, synthesis)
3. Out-of-corpus questions (hallucination detection)
4. Source transparency & traceability
5. Executive-ready reporting

Run:
    python quality_testing_executive.py
"""

import logging
import json
import sys
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from app.services.rag_pipeline import query_rag_with_sources
from app.models.response_models import QueryResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a single quality test."""
    category: str
    question: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    num_sources: int
    passed: bool
    reason: str
    hallucination_risk: bool


class ExecutiveQualityTester:
    """
    Enterprise-grade quality testing with hallucination detection.
    Focuses on demonstrable reliability for C-suite review.
    """
    
    # ========================================================================
    # CATEGORY A: SIMPLE QUESTIONS (1 document, 1 chunk)
    # ========================================================================
    
    SIMPLE_QUESTIONS = [
        {
            "question": "Quel est le délai maximal de traitement d'un litige client ?",
            "category": "simple",
            "description": "Basic factual question - should find exact answer in SLA doc",
            "expected_confidence_min": 0.75,
            "expected_sources": 1,
        },
        {
            "question": "Procédure en cas de retard fournisseur supérieur à 48h",
            "category": "simple",
            "description": "Procedure lookup - clear step-by-step answer expected",
            "expected_confidence_min": 0.70,
            "expected_sources": 1,
        },
        {
            "question": "Quels sont les motifs valides de refus de marchandise ?",
            "category": "simple",
            "description": "List-based factual question from refusal document",
            "expected_confidence_min": 0.70,
            "expected_sources": 1,
        },
        {
            "question": "À partir de combien d'heures de retard parle-t-on d'alerte rouge ?",
            "category": "simple",
            "description": "Specific numerical answer",
            "expected_confidence_min": 0.75,
            "expected_sources": 1,
        }
    ]
    
    # ========================================================================
    # CATEGORY B: COMPLEX QUESTIONS (Multi-documents, synthesis required)
    # ========================================================================
    
    COMPLEX_QUESTIONS = [
        {
            "question": "Procédure complète en cas de retard fournisseur avec impact client",
            "category": "complex",
            "description": "Multi-doc synthesis: Procedure + SLA implications",
            "expected_docs": ["procedure_retard_fournisseur.txt", "sla_fournisseurs.txt"],
            "expected_confidence_min": 0.60,
            "expected_sources_min": 2,
        },
        {
            "question": "Étapes à suivre pour un refus de marchandise à la livraison internationale et impacts sur SLA",
            "category": "complex",
            "description": "Complex workflow: Refusal procedure + SLA compensation",
            "expected_docs": ["refus_marchandise_international.txt", "sla_fournisseurs.txt"],
            "expected_confidence_min": 0.60,
            "expected_sources_min": 2,
        },
        {
            "question": "Comment gérer un fournisseur qui accumule les retards : procédures, pénalités et compensations clients ?",
            "category": "complex",
            "description": "Multi-faceted: Procedure + SLA penalties + client compensation",
            "expected_docs": ["procedure_retard_fournisseur.txt", "sla_fournisseurs.txt"],
            "expected_confidence_min": 0.55,
            "expected_sources_min": 2,
        },
        {
            "question": "Quel est le process opérationnel complet quand un client refuse une marchandise ?",
            "category": "complex",
            "description": "End-to-end workflow across multiple documents",
            "expected_docs": ["refus_marchandise_international.txt", "sla_fournisseurs.txt"],
            "expected_confidence_min": 0.60,
            "expected_sources_min": 2,
        }
    ]
    
    # ========================================================================
    # CATEGORY C: OUT-OF-CORPUS QUESTIONS (Critical hallucination test)
    # ========================================================================
    
    OUT_OF_CORPUS_QUESTIONS = [
        {
            "question": "Quelle est la politique interne sur les crypto-paiements ?",
            "category": "out_of_corpus",
            "description": "Non-existent policy - must refuse",
            "should_refuse": True,
            "expected_confidence_max": 0.35,
        },
        {
            "question": "Procédure drone pour livraison express ?",
            "category": "out_of_corpus",
            "description": "Technology not in documents - must refuse",
            "should_refuse": True,
            "expected_confidence_max": 0.35,
        },
        {
            "question": "Résoudre l'équation x² + 2x + 1 = 0",
            "category": "out_of_corpus",
            "description": "Completely unrelated math question",
            "should_refuse": True,
            "expected_confidence_max": 0.35,
        },
        {
            "question": "Politique de livraison par satellites géostationnaires",
            "category": "out_of_corpus",
            "description": "Science fiction - must refuse",
            "should_refuse": True,
            "expected_confidence_max": 0.35,
        },
        {
            "question": "Comment faire une pizza carbonara ?",
            "category": "out_of_corpus",
            "description": "Cooking recipe - out of scope",
            "should_refuse": True,
            "expected_confidence_max": 0.35,
        }
    ]
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.summary: Dict[str, Any] = {}
    
    def run_category_a(self) -> List[TestResult]:
        """Test Category A: Simple Questions."""
        logger.info("\n" + "="*80)
        logger.info("🔵 CATEGORY A: SIMPLE QUESTIONS (1 Document, 1 Chunk)")
        logger.info("Expected: High confidence (>0.70), clear single source, concise answer")
        logger.info("="*80)
        
        results = []
        for i, test in enumerate(self.SIMPLE_QUESTIONS, 1):
            logger.info(f"\n[A.{i}] {test['question']}")
            logger.info(f"     └─ {test['description']}")
            
            response = query_rag_with_sources(test['question'])
            
            # Evaluation criteria for simple questions
            passed = (
                response.confidence >= test['expected_confidence_min'] and
                len(response.sources) >= test['expected_sources'] and
                not response.is_hallucination_risk and
                len(response.answer) > 20
            )
            
            reason = self._build_reason(
                passed=passed,
                confidence=response.confidence,
                expected_confidence=test['expected_confidence_min'],
                sources=len(response.sources),
                expected_sources=test['expected_sources'],
                is_hallucination_risk=response.is_hallucination_risk,
                answer_length=len(response.answer)
            )
            
            result = TestResult(
                category="simple",
                question=test['question'],
                answer=response.answer[:300],
                sources=[{"doc": s.document, "score": s.score, "chunk": s.chunk[:100]} 
                         for s in response.sources],
                confidence=response.confidence,
                num_sources=len(response.sources),
                passed=passed,
                reason=reason,
                hallucination_risk=response.is_hallucination_risk
            )
            
            results.append(result)
            self._log_test_result(result, is_critical=False)
        
        return results
    
    def run_category_b(self) -> List[TestResult]:
        """Test Category B: Complex Questions."""
        logger.info("\n" + "="*80)
        logger.info("🟠 CATEGORY B: COMPLEX QUESTIONS (Multi-Document Synthesis)")
        logger.info("Expected: Good confidence (>0.60), 2+ sources, structured synthesis")
        logger.info("="*80)
        
        results = []
        for i, test in enumerate(self.COMPLEX_QUESTIONS, 1):
            logger.info(f"\n[B.{i}] {test['question']}")
            logger.info(f"     └─ {test['description']}")
            
            response = query_rag_with_sources(test['question'])
            
            # Evaluation for complex questions
            passed = (
                response.confidence >= test['expected_confidence_min'] and
                len(response.sources) >= test['expected_sources_min'] and
                not response.is_hallucination_risk and
                len(response.answer) > 150  # Need more comprehensive answer
            )
            
            reason = self._build_reason(
                passed=passed,
                confidence=response.confidence,
                expected_confidence=test['expected_confidence_min'],
                sources=len(response.sources),
                expected_sources=test['expected_sources_min'],
                is_hallucination_risk=response.is_hallucination_risk,
                answer_length=len(response.answer),
                min_answer_length=150
            )
            
            result = TestResult(
                category="complex",
                question=test['question'],
                answer=response.answer[:400],
                sources=[{"doc": s.document, "score": s.score, "chunk": s.chunk[:120]} 
                         for s in response.sources],
                confidence=response.confidence,
                num_sources=len(response.sources),
                passed=passed,
                reason=reason,
                hallucination_risk=response.is_hallucination_risk
            )
            
            results.append(result)
            self._log_test_result(result, is_critical=False)
        
        return results
    
    def run_category_c(self) -> List[TestResult]:
        """Test Category C: Out-of-Corpus Questions (Hallucination Detection)."""
        logger.info("\n" + "="*80)
        logger.info("🔴 CATEGORY C: OUT-OF-CORPUS QUESTIONS (Hallucination Detection)")
        logger.info("Expected: LOW confidence (<0.35), MUST refuse or admit 'not found'")
        logger.info("CRITICAL: Any hallucination here is a FAIL")
        logger.info("="*80)
        
        results = []
        for i, test in enumerate(self.OUT_OF_CORPUS_QUESTIONS, 1):
            logger.info(f"\n[C.{i}] {test['question']}")
            logger.info(f"     └─ {test['description']}")
            
            response = query_rag_with_sources(test['question'])
            
            # Hallucination detection logic
            is_properly_refusing = (
                response.confidence <= test['expected_confidence_max'] or
                response.is_hallucination_risk or
                self._contains_refusal(response.answer)
            )
            
            passed = is_properly_refusing
            
            reason = self._build_out_of_corpus_reason(
                passed=passed,
                confidence=response.confidence,
                expected_confidence_max=test['expected_confidence_max'],
                contains_refusal=self._contains_refusal(response.answer),
                hallucination_flag=response.is_hallucination_risk
            )
            
            result = TestResult(
                category="out_of_corpus",
                question=test['question'],
                answer=response.answer[:300],
                sources=[{"doc": s.document, "score": s.score} for s in response.sources],
                confidence=response.confidence,
                num_sources=len(response.sources),
                passed=passed,
                reason=reason,
                hallucination_risk=not passed  # Failed test = hallucinated
            )
            
            results.append(result)
            self._log_test_result(result, is_critical=True)
        
        return results
    
    def run_full_suite(self) -> Dict[str, Any]:
        """Run complete quality test suite."""
        logger.info("\n" + "█"*80)
        logger.info("█ RAG QUALITY TEST SUITE - COMPLETE EXECUTION")
        logger.info("█ Logistics Integration - Enterprise Quality Assurance")
        logger.info("█"*80)
        
        all_results = []
        
        # Run all categories
        category_a = self.run_category_a()
        all_results.extend(category_a)
        
        category_b = self.run_category_b()
        all_results.extend(category_b)
        
        category_c = self.run_category_c()
        all_results.extend(category_c)
        
        self.results = all_results
        
        # Compute summary statistics
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate executive summary report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        hallucinations = sum(1 for r in self.results if r.hallucination_risk)
        
        by_category = {
            "simple": [r for r in self.results if r.category == "simple"],
            "complex": [r for r in self.results if r.category == "complex"],
            "out_of_corpus": [r for r in self.results if r.category == "out_of_corpus"]
        }
        
        category_summary = {}
        for cat, items in by_category.items():
            if items:
                cat_passed = sum(1 for r in items if r.passed)
                category_summary[cat] = {
                    "total": len(items),
                    "passed": cat_passed,
                    "failed": len(items) - cat_passed,
                    "pass_rate": (cat_passed / len(items) * 100) if items else 0
                }
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "hallucinations_detected": hallucinations,
            "overall_pass_rate": (passed / total * 100) if total > 0 else 0,
            "by_category": category_summary,
            "critical_status": "✅ ALL TESTS PASSED" if (passed == total and hallucinations == 0) else "❌ FAILURES DETECTED",
            "results": [asdict(r) for r in self.results]
        }
        
        self.summary = report
        return report
    
    def print_executive_summary(self):
        """Print executive-ready summary for C-suite."""
        if not self.summary:
            logger.error("No summary available. Run full suite first.")
            return
        
        print("\n" + "█"*80)
        print("█ EXECUTIVE SUMMARY - RAG QUALITY ASSURANCE REPORT")
        print("█"*80)
        print(f"\nTimestamp: {self.summary['timestamp']}")
        print(f"System: Logistics RAG Pipeline (Vector-based Document Retrieval)")
        print(f"\n{'─'*80}")
        print("📊 OVERALL RESULTS")
        print(f"{'─'*80}")
        print(f"Total Tests Run:         {self.summary['total_tests']}")
        print(f"Tests Passed:            {self.summary['passed_tests']} ✅")
        print(f"Tests Failed:            {self.summary['failed_tests']} ❌")
        print(f"Hallucinations Detected: {self.summary['hallucinations_detected']} 🚨")
        print(f"Overall Pass Rate:       {self.summary['overall_pass_rate']:.1f}%")
        
        print(f"\n{'─'*80}")
        print("📈 BY CATEGORY BREAKDOWN")
        print(f"{'─'*80}")
        for category, stats in self.summary['by_category'].items():
            print(f"\n{category.upper()}")
            print(f"  Tests:     {stats['total']}")
            print(f"  Passed:    {stats['passed']} ✅")
            print(f"  Failed:    {stats['failed']} ❌")
            print(f"  Pass Rate: {stats['pass_rate']:.1f}%")
        
        print(f"\n{'─'*80}")
        print("🎯 CRITICAL STATUS")
        print(f"{'─'*80}")
        print(f"{self.summary['critical_status']}")
        
        if self.summary['hallucinations_detected'] > 0:
            print(f"\n🚨 WARNING: {self.summary['hallucinations_detected']} hallucination(s) detected!")
            print("   These tests FAILED to properly refuse out-of-corpus questions.")
            for result in self.results:
                if result.hallucination_risk and not result.passed:
                    print(f"\n   Q: {result['question'][:60]}...")
                    print(f"   A: {result['answer'][:100]}...")
        
        print(f"\n{'═'*80}\n")
    
    def export_json_report(self, filepath: str = "quality_report.json"):
        """Export detailed report as JSON for integration with ERP systems."""
        if not self.summary:
            logger.error("No summary available. Run full suite first.")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ JSON report exported to: {filepath}")
    
    def _log_test_result(self, result: TestResult, is_critical: bool = False):
        """Log individual test result."""
        status = "✅ PASS" if result.passed else "❌ FAIL"
        marker = "🚨 CRITICAL FAIL" if (is_critical and not result.passed) else ""
        
        print(f"\n{status} {marker}")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Sources: {result.num_sources} document chunk(s)")
        print(f"   Hallucination Risk: {'YES 🚨' if result.hallucination_risk else 'NO ✅'}")
        print(f"   Reason: {result.reason}")
        print(f"   Answer: {result.answer[:150]}...")
    
    def _contains_refusal(self, text: str) -> bool:
        """Check if response contains refusal markers."""
        refusal_markers = [
            "information non trouvée",
            "pas d'information",
            "non trouvé",
            "document ne contient pas",
            "ne trouve pas",
            "n'a pas trouvé",
            "aucune information",
            "outside",
            "beyond scope",
            "not found"
        ]
        text_lower = text.lower()
        return any(marker in text_lower for marker in refusal_markers)
    
    def _build_reason(self, passed: bool, confidence: float, expected_confidence: float,
                     sources: int, expected_sources: int, is_hallucination_risk: bool,
                     answer_length: int, min_answer_length: int = 20) -> str:
        """Build human-readable test failure reason."""
        if passed:
            return "All criteria met"
        
        issues = []
        if confidence < expected_confidence:
            issues.append(f"Low confidence ({confidence:.3f} < {expected_confidence})")
        if sources < expected_sources:
            issues.append(f"Insufficient sources ({sources} < {expected_sources})")
        if is_hallucination_risk:
            issues.append("Hallucination risk detected")
        if answer_length < min_answer_length:
            issues.append(f"Answer too short ({answer_length} chars)")
        
        return " | ".join(issues) if issues else "Unknown reason"
    
    def _build_out_of_corpus_reason(self, passed: bool, confidence: float,
                                   expected_confidence_max: float, contains_refusal: bool,
                                   hallucination_flag: bool) -> str:
        """Build reason for out-of-corpus test."""
        if passed:
            if contains_refusal:
                return "✅ Correctly refused with 'not found' message"
            if hallucination_flag:
                return "✅ Hallucination flag triggered"
            if confidence <= expected_confidence_max:
                return f"✅ Low confidence ({confidence:.3f})"
            return "✅ Properly refused"
        
        issues = []
        if confidence > expected_confidence_max and not contains_refusal and not hallucination_flag:
            issues.append(f"HIGH confidence on out-of-corpus ({confidence:.3f})")
        if not contains_refusal and not hallucination_flag:
            issues.append("Did not refuse or flag hallucination")
        
        return " | ".join(issues) if issues else "HALLUCINATION - Generated answer for non-existent info"


def main():
    """Main entry point."""
    try:
        # Run tests
        tester = ExecutiveQualityTester()
        report = tester.run_full_suite()
        
        # Print executive summary
        tester.print_executive_summary()
        
        # Export JSON report
        tester.export_json_report("quality_report.json")
        
        # Determine exit code
        if report['hallucinations_detected'] > 0 or report['failed_tests'] > 0:
            logger.error("❌ Quality tests FAILED")
            sys.exit(1)
        else:
            logger.info("✅ Quality tests PASSED")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Error running quality tests: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
