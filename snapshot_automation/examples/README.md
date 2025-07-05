# Examples Directory

This directory contains example input files and output results to demonstrate the capabilities of the Customer Solution Snapshot Generator.

## 📁 Files

### Input Examples
- **`sample_input.vtt`** - Sample WebVTT transcript file showing the expected input format

### Output Examples  
- **`sample_output_markdown.md`** - Example output from `vtt_to_markdown_processor.py`
- **`sample_output_html.html`** - Example output from `vtt_to_html_processor.py`
- **`Percona_Kickoff_Transcript_Summary.md`** - Real-world example of a processed customer meeting transcript

## 🚀 Usage

To test the processors with the sample input:

```bash
# Generate Markdown output
python vtt_to_markdown_processor.py

# Generate HTML output  
python vtt_to_html_processor.py
```

Both processors are configured to use `sample_input.vtt` by default when run directly.

## 📊 What These Examples Show

### Input Format (VTT)
- Standard WebVTT format with timestamps
- Speaker identification in transcript text
- Natural conversation flow

### Markdown Output Features
- Clean transcript formatting
- Named entity extraction
- Topic identification
- Structured markdown for easy reading

### HTML Output Features  
- Same content as Markdown but in HTML format
- Ready for web display or embedding
- Maintains formatting and structure

### Real-World Example (Percona)
- Complete customer meeting analysis
- Project overview and goals
- Key discussion points extracted
- Action items and next steps
- Professional summary format

## 💡 Next Steps

Use these examples to:
1. Understand the expected input format
2. See what the output looks like
3. Test the processors with your own VTT files
4. Customize the processing for your specific needs

For more information, see the main [README](../README.md) and [User Guide](../docs/USER_GUIDE.md).