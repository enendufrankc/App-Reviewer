import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import Layout from '../components/Layout';
import CsvUploadComponent from '../components/CsvUploadComponent';
import ProcessingStatus from '../components/ProcessingStatus';
import { useApp } from '../context/AppContext';
import { EvaluationResults } from '../types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';

const EvaluatePage: React.FC = () => {
  const { state, dispatch, user } = useApp();
  const navigate = useNavigate();
  const [results, setResults] = useState<EvaluationResults | null>(null);

  const handleFileUploaded = (evaluationResults: EvaluationResults) => {
    setResults(evaluationResults);
    dispatch({
      type: 'SET_EVALUATION_RESULTS',
      payload: {
        results: evaluationResults.results,
        summary: evaluationResults.summary
      }
    });
  };

  const handleViewDashboard = () => {
    navigate('/dashboard');
  };

  const isSystemReady = state.credentials.isConfigured && state.criteria.content.trim() !== '';

  // Show login message but don't redirect automatically
  if (!user?.email) {
    return (
      <Layout>
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">Please log in to access the evaluation system.</p>
          <Button onClick={() => navigate('/')} className="mt-4">
            Go to Login
          </Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Evaluate YTP Applications</h1>
          <p className="mt-2 text-gray-600">
            Upload a CSV file to automatically evaluate Young Talents Programme applications using AI
          </p>
          <p className="text-sm text-blue-600 font-medium">
            Logged in as: {user.email}
          </p>
        </div>

        {/* System Status Check */}
        {!isSystemReady && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-yellow-800">
                <AlertCircle className="h-5 w-5" />
                Configuration Required
              </CardTitle>
              <CardDescription>
                Please complete the admin configuration before evaluating YTP applications
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                {!state.credentials.isConfigured && (
                  <div className="flex items-center gap-2 text-red-600">
                    <AlertCircle className="h-4 w-4" />
                    <span>Google Drive credentials not configured</span>
                  </div>
                )}
                {state.criteria.content.trim() === '' && (
                  <div className="flex items-center gap-2 text-red-600">
                    <AlertCircle className="h-4 w-4" />
                    <span>YTP eligibility criteria not defined</span>
                  </div>
                )}
              </div>
              <Button
                onClick={() => navigate('/admin')}
                className="mt-4"
                variant="outline"
              >
                Go to Admin Configuration →
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Main Content */}
        {isSystemReady && (
          <div className="space-y-6">
            {/* Upload Section */}
            {!results && (
              <CsvUploadComponent onFileUploaded={handleFileUploaded} />
            )}

            {/* Results Section */}
            {results && (
              <ProcessingStatus 
                results={results} 
                onViewDashboard={handleViewDashboard}
              />
            )}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default EvaluatePage;
