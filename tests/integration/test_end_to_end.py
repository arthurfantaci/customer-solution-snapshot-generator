"""
Integration tests for end-to-end processing pipeline.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, Mock
import sys

# Add both src and snapshot_automation to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "snapshot_automation"))

from customer_snapshot.utils.config import Config
from customer_snapshot.utils.validators import validate_file_path, safe_file_write
from tests.fixtures import COMPLEX_VTT_CONTENT, SAMPLE_PROCESSED_OUTPUT


@pytest.mark.integration
class TestCompleteWorkflow:
    """Test complete workflow from VTT input to processed output."""

    def test_complete_vtt_processing_workflow(self, temp_dir, test_config):
        """Test the complete VTT processing workflow."""
        # Create input VTT file
        input_file = temp_dir / "test_input.vtt"
        input_file.write_text(COMPLEX_VTT_CONTENT)
        
        # Validate input file
        validated_path = validate_file_path(input_file, allowed_extensions=['.vtt'])
        assert validated_path == input_file
        
        # Mock the NLP processing to avoid requiring actual models
        with patch('spacy.load') as mock_spacy_load:
            mock_nlp = Mock()
            mock_doc = Mock()
            
            # Mock entities
            entities = [
                Mock(text="Percona", label_="ORG"),
                Mock(text="Qlik Cloud Platform", label_="PRODUCT"),
                Mock(text="ServiceNow", label_="PRODUCT")
            ]
            mock_doc.ents = entities
            
            # Mock noun chunks
            chunks = [
                Mock(text="data analytics"),
                Mock(text="booking data dashboard"),
                Mock(text="finance team")
            ]
            mock_doc.noun_chunks = chunks
            
            mock_nlp.return_value = mock_doc
            mock_spacy_load.return_value = mock_nlp
            
            # Import and test the main processing function
            from main_v2 import process_vtt
            
            output_file = temp_dir / "processed_output.md"
            
            # Process the VTT file
            process_vtt(str(input_file), str(output_file))
            
            # Verify output file was created
            assert output_file.exists()
            
            # Read and verify output content
            output_content = output_file.read_text()
            assert len(output_content) > 0
            
            # The output should contain some processing results
            # (exact content depends on the processing logic)
            assert isinstance(output_content, str)

    def test_error_handling_in_complete_workflow(self, temp_dir):
        """Test error handling throughout the complete workflow."""
        # Test with non-existent input file
        non_existent = temp_dir / "missing.vtt"
        output_file = temp_dir / "output.md"
        
        with pytest.raises((FileNotFoundError, RuntimeError)):
            from main_v2 import process_vtt
            process_vtt(str(non_existent), str(output_file))

    def test_configuration_integration(self, test_config):
        """Test integration with configuration system."""
        # Test that configuration is properly loaded and validated
        test_config.validate()
        
        # Test configuration properties
        assert test_config.anthropic_api_key == "test_key_123"
        assert test_config.debug is True
        assert test_config.max_file_size == 1048576  # 1MB for testing
        
        # Test directory creation
        assert test_config.input_dir.exists()
        assert test_config.output_dir.exists()

    def test_file_validation_integration(self, temp_dir, test_config):
        """Test integration of file validation with processing."""
        # Create files with different extensions
        vtt_file = temp_dir / "test.vtt"
        txt_file = temp_dir / "test.txt"
        invalid_file = temp_dir / "test.exe"
        
        vtt_file.write_text(COMPLEX_VTT_CONTENT)
        txt_file.write_text("Plain text content")
        invalid_file.write_text("Executable content")
        
        # Test VTT file validation
        validated_vtt = validate_file_path(vtt_file, ['.vtt'])
        assert validated_vtt == vtt_file
        
        # Test TXT file validation
        validated_txt = validate_file_path(txt_file, ['.txt'])
        assert validated_txt == txt_file
        
        # Test invalid file rejection
        with pytest.raises(ValueError, match="Invalid file type"):
            validate_file_path(invalid_file, ['.vtt', '.txt'])

    @patch('anthropic.Anthropic')
    def test_api_integration_mock(self, mock_anthropic_class, test_config):
        """Test API integration with mocked external services."""
        # Mock Anthropic client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Mocked Claude response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        # Test that we can create and use the client
        from anthropic import Anthropic
        client = Anthropic(api_key=test_config.anthropic_api_key)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=100,
            messages=[{"role": "user", "content": "Test message"}]
        )
        
        assert response.content[0].text == "Mocked Claude response"

    def test_secure_file_operations_integration(self, temp_dir):
        """Test integration of secure file operations."""
        # Test secure file writing with directory creation
        nested_output = temp_dir / "nested" / "deep" / "output.md"
        test_content = "# Test Output\n\nSecurely written content."
        
        # Should create directories and write file securely
        safe_file_write(nested_output, test_content)
        
        assert nested_output.exists()
        assert nested_output.read_text() == test_content
        
        # Verify parent directories were created
        assert nested_output.parent.exists()
        assert nested_output.parent.parent.exists()


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Test performance characteristics of the integrated system."""

    def test_large_file_processing_performance(self, temp_dir):
        """Test processing performance with larger files."""
        # Create a large VTT file
        large_content = "WEBVTT\n\n"
        for i in range(500):  # 500 captions
            start_time = f"00:{i//60:02d}:{i%60:02d}.000"
            end_time = f"00:{(i+1)//60:02d}:{(i+1)%60:02d}.000"
            large_content += f"{start_time} --> {end_time}\n"
            large_content += f"Speaker {i%3+1}: This is caption number {i} with technical terms like API, database, and analytics.\n\n"
        
        large_vtt = temp_dir / "large_transcript.vtt"
        large_vtt.write_text(large_content)
        
        # Test file validation performance
        import time
        start_time = time.time()
        validated_path = validate_file_path(large_vtt, ['.vtt'])
        validation_time = time.time() - start_time
        
        assert validated_path == large_vtt
        assert validation_time < 1.0  # Should validate in under 1 second

    def test_memory_usage_integration(self, temp_dir):
        """Test memory usage during processing."""
        # Create content that could cause memory issues if not handled properly
        content_parts = []
        content_parts.append("WEBVTT\n\n")
        
        for i in range(100):
            content_parts.append(f"00:{i//60:02d}:{i%60:02d}.000 --> 00:{(i+1)//60:02d}:{(i+1)%60:02d}.000\n")
            content_parts.append(f"Speaker: Long content repeated " * 50 + f" number {i}\n\n")
        
        large_content = "".join(content_parts)
        large_file = temp_dir / "memory_test.vtt"
        large_file.write_text(large_content)
        
        # Test that we can process without memory errors
        validated_path = validate_file_path(large_file, ['.vtt'])
        assert validated_path.exists()
        
        # Test reading the large file
        from customer_snapshot.utils.validators import safe_file_read
        content = safe_file_read(large_file)
        assert len(content) == len(large_content)


