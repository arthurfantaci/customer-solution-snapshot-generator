# Advanced Features Tutorial

Master the advanced capabilities of Customer Solution Snapshot Generator.

## Table of Contents

1. [Custom Templates](#custom-templates)
2. [Batch Processing](#batch-processing)
3. [Memory Optimization](#memory-optimization)
4. [API Integration](#api-integration)
5. [Monitoring & Analytics](#monitoring--analytics)
6. [Error Handling](#error-handling)
7. [Performance Tuning](#performance-tuning)
8. [Integration Patterns](#integration-patterns)

## Custom Templates

Create powerful, reusable templates for consistent output formatting.

### Template Syntax

Templates use Jinja2 syntax with custom variables:

```markdown
<!-- templates/executive_brief.md -->
# {{ metadata.title | default("Executive Brief") }}

**Date**: {{ metadata.date }}
**Duration**: {{ metadata.duration }}
**Participants**: {{ metadata.participants | join(", ") }}

## Executive Summary
{{ analysis.executive_summary }}

## Key Metrics
- **Sentiment**: {{ analysis.sentiment | title }}
- **Urgency Level**: {{ analysis.urgency | default("Medium") }}
- **Decision Makers**: {{ analysis.decision_makers | length }}

## Strategic Insights
{% for insight in analysis.strategic_insights %}
### {{ insight.category }}
{{ insight.description }}

**Impact**: {{ insight.impact }}
**Priority**: {{ insight.priority }}
{% endfor %}

## Recommendations
{% for rec in analysis.recommendations %}
1. **{{ rec.title }}**
   - *Rationale*: {{ rec.rationale }}
   - *Timeline*: {{ rec.timeline }}
   - *ROI*: {{ rec.roi }}
{% endfor %}

## Next Actions
{% for action in analysis.action_items %}
- [ ] {{ action.description }} ({{ action.owner }} - {{ action.due_date }})
{% endfor %}
```

### Available Template Variables

```python
{
    "metadata": {
        "title": "Conversation Title",
        "date": "2024-01-15",
        "duration": "45:32",
        "participants": ["John Doe", "Jane Smith"],
        "file_size": "2.5 MB",
        "word_count": 8500
    },
    "analysis": {
        "executive_summary": "Brief overview...",
        "sentiment": "positive",
        "confidence": 0.92,
        "key_topics": ["cloud migration", "security"],
        "entities": ["AWS", "Microsoft", "John Doe"],
        "action_items": [...],
        "decision_makers": [...],
        "budget_mentions": [...],
        "timeline_mentions": [...],
        "pain_points": [...],
        "requirements": [...],
        "competitive_mentions": [...]
    },
    "processing": {
        "model_used": "claude-3-sonnet-20240229",
        "processing_time": "12.4s",
        "chunk_count": 15,
        "api_calls": 8
    }
}
```

### Template Functions

```markdown
<!-- Custom formatting functions -->
{{ text | truncate(100) }}
{{ date | strftime("%B %d, %Y") }}
{{ participants | format_names }}
{{ duration | format_duration }}
{{ currency | format_currency }}
```

### Using Custom Templates

```bash
# Apply custom template
customer-snapshot process call.vtt --template templates/executive_brief.md

# Template with custom variables
customer-snapshot process call.vtt \
  --template templates/sales_report.md \
  --template-vars company="Acme Corp" region="North America"
```

## Batch Processing

Process multiple files efficiently with advanced batch operations.

### Basic Batch Processing

```bash
# Process all VTT files in directory
customer-snapshot batch process ./transcripts/

# Process with pattern matching
customer-snapshot batch process ./2024/**/*.vtt

# Process specific file types
find ./data -name "*.vtt" -mtime -7 | \
  customer-snapshot batch process --stdin
```

### Advanced Batch Options

```bash
# Parallel processing with custom worker count
customer-snapshot batch process ./files/ \
  --parallel --max-workers 8

# Resume failed processing
customer-snapshot batch process ./files/ \
  --resume --checkpoint ./batch_state.json

# Process with different templates per file
customer-snapshot batch process ./files/ \
  --template-mapping templates/mapping.yaml
```

### Batch Configuration

Create `batch_config.yaml`:

```yaml
batch:
  parallel: true
  max_workers: 4
  chunk_size: 1000
  retry_failed: true
  max_retries: 3
  
templates:
  default: templates/standard.md
  mapping:
    "*sales*": templates/sales_call.md
    "*support*": templates/support_ticket.md
    "*executive*": templates/executive_brief.md

output:
  directory: "./processed/{date}/{category}"
  naming: "{filename}_{timestamp}_analysis"
  formats: ["markdown", "json"]

filtering:
  min_duration: 300  # 5 minutes
  max_duration: 7200  # 2 hours
  required_participants: 2
  exclude_patterns: ["test_*", "*_backup"]
```

### Monitoring Batch Jobs

```bash
# Start batch job with monitoring
customer-snapshot batch process ./files/ \
  --monitor --progress --log batch.log

# View batch progress
customer-snapshot batch status --job-id 12345

# Cancel running batch
customer-snapshot batch cancel --job-id 12345
```

## Memory Optimization

Handle large files and memory-constrained environments.

### Streaming Processing

```bash
# Enable streaming for large files
customer-snapshot process large_file.vtt --stream

# Custom streaming buffer size
customer-snapshot process file.vtt --stream --buffer-size 1024
```

### Memory-Optimized Configuration

```yaml
# config.yaml
performance:
  memory_optimization:
    enabled: true
    streaming_threshold_mb: 10
    chunk_overlap: 100
    max_chunk_size: 2000
    gc_frequency: 1000
    
  caching:
    enabled: true
    max_cache_size_mb: 512
    cache_strategy: "lru"
    
  processing:
    lazy_loading: true
    preload_models: false
    batch_size: 10
```

### Memory Profiling

```bash
# Profile memory usage
customer-snapshot process file.vtt --profile-memory

# Detailed memory analysis
python -m memory_profiler optimize.py --input file.vtt

# Monitor memory in real-time
python monitor.py --track-memory --interval 1
```

## API Integration

Integrate with other systems using the Python API.

### Basic API Usage

```python
from customer_snapshot import TranscriptProcessor
from customer_snapshot.monitoring import get_error_tracker

# Initialize with custom config
config = {
    'api_key': 'your-key',
    'model': 'claude-3-sonnet-20240229',
    'chunk_size': 1000
}

processor = TranscriptProcessor(config)

# Process file
result = processor.process_file(
    'transcript.vtt',
    output_format='json',
    template='custom_template.md'
)

print(f"Analysis: {result}")
```

### Advanced API Features

```python
from customer_snapshot import (
    TranscriptProcessor, 
    PerformanceAnalyzer,
    ErrorTracker
)
from customer_snapshot.utils.config import Config

# Custom configuration
config = Config()
config.load_from_file('config.yaml')
config.api.timeout = 60
config.processing.enable_caching = True

# Initialize components
processor = TranscriptProcessor(config)
analyzer = PerformanceAnalyzer()
error_tracker = ErrorTracker()

# Process with error handling
try:
    with analyzer.track_performance("transcript_processing"):
        result = processor.process_file(
            input_path='transcript.vtt',
            output_format='json',
            include_metadata=True,
            extract_entities=True
        )
        
        # Custom post-processing
        enhanced_result = enhance_analysis(result)
        
        return enhanced_result
        
except Exception as e:
    error_tracker.track_exception(e)
    raise
```

### Webhook Integration

```python
import requests
from customer_snapshot import TranscriptProcessor

class WebhookProcessor:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.processor = TranscriptProcessor()
    
    def process_and_notify(self, file_path):
        try:
            # Process transcript
            result = self.processor.process_file(file_path)
            
            # Send webhook notification
            payload = {
                'status': 'completed',
                'file': file_path,
                'analysis': result,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
        except Exception as e:
            # Send error notification
            error_payload = {
                'status': 'failed',
                'file': file_path,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            requests.post(self.webhook_url, json=error_payload)
            raise

# Usage
processor = WebhookProcessor('https://api.example.com/webhooks/transcript')
processor.process_and_notify('transcript.vtt')
```

## Monitoring & Analytics

Comprehensive monitoring and analytics capabilities.

### Health Monitoring

```bash
# Comprehensive health check
customer-snapshot health --detailed

# Monitor specific components
customer-snapshot health --component api
customer-snapshot health --component nlp
customer-snapshot health --component filesystem

# Continuous health monitoring
customer-snapshot health --monitor --interval 30
```

### Performance Analytics

```bash
# Generate performance report
customer-snapshot performance report --last 7d

# Real-time performance monitoring
python performance_dashboard.py --mode interactive

# Custom performance analysis
python benchmark.py --custom-test ./test_files/
```

### Error Analysis

```bash
# View error dashboard
python error_analysis_dashboard.py --mode interactive

# Generate error report
python error_analysis_dashboard.py --mode report --output errors.json

# Track specific error patterns
customer-snapshot errors track --pattern "API timeout"
```

### Custom Metrics

```python
from customer_snapshot.monitoring import MetricsCollector

# Initialize metrics collector
metrics = MetricsCollector()

# Track custom metrics
@metrics.track_time('custom_processing')
@metrics.track_errors('custom_errors')
def custom_processing_step(data):
    # Your processing logic
    result = process_data(data)
    
    # Track custom counter
    metrics.increment('processed_items')
    
    # Track custom gauge
    metrics.gauge('queue_size', len(queue))
    
    return result

# Export metrics
metrics.export_prometheus('/metrics')
```

## Error Handling

Robust error handling and recovery patterns.

### Decorator-Based Error Handling

```python
from customer_snapshot.utils.error_handling import (
    with_retry, with_fallback, with_timeout, ErrorBoundary
)

@with_retry(max_attempts=3, delay=1.0)
@with_timeout(30.0)
@with_fallback(fallback_value="Processing failed")
def robust_processing(file_path):
    return processor.process_file(file_path)

# Error boundary for critical sections
with ErrorBoundary("transcript_processing") as boundary:
    result = process_transcript(file_path)
    
if boundary.errors:
    handle_processing_errors(boundary.errors)
```

### Circuit Breaker Pattern

```python
from customer_snapshot.utils.error_handling import CircuitBreaker

@CircuitBreaker(failure_threshold=5, recovery_timeout=60)
def api_call_with_circuit_breaker():
    return make_api_request()

# Usage
try:
    result = api_call_with_circuit_breaker()
except CircuitBreakerOpenError:
    # Handle when circuit is open
    result = use_cached_response()
```

### Custom Error Recovery

```python
class CustomErrorHandler:
    def __init__(self):
        self.retry_strategies = {
            'api_timeout': self.handle_api_timeout,
            'memory_error': self.handle_memory_error,
            'parse_error': self.handle_parse_error
        }
    
    def handle_api_timeout(self, error, context):
        # Implement exponential backoff
        delay = min(2 ** context.attempt, 60)
        time.sleep(delay)
        return True  # Retry
    
    def handle_memory_error(self, error, context):
        # Reduce chunk size and retry
        context.config.chunk_size //= 2
        return context.config.chunk_size > 100  # Retry if reasonable
    
    def handle_parse_error(self, error, context):
        # Try alternative parsing method
        return try_alternative_parser(context.file_path)
```

## Performance Tuning

Optimize performance for your specific use case.

### API Optimization

```yaml
# config.yaml
api:
  anthropic:
    model: claude-3-haiku-20240307  # Faster model
    max_tokens: 4000
    temperature: 0.1
    timeout: 30
    
  rate_limiting:
    requests_per_minute: 50
    burst_limit: 10
    retry_after_rate_limit: true
    
  connection_pooling:
    max_connections: 10
    keep_alive: true
    pool_timeout: 30
```

### Processing Optimization

```python
# Optimize for throughput
config.processing.chunk_size = 2000  # Larger chunks
config.processing.parallel_chunks = True
config.processing.preload_models = True

# Optimize for memory
config.processing.chunk_size = 500   # Smaller chunks
config.processing.streaming = True
config.processing.gc_frequency = 100

# Optimize for accuracy
config.processing.chunk_overlap = 200
config.processing.context_window = 1000
config.nlp.extract_entities = True
```

### Caching Strategies

```python
from customer_snapshot.utils.caching import CacheManager

# Initialize cache
cache = CacheManager(
    strategy='redis',  # or 'memory', 'file'
    ttl=3600,
    max_size='1GB'
)

# Use cache in processing
@cache.memoize(key_func=lambda x: f"transcript_{hash(x)}")
def cached_processing(transcript_text):
    return expensive_processing(transcript_text)
```

## Integration Patterns

Common integration patterns for enterprise use.

### Microservices Architecture

```python
# transcript_service.py
from flask import Flask, request, jsonify
from customer_snapshot import TranscriptProcessor

app = Flask(__name__)
processor = TranscriptProcessor()

@app.route('/process', methods=['POST'])
def process_transcript():
    file_path = request.json['file_path']
    options = request.json.get('options', {})
    
    try:
        result = processor.process_file(file_path, **options)
        return jsonify({
            'status': 'success',
            'result': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Message Queue Integration

```python
# worker.py
import pika
import json
from customer_snapshot import TranscriptProcessor

def process_message(ch, method, properties, body):
    try:
        data = json.loads(body)
        file_path = data['file_path']
        
        processor = TranscriptProcessor()
        result = processor.process_file(file_path)
        
        # Publish result
        result_message = {
            'file_path': file_path,
            'result': result,
            'status': 'completed'
        }
        
        ch.basic_publish(
            exchange='results',
            routing_key='transcript.completed',
            body=json.dumps(result_message)
        )
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        # Handle error
        error_message = {
            'file_path': data.get('file_path'),
            'error': str(e),
            'status': 'failed'
        }
        
        ch.basic_publish(
            exchange='errors',
            routing_key='transcript.failed',
            body=json.dumps(error_message)
        )
        
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# RabbitMQ setup
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='transcript_queue', durable=True)
channel.basic_consume(
    queue='transcript_queue',
    on_message_callback=process_message
)

channel.start_consuming()
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: transcript-processor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: transcript-processor
  template:
    metadata:
      labels:
        app: transcript-processor
    spec:
      containers:
      - name: processor
        image: arthurfantaci/customer-snapshot-generator:latest
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: anthropic-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command:
            - python
            - /usr/local/bin/healthcheck.py
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - customer-snapshot
            - health
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Next Steps

Now that you've mastered the advanced features:

1. **Contribute**: Help improve the project on [GitHub](https://github.com/arthurfantaci/customer-solution-snapshot-generator)
2. **Customize**: Build custom templates and integrations for your use case  
3. **Scale**: Deploy in production with monitoring and error tracking
4. **Optimize**: Fine-tune performance for your specific requirements

For more information, see:
- [API Documentation](../api/index.html)
- [Architecture Guide](../ARCHITECTURE.md)
- [Performance Guide](../PERFORMANCE.md)
- [Security Guide](../SECURITY.md)