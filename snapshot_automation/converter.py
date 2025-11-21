"""Simple VTT to Markdown converter for meeting transcripts.

This module provides a straightforward conversion utility that transforms WebVTT
transcript files into Markdown format, grouping dialogues by speaker with timestamps.
"""


def vtt_to_md(transcript: str, output_path: str) -> str:
    """Convert a WebVTT meeting transcript file to Markdown format.

    Processes a .vtt file to create a Markdown document with speaker-grouped
    dialogues. Each speaker's continuous dialogue is consolidated with start
    and end timestamps. Removes "WEBVTT" headers and redundant speaker labels.

    Args:
        transcript: Path to the input .vtt file to convert.
        output_path: Intended output path (note: currently unused, see Returns).

    Returns:
        The output_path parameter value (note: actual file is written to
        transcript path with .md extension).

    Raises:
        FileNotFoundError: If the transcript file doesn't exist.
        UnicodeDecodeError: If the file encoding is not UTF-8.
        IOError: If file cannot be read or written.

    Example:
        >>> output = vtt_to_md("meeting.vtt", "meeting.md")
        Reading from meeting.vtt
        Writing to meeting.md
        Successfully converted meeting.vtt to meeting.md
        >>> print(output)
        meeting.md

    Note:
        This function has a minor inconsistency: it creates the output file
        at transcript.replace('.vtt', '.md') but returns the output_path parameter.
    """
    vtt_path = transcript

    print(f"Reading from {vtt_path}")  # Debugging line

    with open(vtt_path, encoding="utf-8") as file:
        vtt_content = file.readlines()

    # Process and refine the content, omitting the "WEBVTT" redundant speaker information
    docs_md = []
    current_speaker = None
    current_start_timestamp = None
    current_end_timestamp = None
    speaker_dialogues = []

    for line in vtt_content:
        line = line.strip()

        # Skip "WEBVTT" and empty lines
        if not line or line == "WEBVTT":
            continue

        # If line contains a speaker's name
        if '"' in line and "-->" not in line:
            new_speaker = line.split('"')[1]  # Get the speaker's name

            # If we have a previous speaker's dialogues, append them to the output
            if current_speaker and new_speaker != current_speaker:
                docs_md.append("\n")
                # Add the previous speaker's name and timestamps to the output
                docs_md.append(
                    f'### "{current_speaker}" [{current_start_timestamp}-{current_end_timestamp}]'
                )
                docs_md.extend(
                    speaker_dialogues
                )  # Add the speaker's dialogues to the output
                speaker_dialogues = []  # Reset the speaker's dialogues
            current_speaker = new_speaker  # Update the current speaker
            current_start_timestamp = None  # Reset the start timestamp

        # If line contains a timestamped dialogue
        elif "-->" in line:
            timestamp_start, timestamp_end = line.split(
                " --> "
            )  # Get the start and end timestamps

            # Setting the start timestamp if it's the first dialogue of the current speaker
            if not current_start_timestamp:
                current_start_timestamp = timestamp_start  # Setting the start timestamp

            # Updating the end timestamp for every dialogue of the current speaker
            current_end_timestamp = timestamp_end

        # If it's a dialogue
        else:
            speaker_dialogues.append(
                line
            )  # Add the dialogue to the speaker's dialogues

    # Add the last speaker's dialogues to the output
    if current_speaker:
        docs_md.append("\n")
        docs_md.append(
            f'### "{current_speaker}" [{current_start_timestamp}-{current_end_timestamp}]'
        )
        docs_md.extend(speaker_dialogues)

    # Write to a .md file
    raw_md = vtt_path.replace(".vtt", ".md")

    print(f"Writing to {raw_md}")  # Debugging line
    with open(raw_md, "w", encoding="utf-8") as file:
        file.write("\n".join(docs_md))
    print(f"Successfully converted {vtt_path} to {output_path}")
    return output_path
