# Troubleshooting Guide

Complete troubleshooting guide for Customer Solution Snapshot Generator.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Problems](#configuration-problems)
3. [Processing Errors](#processing-errors)
4. [Performance Issues](#performance-issues)
5. [API and Network Issues](#api-and-network-issues)
6. [Docker Issues](#docker-issues)
7. [Memory and Resource Issues](#memory-and-resource-issues)
8. [Output and Format Issues](#output-and-format-issues)
9. [Monitoring Issues](#monitoring-issues)
10. [Debug Tools](#debug-tools)

## Installation Issues

### Issue: Package Installation Fails

**Symptoms:**
```bash
ERROR: Could not find a version that satisfies the requirement customer-snapshot
```

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   pip install --upgrade pip
   ```

2. **Install from source:**
   ```bash
   git clone https://github.com/arthurfantaci/customer-solution-snapshot-generator.git
   cd customer-solution-snapshot-generator
   pip install -e .
   ```

3. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install customer-snapshot
   ```

### Issue: spaCy Model Download Fails

**Symptoms:**
```bash
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Solutions:**

1. **Download model manually:**
   ```bash
   python -m spacy download en_core_web_sm

   # If that fails, try direct download:
   pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl
   ```

2. **Use alternative model:**
   ```bash
   # In config or environment
   export SPACY_MODEL=en_core_web_md
   python -m spacy download en_core_web_md
   ```

### Issue: NLTK Data Missing

**Symptoms:**
```bash
LookupError: NLTK data not found
```

**Solutions:**

1. **Download NLTK data:**
   ```bash
   python -m nltk.downloader punkt
   python -m nltk.downloader stopwords
   python -m nltk.downloader wordnet
   ```

2. **Manual download:**
   ```python
   import nltk
   import ssl

   try:
       _create_unverified_https_context = ssl._create_unverified_context
   except AttributeError:
       pass
   else:
       ssl._create_default_https_context = _create_unverified_https_context

   nltk.download('punkt')
   ```

## Configuration Problems

### Issue: API Key Not Found

**Symptoms:**
```bash
Error: ANTHROPIC_API_KEY environment variable not set
```

**Solutions:**

1. **Set environment variable:**
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"

   # Make it permanent (add to ~/.bashrc or ~/.zshrc)
   echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc
   ```

2. **Use .env file:**
   ```bash
   echo "ANTHROPIC_API_KEY=your-key-here" > .env
   ```

3. **Pass as parameter:**
   ```bash
   customer-snapshot process file.vtt --api-key your-key-here
   ```

### Issue: Configuration File Not Loaded

**Symptoms:**
```bash
Warning: Configuration file not found, using defaults
```

**Solutions:**

1. **Create config file:**
   ```yaml
   # config.yaml
   api:
     anthropic_api_key: ${ANTHROPIC_API_KEY}
     model: claude-3-sonnet-20240229

   processing:
     chunk_size: 500
     enable_caching: true
   ```

2. **Specify config path:**
   ```bash
   customer-snapshot process file.vtt --config /path/to/config.yaml
   ```

3. **Validate configuration:**
   ```bash
   customer-snapshot config validate
   customer-snapshot config-info
   ```

## Processing Errors

### Issue: VTT File Format Error

**Symptoms:**
```bash
ValueError: Invalid VTT format: File does not start with 'WEBVTT'
```

**Solutions:**

1. **Check file format:**
   ```bash
   head -n 5 your_file.vtt
   # Should start with "WEBVTT"
   ```

2. **Fix format:**
   ```bash
   # Add WEBVTT header if missing
   echo -e "WEBVTT\n$(cat your_file.vtt)" > fixed_file.vtt
   ```

3. **Convert from other formats:**
   ```bash
   # From SRT to VTT
   ffmpeg -i input.srt output.vtt

   # From plain text (manual VTT creation needed)
   customer-snapshot convert text-to-vtt input.txt output.vtt
   ```

### Issue: Unicode/Encoding Error

**Symptoms:**
```bash
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**Solutions:**

1. **Check file encoding:**
   ```bash
   file -i your_file.vtt
   # Should show charset=utf-8
   ```

2. **Convert encoding:**
   ```bash
   iconv -f ISO-8859-1 -t UTF-8 input.vtt > output.vtt
   ```

3. **Force encoding in Python:**
   ```python
   processor.process_file('file.vtt', encoding='latin-1')
   ```

### Issue: Empty or Invalid Output

**Symptoms:**
- No output file generated
- Empty analysis results
- Truncated content

**Solutions:**

1. **Check input file content:**
   ```bash
   wc -l your_file.vtt  # Should have reasonable line count
   grep -v "^$" your_file.vtt | head -20  # Check content
   ```

2. **Increase verbosity:**
   ```bash
   customer-snapshot process file.vtt -vvv
   ```

3. **Check minimum content requirements:**
   ```bash
   # File should have at least 100 words for meaningful analysis
   customer-snapshot validate file.vtt
   ```

## Performance Issues

### Issue: Processing Too Slow

**Symptoms:**
- Takes hours to process small files
- High CPU usage but slow progress

**Solutions:**

1. **Optimize chunk size:**
   ```bash
   # For large files
   customer-snapshot process file.vtt --chunk-size 2000

   # For small files
   customer-snapshot process file.vtt --chunk-size 1000
   ```

2. **Enable parallel processing:**
   ```bash
   customer-snapshot batch process files/ --parallel --max-workers 4
   ```

3. **Use faster model:**
   ```yaml
   # config.yaml
   api:
     model: claude-3-haiku-20240307  # Faster than sonnet
   ```

4. **Enable caching:**
   ```yaml
   # config.yaml
   processing:
     enable_caching: true
     cache_ttl: 3600
   ```

### Issue: High Memory Usage

**Symptoms:**
```bash
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Enable memory optimization:**
   ```bash
   customer-snapshot process file.vtt --optimize-memory
   ```

2. **Reduce chunk size:**
   ```bash
   customer-snapshot process file.vtt --chunk-size 200
   ```

3. **Use streaming mode:**
   ```bash
   customer-snapshot process file.vtt --stream
   ```

4. **Monitor memory usage:**
   ```bash
   python monitor.py --track-memory
   ```

## API and Network Issues

### Issue: API Timeout

**Symptoms:**
```bash
TimeoutError: API request timed out after 30 seconds
```

**Solutions:**

1. **Increase timeout:**
   ```bash
   customer-snapshot process file.vtt --timeout 60
   ```

2. **Enable retries:**
   ```bash
   customer-snapshot process file.vtt --max-retries 5
   ```

3. **Check network connectivity:**
   ```bash
   curl -I https://api.anthropic.com
   ```

4. **Use exponential backoff:**
   ```yaml
   # config.yaml
   api:
     timeout: 60
     max_retries: 5
     backoff_factor: 2
   ```

### Issue: API Rate Limiting

**Symptoms:**
```bash
RateLimitError: Rate limit exceeded
```

**Solutions:**

1. **Enable rate limiting handling:**
   ```yaml
   # config.yaml
   api:
     rate_limit:
       requests_per_minute: 50
       retry_after_rate_limit: true
   ```

2. **Reduce batch size:**
   ```bash
   customer-snapshot batch process files/ --batch-size 5
   ```

3. **Add delays between requests:**
   ```yaml
   # config.yaml
   api:
     request_delay: 1.0  # 1 second delay
   ```

### Issue: Authentication Error

**Symptoms:**
```bash
AuthenticationError: Invalid API key
```

**Solutions:**

1. **Verify API key:**
   ```bash
   curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
        https://api.anthropic.com/v1/messages
   ```

2. **Check key format:**
   ```bash
   echo $ANTHROPIC_API_KEY | wc -c  # Should be reasonable length
   echo $ANTHROPIC_API_KEY | head -c 20  # Should start with correct prefix
   ```

3. **Regenerate API key:**
   - Go to https://console.anthropic.com/
   - Create new API key
   - Update environment variable

## Docker Issues

### Issue: Docker Image Won't Start

**Symptoms:**
```bash
docker: Error response from daemon: container exited with non-zero status
```

**Solutions:**

1. **Check logs:**
   ```bash
   docker logs container_name
   ```

2. **Run interactively:**
   ```bash
   docker run -it --entrypoint /bin/bash \
     arthurfantaci/customer-snapshot-generator:latest
   ```

3. **Check environment variables:**
   ```bash
   docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
     arthurfantaci/customer-snapshot-generator:latest \
     env | grep ANTHROPIC
   ```

4. **Verify image integrity:**
   ```bash
   docker pull arthurfantaci/customer-snapshot-generator:latest
   docker run --rm arthurfantaci/customer-snapshot-generator:latest \
     customer-snapshot --version
   ```

### Issue: Volume Mount Problems

**Symptoms:**
- Files not accessible inside container
- Permission denied errors

**Solutions:**

1. **Check mount syntax:**
   ```bash
   # Correct syntax
   docker run -v $(pwd)/input:/app/data/input \
     arthurfantaci/customer-snapshot-generator:latest
   ```

2. **Fix permissions:**
   ```bash
   # Make files readable
   chmod -R 755 ./input/

   # Or run with user ID
   docker run --user $(id -u):$(id -g) -v $(pwd):/data \
     arthurfantaci/customer-snapshot-generator:latest
   ```

3. **Use absolute paths:**
   ```bash
   docker run -v /full/path/to/input:/app/data/input \
     arthurfantaci/customer-snapshot-generator:latest
   ```

## Memory and Resource Issues

### Issue: Out of Memory

**Symptoms:**
```bash
Killed
MemoryError
docker: container killed by OOM killer
```

**Solutions:**

1. **Increase Docker memory:**
   ```bash
   # In docker-compose.yml
   services:
     processor:
       mem_limit: 4g

   # Or command line
   docker run -m 4g arthurfantaci/customer-snapshot-generator:latest
   ```

2. **Optimize processing:**
   ```bash
   customer-snapshot process file.vtt \
     --optimize-memory \
     --chunk-size 100 \
     --stream
   ```

3. **Monitor resource usage:**
   ```bash
   docker stats container_name
   python monitor.py --interval 1
   ```

### Issue: Disk Space Error

**Symptoms:**
```bash
OSError: [Errno 28] No space left on device
```

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h
   du -sh ./output/
   ```

2. **Clean up temporary files:**
   ```bash
   customer-snapshot cleanup --temp-files
   rm -rf /tmp/customer_snapshot_*
   ```

3. **Use external storage:**
   ```bash
   # Mount external drive
   docker run -v /external/drive:/app/data/output \
     arthurfantaci/customer-snapshot-generator:latest
   ```

## Output and Format Issues

### Issue: Corrupted Output Files

**Symptoms:**
- Malformed markdown/HTML
- Incomplete JSON
- Binary data in text files

**Solutions:**

1. **Validate output format:**
   ```bash
   customer-snapshot validate-output output.md
   ```

2. **Regenerate with different format:**
   ```bash
   customer-snapshot process file.vtt --output-format json
   ```

3. **Check template syntax:**
   ```bash
   customer-snapshot validate-template templates/custom.md
   ```

### Issue: Missing Content Sections

**Symptoms:**
- Empty executive summary
- Missing action items
- Incomplete analysis

**Solutions:**

1. **Check input quality:**
   ```bash
   customer-snapshot analyze-input file.vtt
   ```

2. **Adjust analysis parameters:**
   ```yaml
   # config.yaml
   nlp:
     extract_entities: true
     sentiment_analysis: true
     min_content_length: 100
   ```

3. **Use different model:**
   ```bash
   customer-snapshot process file.vtt --model claude-3-opus-20240229
   ```

## Monitoring Issues

### Issue: Health Checks Failing

**Symptoms:**
```bash
❌ Health check failed: API connectivity
```

**Solutions:**

1. **Run detailed health check:**
   ```bash
   python healthcheck.py --verbose
   ```

2. **Check individual components:**
   ```bash
   customer-snapshot health --component api
   customer-snapshot health --component nlp
   customer-snapshot health --component filesystem
   ```

3. **Fix component issues:**
   ```bash
   # Fix API connectivity
   export ANTHROPIC_API_KEY="correct-key"

   # Fix NLP models
   python -m spacy download en_core_web_sm

   # Fix filesystem permissions
   chmod 755 /app/data/
   ```

### Issue: Monitoring Dashboard Not Working

**Symptoms:**
- Dashboard won't start
- No data displayed
- Connection errors

**Solutions:**

1. **Check dependencies:**
   ```bash
   pip install psutil prometheus-client
   ```

2. **Enable monitoring:**
   ```bash
   export ENABLE_MONITORING=true
   python monitoring_dashboard.py --mode status
   ```

3. **Check port availability:**
   ```bash
   netstat -tlnp | grep 8080
   ```

4. **Start with debug mode:**
   ```bash
   python monitoring_dashboard.py --mode interactive --debug
   ```

## Debug Tools

### Enable Debug Logging

```bash
# Maximum verbosity
export LOG_LEVEL=DEBUG
customer-snapshot process file.vtt -vvv

# Component-specific debugging
export DEBUG_NLP=true
export DEBUG_API=true
export DEBUG_PARSER=true
```

### Memory Profiling

```bash
# Profile memory usage
python -m memory_profiler optimize.py --input file.vtt

# Track memory over time
python monitor.py --track-memory --output memory_profile.json
```

### Performance Profiling

```bash
# Profile execution time
python -m cProfile -o profile.stats snapshot_automation/vtt_to_html_processor.py

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(10)
"
```

### Network Debugging

```bash
# Test API connectivity
curl -v -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/messages

# Check DNS resolution
nslookup api.anthropic.com

# Test with proxy (if applicable)
export https_proxy=http://proxy:8080
customer-snapshot process file.vtt
```

### File System Debugging

```bash
# Check file permissions
ls -la file.vtt
namei -l file.vtt

# Check file content
file file.vtt
hexdump -C file.vtt | head -20

# Test file operations
customer-snapshot validate file.vtt
```

## Getting Additional Help

### Diagnostic Information

When reporting issues, include:

```bash
# System information
customer-snapshot diagnose --full > diagnostic_info.txt

# Version information
customer-snapshot --version
python --version
docker --version

# Configuration
customer-snapshot config-info

# Recent logs
tail -100 ~/.customer_snapshot/logs/app.log
```

### Creating Bug Reports

Include in your bug report:

1. **Environment Details:**
   - Operating system
   - Python version
   - Installation method (pip/docker/source)

2. **Input Information:**
   - File size and format
   - Sample content (anonymized)
   - Command used

3. **Error Information:**
   - Complete error message
   - Stack trace
   - Log files

4. **Reproduction Steps:**
   - Minimal example
   - Expected vs actual behavior

### Community Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/arthurfantaci/customer-solution-snapshot-generator/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/arthurfantaci/customer-solution-snapshot-generator/discussions)
- **Documentation**: [Full documentation](https://arthurfantaci.github.io/customer-solution-snapshot-generator/)

---

*If you've tried all suggested solutions and still have issues, please create a GitHub issue with detailed information.*
