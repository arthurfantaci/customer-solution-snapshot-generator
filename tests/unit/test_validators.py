"""
Unit tests for validation utilities.
"""

from unittest.mock import patch

import pytest

from customer_snapshot.utils.validators import (
    create_safe_directory,
    get_safe_output_path,
    safe_file_read,
    safe_file_write,
    sanitize_filename,
    validate_file_path,
)


class TestValidateFilePath:
    """Test cases for file path validation."""

    def test_validate_valid_vtt_file(self, sample_vtt_file):
        """Test validation of valid VTT file."""
        result = validate_file_path(sample_vtt_file, allowed_extensions=[".vtt"])
        assert result == sample_vtt_file
        assert result.exists()

    def test_validate_file_not_found(self, temp_dir):
        """Test validation with non-existent file."""
        non_existent = temp_dir / "missing.vtt"

        with pytest.raises(FileNotFoundError, match="File not found"):
            validate_file_path(non_existent)

    def test_validate_invalid_extension(self, temp_dir):
        """Test validation with invalid file extension."""
        invalid_file = temp_dir / "test.exe"
        invalid_file.write_text("test content")

        with pytest.raises(ValueError, match="Invalid file type"):
            validate_file_path(invalid_file, allowed_extensions=[".vtt", ".txt"])

    def test_validate_file_too_large(self, temp_dir):
        """Test validation with file that exceeds size limit."""
        large_file = temp_dir / "large.vtt"
        # Create a file that exceeds 1KB limit
        large_file.write_text("x" * 2000)

        with pytest.raises(ValueError, match="File too large"):
            validate_file_path(large_file, max_size=1024)

    def test_validate_directory_instead_of_file(self, temp_dir):
        """Test validation when path points to directory."""
        with pytest.raises(ValueError, match="Path is not a file"):
            validate_file_path(temp_dir)

    def test_validate_with_default_extensions(self, temp_dir):
        """Test validation with default allowed extensions."""
        for ext in [".vtt", ".txt", ".md", ".html"]:
            test_file = temp_dir / f"test{ext}"
            test_file.write_text("test content")

            # Should not raise exception
            result = validate_file_path(test_file)
            assert result == test_file


class TestSafeFileRead:
    """Test cases for safe file reading."""

    def test_safe_file_read_success(self, sample_vtt_file):
        """Test successful file reading."""
        content = safe_file_read(sample_vtt_file)

        assert "WEBVTT" in content
        assert "Speaker 1" in content
        assert len(content) > 0

    def test_safe_file_read_with_encoding(self, temp_dir):
        """Test file reading with specific encoding."""
        test_file = temp_dir / "utf8.txt"
        test_content = "Test content with special chars: éñ中文"
        test_file.write_text(test_content, encoding="utf-8")

        content = safe_file_read(test_file, encoding="utf-8")
        assert content == test_content

    def test_safe_file_read_invalid_encoding(self, temp_dir):
        """Test file reading with invalid encoding."""
        test_file = temp_dir / "binary.txt"
        test_file.write_bytes(b"\x80\x81\x82\x83")  # Invalid UTF-8

        with pytest.raises(ValueError, match="Invalid file encoding"):
            safe_file_read(test_file, encoding="utf-8")

    def test_safe_file_read_file_not_found(self, temp_dir):
        """Test file reading with non-existent file."""
        non_existent = temp_dir / "missing.txt"

        with pytest.raises(FileNotFoundError):
            safe_file_read(non_existent)


class TestSafeFileWrite:
    """Test cases for safe file writing."""

    def test_safe_file_write_success(self, temp_dir):
        """Test successful file writing."""
        output_file = temp_dir / "output.txt"
        test_content = "Test output content"

        safe_file_write(output_file, test_content)

        assert output_file.exists()
        assert output_file.read_text() == test_content

    def test_safe_file_write_creates_directories(self, temp_dir):
        """Test that file writing creates parent directories."""
        nested_file = temp_dir / "nested" / "deep" / "output.txt"
        test_content = "Nested file content"

        safe_file_write(nested_file, test_content)

        assert nested_file.exists()
        assert nested_file.read_text() == test_content

    def test_safe_file_write_with_encoding(self, temp_dir):
        """Test file writing with specific encoding."""
        output_file = temp_dir / "utf8_output.txt"
        test_content = "Content with special chars: éñ中文"

        safe_file_write(output_file, test_content, encoding="utf-8")

        assert output_file.read_text(encoding="utf-8") == test_content

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_safe_file_write_permission_error(self, mock_open_func, temp_dir):
        """Test file writing with permission error."""
        output_file = temp_dir / "protected.txt"

        with pytest.raises(PermissionError):
            safe_file_write(output_file, "content")


