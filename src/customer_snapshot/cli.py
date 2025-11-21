"""
Command-line interface for Customer Solution Snapshot Generator.

This module provides a CLI interface for processing VTT transcripts
and generating customer solution snapshots.
"""

import sys
from pathlib import Path
from typing import Optional

import click

from .core.processor import TranscriptProcessor
from .utils.config import Config
from .utils.logging_config import get_logger, setup_logging


@click.group()
@click.option("--debug/--no-debug", default=False, help="Enable debug logging")
@click.option(
    "--config", type=click.Path(exists=True), help="Path to configuration file"
)
@click.pass_context
def cli(ctx: click.Context, debug: bool, config: Optional[str]) -> None:
    """
    Customer Solution Snapshot Generator CLI.

    Transform VTT transcripts into structured customer success snapshots
    using AI-powered NLP analysis.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Set up logging
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(log_level)

    # Load configuration
    if config:
        ctx.obj["config"] = Config.from_env_file(config)
    else:
        ctx.obj["config"] = Config.get_default()

    ctx.obj["logger"] = get_logger(__name__)

    if debug:
        ctx.obj["logger"].debug("Debug mode enabled")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (auto-generated if not specified)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "html"]),
    default="markdown",
    help="Output format",
)
@click.option(
    "--validate-only", is_flag=True, help="Only validate input file without processing"
)
@click.pass_context
def process(
    ctx: click.Context,
    input_file: Path,
    output: Optional[Path],
    format: str,
    validate_only: bool,
) -> None:
    """
    Process a VTT transcript file into a customer solution snapshot.

    INPUT_FILE: Path to the VTT transcript file to process.

    Examples:

        # Process with default settings
        customer-snapshot process transcript.vtt

        # Specify output file and format
        customer-snapshot process transcript.vtt -o output.html -f html

        # Validate file only
        customer-snapshot process transcript.vtt --validate-only
    """
    config = ctx.obj["config"]
    logger = ctx.obj["logger"]

    try:
        logger.info(f"Processing VTT file: {input_file}")

        # Initialize processor
        processor = TranscriptProcessor(config)

        if validate_only:
            # Only validate the input file
            from .io.vtt_reader import VTTReader

            reader = VTTReader(config)
            is_valid = reader.validate_vtt_format(input_file)

            if is_valid:
                click.echo(f"✅ VTT file is valid: {input_file}")
                metadata = reader.get_vtt_metadata(input_file)
                click.echo(f"   Captions: {metadata.get('total_captions', 'Unknown')}")
                click.echo(
                    f"   Duration: {metadata.get('duration_seconds', 'Unknown')} seconds"
                )
                click.echo(
                    f"   Speakers: {metadata.get('estimated_speakers', 'Unknown')}"
                )
            else:
                click.echo(f"❌ VTT file is invalid: {input_file}")
                sys.exit(1)
            return

        # Process the file
        output_path = processor.process_file(
            input_path=input_file, output_path=output, output_format=format
        )

        click.echo("✅ Processing completed successfully!")
        click.echo(f"   Output: {output_path}")

        # Show statistics
        stats = processor.get_processing_stats()
        click.echo(f"   Model: {stats.get('nlp_model', 'Unknown')}")
        click.echo(f"   Format: {format}")

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        click.echo(f"❌ Error: Input file not found: {input_file}", err=True)
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Processing failed: {type(e).__name__}: {e}")
        click.echo(f"❌ Processing failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def analyze(ctx: click.Context, input_file: Path) -> None:
    """
    Analyze a VTT file and extract metadata without full processing.

    INPUT_FILE: Path to the VTT transcript file to analyze.

    Examples:

        # Analyze VTT file
        customer-snapshot analyze transcript.vtt
    """
    config = ctx.obj["config"]
    logger = ctx.obj["logger"]

    try:
        logger.info(f"Analyzing VTT file: {input_file}")

        from .io.vtt_reader import VTTReader

        reader = VTTReader(config)

        # Get metadata
        metadata = reader.get_vtt_metadata(input_file)
        speakers = reader.extract_speakers(input_file)

        # Display analysis results
        click.echo(f"📊 Analysis Results for: {input_file}")
        click.echo(f"   File size: {metadata.get('file_size_bytes', 0):,} bytes")
        click.echo(f"   Total captions: {metadata.get('total_captions', 0)}")
        click.echo(f"   Duration: {metadata.get('duration_seconds', 0):.1f} seconds")
        click.echo(f"   Estimated speakers: {metadata.get('estimated_speakers', 0)}")

        if speakers:
            click.echo(f"   Speaker names: {', '.join(speakers)}")

        # Validate format
        is_valid = reader.validate_vtt_format(input_file)
        status_icon = "✅" if is_valid else "❌"
        click.echo(f"   Format valid: {status_icon}")

    except Exception as e:
        logger.error(f"Analysis failed: {type(e).__name__}: {e}")
        click.echo(f"❌ Analysis failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def config_info(ctx: click.Context) -> None:
    """
    Display current configuration information.

    Shows the current configuration settings being used,
    including API key status and processing parameters.
    """
    config = ctx.obj["config"]

    try:
        # Validate configuration
        config.validate()

        # Get safe configuration info (no sensitive data)
        config_dict = config.to_dict()

        click.echo("⚙️  Configuration Information:")
        click.echo(f"   Default model: {config_dict.get('default_model')}")
        click.echo(f"   Max tokens: {config_dict.get('max_tokens')}")
        click.echo(f"   Temperature: {config_dict.get('temperature')}")
        click.echo(f"   Chunk size: {config_dict.get('chunk_size')}")
        click.echo(
            f"   Max file size: {config_dict.get('max_file_size') // (1024 * 1024)}MB"
        )
        click.echo(f"   Debug mode: {config_dict.get('debug')}")

        # API key status
        api_status = config_dict.get("api_keys_configured", {})
        click.echo("   API Keys:")
        for service, configured in api_status.items():
            status_icon = "✅" if configured else "❌"
            click.echo(f"     {service}: {status_icon}")

    except ValueError as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="test_output.md",
    help="Output file for test",
)
@click.pass_context
def test(ctx: click.Context, output: Path) -> None:
    """
    Run a basic test to verify the system is working correctly.

    Creates a sample VTT file and processes it to verify that
    all components are functioning properly.
    """
    config = ctx.obj["config"]
    logger = ctx.obj["logger"]

    try:
        click.echo("🧪 Running system test...")

        # Create a test VTT file
        test_vtt_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Speaker 1: Welcome to the Qlik implementation meeting.

00:00:05.000 --> 00:00:10.000
Speaker 2: Thank you for joining. We'll discuss the project timeline and deliverables.

00:00:10.000 --> 00:00:15.000
Speaker 1: The main goal is to implement Qlik Cloud Platform for data analytics.
"""

        test_vtt_path = Path("test_input.vtt")
        test_vtt_path.write_text(test_vtt_content)

        logger.info("Created test VTT file")

        # Process the test file
        processor = TranscriptProcessor(config)
        result_path = processor.process_file(
            input_path=test_vtt_path, output_path=output, output_format="markdown"
        )

        # Clean up test file
        test_vtt_path.unlink()

        click.echo("✅ System test completed successfully!")
        click.echo(f"   Test output: {result_path}")
        click.echo("   All components are functioning correctly.")

    except Exception as e:
        # Clean up on error
        if Path("test_input.vtt").exists():
            Path("test_input.vtt").unlink()

        logger.error(f"System test failed: {type(e).__name__}: {e}")
        click.echo(f"❌ System test failed: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """
    Main entry point for the CLI application.

    This function is called when the package is run as a script
    or when the 'customer-snapshot' command is executed.
    """
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n⏹️  Operation cancelled by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
