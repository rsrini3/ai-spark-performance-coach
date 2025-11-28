"""Performance rules to detect common Spark performance issues."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class PerformanceIssue:
    """Represents a detected performance issue."""
    issue_type: str
    stage_id: int
    severity: str  # "high", "medium", "low"
    description: str
    metrics: Dict[str, Any]


class PerformanceRules:
    """Detect performance issues from Spark metrics."""
    
    # Thresholds
    SKEW_RATIO_THRESHOLD = 3.0  # max/median ratio
    LARGE_SHUFFLE_THRESHOLD_MB = 500  # MB
    VERY_LARGE_SHUFFLE_THRESHOLD_MB = 2000  # MB
    LONG_STAGE_THRESHOLD_SEC = 60  # seconds
    
    @staticmethod
    def detect_skew(stage: Dict[str, Any]) -> Optional[PerformanceIssue]:
        """
        Detect task skew in a stage.
        
        Args:
            stage: Stage metrics dictionary
            
        Returns:
            PerformanceIssue if skew detected, None otherwise
        """
        max_duration = stage.get("max_task_duration", 0)
        median_duration = stage.get("median_task_duration", 0)
        
        if median_duration == 0:
            return None
        
        ratio = max_duration / median_duration
        
        if ratio >= PerformanceRules.SKEW_RATIO_THRESHOLD:
            severity = "high" if ratio >= 10 else "medium"
            return PerformanceIssue(
                issue_type="task_skew",
                stage_id=stage["stage_id"],
                severity=severity,
                description=f"Task skew detected: max task took {max_duration:.1f}s while median task took {median_duration:.1f}s (ratio: {ratio:.1f}x)",
                metrics={
                    "max_duration": max_duration,
                    "median_duration": median_duration,
                    "ratio": ratio,
                    "num_tasks": stage.get("num_tasks", 0)
                }
            )
        
        return None
    
    @staticmethod
    def detect_large_shuffle(stage: Dict[str, Any]) -> Optional[PerformanceIssue]:
        """
        Detect large shuffle operations.
        
        Args:
            stage: Stage metrics dictionary
            
        Returns:
            PerformanceIssue if large shuffle detected, None otherwise
        """
        shuffle_read_mb = stage.get("shuffle_read_size_mb", 0)
        
        if shuffle_read_mb >= PerformanceRules.VERY_LARGE_SHUFFLE_THRESHOLD_MB:
            return PerformanceIssue(
                issue_type="large_shuffle",
                stage_id=stage["stage_id"],
                severity="high",
                description=f"Very large shuffle detected: {shuffle_read_mb:.1f} MB read",
                metrics={
                    "shuffle_read_mb": shuffle_read_mb,
                    "shuffle_write_mb": stage.get("shuffle_write_size_mb", 0)
                }
            )
        elif shuffle_read_mb >= PerformanceRules.LARGE_SHUFFLE_THRESHOLD_MB:
            return PerformanceIssue(
                issue_type="large_shuffle",
                stage_id=stage["stage_id"],
                severity="medium",
                description=f"Large shuffle detected: {shuffle_read_mb:.1f} MB read",
                metrics={
                    "shuffle_read_mb": shuffle_read_mb,
                    "shuffle_write_mb": stage.get("shuffle_write_size_mb", 0)
                }
            )
        
        return None
    
    @staticmethod
    def detect_long_stage(stage: Dict[str, Any], total_duration: float) -> Optional[PerformanceIssue]:
        """
        Detect stages that take a significant portion of total time.
        
        Args:
            stage: Stage metrics dictionary
            total_duration: Total duration of all stages
            
        Returns:
            PerformanceIssue if long stage detected, None otherwise
        """
        stage_duration = stage.get("total_duration", 0)
        
        if total_duration == 0:
            return None
        
        percentage = (stage_duration / total_duration) * 100
        
        if stage_duration >= PerformanceRules.LONG_STAGE_THRESHOLD_SEC and percentage >= 50:
            return PerformanceIssue(
                issue_type="long_stage",
                stage_id=stage["stage_id"],
                severity="high",
                description=f"Stage {stage['stage_id']} took {percentage:.0f}% of total time ({stage_duration:.1f}s)",
                metrics={
                    "stage_duration": stage_duration,
                    "total_duration": total_duration,
                    "percentage": percentage
                }
            )
        elif percentage >= 70:
            return PerformanceIssue(
                issue_type="long_stage",
                stage_id=stage["stage_id"],
                severity="high",
                description=f"Stage {stage['stage_id']} took {percentage:.0f}% of total time ({stage_duration:.1f}s)",
                metrics={
                    "stage_duration": stage_duration,
                    "total_duration": total_duration,
                    "percentage": percentage
                }
            )
        
        return None
    
    @classmethod
    def analyze(cls, summary: Dict[str, Any]) -> List[PerformanceIssue]:
        """
        Analyze Spark metrics and detect performance issues.
        
        Args:
            summary: Summary dictionary from SparkLogParser
            
        Returns:
            List of detected performance issues
        """
        issues = []
        stages = summary.get("stages", [])
        total_duration = summary.get("total_duration", 0)
        
        for stage in stages:
            # Check for skew
            skew_issue = cls.detect_skew(stage)
            if skew_issue:
                issues.append(skew_issue)
            
            # Check for large shuffle
            shuffle_issue = cls.detect_large_shuffle(stage)
            if shuffle_issue:
                issues.append(shuffle_issue)
            
            # Check for long stage
            long_stage_issue = cls.detect_long_stage(stage, total_duration)
            if long_stage_issue:
                issues.append(long_stage_issue)
        
        return issues

