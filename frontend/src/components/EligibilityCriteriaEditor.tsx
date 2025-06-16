import React, { useState, useEffect } from 'react';
import { Save, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { evaluationService } from '../services/evaluationService';
import { useApp } from '../context/AppContext';
import LoadingSpinner from './LoadingSpinner';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Textarea } from './ui/textarea';

const EligibilityCriteriaEditor: React.FC = () => {
  const { state, dispatch, showNotification } = useApp();
  const [content, setContent] = useState('');
  const [isValid, setIsValid] = useState(true);
  const [validationMessage, setValidationMessage] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadCriteria();
  }, []);

  const loadCriteria = async () => {
    dispatch({ type: 'SET_CRITERIA_LOADING', payload: true });
    try {
      const response = await evaluationService.getCriteria();
      const criteriaContent = response.data.content;
      setContent(criteriaContent);
      dispatch({ type: 'SET_CRITERIA_CONTENT', payload: criteriaContent });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to load criteria';
      showNotification(message, 'error');
      dispatch({ type: 'SET_CRITERIA_LOADING', payload: false });
    }
  };

  const validateCriteria = async (criteriaContent: string) => {
    if (!criteriaContent.trim()) {
      setIsValid(false);
      setValidationMessage('Criteria cannot be empty');
      return;
    }

    try {
      const response = await evaluationService.validateCriteria(criteriaContent);
      setIsValid(response.data.valid);
      setValidationMessage(response.data.message);
    } catch (error: any) {
      setIsValid(false);
      setValidationMessage(error.response?.data?.detail || 'Validation failed');
    }
  };

  const handleContentChange = (value: string) => {
    setContent(value);
    // Debounce validation
    const timeoutId = setTimeout(() => {
      validateCriteria(value);
    }, 500);
    return () => clearTimeout(timeoutId);
  };

  const handleSave = async () => {
    if (!isValid) {
      showNotification('Please fix validation errors before saving', 'error');
      return;
    }

    setSaving(true);
    try {
      await evaluationService.updateCriteria(content);
      dispatch({ type: 'SET_CRITERIA_CONTENT', payload: content });
      showNotification('Eligibility criteria updated successfully!', 'success');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to save criteria';
      showNotification(message, 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          YTP Eligibility Criteria Configuration
        </CardTitle>
        <CardDescription>
          Define the criteria that AI will use to evaluate Young Talents Programme applications
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Format Guidelines */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Format Guidelines:</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-blue-800">
            <li>Start with "Young Talents Programme Eligibility Criteria" as the header</li>
            <li>Use → symbol to mark each criterion</li>
            <li>Be specific and clear in your requirements</li>
            <li>Include both educational and age requirements</li>
          </ul>
        </div>

        {/* Editor */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            YTP Criteria Content
          </label>
          {state.criteria.loading ? (
            <div className="h-64 flex items-center justify-center border border-gray-300 rounded-lg">
              <LoadingSpinner size={32} />
            </div>
          ) : (
            <Textarea
              value={content}
              onChange={(e) => handleContentChange(e.target.value)}
              placeholder="Young Talents Programme Eligibility Criteria
→ First Class or Second Class Upper degree (or equivalent)
→ Must be under 30 years old at the time of application
→ Master's degree holders are welcome to apply
→ Strong interest in leadership, entrepreneurship, and career development"
              className="min-h-[200px] font-mono text-sm"
            />
          )}
        </div>

        {/* Validation Status */}
        {validationMessage && (
          <div className={`flex items-center gap-2 p-3 rounded-lg ${
            isValid 
              ? 'bg-green-50 border border-green-200 text-green-800' 
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            {isValid ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600" />
            )}
            <span className="text-sm">{validationMessage}</span>
          </div>
        )}

        {/* Save Button */}
        <div className="flex justify-end">
          <Button
            onClick={handleSave}
            disabled={!isValid || saving || state.criteria.loading}
            className="flex items-center gap-2"
          >
            {saving ? (
              <>
                <LoadingSpinner size={16} />
                <span>Saving...</span>
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>Save YTP Criteria</span>
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default EligibilityCriteriaEditor;
