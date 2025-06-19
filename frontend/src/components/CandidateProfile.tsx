import React, { useState } from 'react';
import { User, Mail, Phone, MapPin, Building, GraduationCap, Award, Heart, FileText, Calendar, ExternalLink, Video, AlertCircle } from 'lucide-react';
import { CandidateResult } from '../types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface CandidateProfileProps {
  candidate: CandidateResult;
}

const CandidateProfile: React.FC<CandidateProfileProps> = ({ candidate }) => {
  // Generate a unique identifier for this specific evaluation
  const evaluationId = candidate.session_id 
    ? `${candidate.email}-${candidate.session_id}`
    : `${candidate.email}-${candidate.evaluation_timestamp || Date.now()}`;

  const getOutcomeBadgeVariant = (outcome: string) => {
    switch (outcome) {
      case 'Accepted':
        return 'default';
      case 'Rejected':
        return 'destructive';
      case 'Error':
        return 'secondary';
      default:
        return 'secondary';
    }
  };

  const getOutcomeColor = (outcome: string) => {
    switch (outcome) {
      case 'Accepted':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'Rejected':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const InfoItem: React.FC<{ icon: React.ReactNode; label: string; value: string | undefined }> = ({ icon, label, value }) => {
    if (!value) return null;
    return (
      <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
        <div className="text-gray-600 mt-0.5">{icon}</div>
        <div>
          <div className="text-sm font-medium text-gray-700">{label}</div>
          <div className="text-gray-900">{value}</div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Evaluation Summary */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">{candidate.name || 'Unknown Applicant'}</CardTitle>
              <CardDescription className="text-lg">{candidate.email}</CardDescription>
            </div>
            <Badge variant={getOutcomeBadgeVariant(candidate.outcome)} className="text-lg px-4 py-2">
              {candidate.outcome}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">AI Evaluation Rationale:</h4>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-blue-900 whitespace-pre-wrap">{candidate.rationale}</p>
              </div>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span>Evaluated: {new Date(candidate.evaluation_timestamp).toLocaleString()}</span>
              {candidate.session_id && (
                <span className="bg-gray-100 px-2 py-1 rounded text-xs">
                  Session: {candidate.session_name || candidate.session_id}
                </span>
              )}
              {candidate.files_processed_successfully ? (
                <Badge variant="outline" className="text-green-700 border-green-300">Files Processed</Badge>
              ) : (
                <Badge variant="outline" className="text-yellow-700 border-yellow-300">Processing Issues</Badge>
              )}
            </div>

            {/* Score Display */}
            <div className="flex items-center justify-between p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Evaluation Score</h3>
                <p className="text-sm text-gray-600">AI-generated score based on YTP eligibility criteria</p>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-gray-900 mb-1">
                  {candidate.score?.toFixed(1) || 'N/A'}
                </div>
                <div className="text-sm text-gray-500 mb-3">out of 100</div>
                {candidate.score !== undefined && (
                  <div className="w-32 bg-gray-200 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-500 ${getScoreColor(candidate.score)}`}
                      style={{ width: `${Math.min(candidate.score, 100)}%` }}
                    />
                  </div>
                )}
              </div>
            </div>
            
            {/* AI Rationale */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-2">
                <FileText className="h-4 w-4" />
                AI Evaluation Rationale
              </h3>
              <p className="text-sm text-gray-700 leading-relaxed">
                {candidate.rationale}
              </p>
            </div>
            
            {/* Processing Errors */}
            {candidate.processing_errors && candidate.processing_errors.length > 0 && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <h3 className="text-sm font-medium text-red-900 mb-2 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Processing Issues
                </h3>
                <ul className="text-sm text-red-700 space-y-1">
                  {candidate.processing_errors.map((error, index) => (
                    <li key={index}>• {error}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Evaluation Timestamp */}
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <Calendar className="h-4 w-4" />
              Evaluated on: {new Date(candidate.evaluation_timestamp).toLocaleString()}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Personal Information Tabs */}
      <Card>
        <CardHeader>
          <CardTitle>Applicant Information</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="basic">Basic</TabsTrigger>
              <TabsTrigger value="education">Education</TabsTrigger>
              <TabsTrigger value="professional">Professional</TabsTrigger>
              <TabsTrigger value="essay">Essay</TabsTrigger>
              <TabsTrigger value="files">Files</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-4 mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <InfoItem icon={<User className="h-4 w-4" />} label="Gender" value={candidate.gender} />
                <InfoItem icon={<Calendar className="h-4 w-4" />} label="Date of Birth" value={candidate.date_of_birth} />
                <InfoItem icon={<Heart className="h-4 w-4" />} label="Marital Status" value={candidate.marital_status} />
                <InfoItem icon={<Heart className="h-4 w-4" />} label="Religion" value={candidate.religion} />
                <InfoItem icon={<Phone className="h-4 w-4" />} label="Phone Number" value={candidate.phone_number} />
                <InfoItem icon={<MapPin className="h-4 w-4" />} label="Address" value={candidate.residential_address} />
              </div>
            </TabsContent>

            <TabsContent value="education" className="space-y-4 mt-6">
              <div className="space-y-4">
                <InfoItem icon={<GraduationCap className="h-4 w-4" />} label="University" value={candidate.university_attended} />
                
                {/* Undergraduate */}
                {candidate.undergraduate_degree_type && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-medium text-blue-900 mb-3">Undergraduate Education</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm font-medium text-blue-700">Degree Type</div>
                        <div className="text-blue-900">{candidate.undergraduate_degree_type}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-blue-700">Programme</div>
                        <div className="text-blue-900">{candidate.undergraduate_programme}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-blue-700">Class</div>
                        <div className="text-blue-900">{candidate.undergraduate_class}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-blue-700">Completion Date</div>
                        <div className="text-blue-900">{candidate.undergraduate_completion_date}</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Postgraduate */}
                {candidate.postgraduate_degree_type && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="font-medium text-green-900 mb-3">Postgraduate Education</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm font-medium text-green-700">Degree Type</div>
                        <div className="text-green-900">{candidate.postgraduate_degree_type}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-green-700">Programme</div>
                        <div className="text-green-900">{candidate.postgraduate_programme}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-green-700">Class</div>
                        <div className="text-green-900">{candidate.postgraduate_class}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-green-700">Completion Date</div>
                        <div className="text-green-900">{candidate.postgraduate_completion_date}</div>
                      </div>
                    </div>
                  </div>
                )}

                <InfoItem icon={<Award className="h-4 w-4" />} label="Education Qualifications" value={candidate.education_qualifications} />
              </div>
            </TabsContent>

            <TabsContent value="professional" className="space-y-4 mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <InfoItem icon={<Building className="h-4 w-4" />} label="Current Employment" value={candidate.current_employment} />
                <InfoItem icon={<Building className="h-4 w-4" />} label="Employment Category" value={candidate.employment_category} />
                <InfoItem icon={<MapPin className="h-4 w-4" />} label="Company Address" value={candidate.company_address} />
                <InfoItem icon={<Award className="h-4 w-4" />} label="Professional Qualifications" value={candidate.professional_qualifications} />
                <InfoItem icon={<Heart className="h-4 w-4" />} label="Career Interests" value={candidate.career_interests} />
                <InfoItem icon={<Heart className="h-4 w-4" />} label="MSA Interests" value={candidate.msa_interests} />
                <InfoItem icon={<FileText className="h-4 w-4" />} label="Previous Applications" value={candidate.previous_applications} />
              </div>
            </TabsContent>

            <TabsContent value="essay" className="space-y-4 mt-6">
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <h4 className="font-medium text-gray-900 mb-4">Application Essay</h4>
                {candidate.candidate_essay ? (
                  <div className="prose max-w-none">
                    <p className="whitespace-pre-wrap text-gray-700">{candidate.candidate_essay}</p>
                  </div>
                ) : (
                  <p className="text-gray-500 italic">No essay provided</p>
                )}
              </div>
            </TabsContent>

            <TabsContent value="files" className="space-y-4 mt-6">
              <div className="space-y-4">
                {/* File Processing Status */}
                <div className={`p-4 rounded-lg border ${
                  candidate.files_processed_successfully 
                    ? 'bg-green-50 border-green-200' 
                    : 'bg-yellow-50 border-yellow-200'
                }`}>
                  <h4 className={`font-medium mb-2 ${
                    candidate.files_processed_successfully ? 'text-green-900' : 'text-yellow-900'
                  }`}>
                    File Processing Status
                  </h4>
                  <p className={`text-sm ${
                    candidate.files_processed_successfully ? 'text-green-800' : 'text-yellow-800'
                  }`}>
                    {candidate.files_processed_successfully 
                      ? 'All files processed successfully' 
                      : 'Some files encountered processing issues'
                    }
                  </p>
                </div>

                {/* Processing Errors */}
                {candidate.processing_errors.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h4 className="font-medium text-red-900 mb-2">Processing Errors</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-red-800">
                      {candidate.processing_errors.map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* CV Information */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-3">CV Information</h4>
                  <div className="flex items-center gap-3">
                    <Button
                      onClick={() => window.open(candidate.cv_url, '_blank')}
                      variant="outline"
                      size="sm"
                      className="flex items-center gap-2"
                    >
                      <FileText className="h-4 w-4" />
                      View CV
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                    <span className="text-sm text-blue-700">PDF Document</span>
                  </div>
                </div>

                {/* Video Information */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h4 className="font-medium text-purple-900 mb-3">Video Information</h4>
                  <div className="flex items-center gap-3">
                    <Button
                      onClick={() => window.open(candidate.video_url, '_blank')}
                      variant="outline"
                      size="sm"
                      className="flex items-center gap-2"
                    >
                      <Video className="h-4 w-4" />
                      Watch Video
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                    <span className="text-sm text-purple-700">Video Submission</span>
                  </div>
                  {candidate.video_transcript && (
                    <div className="mt-3">
                      <span className="font-medium text-purple-700">Transcript Preview: </span>
                      <div className="bg-white border border-purple-200 rounded p-2 mt-1 max-h-32 overflow-y-auto">
                        <p className="text-gray-700 text-xs">{candidate.video_transcript.substring(0, 200)}...</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default CandidateProfile;
