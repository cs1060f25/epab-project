"""
Test Suite for preprocess_clean.py
"""
import pytest
import pandas as pd
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch
import csv

# Add datapipeline directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'datapipeline'))
import preprocess_clean


class TestCreateCompleteRows:
    """Unit Tests for create_complete_rows()"""
    
    @pytest.mark.unit
    def test_valid_label_filtering(self):
        """Test that only labels '0' and '1' are included and converted to int"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_file = f.name
            writer = csv.writer(f)
            writer.writerow(['sender', 'receiver', 'date', 'subject', 'body', 'label', 'urls', 'spam_flag'])
            writer.writerow(['sender1', 'receiver1', '2024-01-01', 'Subject 1', 'Body 1', '0', 'url1', '0'])
            writer.writerow(['sender2', 'receiver2', '2024-01-02', 'Subject 2', 'Body 2', '1', 'url2', '1'])
            writer.writerow(['sender3', 'receiver3', '2024-01-03', 'Subject 3', 'Body 3', '2', 'url3', '0'])
            writer.writerow(['sender4', 'receiver4', '2024-01-04', 'Subject 4', 'Body 4', 'invalid', 'url4', '0'])
        
        try:
            result = preprocess_clean.create_complete_rows(csv_file)
            
            assert len(result) == 2
            assert result[0]['label'] == 0
            assert result[1]['label'] == 1
            assert all(isinstance(row['label'], int) for row in result)
        finally:
            os.unlink(csv_file)
    
    @pytest.mark.unit
    def test_missing_fields_handling(self):
        """Test that missing optional fields default to empty string or 0"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_file = f.name
            writer = csv.writer(f)
            writer.writerow(['sender', 'receiver', 'date', 'subject', 'body', 'label'])
            writer.writerow(['sender1', 'receiver1', '2024-01-01', 'Subject 1', 'Body 1', '0'])
        
        try:
            result = preprocess_clean.create_complete_rows(csv_file)
            
            assert len(result) == 1
            assert result[0]['urls'] == ''
            assert result[0]['spam_flag'] == 0
            assert result[0]['sender'] == 'sender1'
        finally:
            os.unlink(csv_file)
    
    @pytest.mark.unit
    def test_field_extraction(self):
        """Test that all fields are extracted correctly, original_db = filename only"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_file = f.name
            writer = csv.writer(f)
            writer.writerow(['sender', 'receiver', 'date', 'subject', 'body', 'label', 'urls', 'spam_flag'])
            writer.writerow(['sender1', 'receiver1', '2024-01-01', 'Subject 1', 'Body 1', '1', 'url1,url2', '1'])
        
        try:
            result = preprocess_clean.create_complete_rows(csv_file)
            
            assert len(result) == 1
            row = result[0]
            assert row['sender'] == 'sender1'
            assert row['receiver'] == 'receiver1'
            assert row['date'] == '2024-01-01'
            assert row['subject'] == 'Subject 1'
            assert row['body'] == 'Body 1'
            assert row['label'] == 1
            assert row['urls'] == 'url1,url2'
            assert row['spam_flag'] == 1
            assert row['original_db'] == os.path.basename(csv_file)
        finally:
            os.unlink(csv_file)
    
    @pytest.mark.unit
    def test_empty_file(self):
        """Test that empty CSV with header only returns empty list"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_file = f.name
            writer = csv.writer(f)
            writer.writerow(['sender', 'receiver', 'date', 'subject', 'body', 'label', 'urls', 'spam_flag'])
        
        try:
            result = preprocess_clean.create_complete_rows(csv_file)
            
            assert result == []
        finally:
            os.unlink(csv_file)
    
    @pytest.mark.unit
    def test_large_fields(self):
        """Test that very large body field is processed without truncation"""
        large_body = 'A' * 1000000  # 1MB of text
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_file = f.name
            writer = csv.writer(f)
            writer.writerow(['sender', 'receiver', 'date', 'subject', 'body', 'label', 'urls', 'spam_flag'])
            writer.writerow(['sender1', 'receiver1', '2024-01-01', 'Subject 1', large_body, '0', '', '0'])
        
        try:
            result = preprocess_clean.create_complete_rows(csv_file)
            
            assert len(result) == 1
            assert len(result[0]['body']) == 1000000
            assert result[0]['body'] == large_body
        finally:
            os.unlink(csv_file)


