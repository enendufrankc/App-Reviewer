
import React from 'react';
import { CheckCircle, AlertCircle, BarChart3, Users, UserCheck, UserX } from 'lucide-react';
import { EvaluationResults } from '../types';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

interface ProcessingStatusProps {
  results: EvaluationResults | null;
  onViewDashboard: () => void;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ results, onViewDashboard }) => {
  if (!results) return null;

  const { summary } = results;
  const successRate = summary.total_processed > 0 
    ? Math.round((summary.accepted / summary.total_processed) * 100) 
    : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CheckCircle className="h-5 w-5 text-green-600" />
          Processing Complete
        </CardTitle>
        <CardDescription>
          {results.message}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <Users className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-blue-900">{summary.total_processed}</div>
            <div className="text-sm text-blue-700">Total Processed</div>
          </div>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <UserCheck className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-green-900">{summary.accepted}</div>
            <div className="text-sm text-green-700">Accepted</div>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
            <UserX className="h-8 w-8 text-red-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-red-900">{summary.rejected}</div>
            <div className="text-sm text-red-700">Rejected</div>
          </div>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
            <AlertCircle className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-yellow-900">{summary.errors}</div>
            <div className="text-sm text-yellow-700">Errors</div>
          </div>
        </div>

        {/* Success Rate */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Success Rate:</span>
            <span className="text-lg font-bold text-gray-900">{successRate}%</span>
          </div>
          <div className="mt-2 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${successRate}%` }}
            />
          </div>
        </div>

        {/* Action Button */}
        <div className="flex justify-center">
          <Button
            onClick={onViewDashboard}
            className="flex items-center gap-2"
            size="lg"
          >
            <BarChart3 className="h-5 w-5" />
            View Detailed Results
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProcessingStatus;
