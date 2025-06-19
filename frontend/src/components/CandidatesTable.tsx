import React, { useState, useMemo } from 'react';
import { Search, Filter, Eye, Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { CandidateResult } from '../types';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';

interface CandidatesTableProps {
  candidates: CandidateResult[];
  onViewCandidate: (candidate: CandidateResult) => void;
}

const CandidatesTable: React.FC<CandidatesTableProps> = ({ candidates, onViewCandidate }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [outcomeFilter, setOutcomeFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // Filter and search candidates
  const filteredCandidates = useMemo(() => {
    return candidates.filter(candidate => {
      const matchesSearch = candidate.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          candidate.email.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesOutcome = outcomeFilter === 'all' || candidate.outcome === outcomeFilter;
      return matchesSearch && matchesOutcome;
    });
  }, [candidates, searchTerm, outcomeFilter]);

  // Paginate results
  const paginatedCandidates = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredCandidates.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredCandidates, currentPage]);

  const totalPages = Math.ceil(filteredCandidates.length / itemsPerPage);

  const getOutcomeBadgeVariant = (outcome: string) => {
    switch (outcome) {
      case 'Accepted':
        return 'default'; // This will be green
      case 'Rejected':
        return 'destructive'; // This will be red
      case 'Error':
        return 'secondary'; // This will be gray
      default:
        return 'secondary';
    }
  };

  const exportToCsv = () => {
    const csvContent = [
      // Headers
      ['Name', 'Email', 'Outcome', 'Rationale', 'Timestamp'].join(','),
      // Data
      ...filteredCandidates.map(candidate => [
        candidate.name || '',
        candidate.email,
        candidate.outcome,
        `"${candidate.rationale.replace(/"/g, '""')}"`, // Escape quotes
        candidate.timestamp
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ytp_applications_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const getOutcomeColor = (outcome: string) => {
    switch (outcome) {
      case 'Accepted':
        return 'bg-green-100 text-green-800';
      case 'Rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <CardTitle>YTP Evaluation Results ({filteredCandidates.length} applications)</CardTitle>
          <Button onClick={exportToCsv} variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
        </div>
        
        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search by name or email..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1); // Reset to first page when searching
              }}
              className="pl-10"
            />
          </div>
          <Select value={outcomeFilter} onValueChange={(value) => {
            setOutcomeFilter(value);
            setCurrentPage(1); // Reset to first page when filtering
          }}>
            <SelectTrigger className="w-full sm:w-48">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Filter by outcome" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Outcomes</SelectItem>
              <SelectItem value="Accepted">Accepted</SelectItem>
              <SelectItem value="Rejected">Rejected</SelectItem>
              <SelectItem value="Error">Error</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Table */}
        <div className="overflow-x-auto">
          <Table className="w-full border-collapse">
            <TableHeader>
              <TableRow className="border-b border-gray-200">
                <TableHead className="text-left p-3 font-medium text-gray-900">Name</TableHead>
                <TableHead className="text-left p-3 font-medium text-gray-900">Email</TableHead>
                <TableHead className="text-left p-3 font-medium text-gray-900">Outcome</TableHead>
                <TableHead className="text-left p-3 font-medium text-gray-900">Score</TableHead>
                <TableHead className="text-left p-3 font-medium text-gray-900">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedCandidates.map((candidate, index) => (
                <TableRow 
                  key={`${candidate.email}-${candidate.session_id || index}`} // Use email + session_id for unique keys
                  className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                  onClick={() => onViewCandidate(candidate)}
                >
                  <TableCell className="p-3">
                    <div className="font-medium text-gray-900">
                      {candidate.name || 'N/A'}
                    </div>
                  </TableCell>
                  <TableCell className="p-3 text-gray-600">
                    {candidate.email}
                  </TableCell>
                  <TableCell className="p-3">
                    <Badge variant={getOutcomeBadgeVariant(candidate.outcome)}>
                      {candidate.outcome}
                    </Badge>
                  </TableCell>
                  <TableCell className="p-3">
                    <div className="flex items-center space-x-2">
                      <div className="text-sm font-medium">
                        {candidate.score?.toFixed(1) || 'N/A'}/100
                      </div>
                      {candidate.score !== undefined && (
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getScoreColor(candidate.score)}`}
                            style={{ width: `${Math.min(candidate.score, 100)}%` }}
                          />
                        </div>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="p-3">
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        onViewCandidate(candidate);
                      }}
                      variant="outline"
                      size="sm"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-6">
            <div className="text-sm text-gray-600">
              Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, filteredCandidates.length)} of {filteredCandidates.length} candidates
            </div>
            <div className="flex items-center gap-2">
              <Button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                variant="outline"
                size="sm"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <span className="text-sm text-gray-600">
                Page {currentPage} of {totalPages}
              </span>
              <Button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                variant="outline"
                size="sm"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}

        {/* Empty State */}
        {filteredCandidates.length === 0 && (
          <div className="text-center py-8">
            <div className="text-gray-500">
              {searchTerm || outcomeFilter !== 'all' 
                ? 'No applications match your filters' 
                : 'No applications found'
              }
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CandidatesTable;