class TestMain:
    """Integration Tests for main()"""
    
    @pytest.mark.integration
    def test_full_pipeline(self):
        """Test full pipeline: get files, process, create parquet, upload"""
        temp_dir = tempfile.mkdtemp()
        processed_dir = os.path.join(temp_dir, 'processed-dataset')
        os.makedirs(processed_dir, exist_ok=True)
        
        # Create test CSV files
        csv1 = create_test_csv(temp_dir, 'test1.csv', [
            ['sender1', 'receiver1', '2024-01-01', 'Subject 1', 'Body 1', '0', 'url1', '0']
        ])
        csv2 = create_test_csv(temp_dir, 'test2.csv', [
            ['sender2', 'receiver2', '2024-01-02', 'Subject 2', 'Body 2', '1', 'url2', '1']
        ])
        
        output_path = os.path.join(processed_dir, 'cleaned_dataset.parquet')
        
        try:
            with patch('preprocess_clean.dataloader.get_raw_files_local') as mock_get_files, \
                 patch('preprocess_clean.dataloader.upload_processed_files') as mock_upload:
                
                mock_get_files.return_value = [csv1, csv2]
                
                old_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    preprocess_clean.main()
                    
                    # Assert parquet was created
                    assert os.path.exists(output_path)
                    
                    # Assert parquet has correct schema
                    df = pd.read_parquet(output_path)
                    expected_columns = ['sender', 'receiver', 'date', 'subject', 'body', 'label', 'urls', 'spam_flag', 'original_db']
                    assert all(col in df.columns for col in expected_columns)
                    assert len(df) == 2
                    assert df['label'].dtype == 'int64'
                    
                    # Assert upload was called
                    mock_upload.assert_called_once()
                finally:
                    os.chdir(old_cwd)
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.mark.integration
    def test_skip_existing_output(self):
        """Test that existing parquet file skips processing but still uploads"""
        temp_dir = tempfile.mkdtemp()
        processed_dir = os.path.join(temp_dir, 'processed-dataset')
        os.makedirs(processed_dir, exist_ok=True)
        
        output_path = os.path.join(processed_dir, 'cleaned_dataset.parquet')
        
        # Create existing parquet file
        existing_df = pd.DataFrame([{'sender': 'existing', 'label': 0, 'body': 'test'}])
        existing_df.to_parquet(output_path, compression='snappy', engine='pyarrow')
        original_size = os.path.getsize(output_path)
        
        try:
            with patch('preprocess_clean.dataloader.get_raw_files_local') as mock_get_files, \
                 patch('preprocess_clean.dataloader.upload_processed_files') as mock_upload:
                
                mock_get_files.return_value = []
                
                # Change working directory temporarily
                old_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    preprocess_clean.main()
                    
                    # Assert file size unchanged (not reprocessed)
                    assert os.path.getsize(output_path) == original_size
                    
                    # Assert upload still called
                    mock_upload.assert_called_once()
                finally:
                    os.chdir(old_cwd)
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.mark.integration
    def test_multiple_files_consolidation(self):
        """Test that multiple CSV files are consolidated and original_db tracks source"""
        temp_dir = tempfile.mkdtemp()
        processed_dir = os.path.join(temp_dir, 'processed-dataset')
        os.makedirs(processed_dir, exist_ok=True)
        
        csv1 = create_test_csv(temp_dir, 'file1.csv', [
            ['sender1', 'receiver1', '2024-01-01', 'Subject 1', 'Body 1', '0', '', '0']
        ])
        csv2 = create_test_csv(temp_dir, 'file2.csv', [
            ['sender2', 'receiver2', '2024-01-02', 'Subject 2', 'Body 2', '1', '', '0']
        ])
        csv3 = create_test_csv(temp_dir, 'file3.csv', [
            ['sender3', 'receiver3', '2024-01-03', 'Subject 3', 'Body 3', '0', '', '0']
        ])
        
        output_path = os.path.join(processed_dir, 'cleaned_dataset.parquet')
        
        try:
            with patch('preprocess_clean.dataloader.get_raw_files_local') as mock_get_files, \
                 patch('preprocess_clean.dataloader.upload_processed_files') as mock_upload:
                
                mock_get_files.return_value = [csv1, csv2, csv3]
                
                old_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    preprocess_clean.main()
                    
                    df = pd.read_parquet(output_path)
                    assert len(df) == 3
                    
                    # Check original_db tracks source files
                    original_dbs = df['original_db'].unique().tolist()
                    assert 'file1.csv' in original_dbs
                    assert 'file2.csv' in original_dbs
                    assert 'file3.csv' in original_dbs
                finally:
                    os.chdir(old_cwd)
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.mark.integration
    def test_no_files_found(self):
        """Test that empty file list is handled gracefully"""
        temp_dir = tempfile.mkdtemp()
        processed_dir = os.path.join(temp_dir, 'processed-dataset')
        os.makedirs(processed_dir, exist_ok=True)
        
        output_path = os.path.join(processed_dir, 'cleaned_dataset.parquet')
        
        try:
            with patch('preprocess_clean.dataloader.get_raw_files_local') as mock_get_files, \
                 patch('preprocess_clean.dataloader.upload_processed_files') as mock_upload:
                
                mock_get_files.return_value = []
                
                old_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    preprocess_clean.main()
                    
                    # Should create empty DataFrame or handle gracefully
                    if os.path.exists(output_path):
                        df = pd.read_parquet(output_path)
                        assert len(df) == 0
                    
                    mock_upload.assert_called_once()
                finally:
                    os.chdir(old_cwd)
        finally:
            shutil.rmtree(temp_dir)


