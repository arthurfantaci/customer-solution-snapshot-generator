"""
Output writing functionality for processed transcripts.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from customer_snapshot.utils.config import Config
from customer_snapshot.utils.validators import safe_file_write, sanitize_filename


logger = logging.getLogger(__name__)


class OutputWriter:
    """
    Writer for processed transcript output in various formats.

    Handles secure writing of processed content to different output formats
    including Markdown and HTML.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the output writer.

        Args:
            config: Configuration object
        """
        self.config = config
        logger.debug("OutputWriter initialized")

    def write_output(
        self,
        content: str,
        output_path: Union[str, Path],
        format_type: str = "markdown",
        metadata: Optional[dict[str, Any]] = None,
    ) -> Path:
        """
        Write processed content to output file.

        Args:
            content: Processed content to write
            output_path: Path for output file
            format_type: Output format ('markdown' or 'html')
            metadata: Optional metadata to include

        Returns:
            Path to the written output file

        Raises:
            ValueError: If format type is not supported
            PermissionError: If cannot write to output location
            OSError: If file system error occurs
        """
        try:
            # Validate and sanitize output path
            output_path = Path(output_path)
            sanitized_filename = sanitize_filename(output_path.name)
            safe_output_path = output_path.parent / sanitized_filename

            # Format content based on type
            formatted_content = self._format_content(content, format_type, metadata)

            # Write to file securely
            safe_file_write(safe_output_path, formatted_content)

            logger.info(f"Output written successfully: {safe_output_path}")
            return safe_output_path

        except Exception as e:
            logger.error(f"Failed to write output: {type(e).__name__}: {e}")
            raise

    def _format_content(
        self, content: str, format_type: str, metadata: Optional[dict[str, Any]] = None
    ) -> str:
        """
        Format content according to the specified type.

        Args:
            content: Raw content to format
            format_type: Target format ('markdown' or 'html')
            metadata: Optional metadata to include

        Returns:
            Formatted content string

        Raises:
            ValueError: If format type is not supported
        """
        if format_type.lower() == "markdown":
            return self._format_markdown(content, metadata)
        elif format_type.lower() == "html":
            return self._format_html(content, metadata)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def _format_markdown(
        self, content: str, metadata: Optional[dict[str, Any]] = None
    ) -> str:
        """
        Format content as Markdown.

        Args:
            content: Content to format
            metadata: Optional metadata

        Returns:
            Markdown-formatted content
        """
        # Build header with metadata
        header_parts = ["# Customer Solution Snapshot"]

        if metadata:
            header_parts.append("")
            header_parts.append("**Document Information:**")

            # Add generation timestamp
            header_parts.append(
                f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # Add metadata items
            for key, value in metadata.items():
                if key != "generated_at":
                    formatted_key = key.replace("_", " ").title()
                    header_parts.append(f"- **{formatted_key}:** {value}")

            header_parts.append("")
            header_parts.append("---")

        header_parts.append("")

        # Combine header with content
        header = "\n".join(header_parts)

        # Ensure content has proper Markdown structure
        formatted_content = self._enhance_markdown_structure(content)

        return f"{header}{formatted_content}"

    def _format_html(
        self, content: str, metadata: Optional[dict[str, Any]] = None
    ) -> str:
        """
        Format content as HTML.

        Args:
            content: Content to format
            metadata: Optional metadata

        Returns:
            HTML-formatted content
        """
        # Convert Markdown-like content to HTML
        html_content = self._markdown_to_html(content)

        # Build metadata section
        metadata_html = ""
        if metadata:
            metadata_items = []
            metadata_items.append(
                f"<li><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>"
            )

            for key, value in metadata.items():
                if key != "generated_at":
                    formatted_key = key.replace("_", " ").title()
                    metadata_items.append(
                        f"<li><strong>{formatted_key}:</strong> {value}</li>"
                    )

            metadata_html = f"""
            <div class="metadata">
                <h3>Document Information</h3>
                <ul>
                    {"".join(metadata_items)}
                </ul>
            </div>
            <hr>
            """

        # Create complete HTML document
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer Solution Snapshot</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .metadata {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .metadata ul {{ margin: 0; }}
        code {{ background: #f1f1f1; padding: 2px 4px; border-radius: 3px; }}
        blockquote {{ border-left: 4px solid #3498db; padding-left: 15px; margin-left: 0; }}
        hr {{ border: none; height: 1px; background: #ddd; margin: 30px 0; }}
    </style>
</head>
<body>
    <h1>Customer Solution Snapshot</h1>
    {metadata_html}
    {html_content}
</body>
</html>"""

        return html_template

    def _enhance_markdown_structure(self, content: str) -> str:
        """
        Enhance Markdown structure and formatting.

        Args:
            content: Raw content

        Returns:
            Enhanced Markdown content
        """
        lines = content.split("\n")
        enhanced_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                enhanced_lines.append("")
                continue

            # Enhance headers (simple heuristic)
            if any(
                keyword in line.lower()
                for keyword in [
                    "entities identified",
                    "topics discussed",
                    "summary",
                    "overview",
                ]
            ):
                if not line.startswith("#"):
                    line = f"## {line}"

            # Enhance lists
            if line.startswith("-") and not line.startswith("- "):
                line = f"- {line[1:].strip()}"

            enhanced_lines.append(line)

        return "\n".join(enhanced_lines)

    def _markdown_to_html(self, content: str) -> str:
        """
        Convert Markdown-like content to basic HTML.

        Args:
            content: Markdown content

        Returns:
            HTML content
        """
        lines = content.split("\n")
        html_lines = []
        in_list = False

        for line in lines:
            line = line.strip()

            if not line:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append("")
                continue

            # Headers
            if line.startswith("### "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith("## "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("# "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h1>{line[2:]}</h1>")

            # Lists
            elif line.startswith("- "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                # Handle bold text in list items
                list_content = line[2:]
                list_content = self._format_inline_markdown(list_content)
                html_lines.append(f"<li>{list_content}</li>")

            # Regular paragraphs
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                formatted_line = self._format_inline_markdown(line)
                html_lines.append(f"<p>{formatted_line}</p>")

        # Close any open lists
        if in_list:
            html_lines.append("</ul>")

        return "\n".join(html_lines)

    def _format_inline_markdown(self, text: str) -> str:
        """
        Format inline Markdown elements (bold, italic, etc.).

        Args:
            text: Text with Markdown formatting

        Returns:
            Text with HTML formatting
        """
        # Bold text (**text** or __text__)
        import re

        text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"__(.*?)__", r"<strong>\1</strong>", text)

        # Italic text (*text* or _text_)
        text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
        text = re.sub(r"_(.*?)_", r"<em>\1</em>", text)

        # Code (`text`)
        text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)

        return text

    def create_summary_report(
        self, processing_stats: dict[str, Any], output_path: Union[str, Path]
    ) -> Path:
        """
        Create a summary report of the processing operation.

        Args:
            processing_stats: Statistics from processing
            output_path: Path for the report

        Returns:
            Path to the created report
        """
        try:
            report_content = self._generate_summary_report(processing_stats)

            report_path = Path(output_path).parent / "processing_summary.md"
            safe_file_write(report_path, report_content)

            logger.info(f"Summary report created: {report_path}")
            return report_path

        except Exception as e:
            logger.error(f"Failed to create summary report: {e}")
            raise

    def _generate_summary_report(self, stats: dict[str, Any]) -> str:
        """
        Generate content for summary report.

        Args:
            stats: Processing statistics

        Returns:
            Report content as string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Processing Summary Report

**Generated:** {timestamp}

## Configuration Used

- **NLP Model:** {stats.get("nlp_model", "N/A")}
- **Chunk Size:** {stats.get("chunk_size", "N/A")}
- **Max Tokens:** {stats.get("max_tokens", "N/A")}

## Processing Results

- **Status:** Completed Successfully
- **Output Format:** {stats.get("output_format", "N/A")}
- **Processing Time:** {stats.get("processing_time", "N/A")}

## Quality Metrics

- **Text Quality:** {stats.get("text_quality", "N/A")}
- **Entity Extraction:** {stats.get("entities_found", 0)} entities identified
- **Topics Identified:** {stats.get("topics_found", 0)} topics found

---

*Report generated by Customer Solution Snapshot Generator*
"""

        return report


class OutputWritingError(Exception):
    """Custom exception for output writing errors."""

    pass
