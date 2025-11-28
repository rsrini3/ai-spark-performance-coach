"""Parse Spark event logs to extract performance metrics."""

import json
import gzip
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class TaskMetrics:
    """Metrics for a single task."""
    task_id: int
    stage_id: int
    duration: float
    shuffle_read_size: int = 0
    shuffle_write_size: int = 0
    input_size: int = 0


@dataclass
class StageMetrics:
    """Metrics for a Spark stage."""
    stage_id: int
    stage_name: str
    num_tasks: int = 0
    tasks: List[TaskMetrics] = field(default_factory=list)
    total_duration: float = 0.0
    shuffle_read_size: int = 0
    shuffle_write_size: int = 0
    
    @property
    def median_task_duration(self) -> float:
        """Calculate median task duration."""
        if not self.tasks:
            return 0.0
        durations = sorted([t.duration for t in self.tasks])
        mid = len(durations) // 2
        if len(durations) % 2 == 0:
            return (durations[mid - 1] + durations[mid]) / 2.0
        return durations[mid]
    
    @property
    def max_task_duration(self) -> float:
        """Get maximum task duration."""
        if not self.tasks:
            return 0.0
        return max(t.duration for t in self.tasks)
    
    @property
    def min_task_duration(self) -> float:
        """Get minimum task duration."""
        if not self.tasks:
            return 0.0
        return min(t.duration for t in self.tasks)


@dataclass
class JobMetrics:
    """Metrics for a Spark job."""
    job_id: int
    stages: List[StageMetrics] = field(default_factory=list)
    total_duration: float = 0.0


class SparkLogParser:
    """Parse Spark event logs and extract performance metrics."""
    
    def __init__(self, event_log_path: str):
        """
        Initialize parser with event log path.
        
        Args:
            event_log_path: Path to Spark event log file
        """
        self.event_log_path = Path(event_log_path)
        if not self.event_log_path.exists():
            raise FileNotFoundError(f"Event log not found: {event_log_path}")
        
        self.jobs: Dict[int, JobMetrics] = {}
        self.stages: Dict[int, StageMetrics] = {}
        self.tasks: List[TaskMetrics] = []
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse the event log file and extract metrics.
        
        Returns:
            Dictionary containing parsed metrics
        """
        # Determine if file is gzipped
        open_func = gzip.open if self.event_log_path.suffix == '.gz' else open
        mode = 'rt' if self.event_log_path.suffix == '.gz' else 'r'
        
        with open_func(self.event_log_path, mode) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    event = json.loads(line)
                    self._process_event(event)
                except json.JSONDecodeError:
                    continue
        
        return self._summarize()
    
    def _process_event(self, event: Dict[str, Any]):
        """Process a single event log entry."""
        event_type = event.get("Event")
        
        if event_type == "SparkListenerJobStart":
            self._process_job_start(event)
        elif event_type == "SparkListenerStageSubmitted":
            self._process_stage_submitted(event)
        elif event_type == "SparkListenerTaskEnd":
            self._process_task_end(event)
        elif event_type == "SparkListenerStageCompleted":
            self._process_stage_completed(event)
    
    def _process_job_start(self, event: Dict[str, Any]):
        """Process job start event."""
        job_id = event.get("Job ID", 0)
        self.jobs[job_id] = JobMetrics(job_id=job_id)
    
    def _process_stage_submitted(self, event: Dict[str, Any]):
        """Process stage submitted event."""
        stage_info = event.get("Stage Info", {})
        stage_id = stage_info.get("Stage ID", 0)
        stage_name = stage_info.get("Stage Name", f"Stage {stage_id}")
        
        self.stages[stage_id] = StageMetrics(
            stage_id=stage_id,
            stage_name=stage_name
        )
    
    def _process_task_end(self, event: Dict[str, Any]):
        """Process task end event."""
        task_info = event.get("Task Info", {})
        task_metrics = event.get("Task Metrics", {})
        
        task_id = task_info.get("Task ID", 0)
        stage_id = task_info.get("Stage ID", 0)
        duration = task_info.get("Finish Time", 0) - task_info.get("Launch Time", 0)
        duration_ms = duration / 1000.0  # Convert to seconds
        
        # Extract shuffle metrics
        shuffle_read = task_metrics.get("Shuffle Read Metrics", {})
        shuffle_write = task_metrics.get("Shuffle Write Metrics", {})
        input_metrics = task_metrics.get("Input Metrics", {})
        
        shuffle_read_size = shuffle_read.get("Remote Bytes Read", 0)
        shuffle_write_size = shuffle_write.get("Bytes Written", 0)
        input_size = input_metrics.get("Bytes Read", 0)
        
        task = TaskMetrics(
            task_id=task_id,
            stage_id=stage_id,
            duration=duration_ms,
            shuffle_read_size=shuffle_read_size,
            shuffle_write_size=shuffle_write_size,
            input_size=input_size
        )
        
        self.tasks.append(task)
        
        # Add task to stage
        if stage_id in self.stages:
            self.stages[stage_id].tasks.append(task)
            self.stages[stage_id].num_tasks = len(self.stages[stage_id].tasks)
    
    def _process_stage_completed(self, event: Dict[str, Any]):
        """Process stage completed event."""
        stage_info = event.get("Stage Info", {})
        stage_id = stage_info.get("Stage ID", 0)
        
        if stage_id in self.stages:
            stage = self.stages[stage_id]
            # Calculate total shuffle sizes
            stage.shuffle_read_size = sum(t.shuffle_read_size for t in stage.tasks)
            stage.shuffle_write_size = sum(t.shuffle_write_size for t in stage.tasks)
            
            if stage.tasks:
                stage.total_duration = max(t.duration for t in stage.tasks)
    
    def _summarize(self) -> Dict[str, Any]:
        """Create summary of parsed metrics."""
        stage_summaries = []
        
        for stage_id, stage in sorted(self.stages.items()):
            stage_summaries.append({
                "stage_id": stage.stage_id,
                "stage_name": stage.stage_name,
                "num_tasks": stage.num_tasks,
                "total_duration": stage.total_duration,
                "median_task_duration": stage.median_task_duration,
                "max_task_duration": stage.max_task_duration,
                "min_task_duration": stage.min_task_duration,
                "shuffle_read_size_mb": stage.shuffle_read_size / (1024 * 1024),
                "shuffle_write_size_mb": stage.shuffle_write_size / (1024 * 1024),
            })
        
        total_duration = sum(s.total_duration for s in self.stages.values())
        
        return {
            "num_jobs": len(self.jobs),
            "num_stages": len(self.stages),
            "total_duration": total_duration,
            "stages": stage_summaries
        }

