"""
Service for managing LLM/Mood Analysis operations through API.
Abstracts mood analyzer functionality for API consumption.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from app.core.logger import logger
from app.core.config import settings
from app.core.exceptions import LLMException, ProcessingError


class MoodAnalyzerService:
    """Service for mood analysis operations."""

    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.analyzer = None
        self._initialize_analyzer()

    def _initialize_analyzer(self):
        """Initialize the mood analyzer."""
        try:
            # Import the mood analyzer from llms directory
            import sys
            from pathlib import Path
            
            llms_path = Path(__file__).parent.parent.parent.parent / "llms"
            sys.path.insert(0, str(llms_path))
            
            # This will be imported when needed
            logger.info("Mood analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize mood analyzer: {str(e)}")

    async def start_analysis(
        self,
        data_source: str = "scrapper",
        input_file: Optional[str] = None,
        models: Optional[List[str]] = None,
        batch_size: int = 5,
        resume: bool = False,
    ) -> str:
        """
        Start a mood analysis job.
        
        Args:
            data_source: Source of data (scrapper or file)
            input_file: Input file path if using file source
            models: Specific models to use
            batch_size: Batch size for processing
            resume: Resume from checkpoint
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "id": job_id,
            "status": "pending",
            "data_source": data_source,
            "input_file": input_file,
            "models": models or [],
            "batch_size": batch_size,
            "resume": resume,
            "total_entries": 0,
            "successful_entries": 0,
            "failed_entries": 0,
            "entries_processed": 0,
            "aggregated_sentiment": None,
            "aggregated_confidence": None,
            "output_file": None,
            "error": None,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
        }
        
        # Start analysis in background
        asyncio.create_task(
            self._execute_analysis(job_id, data_source, input_file, models, batch_size, resume)
        )
        
        logger.info(f"Started mood analysis job {job_id}")
        return job_id

    async def _execute_analysis(
        self,
        job_id: str,
        data_source: str,
        input_file: Optional[str],
        models: Optional[List[str]],
        batch_size: int,
        resume: bool,
    ):
        """Execute mood analysis job."""
        try:
            self.jobs[job_id]["status"] = "running"
            
            # Load data
            if data_source == "scrapper":
                data = await self._load_scrapper_data()
            elif data_source == "file":
                if not input_file:
                    raise ProcessingError("input_file required when data_source is 'file'")
                data = await self._load_file_data(input_file)
            else:
                raise ProcessingError(f"Unknown data source: {data_source}")
            
            if not data:
                raise ProcessingError("No data available for analysis")
            
            self.jobs[job_id]["total_entries"] = len(data.get("entries", []))
            
            # Import and use the actual mood analyzer
            import sys
            from pathlib import Path
            
            llms_path = Path(__file__).parent.parent.parent.parent / "llms"
            sys.path.insert(0, str(llms_path))
            
            from market_mood_analyzer import MoodAnalyzer
            import config as llm_config
            
            # Create analyzer instance
            analyzer = MoodAnalyzer(
                data_dir=llms_path.parent / "scrapper" / "data_sourcing" / "output",
                checkpoint_dir=settings.checkpoint_dir,
            )
            
            # Run analysis
            results = await analyzer.analyze_batch(
                data.get("entries", []),
                models=models,
                batch_size=batch_size,
                resume=resume,
            )
            
            # Process results
            successful = sum(1 for r in results if r["status"] == "completed")
            failed = sum(1 for r in results if r["status"] == "failed")
            
            self.jobs[job_id]["successful_entries"] = successful
            self.jobs[job_id]["failed_entries"] = failed
            self.jobs[job_id]["entries_processed"] = successful + failed
            
            # Calculate aggregated sentiment
            completed_results = [r for r in results if r["status"] == "completed"]
            if completed_results:
                avg_sentiment = sum(r["aggregated_sentiment"] for r in completed_results) / len(completed_results)
                avg_confidence = sum(r["aggregated_confidence"] for r in completed_results) / len(completed_results)
                
                self.jobs[job_id]["aggregated_sentiment"] = avg_sentiment
                self.jobs[job_id]["aggregated_confidence"] = avg_confidence
            
            # Save results
            output_file = await self._save_analysis_results(job_id, results)
            self.jobs[job_id]["output_file"] = output_file
            
            self.jobs[job_id]["status"] = "completed"
            self.jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Mood analysis job {job_id} completed successfully")
            
        except Exception as e:
            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["error"] = str(e)
            self.jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
            logger.error(f"Mood analysis job {job_id} failed: {str(e)}")

    async def _load_scrapper_data(self) -> Optional[Dict[str, Any]]:
        """Load data from scrapper output."""
        try:
            output_dir = settings.data_dir
            
            if not output_dir.exists():
                logger.warning(f"Data directory {output_dir} does not exist")
                return None
            
            # Find the latest JSON file
            json_files = list(output_dir.glob("*.json"))
            
            if not json_files:
                logger.warning(f"No JSON files found in {output_dir}")
                return None
            
            latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_file, "r") as f:
                data = json.load(f)
            
            logger.info(f"Loaded scrapper data from {latest_file}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading scrapper data: {str(e)}")
            raise LLMException(f"Failed to load scrapper data: {str(e)}")

    async def _load_file_data(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load data from file."""
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise ProcessingError(f"File {file_path} does not exist")
            
            with open(path, "r") as f:
                data = json.load(f)
            
            logger.info(f"Loaded data from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading file data: {str(e)}")
            raise LLMException(f"Failed to load file data: {str(e)}")

    async def _save_analysis_results(self, job_id: str, results: List[Dict[str, Any]]) -> str:
        """Save analysis results to file."""
        try:
            output_file = settings.output_dir / f"mood_analysis_{job_id}.json"
            
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Saved analysis results to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise ProcessingError(f"Failed to save results: {str(e)}")

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of an analysis job."""
        if job_id not in self.jobs:
            raise LLMException(f"Job {job_id} not found")
        return self.jobs[job_id]

    async def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """Get the latest mood analysis report."""
        try:
            output_dir = settings.output_dir
            
            if not output_dir.exists():
                return None
            
            # Find the latest JSON file
            json_files = list(output_dir.glob("*.json"))
            
            if not json_files:
                return None
            
            latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_file, "r") as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading latest report: {str(e)}")
            raise LLMException(f"Failed to load latest report: {str(e)}")

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel an analysis job."""
        if job_id not in self.jobs:
            raise LLMException(f"Job {job_id} not found")
        
        if self.jobs[job_id]["status"] in ["completed", "failed"]:
            raise LLMException(f"Cannot cancel job with status {self.jobs[job_id]['status']}")
        
        self.jobs[job_id]["status"] = "cancelled"
        logger.info(f"Cancelled job {job_id}")
        return True

    async def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return [
            "kimi-k2.5:cloud",
            "minimax-m2.5:cloud",
            "qwen2.5vl:latest",
            "mistral-large-3:675b-cloud",
            "llama3.1:latest",
            "deepseek-coder:latest",
        ]