class TestEdgeCases:
    """Edge Cases Tests"""
    
    @pytest.mark.unit
    def test_malformed_csv(self):
        """Test that malformed CSV with inconsistent column counts raises exception"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_file = f.name
            writer = csv.writer(f)
            # Header has 'label' as 6th column, but row only has 3 columns
            writer.writerow(['sender', 'receiver', 'date', 'subject', 'body', 'label'])
            writer.writerow(['sender1', 'receiver1', '2024-01-01'])  # Missing columns including 'label'
        
        try:
            # This should raise KeyError when trying to access row_dict['label']
            with pytest.raises(KeyError):
                preprocess_clean.create_complete_rows(csv_file)
        finally:
            os.unlink(csv_file)
    
    @pytest.mark.integration
    def test_gcs_upload_failure(self):
        """Test that GCS upload failure logs error but local file is still created"""
        temp_dir = tempfile.mkdtemp()
        processed_dir = os.path.join(temp_dir, 'processed-dataset')
        os.makedirs(processed_dir, exist_ok=True)
        
        csv1 = create_test_csv(temp_dir, 'test1.csv', [
            ['sender1', 'receiver1', '2024-01-01', 'Subject 1', 'Body 1', '0', '', '0']
        ])
        
        output_path = os.path.join(processed_dir, 'cleaned_dataset.parquet')
        
        try:
            with patch('preprocess_clean.dataloader.get_raw_files_local') as mock_get_files, \
                 patch('preprocess_clean.dataloader.upload_processed_files') as mock_upload:
                
                mock_get_files.return_value = [csv1]
                mock_upload.side_effect = Exception("GCS upload failed")
                
                old_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    # Should raise exception but local file should exist
                    with pytest.raises(Exception):
                        preprocess_clean.main()
                    
                    # Local file should still be created
                    assert os.path.exists(output_path)
                finally:
                    os.chdir(old_cwd)
        finally:
            shutil.rmtree(temp_dir)


# Test Utilities

def create_test_csv(directory, filename, rows):
    """Generate temporary CSV files for testing"""
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sender', 'receiver', 'date', 'subject', 'body', 'label', 'urls', 'spam_flag'])
        for row in rows:
            writer.writerow(row)
    return filepath


def mock_dataloader():
    """Mock GCS operations for testing"""
    return {
        'get_raw_files_local': Mock(return_value=[]),
        'upload_processed_files': Mock()
    }


def cleanup_test_files(directory):
    """Cleanup test files and directories"""
    if os.path.exists(directory):
        shutil.rmtree(directory)

