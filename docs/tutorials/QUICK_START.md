# Quick Start Tutorial

Get up and running with Customer Solution Snapshot Generator in 5 minutes!

## 🚀 Installation (1 minute)

### Option A: Using Docker (Recommended)
```bash
docker pull arthurfantaci/customer-snapshot-generator:latest
```

### Option B: Using pip
```bash
pip install customer-snapshot
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt
```

## 🔑 Setup API Key (30 seconds)

```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

Get your API key from: https://console.anthropic.com/

## 📝 Your First Analysis (2 minutes)

### 1. Prepare Your Transcript

Save this sample as `sample.vtt`:

```vtt
WEBVTT

00:00:00.000 --> 00:00:10.000
John (Customer): Hi, we're looking to migrate our on-premise infrastructure to the cloud.

00:00:10.000 --> 00:00:25.000
Sarah (Sales): Great! Can you tell me about your current setup and what's driving this migration?

00:00:25.000 --> 00:00:45.000
John (Customer): We have about 50 servers running various applications. Our main concerns are scalability and disaster recovery. We've had some downtime issues lately.

00:00:45.000 --> 00:01:05.000
Sarah (Sales): I understand. Cloud migration can definitely address those concerns. What's your timeline for this project?
```

### 2. Run the Analysis

```bash
# Using Docker
docker run -v $(pwd):/data -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  arthurfantaci/customer-snapshot-generator:latest \
  customer-snapshot process /data/sample.vtt

# Or using pip installation
customer-snapshot process sample.vtt
```

### 3. View Your Report

Open `sample_analysis.md` to see:

```markdown
# Customer Solution Snapshot

**Date**: 2024-01-15
**Participants**: John (Customer), Sarah (Sales)

## Executive Summary
Customer is seeking cloud migration solution for 50 on-premise servers,
driven by scalability needs and disaster recovery concerns...

## Key Discussion Points
1. **Current Infrastructure**: 50 on-premise servers
2. **Pain Points**: Downtime issues, scalability limitations
3. **Requirements**: Disaster recovery, improved scalability

## Next Steps
- Assess current infrastructure in detail
- Provide cloud migration proposal
- Discuss timeline and budget
```

## ✨ Next Steps (1 minute)

### Try Different Output Formats

```bash
# HTML format for web viewing
customer-snapshot process sample.vtt --output-format html

# JSON format for integration
customer-snapshot process sample.vtt --output-format json
```

### Process Multiple Files

```bash
# Process all VTT files in a directory
customer-snapshot batch process ./transcripts/
```

### Monitor Performance

```bash
# Check system health
customer-snapshot health

# View monitoring dashboard
python monitoring_dashboard.py
```

## 🎉 Congratulations!

You've successfully:
- ✅ Installed Customer Solution Snapshot Generator
- ✅ Configured your API key
- ✅ Processed your first transcript
- ✅ Generated an AI-powered analysis

## 📚 Learn More

- [Full User Guide](../USER_GUIDE.md)
- [Advanced Features](./ADVANCED_FEATURES.md)
- [API Documentation](../api/index.html)

## 💡 Tips

1. **Large Files**: For files >10MB, use `--optimize-memory`
2. **Batch Processing**: Use `--parallel` for faster processing
3. **Custom Output**: Create templates in `templates/` directory

Need help? Check our [Troubleshooting Guide](./TROUBLESHOOTING.md) or [create an issue](https://github.com/arthurfantaci/customer-solution-snapshot-generator/issues).