@pytest.mark.integration
class TestConfigurationWorkflow:
    """Test configuration system integration."""

    def test_environment_configuration_workflow(self, temp_dir):
        """Test complete configuration workflow with environment variables."""
        import os
        
        # Set up test environment
        env_file = temp_dir / ".env.test"
        env_file.write_text("""
ANTHROPIC_API_KEY=integration_test_key
VOYAGEAI_API_KEY=voyage_test_key
MAX_TOKENS=2000
TEMPERATURE=0.2
DEBUG=true
CHUNK_SIZE=300
        """.strip())
        
        # Load configuration from file
        config = Config.from_env_file(str(env_file))
        
        # Verify configuration loaded correctly
        assert config.anthropic_api_key == "integration_test_key"
        assert config.voyage_api_key == "voyage_test_key"
        assert config.max_tokens == 2000
        assert config.temperature == 0.2
        assert config.debug is True
        assert config.chunk_size == 300
        
        # Test validation
        config.validate()  # Should not raise

    def test_configuration_error_handling(self, temp_dir):
        """Test configuration error handling."""
        # Create config with missing required values
        env_file = temp_dir / ".env.invalid"
        env_file.write_text("""
# Missing ANTHROPIC_API_KEY
MAX_TOKENS=-100
TEMPERATURE=2.0
        """.strip())
        
        config = Config.from_env_file(str(env_file))
        
        # Should raise validation error
        with pytest.raises(ValueError, match="Configuration errors"):
            config.validate()

    def test_config_serialization_integration(self, test_config):
        """Test configuration serialization for debugging/monitoring."""
        config_dict = test_config.to_dict()
        
        # Verify structure
        assert isinstance(config_dict, dict)
        assert "default_model" in config_dict
        assert "api_keys_configured" in config_dict
        
        # Verify sensitive data is not included
        assert "anthropic_api_key" not in config_dict
        assert "voyage_api_key" not in config_dict
        
        # Verify API key status is indicated safely
        assert config_dict["api_keys_configured"]["anthropic"] is True