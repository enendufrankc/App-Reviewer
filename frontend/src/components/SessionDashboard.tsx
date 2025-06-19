import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { evaluationService } from '../services/evaluationService';
import { EvaluationSession } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Calendar, Users, CheckCircle, XCircle, AlertCircle, Clock } from 'lucide-react';

const SessionDashboard: React.FC = () => {
  const { userEmail } = useUser();
  const [sessions, setSessions] = useState<EvaluationSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, [userEmail]);

  const loadSessions = async () => {
    if (!userEmail) return;
    
    try {
      const response = await evaluationService.getUserSessions(userEmail);
      setSessions(response.data.sessions);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'completed': return 'default';
      case 'processing': return 'secondary';
      case 'failed': return 'destructive';
      default: return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'processing': return <Clock className="h-4 w-4" />;
      case 'failed': return <XCircle className="h-4 w-4" />;
      default: return <AlertCircle className="h-4 w-4" />;
    }
  };

  if (loading) {
    return <div>Loading sessions...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Your Evaluation Sessions</h2>
        <p className="text-gray-600">Track and manage your candidate evaluation sessions</p>
      </div>

      <div className="grid gap-4">
        {sessions.map((session) => (
          <Card key={session.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  {session.name}
                </CardTitle>
                <Badge variant={getStatusBadgeVariant(session.status)} className="flex items-center gap-1">
                  {getStatusIcon(session.status)}
                  {session.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="font-medium">Total</div>
                    <div>{session.total_candidates}</div>
                  </div>
                  <div>
                    <div className="font-medium">Accepted</div>
                    <div className="text-green-600">{session.accepted_count}</div>
                  </div>
                  <div>
                    <div className="font-medium">Rejected</div>
                    <div className="text-red-600">{session.rejected_count}</div>
                  </div>
                  <div>
                    <div className="font-medium">Errors</div>
                    <div className="text-yellow-600">{session.error_count}</div>
                  </div>
                </div>

                {session.status === 'processing' && (
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Progress (Batch {session.current_batch}/{session.total_batches})</span>
                      <span>{session.progress_percentage.toFixed(1)}%</span>
                    </div>
                    <Progress value={session.progress_percentage} />
                  </div>
                )}

                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Calendar className="h-4 w-4" />
                    Created: {new Date(session.created_at).toLocaleDateString()}
                  </div>
                  {session.status === 'completed' && (
                    <Button 
                      onClick={() => window.location.href = `/sessions/${session.id}/results`}
                      size="sm"
                    >
                      View Results
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {sessions.length === 0 && (
          <Card>
            <CardContent className="text-center py-8">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No evaluation sessions found</p>
              <Button 
                onClick={() => window.location.href = '/evaluate'}
                className="mt-4"
              >
                Start Your First Evaluation
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default SessionDashboard;
