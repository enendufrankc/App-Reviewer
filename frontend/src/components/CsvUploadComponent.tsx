import React, { useState, useCallback } from 'react';
import { Upload, FileSpreadsheet, AlertCircle, CheckCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { evaluationService } from '../services/evaluationService';
import { useApp } from '../context/AppContext';
import LoadingSpinner from './LoadingSpinner';
import { EvaluationResults } from '../types';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';

interface CsvUploadComponentProps {
  onFileUploaded: (results: EvaluationResults) => void;
}

const CsvUploadComponent: React.FC<CsvUploadComponentProps> = ({ onFileUploaded }) => {
  const { showNotification } = useApp();
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStatus, setProcessingStatus] = useState('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.csv')) {
      showNotification('Please upload a CSV file', 'error');
      return;
    }

    if (file.size > 50 * 1024 * 1024) { // 50MB limit
      showNotification('File size must be less than 50MB', 'error');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setProcessingStatus('Uploading CSV file...');

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return 95;
          }
          return prev + 5;
        });
      }, 200);

      setProcessingStatus('Processing candidates...');
      const response = await evaluationService.evaluateCandidates(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setProcessingStatus('Evaluation completed!');
      
      showNotification(`Successfully processed ${response.data.summary.total_processed} YTP applications`, 'success');
      onFileUploaded(response.data);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to process candidates';
      showNotification(message, 'error');
      setProcessingStatus('Processing failed');
    } finally {
      setTimeout(() => {
        setUploading(false);
        setUploadProgress(0);
        setProcessingStatus('');
      }, 2000);
    }
  }, [showNotification, onFileUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: false,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileSpreadsheet className="h-5 w-5" />
          Upload YTP Application CSV
        </CardTitle>
        <CardDescription>
          Upload a CSV file containing Young Talents Programme application information for evaluation
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Requirements */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">CSV Requirements:</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-blue-800">
            <li><strong>Required column:</strong> "Email address"</li>
            <li><strong>Recommended columns:</strong> Name, CV URL, Video URL, Essay</li>
            <li><strong>File size:</strong> Maximum 50MB</li>
            <li><strong>Format:</strong> Standard CSV with headers</li>
          </ul>
        </div>

        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive || dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${uploading ? 'pointer-events-none opacity-50' : ''}`}
        >
          <input {...getInputProps()} />
          {uploading ? (
            <div className="space-y-4">
              <LoadingSpinner size={32} />
              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-900">{processingStatus}</p>
                <Progress value={uploadProgress} className="w-full max-w-md mx-auto" />
                <p className="text-sm text-gray-600">{uploadProgress}% completed</p>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <Upload className="h-12 w-12 text-gray-400 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900">
                  Drop your CSV file here
                </p>
                <p className="text-gray-600">or click to browse</p>
              </div>
            </div>
          )}
        </div>

        {/* Processing Info */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div className="text-sm text-yellow-800">
              <p className="font-medium mb-1">Processing Information:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Large files may take several minutes to process</li>
                <li>CVs and videos will be downloaded from Google Drive</li>
                <li>AI evaluation will be performed for each YTP applicant</li>
                <li>You'll be redirected to view results when complete</li>
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CsvUploadComponent;
