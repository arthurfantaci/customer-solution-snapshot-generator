# API Examples and Integration Guide

Comprehensive examples for integrating Customer Solution Snapshot Generator into your applications.

## Table of Contents

1. [Basic Python API](#basic-python-api)
2. [Advanced Configuration](#advanced-configuration)
3. [Batch Processing](#batch-processing)
4. [Custom Templates](#custom-templates)
5. [Error Handling](#error-handling)
6. [Performance Optimization](#performance-optimization)
7. [Web Service Integration](#web-service-integration)
8. [Real-time Processing](#real-time-processing)
9. [Database Integration](#database-integration)
10. [Webhook Integration](#webhook-integration)

## Basic Python API

### Simple Processing

```python
from customer_snapshot import TranscriptProcessor

# Initialize processor
processor = TranscriptProcessor()

# Process a single file
result = processor.process_file(
    input_path="transcript.vtt",
    output_format="markdown"
)

print(f"Analysis completed: {result}")
```

### With Custom Configuration

```python
from customer_snapshot import TranscriptProcessor
from customer_snapshot.utils.config import Config

# Create custom configuration
config = Config()
config.api.anthropic_api_key = "your-api-key"
config.api.model = "claude-3-sonnet-20240229"
config.api.timeout = 60
config.processing.chunk_size = 1000

# Initialize with custom config
processor = TranscriptProcessor(config)

# Process file
result = processor.process_file(
    input_path="transcript.vtt",
    output_path="analysis.md",
    output_format="markdown"
)
```

### Using Environment Variables

```python
import os
from customer_snapshot import TranscriptProcessor

# Set environment variables
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"
os.environ["CHUNK_SIZE"] = "1500"
os.environ["ENABLE_CACHING"] = "true"

# Initialize (uses environment variables)
processor = TranscriptProcessor()

# Process with additional options
result = processor.process_file(
    input_path="transcript.vtt",
    include_metadata=True,
    extract_entities=True,
    sentiment_analysis=True
)
```

## Advanced Configuration

### Configuration Classes

```python
from customer_snapshot.utils.config import Config, APIConfig, ProcessingConfig, NLPConfig

# Create detailed configuration
config = Config()

# API configuration
config.api = APIConfig(
    anthropic_api_key="your-key",
    model="claude-3-sonnet-20240229",
    max_retries=3,
    timeout=30,
    rate_limit_requests_per_minute=50
)

# Processing configuration
config.processing = ProcessingConfig(
    chunk_size=1000,
    chunk_overlap=100,
    enable_caching=True,
    cache_ttl=3600,
    parallel_processing=True,
    max_workers=4
)

# NLP configuration
config.nlp = NLPConfig(
    language="en",
    extract_entities=True,
    sentiment_analysis=True,
    extract_key_phrases=True,
    summarization_strategy="extractive"
)

# Initialize processor
processor = TranscriptProcessor(config)
```

### Dynamic Configuration

```python
from customer_snapshot import TranscriptProcessor
import yaml

class DynamicProcessor:
    def __init__(self, config_file=None):
        self.processor = TranscriptProcessor()
        if config_file:
            self.load_config(config_file)

    def load_config(self, config_file):
        """Load configuration from YAML file."""
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        # Update processor configuration
        self.processor.config.update_from_dict(config_data)

    def process_with_profile(self, input_path, profile="default"):
        """Process using predefined profiles."""
        profiles = {
            "fast": {
                "chunk_size": 2000,
                "model": "claude-3-haiku-20240307",
                "extract_entities": False
            },
            "detailed": {
                "chunk_size": 500,
                "model": "claude-3-opus-20240229",
                "extract_entities": True,
                "sentiment_analysis": True
            },
            "balanced": {
                "chunk_size": 1000,
                "model": "claude-3-sonnet-20240229",
                "extract_entities": True
            }
        }

        # Apply profile settings
        if profile in profiles:
            for key, value in profiles[profile].items():
                setattr(self.processor.config.processing, key, value)

        return self.processor.process_file(input_path)

# Usage
processor = DynamicProcessor("config.yaml")
result = processor.process_with_profile("transcript.vtt", profile="detailed")
```

## Batch Processing

### Basic Batch Processing

```python
from customer_snapshot import BatchProcessor
from pathlib import Path
import asyncio

class BatchTranscriptProcessor:
    def __init__(self):
        self.batch_processor = BatchProcessor()

    def process_directory(self, input_dir, output_dir):
        """Process all VTT files in a directory."""
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        # Find all VTT files
        vtt_files = list(input_path.glob("**/*.vtt"))

        # Process batch
        results = self.batch_processor.process_files(
            files=vtt_files,
            output_directory=output_path,
            parallel=True,
            max_workers=4
        )

        return results

    async def async_batch_process(self, files):
        """Asynchronous batch processing."""
        tasks = []

        for file in files:
            task = asyncio.create_task(
                self.process_file_async(file)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results

    async def process_file_async(self, file_path):
        """Asynchronous file processing."""
        loop = asyncio.get_event_loop()

        # Run in executor to avoid blocking
        result = await loop.run_in_executor(
            None,
            self.batch_processor.process_file,
            file_path
        )

        return result

# Usage
processor = BatchTranscriptProcessor()

# Synchronous batch processing
results = processor.process_directory("./transcripts", "./output")

# Asynchronous batch processing
async def main():
    files = ["file1.vtt", "file2.vtt", "file3.vtt"]
    results = await processor.async_batch_process(files)
    return results

# Run async
results = asyncio.run(main())
```

### Progress Tracking

```python
from customer_snapshot import BatchProcessor
from tqdm import tqdm
import logging

class ProgressTrackingProcessor:
    def __init__(self):
        self.batch_processor = BatchProcessor()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def process_with_progress(self, files):
        """Process files with progress bar and logging."""
        results = []

        with tqdm(total=len(files), desc="Processing transcripts") as pbar:
            for file in files:
                try:
                    self.logger.info(f"Processing {file}")

                    result = self.batch_processor.process_file(file)
                    results.append({
                        'file': file,
                        'status': 'success',
                        'result': result
                    })

                    self.logger.info(f"Completed {file}")

                except Exception as e:
                    self.logger.error(f"Failed to process {file}: {e}")
                    results.append({
                        'file': file,
                        'status': 'error',
                        'error': str(e)
                    })

                finally:
                    pbar.update(1)

        return results

    def generate_report(self, results):
        """Generate processing report."""
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']

        report = {
            'total_files': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(results) * 100,
            'failed_files': [r['file'] for r in failed]
        }

        self.logger.info(f"Processing complete: {report}")
        return report
```

## Custom Templates

### Template Management

```python
from customer_snapshot import TranscriptProcessor
from jinja2 import Environment, FileSystemLoader
import json

class TemplateManager:
    def __init__(self, template_dir="templates"):
        self.processor = TranscriptProcessor()
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def create_template(self, name, content):
        """Create a new template."""
        template_path = f"{self.template_dir}/{name}.md"
        with open(template_path, 'w') as f:
            f.write(content)

    def list_templates(self):
        """List available templates."""
        return self.env.list_templates()

    def process_with_template(self, input_file, template_name, **kwargs):
        """Process file with specific template."""
        # Load template
        template = self.env.get_template(f"{template_name}.md")

        # Process transcript
        analysis = self.processor.process_file(
            input_file,
            output_format="json"
        )

        # Merge with additional variables
        template_vars = {**analysis, **kwargs}

        # Render template
        output = template.render(**template_vars)

        return output

    def validate_template(self, template_name):
        """Validate template syntax."""
        try:
            template = self.env.get_template(f"{template_name}.md")
            # Try to render with dummy data
            template.render(
                metadata={'date': '2024-01-01', 'participants': []},
                analysis={'executive_summary': 'Test summary'}
            )
            return True, "Template is valid"
        except Exception as e:
            return False, str(e)

# Usage
template_mgr = TemplateManager()

# Create custom template
executive_template = """
# Executive Summary Report

**Date**: {{ metadata.date }}
**Participants**: {{ metadata.participants | join(", ") }}

## Key Insights
{{ analysis.executive_summary }}

## Strategic Recommendations
{% for rec in analysis.recommendations %}
- {{ rec.title }}: {{ rec.description }}
{% endfor %}

## Custom Section
{{ custom_message }}
"""

template_mgr.create_template("executive_brief", executive_template)

# Use template
result = template_mgr.process_with_template(
    "transcript.vtt",
    "executive_brief",
    custom_message="This is a custom message"
)
```

### Dynamic Template Generation

```python
from customer_snapshot import TranscriptProcessor

class DynamicTemplateGenerator:
    def __init__(self):
        self.processor = TranscriptProcessor()

    def generate_template_for_use_case(self, use_case):
        """Generate template based on use case."""
        templates = {
            "sales_call": self._sales_call_template(),
            "support_ticket": self._support_ticket_template(),
            "customer_interview": self._customer_interview_template(),
            "product_feedback": self._product_feedback_template()
        }

        return templates.get(use_case, self._default_template())

    def _sales_call_template(self):
        return """
# Sales Call Summary

**Prospect**: {{ metadata.customer }}
**Date**: {{ metadata.date }}
**Sales Rep**: {{ metadata.sales_rep }}

## Opportunity Overview
{{ analysis.opportunity_summary }}

## Pain Points Identified
{% for pain in analysis.pain_points %}
- **{{ pain.category }}**: {{ pain.description }}
  - Impact: {{ pain.impact }}
  - Urgency: {{ pain.urgency }}
{% endfor %}

## Solution Alignment
{{ analysis.solution_fit }}

## Next Steps
{% for step in analysis.next_steps %}
- [ ] {{ step.action }} ({{ step.owner }} - {{ step.due_date }})
{% endfor %}

## Deal Qualification
- Budget: {{ analysis.budget_status }}
- Authority: {{ analysis.decision_maker }}
- Need: {{ analysis.need_level }}
- Timeline: {{ analysis.timeline }}
"""

    def _support_ticket_template(self):
        return """
# Support Ticket Summary

**Ticket ID**: {{ metadata.ticket_id }}
**Customer**: {{ metadata.customer }}
**Priority**: {{ metadata.priority }}

## Issue Description
{{ analysis.issue_summary }}

## Resolution Steps
{% for step in analysis.resolution_steps %}
{{ loop.index }}. {{ step.action }}
   - Result: {{ step.result }}
{% endfor %}

## Root Cause
{{ analysis.root_cause }}

## Prevention Measures
{% for measure in analysis.prevention %}
- {{ measure.description }}
{% endfor %}
"""

    def process_with_dynamic_template(self, input_file, use_case):
        """Process file with dynamically generated template."""
        template_content = self.generate_template_for_use_case(use_case)

        # Process file
        analysis = self.processor.process_file(
            input_file,
            output_format="json"
        )

        # Render template
        from jinja2 import Template
        template = Template(template_content)
        result = template.render(**analysis)

        return result
```

## Error Handling

### Comprehensive Error Handling

```python
from customer_snapshot import TranscriptProcessor
from customer_snapshot.utils.error_handling import (
    with_retry, with_fallback, ErrorBoundary
)
from customer_snapshot.monitoring.error_tracker import get_error_tracker
import logging

class RobustProcessor:
    def __init__(self):
        self.processor = TranscriptProcessor()
        self.error_tracker = get_error_tracker()
        self.logger = logging.getLogger(__name__)

    @with_retry(max_attempts=3, delay=1.0)
    @with_fallback(fallback_value=None)
    def safe_process_file(self, input_path, **kwargs):
        """Process file with comprehensive error handling."""
        try:
            with ErrorBoundary("transcript_processing") as boundary:
                # Validate input
                self.validate_input(input_path)

                # Process file
                result = self.processor.process_file(input_path, **kwargs)

                # Validate output
                self.validate_output(result)

                return result

            if boundary.errors:
                self.logger.error(f"Processing failed with {len(boundary.errors)} errors")
                self.handle_processing_errors(boundary.errors)
                return None

        except Exception as e:
            self.error_tracker.track_exception(e)
            self.logger.error(f"Unexpected error processing {input_path}: {e}")
            raise

    def validate_input(self, input_path):
        """Validate input file."""
        from pathlib import Path

        path = Path(input_path)

        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not path.suffix.lower() == '.vtt':
            raise ValueError(f"Invalid file format. Expected .vtt, got {path.suffix}")

        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 100:  # 100MB limit
            raise ValueError(f"File too large: {size_mb:.1f}MB (limit: 100MB)")

        # Check content
        with open(path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if not first_line.startswith('WEBVTT'):
                raise ValueError("Invalid VTT format: missing WEBVTT header")

    def validate_output(self, result):
        """Validate processing output."""
        if not result:
            raise ValueError("Processing returned empty result")

        # Add specific validation logic based on your requirements
        if isinstance(result, dict):
            required_fields = ['analysis', 'metadata']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field in output: {field}")

    def handle_processing_errors(self, errors):
        """Handle specific processing errors."""
        for error in errors:
            if "API" in str(error):
                self.logger.warning("API error detected, consider rate limiting")
            elif "Memory" in str(error):
                self.logger.warning("Memory error detected, consider smaller chunks")
            elif "Timeout" in str(error):
                self.logger.warning("Timeout error detected, consider longer timeouts")

    def process_with_recovery(self, input_path, **kwargs):
        """Process with automatic recovery strategies."""
        strategies = [
            # Strategy 1: Default processing
            lambda: self.processor.process_file(input_path, **kwargs),

            # Strategy 2: Smaller chunks
            lambda: self.processor.process_file(
                input_path, chunk_size=500, **kwargs
            ),

            # Strategy 3: Memory optimized
            lambda: self.processor.process_file(
                input_path, optimize_memory=True, **kwargs
            ),

            # Strategy 4: Simplified analysis
            lambda: self.processor.process_file(
                input_path, extract_entities=False, **kwargs
            )
        ]

        last_error = None
        for i, strategy in enumerate(strategies):
            try:
                self.logger.info(f"Attempting processing strategy {i+1}")
                result = strategy()
                self.logger.info(f"Strategy {i+1} succeeded")
                return result
            except Exception as e:
                last_error = e
                self.logger.warning(f"Strategy {i+1} failed: {e}")
                continue

        # All strategies failed
        self.logger.error("All recovery strategies failed")
        raise last_error
```

### Circuit Breaker Pattern

```python
from customer_snapshot.utils.error_handling import CircuitBreaker
import time

class ProcessorWithCircuitBreaker:
    def __init__(self):
        self.processor = TranscriptProcessor()

        # Circuit breaker for API calls
        self.api_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception
        )

    @CircuitBreaker(failure_threshold=3, recovery_timeout=30)
    def process_with_breaker(self, input_path):
        """Process with circuit breaker protection."""
        return self.processor.process_file(input_path)

    def process_with_fallback_service(self, input_path):
        """Process with fallback to alternative service."""
        try:
            return self.process_with_breaker(input_path)
        except Exception as e:
            if "Circuit breaker is OPEN" in str(e):
                self.logger.info("Circuit breaker open, using fallback service")
                return self.fallback_processing_service(input_path)
            raise

    def fallback_processing_service(self, input_path):
        """Fallback processing service (simplified analysis)."""
        # Implement fallback logic
        # Could be a simpler local NLP model or cached response
        return {
            "status": "fallback_processed",
            "message": "Processed using fallback service due to API issues",
            "basic_analysis": "Basic content extracted from transcript"
        }
```

## Performance Optimization

### Caching and Memoization

```python
from customer_snapshot import TranscriptProcessor
from functools import lru_cache
import hashlib
import pickle
import os

class OptimizedProcessor:
    def __init__(self, cache_dir="./cache"):
        self.processor = TranscriptProcessor()
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def process_with_cache(self, input_path, **kwargs):
        """Process with file-based caching."""
        # Generate cache key
        cache_key = self.generate_cache_key(input_path, **kwargs)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        # Check cache
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)

        # Process and cache
        result = self.processor.process_file(input_path, **kwargs)

        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)

        return result

    def generate_cache_key(self, input_path, **kwargs):
        """Generate unique cache key."""
        # Include file content hash and parameters
        with open(input_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        params_str = str(sorted(kwargs.items()))
        params_hash = hashlib.md5(params_str.encode()).hexdigest()

        return f"{file_hash}_{params_hash}"

    @lru_cache(maxsize=128)
    def cached_chunk_processing(self, chunk_content, model, **kwargs):
        """Memory-based caching for chunk processing."""
        # This would be implemented at the chunk level
        pass

    def process_with_preloading(self, files):
        """Process multiple files with model preloading."""
        # Preload models once
        self.processor.preload_models()

        results = []
        for file in files:
            result = self.processor.process_file(file)
            results.append(result)

        return results
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import cpu_count
import asyncio

class ParallelProcessor:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or cpu_count()
        self.processor = TranscriptProcessor()

    def process_parallel_threads(self, files):
        """Process files using thread pool."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.processor.process_file, file)
                for file in files
            ]

            results = []
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({'error': str(e)})

            return results

    def process_parallel_processes(self, files):
        """Process files using process pool."""
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(process_single_file, file)
                for file in files
            ]

            results = [future.result() for future in futures]
            return results

    async def process_async(self, files):
        """Asynchronous processing."""
        semaphore = asyncio.Semaphore(self.max_workers)

        async def process_with_semaphore(file):
            async with semaphore:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None, self.processor.process_file, file
                )

        tasks = [process_with_semaphore(file) for file in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

def process_single_file(file_path):
    """Function for process pool processing."""
    processor = TranscriptProcessor()
    return processor.process_file(file_path)
```

## Web Service Integration

### Flask API

```python
from flask import Flask, request, jsonify, send_file
from customer_snapshot import TranscriptProcessor
import tempfile
import os

app = Flask(__name__)
processor = TranscriptProcessor()

@app.route('/api/process', methods=['POST'])
def process_transcript():
    """Process transcript via REST API."""
    try:
        # Handle file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get options
        output_format = request.form.get('output_format', 'markdown')
        template = request.form.get('template', None)

        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.vtt') as tmp_file:
            file.save(tmp_file.name)

            try:
                # Process file
                result = processor.process_file(
                    tmp_file.name,
                    output_format=output_format,
                    template=template
                )

                return jsonify({
                    'status': 'success',
                    'result': result
                })

            finally:
                os.unlink(tmp_file.name)

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/process/async', methods=['POST'])
def process_transcript_async():
    """Start asynchronous processing."""
    # Implementation for async processing with job queue
    pass

@app.route('/api/templates', methods=['GET'])
def list_templates():
    """List available templates."""
    templates = processor.list_templates()
    return jsonify({'templates': templates})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test processor
        status = processor.health_check()
        return jsonify({
            'status': 'healthy',
            'details': status
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### FastAPI Service

```python
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from customer_snapshot import TranscriptProcessor
import asyncio
import uuid
import tempfile

app = FastAPI(title="Customer Snapshot API")
processor = TranscriptProcessor()

class ProcessingRequest(BaseModel):
    output_format: str = "markdown"
    template: str = None
    extract_entities: bool = True
    sentiment_analysis: bool = True

class ProcessingResponse(BaseModel):
    job_id: str
    status: str
    result: dict = None
    error: str = None

# Job storage (use Redis in production)
jobs = {}

@app.post("/api/v1/process", response_model=ProcessingResponse)
async def process_transcript(
    file: UploadFile = File(...),
    request: ProcessingRequest = ProcessingRequest()
):
    """Process transcript file."""
    if not file.filename.endswith('.vtt'):
        raise HTTPException(status_code=400, detail="Only VTT files are supported")

    try:
        # Read file content
        content = await file.read()

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.vtt') as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()

            # Process
            result = processor.process_file(
                tmp_file.name,
                output_format=request.output_format,
                template=request.template,
                extract_entities=request.extract_entities,
                sentiment_analysis=request.sentiment_analysis
            )

            return ProcessingResponse(
                job_id=str(uuid.uuid4()),
                status="completed",
                result=result
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/process/async")
async def process_transcript_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    request: ProcessingRequest = ProcessingRequest()
):
    """Start asynchronous processing."""
    job_id = str(uuid.uuid4())

    # Initialize job
    jobs[job_id] = {
        'status': 'pending',
        'created_at': asyncio.get_event_loop().time()
    }

    # Start background processing
    background_tasks.add_task(
        process_in_background,
        job_id,
        await file.read(),
        request
    )

    return {'job_id': job_id, 'status': 'pending'}

async def process_in_background(job_id: str, file_content: bytes, request: ProcessingRequest):
    """Background processing task."""
    try:
        jobs[job_id]['status'] = 'processing'

        # Process file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.vtt') as tmp_file:
            tmp_file.write(file_content)
            tmp_file.flush()

            result = processor.process_file(
                tmp_file.name,
                output_format=request.output_format,
                template=request.template
            )

            jobs[job_id].update({
                'status': 'completed',
                'result': result
            })

    except Exception as e:
        jobs[job_id].update({
            'status': 'failed',
            'error': str(e)
        })

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Customer Snapshot API"}
```

## Real-time Processing

### WebSocket Implementation

```python
import asyncio
import websockets
import json
from customer_snapshot import TranscriptProcessor

class RealtimeProcessor:
    def __init__(self):
        self.processor = TranscriptProcessor()
        self.clients = set()

    async def register_client(self, websocket):
        """Register new WebSocket client."""
        self.clients.add(websocket)
        await websocket.send(json.dumps({
            'type': 'connected',
            'message': 'Connected to transcript processor'
        }))

    async def unregister_client(self, websocket):
        """Unregister WebSocket client."""
        self.clients.discard(websocket)

    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection."""
        await self.register_client(websocket)

        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_message(websocket, data)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)

    async def process_message(self, websocket, data):
        """Process incoming WebSocket message."""
        message_type = data.get('type')

        if message_type == 'process_transcript':
            await self.handle_transcript_processing(websocket, data)
        elif message_type == 'get_status':
            await self.handle_status_request(websocket, data)

    async def handle_transcript_processing(self, websocket, data):
        """Handle transcript processing request."""
        try:
            # Send processing started message
            await websocket.send(json.dumps({
                'type': 'processing_started',
                'job_id': data.get('job_id')
            }))

            # Process transcript
            result = await self.process_async(data['transcript_path'])

            # Send result
            await websocket.send(json.dumps({
                'type': 'processing_completed',
                'job_id': data.get('job_id'),
                'result': result
            }))

        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'processing_error',
                'job_id': data.get('job_id'),
                'error': str(e)
            }))

    async def process_async(self, transcript_path):
        """Asynchronous transcript processing."""
        loop = asyncio.get_event_loop()

        result = await loop.run_in_executor(
            None,
            self.processor.process_file,
            transcript_path
        )

        return result

    async def broadcast_status(self, status):
        """Broadcast status to all connected clients."""
        if self.clients:
            message = json.dumps({
                'type': 'status_update',
                'status': status
            })

            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )

# Start WebSocket server
processor = RealtimeProcessor()

start_server = websockets.serve(
    processor.handle_client,
    "localhost",
    8765
)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

### Streaming Processing

```python
import asyncio
from customer_snapshot import TranscriptProcessor

class StreamingProcessor:
    def __init__(self):
        self.processor = TranscriptProcessor()

    async def process_stream(self, transcript_stream):
        """Process transcript data as it streams in."""
        buffer = ""
        chunk_size = 1000  # Process every 1000 characters

        async for chunk in transcript_stream:
            buffer += chunk

            # Process when buffer reaches chunk size
            if len(buffer) >= chunk_size:
                # Extract complete sentences
                sentences = self.extract_complete_sentences(buffer)

                if sentences:
                    # Process sentences
                    analysis = await self.process_chunk_async(sentences)
                    yield analysis

                    # Keep remaining incomplete text
                    buffer = self.get_remaining_text(buffer, sentences)

        # Process remaining buffer
        if buffer.strip():
            analysis = await self.process_chunk_async(buffer)
            yield analysis

    def extract_complete_sentences(self, text):
        """Extract complete sentences from text buffer."""
        # Simple sentence extraction (improve with NLP)
        sentences = []
        for sentence in text.split('.'):
            if sentence.strip():
                sentences.append(sentence.strip() + '.')

        return sentences[:-1]  # Keep last incomplete sentence in buffer

    def get_remaining_text(self, buffer, processed_sentences):
        """Get remaining unprocessed text."""
        processed_text = ' '.join(processed_sentences)
        return buffer.replace(processed_text, '').strip()

    async def process_chunk_async(self, text_chunk):
        """Process a chunk of text asynchronously."""
        loop = asyncio.get_event_loop()

        # Run processing in executor to avoid blocking
        result = await loop.run_in_executor(
            None,
            self.processor.process_text_chunk,
            text_chunk
        )

        return result

# Usage example
async def main():
    processor = StreamingProcessor()

    # Simulate streaming transcript data
    async def transcript_stream():
        chunks = [
            "Hello, welcome to our call today. ",
            "I wanted to discuss our cloud migration project. ",
            "We have some concerns about the timeline and costs. ",
            "Can you help us understand the best approach?"
        ]

        for chunk in chunks:
            yield chunk
            await asyncio.sleep(1)  # Simulate real-time streaming

    # Process stream
    async for analysis in processor.process_stream(transcript_stream()):
        print(f"Partial analysis: {analysis}")

asyncio.run(main())
```

## Database Integration

### SQLAlchemy Integration

```python
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from customer_snapshot import TranscriptProcessor

Base = declarative_base()

class TranscriptRecord(Base):
    __tablename__ = 'transcripts'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_path = Column(String(500))
    processed_at = Column(DateTime, default=datetime.utcnow)
    analysis_result = Column(JSON)
    metadata = Column(JSON)
    status = Column(String(50), default='pending')
    error_message = Column(Text)

class DatabaseProcessor:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.processor = TranscriptProcessor()

    def process_and_store(self, file_path):
        """Process transcript and store in database."""
        # Create database record
        record = TranscriptRecord(
            filename=os.path.basename(file_path),
            original_path=file_path,
            status='processing'
        )
        self.session.add(record)
        self.session.commit()

        try:
            # Process transcript
            result = self.processor.process_file(file_path)

            # Update record with results
            record.analysis_result = result
            record.status = 'completed'
            record.processed_at = datetime.utcnow()

            self.session.commit()
            return record.id

        except Exception as e:
            # Update record with error
            record.status = 'failed'
            record.error_message = str(e)
            self.session.commit()
            raise

    def get_analysis(self, record_id):
        """Retrieve analysis from database."""
        record = self.session.query(TranscriptRecord).filter_by(id=record_id).first()
        return record.analysis_result if record else None

    def search_transcripts(self, query):
        """Search transcripts by content."""
        # This would use full-text search capabilities of your database
        records = self.session.query(TranscriptRecord).filter(
            TranscriptRecord.analysis_result.contains(query)
        ).all()

        return [(r.id, r.filename, r.analysis_result) for r in records]

    def get_analytics(self):
        """Get processing analytics."""
        total = self.session.query(TranscriptRecord).count()
        completed = self.session.query(TranscriptRecord).filter_by(status='completed').count()
        failed = self.session.query(TranscriptRecord).filter_by(status='failed').count()

        return {
            'total_processed': total,
            'successful': completed,
            'failed': failed,
            'success_rate': completed / total if total > 0 else 0
        }

# Usage
processor = DatabaseProcessor('postgresql://user:pass@localhost/transcripts')
record_id = processor.process_and_store('transcript.vtt')
analysis = processor.get_analysis(record_id)
```

## Webhook Integration

### Webhook Client

```python
import requests
import json
from customer_snapshot import TranscriptProcessor

class WebhookProcessor:
    def __init__(self, webhook_urls=None):
        self.processor = TranscriptProcessor()
        self.webhook_urls = webhook_urls or []

    def process_with_webhooks(self, input_path, **kwargs):
        """Process transcript and send webhooks."""
        try:
            # Send processing started webhook
            self.send_webhook('processing_started', {
                'file': input_path,
                'timestamp': datetime.now().isoformat()
            })

            # Process transcript
            result = self.processor.process_file(input_path, **kwargs)

            # Send success webhook
            self.send_webhook('processing_completed', {
                'file': input_path,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })

            return result

        except Exception as e:
            # Send error webhook
            self.send_webhook('processing_failed', {
                'file': input_path,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            raise

    def send_webhook(self, event_type, data):
        """Send webhook to all configured URLs."""
        payload = {
            'event': event_type,
            'data': data
        }

        for url in self.webhook_urls:
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                response.raise_for_status()
                print(f"Webhook sent successfully to {url}")

            except requests.exceptions.RequestException as e:
                print(f"Failed to send webhook to {url}: {e}")

    def add_webhook_url(self, url):
        """Add webhook URL."""
        self.webhook_urls.append(url)

    def remove_webhook_url(self, url):
        """Remove webhook URL."""
        if url in self.webhook_urls:
            self.webhook_urls.remove(url)

# Usage
processor = WebhookProcessor([
    'https://api.example.com/webhooks/transcript',
    'https://internal.company.com/api/transcript-webhook'
])

result = processor.process_with_webhooks('transcript.vtt')
```

### Webhook Server Example

```python
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhook/transcript', methods=['POST'])
def handle_transcript_webhook():
    """Handle incoming transcript processing webhooks."""
    try:
        data = request.get_json()
        event_type = data.get('event')
        event_data = data.get('data')

        if event_type == 'processing_started':
            print(f"Processing started for: {event_data['file']}")

        elif event_type == 'processing_completed':
            print(f"Processing completed for: {event_data['file']}")
            # Handle successful processing
            handle_successful_processing(event_data)

        elif event_type == 'processing_failed':
            print(f"Processing failed for: {event_data['file']}")
            # Handle failed processing
            handle_failed_processing(event_data)

        return jsonify({'status': 'received'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

def handle_successful_processing(data):
    """Handle successful processing webhook."""
    # Update database, send notifications, etc.
    pass

def handle_failed_processing(data):
    """Handle failed processing webhook."""
    # Log error, retry processing, notify administrators
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

---

*These examples provide comprehensive patterns for integrating Customer Solution Snapshot Generator into various application architectures. Adapt them to your specific requirements and infrastructure.*
