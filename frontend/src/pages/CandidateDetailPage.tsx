import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import Layout from '../components/Layout';
import CandidateProfile from '../components/CandidateProfile';
import { useApp } from '../context/AppContext';
import { Button } from '../components/ui/button';

const CandidateDetailPage: React.FC = () => {
  const { email } = useParams<{ email: string }>();
  const navigate = useNavigate();
  const { state } = useApp();

  if (!email) {
    return (
      <Layout>
        <div className="text-center py-8">
          <p className="text-gray-500">Invalid candidate email</p>
          <Button onClick={() => navigate('/dashboard')} className="mt-4">
            Return to Dashboard
          </Button>
        </div>
      </Layout>
    );
  }

  const candidate = state.evaluation.results.find(
    c => c.email === decodeURIComponent(email)
  );

  if (!candidate) {
    return (
      <Layout>
        <div className="text-center py-8">
          <p className="text-gray-500">Candidate not found</p>
          <Button onClick={() => navigate('/dashboard')} className="mt-4">
            Return to Dashboard
          </Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Back Button */}
        <Button
          onClick={() => navigate('/dashboard')}
          variant="outline"
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Button>

        {/* Candidate Profile */}
        <CandidateProfile candidate={candidate} />
      </div>
    </Layout>
  );
};

export default CandidateDetailPage;
