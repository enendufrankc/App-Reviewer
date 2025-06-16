import React, { useState, useCallback } from 'react';
import { Upload, CheckCircle, AlertCircle, FileText, TestTube } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { credentialsService } from '../services/credentialsService';
import { useApp } from '../context/AppContext';
import LoadingSpinner from './LoadingSpinner';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

const GoogleCredentialsSetup: React.FC = () => {
  const { state, dispatch, showNotification } = useApp();
  const [dragActive, setDragActive] = useState(false);
  const [validating, setValidating] = useState(false);
  const [testing, setTesting] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (file.type !== 'application/json') {
      showNotification('Please upload a JSON file', 'error');
      return;
    }

    setValidating(true);
    try {
      const response = await credentialsService.validateCredentials(file);
      if (response.data.valid) {
        showNotification('Credentials file is valid! Click Upload to save.', 'success');
        // Now upload the validated file
        await handleUpload(file);
      } else {
        showNotification('Invalid credentials file', 'error');
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to validate credentials';
      showNotification(message, 'error');
    } finally {
      setValidating(false);
    }
  }, [showNotification]);

  const handleUpload = async (file: File) => {
    dispatch({ type: 'SET_CREDENTIALS_LOADING', payload: true });
    try {
      const response = await credentialsService.uploadCredentials(file);
      dispatch({ type: 'SET_CREDENTIALS_INFO', payload: response.data.credentials_info });
      showNotification('Credentials uploaded successfully!', 'success');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to upload credentials';
      showNotification(message, 'error');
      dispatch({ type: 'SET_CREDENTIALS_LOADING', payload: false });
    }
  };

  const handleTestCredentials = async () => {
    setTesting(true);
    try {
      const response = await credentialsService.testCredentials();
      showNotification('Credentials test successful!', 'success');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Credentials test failed';
      showNotification(message, 'error');
    } finally {
      setTesting(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json']
    },
    multiple: false,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  });

  const loadCredentialsInfo = async () => {
    dispatch({ type: 'SET_CREDENTIALS_LOADING', payload: true });
    try {
      const response = await credentialsService.getCredentialsInfo();
      dispatch({ type: 'SET_CREDENTIALS_INFO', payload: response.data.credentials_info });
    } catch (error: any) {
      dispatch({ type: 'SET_CREDENTIALS_INFO', payload: null });
    }
  };

  React.useEffect(() => {
    loadCredentialsInfo();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Google Drive Credentials Setup
        </CardTitle>
        <CardDescription>
          Configure Google Drive access for downloading YTP applicant CVs and videos
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Setup Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Setup Instructions:</h4>
          <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
            <li>Create a Google Cloud Project</li>
            <li>Enable Google Drive API</li>
            <li>Create a Service Account</li>
            <li>Download the credentials.json file</li>
            <li>Share your Drive folder with the service account email</li>
          </ol>
        </div>

        {/* Current Status */}
        {state.credentials.info && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <h4 className="font-medium text-green-900">Credentials Configured</h4>
            </div>
            <div className="text-sm text-green-800 space-y-1">
              <p><strong>Project ID:</strong> {state.credentials.info.project_id}</p>
              <p><strong>Service Email:</strong> {state.credentials.info.client_email}</p>
              <p><strong>Last Modified:</strong> {new Date(state.credentials.info.last_modified).toLocaleString()}</p>
            </div>
            <Button
              onClick={handleTestCredentials}
              disabled={testing}
              className="mt-3"
              variant="outline"
              size="sm"
            >
              {testing ? (
                <>
                  <LoadingSpinner size={16} />
                  <span className="ml-2">Testing...</span>
                </>
              ) : (
                <>
                  <TestTube className="h-4 w-4 mr-2" />
                  Test Connection
                </>
              )}
            </Button>
          </div>
        )}

        {/* File Upload */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive || dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          {validating || state.credentials.loading ? (
            <div className="space-y-2">
              <LoadingSpinner size={32} />
              <p className="text-gray-600">
                {validating ? 'Validating credentials...' : 'Uploading credentials...'}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              <Upload className="h-12 w-12 text-gray-400 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900">
                  Drop your credentials.json file here
                </p>
                <p className="text-gray-600">or click to browse</p>
              </div>
            </div>
          )}
        </div>

        {!state.credentials.isConfigured && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              <p className="text-yellow-800">
                Google Drive credentials must be configured before evaluating YTP applications.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default GoogleCredentialsSetup;
