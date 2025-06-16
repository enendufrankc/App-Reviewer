import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, CheckCircle } from 'lucide-react';
import Layout from '../components/Layout';
import GoogleCredentialsSetup from '../components/GoogleCredentialsSetup';
import EligibilityCriteriaEditor from '../components/EligibilityCriteriaEditor';
import { useApp } from '../context/AppContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

const AdminPage: React.FC = () => {
  const { state } = useApp();
  const navigate = useNavigate();

  const canProceed = state.credentials.isConfigured && state.criteria.content.trim() !== '';

  return (
    <Layout>
      <div className="space-y-8">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Configuration</h1>
          <p className="mt-2 text-gray-600">
            Set up your system before evaluating Young Talents Programme applications
          </p>
        </div>

        {/* Configuration Steps */}
        <div className="space-y-6">
          {/* Step 1: Google Drive Credentials */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                state.credentials.isConfigured 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {state.credentials.isConfigured ? <CheckCircle className="h-4 w-4" /> : '1'}
              </div>
              <h2 className="text-xl font-semibold text-gray-900">
                Google Drive Credentials
              </h2>
            </div>
            <GoogleCredentialsSetup />
          </div>

          {/* Step 2: Eligibility Criteria */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                state.criteria.content.trim() !== '' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {state.criteria.content.trim() !== '' ? <CheckCircle className="h-4 w-4" /> : '2'}
              </div>
              <h2 className="text-xl font-semibold text-gray-900">
                YTP Eligibility Criteria
              </h2>
            </div>
            <EligibilityCriteriaEditor />
          </div>
        </div>

        {/* Next Steps */}
        <Card>
          <CardHeader>
            <CardTitle>Ready to Evaluate YTP Applications?</CardTitle>
            <CardDescription>
              {canProceed 
                ? 'Your system is configured and ready to process Young Talents Programme applications'
                : 'Complete the configuration steps above to proceed'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={() => navigate('/evaluate')}
              disabled={!canProceed}
              className="flex items-center gap-2"
            >
              <span>Start Evaluating Applications</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default AdminPage;
