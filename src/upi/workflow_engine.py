"""Workflow engine primitives for autonomous analysis, planning, and release gating."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import json
from pathlib import Path


class CrewRole(str, Enum):
    """Crew roles used in the autonomous pipeline."""

    ANALYZER = "analyzer"
    PLANNER = "planner"
    PATCHER = "patcher"
    VALIDATOR = "validator"
    GATEKEEPER = "gatekeeper"


class IssueSeverity(str, Enum):
    """Severity used to rank workflow issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class WorkflowIssue:
    """Normalized issue input for the workflow engine."""

    issue_id: str
    severity: IssueSeverity
    source: str
    description: str
    confidence: float
    risk: float


@dataclass(frozen=True)
class CandidatePlan:
    """A generated plan candidate for resolving a specific issue."""

    issue_id: str
    crew_role: CrewRole
    rationale: str
    proposed_action: str
    score: float
    confidence: float
    risk: float
    release_allowed: bool
    release_reason: str


def _severity_weight(severity: IssueSeverity) -> float:
    if severity == IssueSeverity.CRITICAL:
        return 1.0
    if severity == IssueSeverity.HIGH:
        return 0.8
    if severity == IssueSeverity.MEDIUM:
        return 0.6
    return 0.4


class WorkflowEngine:
    """Autonomous workflow engine with deterministic optimal-candidate gating."""

    def __init__(self, min_score: float = 0.75, max_risk: float = 0.35):
        self.min_score = min_score
        self.max_risk = max_risk

    def ingest_repo_audit(self, report: dict) -> list[WorkflowIssue]:
        """Convert repo_audit.py output into normalized workflow issues."""
        issues: list[WorkflowIssue] = []

        for idx, message in enumerate(report.get("critical_conflicts", [])):
            issues.append(
                WorkflowIssue(
                    issue_id=f"critical-{idx}",
                    severity=IssueSeverity.CRITICAL,
                    source="critical_conflicts",
                    description=message,
                    confidence=0.95,
                    risk=0.15,
                )
            )

        for idx, message in enumerate(report.get("port_conflicts", [])):
            issues.append(
                WorkflowIssue(
                    issue_id=f"ports-{idx}",
                    severity=IssueSeverity.HIGH,
                    source="port_conflicts",
                    description=message,
                    confidence=0.85,
                    risk=0.25,
                )
            )

        for idx, message in enumerate(report.get("missing_files", [])):
            issues.append(
                WorkflowIssue(
                    issue_id=f"missing-{idx}",
                    severity=IssueSeverity.MEDIUM,
                    source="missing_files",
                    description=f"Missing required file: {message}",
                    confidence=0.8,
                    risk=0.2,
                )
            )

        return issues

    def _score_issue(self, issue: WorkflowIssue) -> float:
        """Score issue candidate using severity, confidence, and risk penalty."""
        impact = _severity_weight(issue.severity)
        raw_score = (0.5 * impact) + (0.4 * issue.confidence) - (0.3 * issue.risk)
        return max(0.0, min(1.0, raw_score))

    def build_candidate_plans(self, issues: list[WorkflowIssue]) -> list[CandidatePlan]:
        """Generate one deterministic patch plan per issue."""
        candidates: list[CandidatePlan] = []

        for issue in issues:
            score = self._score_issue(issue)
            allowed = score >= self.min_score and issue.risk <= self.max_risk
            release_reason = "accepted-by-optimal-gate" if allowed else "blocked-by-optimal-gate"

            candidates.append(
                CandidatePlan(
                    issue_id=issue.issue_id,
                    crew_role=CrewRole.PATCHER,
                    rationale=f"{issue.source}: {issue.description}",
                    proposed_action=f"debug-and-patch::{issue.source}::{issue.issue_id}",
                    score=score,
                    confidence=issue.confidence,
                    risk=issue.risk,
                    release_allowed=allowed,
                    release_reason=release_reason,
                )
            )

        return sorted(candidates, key=lambda c: c.score, reverse=True)

    def evaluate_release(self, candidates: list[CandidatePlan]) -> dict:
        """Return release gate decision with accepted and blocked candidates."""
        accepted = [asdict(c) for c in candidates if c.release_allowed]
        blocked = [asdict(c) for c in candidates if not c.release_allowed]

        return {
            "summary": {
                "accepted_count": len(accepted),
                "blocked_count": len(blocked),
                "min_score": self.min_score,
                "max_risk": self.max_risk,
                "release_ready": len(blocked) == 0,
            },
            "accepted": accepted,
            "blocked": blocked,
        }

    def run_from_report(self, report: dict) -> dict:
        """Run full crew flow from audit report to optimal release gate."""
        issues = self.ingest_repo_audit(report)
        candidates = self.build_candidate_plans(issues)
        return self.evaluate_release(candidates)

    def run_from_report_file(self, report_path: str | Path) -> dict:
        """Run full workflow flow from JSON report path."""
        path = Path(report_path)
        report = json.loads(path.read_text(encoding="utf-8"))
        return self.run_from_report(report)
