import React from 'react';
import { Users, UserCheck, UserX, AlertCircle, TrendingUp } from 'lucide-react';
import { EvaluationSummary, CandidateResult } from '../types';
import { Card, CardContent } from './ui/card';

interface DashboardStatsProps {
  summary: EvaluationSummary;
  candidates?: CandidateResult[];
}

const DashboardStats: React.FC<DashboardStatsProps> = ({ summary, candidates = [] }) => {
  const acceptanceRate = summary.total_processed > 0 
    ? Math.round((summary.accepted / summary.total_processed) * 100) 
    : 0;

  const averageScore = candidates.length > 0 
    ? candidates.reduce((sum, candidate) => sum + (candidate.score || 0), 0) / candidates.length
    : 0;

  const stats = [
    {
      name: 'Total Processed',
      value: summary.total_processed,
      icon: Users,
      color: 'blue',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      textColor: 'text-blue-900'
    },
    {
      name: 'Accepted',
      value: summary.accepted,
      icon: UserCheck,
      color: 'green',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      textColor: 'text-green-900'
    },
    {
      name: 'Rejected',
      value: summary.rejected,
      icon: UserX,
      color: 'red',
      bgColor: 'bg-red-50',
      iconColor: 'text-red-600',
      textColor: 'text-red-900'
    },
    {
      name: 'Errors',
      value: summary.errors,
      icon: AlertCircle,
      color: 'yellow',
      bgColor: 'bg-yellow-50',
      iconColor: 'text-yellow-600',
      textColor: 'text-yellow-900'
    },
    {
      name: 'Average Score',
      value: averageScore.toFixed(1),
      icon: TrendingUp,
      color: 'purple',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      textColor: 'text-purple-900'
    }
  ];

  return (
    <div className="space-y-4">
      {/* Main Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.name} className={`${stat.bgColor} border-${stat.color}-200`}>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Icon className={`h-8 w-8 ${stat.iconColor}`} />
                  </div>
                  <div className="ml-4">
                    <div className={`text-2xl font-bold ${stat.textColor}`}>
                      {stat.value}
                    </div>
                    <div className={`text-sm ${stat.textColor} opacity-75`}>
                      {stat.name}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Acceptance Rate */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-blue-900">
                {acceptanceRate}%
              </div>
              <div className="text-blue-700">Acceptance Rate</div>
            </div>
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <div className="text-2xl font-bold text-blue-600">
                {summary.accepted}/{summary.total_processed}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardStats;
