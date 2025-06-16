import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import DashboardStats from '../components/DashboardStats';
import CandidatesTable from '../components/CandidatesTable';
import { useApp } from '../context/AppContext';
import { CandidateResult } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';

const DashboardPage: React.FC = () => {
  const { state } = useApp();
  const navigate = useNavigate();

  const handleViewCandidate = (candidate: CandidateResult) => {
    // Navigate to candidate detail page
    navigate(`/candidate/${encodeURIComponent(candidate.email)}`);
  };

  // If no evaluation results, redirect to evaluate page
  useEffect(() => {
    if (!state.evaluation.results.length && !state.evaluation.loading) {
      navigate('/evaluate');
    }
  }, [state.evaluation.results.length, state.evaluation.loading, navigate]);

  if (state.evaluation.loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-64">
          <LoadingSpinner size={48} />
        </div>
      </Layout>
    );
  }

  if (!state.evaluation.summary) {
    return (
      <Layout>
        <div className="text-center py-8">
          <p className="text-gray-500">No evaluation results found.</p>
          <button
            onClick={() => navigate('/evaluate')}
            className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            Start Evaluating YTP Applications →
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">YTP Evaluation Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Overview of Young Talents Programme application evaluation results
          </p>
        </div>

        {/* Statistics */}
        <DashboardStats 
          summary={state.evaluation.summary} 
          candidates={state.evaluation.results} 
        />

        {/* Results Table */}
        <CandidatesTable 
          candidates={state.evaluation.results}
          onViewCandidate={handleViewCandidate}
        />
      </div>
    </Layout>
  );
};

export default DashboardPage;
