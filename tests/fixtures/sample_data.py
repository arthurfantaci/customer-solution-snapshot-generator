"""
Sample data fixtures for testing.
"""

# Sample VTT content for different test scenarios
SIMPLE_VTT_CONTENT = """WEBVTT

00:00:01.000 --> 00:00:05.000
Speaker 1: Hello world.

00:00:05.000 --> 00:00:10.000
Speaker 2: This is a test.
"""

COMPLEX_VTT_CONTENT = """WEBVTT

00:00:01.000 --> 00:00:05.000
John Smith: Welcome to the Percona Qlik implementation kickoff meeting.

00:00:05.000 --> 00:00:15.000
Sarah Johnson: Thank you for joining us. Today we'll discuss the Qlik Cloud Platform implementation for data analytics.

00:00:15.000 --> 00:00:25.000
John Smith: Our primary goal is to create a booking data dashboard for the finance team.

00:00:25.000 --> 00:00:35.000
Sarah Johnson: We also need to resolve the ServiceNow data connector issues that have been ongoing.

00:00:35.000 --> 00:00:45.000
John Smith: The project timeline is July 14-26, 2024, with 80 hours split into two phases.

00:00:45.000 --> 00:00:55.000
Sarah Johnson: Phase 1 will focus on infrastructure setup and basic dashboard creation.

00:00:55.000 --> 00:01:05.000
John Smith: Phase 2 will include advanced analytics, training materials, and data catalog preparation.

00:01:05.000 --> 00:01:15.000
Sarah Johnson: We'll need to ensure proper data governance and security compliance throughout.

00:01:15.000 --> 00:01:25.000
John Smith: The ROI metrics will include reduced reporting time and improved decision-making speed.
"""

# Sample processed text outputs
SAMPLE_PROCESSED_OUTPUT = """# Meeting Transcript Summary

**Participants:** John Smith, Sarah Johnson

## Key Discussion Points

The meeting focused on the Percona Qlik implementation project. Key objectives include:

- Implementing Qlik Cloud Platform for data analytics
- Creating booking data dashboard for finance team
- Resolving ServiceNow data connector issues
- Completing project in two phases (July 14-26, 2024)

## Technical Terms Identified
- Qlik Cloud Platform
- ServiceNow
- data analytics
- data dashboard
- data governance
- ROI metrics

## Project Timeline
- **Duration:** July 14-26, 2024
- **Total Hours:** 80 hours
- **Phase 1:** Infrastructure and basic dashboard
- **Phase 2:** Advanced analytics and training

## Expected Outcomes
- Reduced reporting time
- Improved decision-making speed
- Enhanced data governance
"""

# Sample entities and noun phrases for NLP testing
SAMPLE_ENTITIES = [
    {"text": "Percona", "label": "ORG"},
    {"text": "Qlik Cloud Platform", "label": "PRODUCT"},
    {"text": "ServiceNow", "label": "PRODUCT"},
    {"text": "July 14-26, 2024", "label": "DATE"},
    {"text": "John Smith", "label": "PERSON"},
    {"text": "Sarah Johnson", "label": "PERSON"},
]

SAMPLE_NOUN_PHRASES = [
    "data analytics",
    "booking data dashboard",
    "finance team",
    "data connector issues",
    "project timeline",
    "infrastructure setup",
    "training materials",
    "data catalog",
    "data governance",
    "security compliance",
]

# Sample technical terms
SAMPLE_TECHNICAL_TERMS = [
    "Qlik Cloud Platform",
    "ServiceNow",
    "data analytics",
    "dashboard",
    "API",
    "data connector",
    "ETL",
    "business intelligence",
    "data governance",
    "ROI metrics",
]

# Invalid VTT content for error testing
INVALID_VTT_CONTENT = """This is not a valid VTT file
It's missing the WEBVTT header
And proper timestamp formatting
"""

MALFORMED_VTT_CONTENT = """WEBVTT

INVALID_TIMESTAMP --> 00:00:05.000
Speaker: This has invalid timestamps.

00:00:05.000 --> INVALID_END_TIME
Speaker: This also has invalid timestamps.
"""

# Large content for performance testing
LARGE_VTT_CONTENT = """WEBVTT

""" + "\n".join(
    [
        f"00:{i:02d}:{(i * 5) % 60:02d}.000 --> 00:{i:02d}:{((i * 5) + 5) % 60:02d}.000\nSpeaker {i % 3 + 1}: This is a long transcript entry number {i} with various technical terms and business discussions."
        for i in range(100)
    ]
)

# Mock API responses
MOCK_CLAUDE_RESPONSE = {
    "content": [
        {
            "text": "This is a test response from Claude API containing analysis of the transcript."
        }
    ],
    "usage": {"input_tokens": 100, "output_tokens": 50},
}

MOCK_VOYAGE_EMBEDDINGS = [
    [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dimensional embedding
]

# Configuration test data
TEST_ENV_VARS = {
    "ANTHROPIC_API_KEY": "test_anthropic_key_123",
    "VOYAGEAI_API_KEY": "test_voyage_key_456",
    "TAVILY_API_KEY": "test_tavily_key_789",
    "DEFAULT_MODEL": "claude-3-5-sonnet-20240620",
    "MAX_TOKENS": "2000",
    "TEMPERATURE": "0.1",
    "MAX_FILE_SIZE": "1048576",  # 1MB
    "CHUNK_SIZE": "300",
    "DEBUG": "true",
    "LOG_LEVEL": "DEBUG",
}

# Error scenarios for testing
ERROR_SCENARIOS = {
    "file_not_found": {"path": "/nonexistent/file.vtt", "error": "FileNotFoundError"},
    "invalid_extension": {"path": "/tmp/test.txt", "error": "ValueError"},
    "file_too_large": {
        "size": 100 * 1024 * 1024,  # 100MB
        "error": "ValueError",
    },
    "permission_denied": {"path": "/root/protected.vtt", "error": "PermissionError"},
}