class TestGetSafeOutputPath:
    """Test cases for safe output path generation."""

    def test_get_safe_output_path_default_suffix(self, temp_dir):
        """Test output path generation with default suffix."""
        input_file = temp_dir / "input.vtt"

        output_path = get_safe_output_path(input_file)

        assert output_path.parent == temp_dir
        assert output_path.name == "input_processed.vtt"

    def test_get_safe_output_path_custom_suffix(self, temp_dir):
        """Test output path generation with custom suffix."""
        input_file = temp_dir / "transcript.vtt"

        output_path = get_safe_output_path(input_file, suffix="_formatted")

        assert output_path.name == "transcript_formatted.vtt"

    def test_get_safe_output_path_no_extension(self, temp_dir):
        """Test output path generation for file without extension."""
        input_file = temp_dir / "README"

        output_path = get_safe_output_path(input_file)

        assert output_path.name == "README_processed"


class TestSanitizeFilename:
    """Test cases for filename sanitization."""

    def test_sanitize_normal_filename(self):
        """Test sanitization of normal filename."""
        filename = "normal_file-123.txt"
        result = sanitize_filename(filename)
        assert result == "normal_file-123.txt"

    def test_sanitize_filename_with_dangerous_chars(self):
        """Test sanitization removes dangerous characters."""
        filename = "file/with\\dangerous:chars*?.txt"
        result = sanitize_filename(filename)
        assert "/" not in result
        assert "\\" not in result
        assert ":" not in result
        assert "*" not in result
        assert "?" not in result

    def test_sanitize_hidden_file(self):
        """Test sanitization of hidden files."""
        filename = ".hidden"
        result = sanitize_filename(filename)
        assert result == "safe_.hidden"

    def test_sanitize_current_directory_reference(self):
        """Test sanitization of current directory reference."""
        filename = "."
        result = sanitize_filename(filename)
        assert result == "safe_."

    def test_sanitize_parent_directory_reference(self):
        """Test sanitization of parent directory reference."""
        filename = ".."
        result = sanitize_filename(filename)
        assert result == "safe_.."

    def test_sanitize_empty_filename(self):
        """Test sanitization of empty filename."""
        filename = ""
        result = sanitize_filename(filename)
        assert result == "safe_"

    def test_sanitize_unicode_filename(self):
        """Test sanitization preserves alphanumeric unicode characters."""
        filename = "файл123测试.txt"
        result = sanitize_filename(filename)
        # Should preserve alphanumeric characters and allowed punctuation
        assert "123" in result
        assert ".txt" in result


class TestCreateSafeDirectory:
    """Test cases for safe directory creation."""

    def test_create_safe_directory_success(self, temp_dir):
        """Test successful directory creation."""
        new_dir = temp_dir / "new_directory"

        result = create_safe_directory(new_dir)

        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_safe_directory_nested(self, temp_dir):
        """Test creation of nested directories."""
        nested_dir = temp_dir / "level1" / "level2" / "level3"

        result = create_safe_directory(nested_dir)

        assert result == nested_dir
        assert nested_dir.exists()

    def test_create_safe_directory_already_exists(self, temp_dir):
        """Test directory creation when directory already exists."""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()

        # Should not raise exception
        result = create_safe_directory(existing_dir)
        assert result == existing_dir

    @patch("pathlib.Path.mkdir", side_effect=PermissionError("Permission denied"))
    def test_create_safe_directory_permission_error(self, mock_mkdir, temp_dir):
        """Test directory creation with permission error."""
        new_dir = temp_dir / "protected"

        with pytest.raises(PermissionError):
            create_safe_directory(new_dir)
