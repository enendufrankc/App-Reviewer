import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trash2, RefreshCw } from 'lucide-react';
import Layout from '../components/Layout';
import DashboardStats from '../components/DashboardStats';
import CandidatesTable from '../components/CandidatesTable';
import { useApp } from '../context/AppContext';
import { CandidateResult, EvaluationSession } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { evaluationService } from '../services/evaluationService';

const DashboardPage: React.FC = () => {
  const { state, user, showNotification } = useApp(); // Use 'user' instead of 'currentUser'
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<EvaluationSession[]>([]);
  const [allCandidates, setAllCandidates] = useState<CandidateResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleViewCandidate = (candidate: CandidateResult) => {
    navigate(`/candidate/${encodeURIComponent(candidate.email)}`);
  };

  const loadUserEvaluationHistory = async () => {
    if (!user?.email) return;
    
    setLoading(true);
    try {
      console.log(`📊 Loading evaluation history for ${user.email}`);
      
      // Get user sessions
      const sessionsResponse = await evaluationService.getUserSessions(user.email);
      const userSessions = sessionsResponse.data.sessions || [];
      setSessions(userSessions);
      
      console.log(`Found ${userSessions.length} sessions for user`);
      
      // Get candidates from all sessions
      const allCandidatesData: CandidateResult[] = [];
      const seenEmails = new Set<string>(); // Track unique emails
      
      for (const session of userSessions) {
        try {
          const candidatesResponse = await evaluationService.getSessionCandidates(session.id);
          const sessionCandidates = candidatesResponse.data.candidates || [];
          
          // Add session info to each candidate and deduplicate by email
          sessionCandidates.forEach((candidate: any) => {
            const candidateWithSession = {
              ...candidate,
              session_id: session.id,
              session_name: session.name
            };
            
            // Only add if we haven't seen this email before (keeps most recent evaluation)
            if (!seenEmails.has(candidate.email)) {
              seenEmails.add(candidate.email);
              allCandidatesData.push(candidateWithSession);
            } else {
              console.log(`🔄 Duplicate candidate email found: ${candidate.email} (using most recent evaluation)`);
            }
          });
        } catch (error) {
          console.error(`Error loading candidates for session ${session.id}:`, error);
        }
      }
      
      setAllCandidates(allCandidatesData);
      console.log(`📋 Loaded ${allCandidatesData.length} unique candidates`);
      
    } catch (error: any) {
      console.error('Error loading evaluation history:', error);
      showNotification('Failed to load evaluation history', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleClearAllData = async () => {
    if (!user?.email) return;
    
    if (!confirm('Are you sure you want to delete ALL your evaluation data? This action cannot be undone.')) {
      return;
    }
    
    setDeleting(true);
    try {
      console.log(`🗑️ Clearing all data for ${user.email}`);
      
      const response = await evaluationService.deleteUserSessions(user.email);
      
      showNotification(
        `Successfully deleted ${response.data.deleted_sessions} sessions and ${response.data.deleted_candidates} evaluations`, 
        'success'
      );
      
      // Clear local state
      setSessions([]);
      setAllCandidates([]);
      
    } catch (error: any) {
      console.error('Error clearing data:', error);
      const message = error.response?.data?.detail || 'Failed to clear evaluation data';
      showNotification(message, 'error');
    } finally {
      setDeleting(false);
    }
  };

  useEffect(() => {
    if (user?.email) {
      loadUserEvaluationHistory();
    }
  }, [user?.email]);

  // Calculate summary from loaded data
  const summary = {
    total_processed: allCandidates.length,
    accepted: allCandidates.filter(c => c.outcome === 'Accepted').length,
    rejected: allCandidates.filter(c => c.outcome === 'Rejected').length,
    errors: allCandidates.filter(c => c.outcome === 'Error').length,
  };

  if (!user) {
    return (
      <Layout>
        <div className="text-center py-8">
          <p className="text-gray-500">Please log in to view your evaluation history.</p>
          <Button onClick={() => navigate('/')} className="mt-4">
            Go to Login
          </Button>
        </div>
      </Layout>
    );
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-64">
          <LoadingSpinner size={48} />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">YTP Evaluation Dashboard</h1>
            <p className="mt-2 text-gray-600">
              Your Young Talents Programme evaluation history - {user.email}
            </p>
          </div>
          <div className="flex gap-3">
            <Button 
              onClick={loadUserEvaluationHistory} 
              variant="outline"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button 
              onClick={handleClearAllData} 
              variant="destructive"
              disabled={deleting || allCandidates.length === 0}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              {deleting ? 'Clearing...' : 'Clear All Data'}
            </Button>
          </div>
        </div>

        {/* Session Summary */}
        {sessions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Evaluation Sessions</CardTitle>
              <CardDescription>
                Your evaluation session history
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sessions.map((session) => (
                  <div key={session.id} className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900">{session.name}</h4>
                    <p className="text-sm text-gray-600">
                      {session.total_candidates || 0} candidates processed
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(session.created_at).toLocaleDateString()}
                    </p>
                    <div className="mt-2">
                      <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                        session.status === 'completed' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {session.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {allCandidates.length > 0 ? (
          <>
            {/* Statistics */}
            <DashboardStats 
              summary={summary} 
              candidates={allCandidates} 
            />

            {/* Results Table */}
            <CandidatesTable 
              candidates={allCandidates}
              onViewCandidate={handleViewCandidate}
            />
          </>
        ) : (
          <Card>
            <CardContent className="text-center py-8">
              <p className="text-gray-500 mb-4">No evaluation results found.</p>
              <Button onClick={() => navigate('/evaluate')}>
                Start Evaluating YTP Applications →
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default DashboardPage;
