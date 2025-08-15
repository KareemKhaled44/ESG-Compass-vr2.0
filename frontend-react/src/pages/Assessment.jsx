import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import Layout from '../components/layout/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import Modal from '../components/ui/Modal';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { esgAPI } from '../services/api';

const Assessment = () => {
  const [currentAssessment, setCurrentAssessment] = useState(null);
  const [currentCategory, setCurrentCategory] = useState('environmental');
  const [showNewAssessmentModal, setShowNewAssessmentModal] = useState(false);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [selectedQuestionId, setSelectedQuestionId] = useState(null);
  const [responses, setResponses] = useState({});

  const queryClient = useQueryClient();

  const {
    register: registerAssessment,
    handleSubmit: handleAssessmentSubmit,
    reset: resetAssessmentForm,
    formState: { errors: assessmentErrors }
  } = useForm();

  const {
    register: registerEvidence,
    handleSubmit: handleEvidenceSubmit,
    reset: resetEvidenceForm
  } = useForm();

  // Load assessments
  const { data: assessments, isLoading: assessmentsLoading } = useQuery(
    'assessments',
    () => esgAPI.getESGAssessments(),
    {
      onSuccess: (data) => {
        if (data && data.length > 0 && !currentAssessment) {
          setCurrentAssessment(data[0]);
        }
      }
    }
  );

  // Load questions for current category
  const { data: questions, isLoading: questionsLoading } = useQuery(
    ['questions', currentCategory],
    () => esgAPI.getESGQuestions(currentCategory),
    {
      enabled: !!currentAssessment
    }
  );

  // Create assessment mutation
  const createAssessmentMutation = useMutation(
    (data) => esgAPI.createESGAssessment(data),
    {
      onSuccess: (newAssessment) => {
        queryClient.invalidateQueries('assessments');
        setCurrentAssessment(newAssessment);
        setShowNewAssessmentModal(false);
        resetAssessmentForm();
        toast.success('Assessment created successfully!');
      },
      onError: () => {
        toast.error('Failed to create assessment');
      }
    }
  );

  // Submit response mutation
  const submitResponseMutation = useMutation(
    (data) => esgAPI.submitESGResponse(data),
    {
      onSuccess: (response) => {
        setResponses(prev => ({
          ...prev,
          [response.question]: response
        }));
        toast.success('Response saved successfully!');
      },
      onError: () => {
        toast.error('Failed to save response');
      }
    }
  );

  // Upload evidence mutation
  const uploadEvidenceMutation = useMutation(
    ({ responseId, fileData }) => esgAPI.uploadESGEvidence(responseId, fileData),
    {
      onSuccess: () => {
        setShowEvidenceModal(false);
        resetEvidenceForm();
        toast.success('Evidence uploaded successfully!');
      },
      onError: () => {
        toast.error('Failed to upload evidence');
      }
    }
  );

  const categories = [
    { id: 'environmental', label: 'Environmental', icon: 'fa-solid fa-leaf', color: '#2EC57D' },
    { id: 'social', label: 'Social', icon: 'fa-solid fa-users', color: '#3DAEFF' },
    { id: 'governance', label: 'Governance', icon: 'fa-solid fa-shield-halved', color: '#20C5C5' }
  ];

  const handleAssessmentChange = (e) => {
    const assessmentId = e.target.value;
    const assessment = assessments?.find(a => a.id === assessmentId);
    setCurrentAssessment(assessment);
  };

  const handleCategoryChange = (categoryId) => {
    setCurrentCategory(categoryId);
  };

  const handleNewAssessment = (data) => {
    createAssessmentMutation.mutate({
      name: data.name,
      description: data.description,
      assessment_period_start: data.assessment_period_start,
      assessment_period_end: data.assessment_period_end,
      status: 'draft'
    });
  };

  const handleResponseSave = async (questionId) => {
    const questionCard = document.querySelector(`[data-question-id="${questionId}"]`);
    const input = questionCard?.querySelector(`[name="q_${questionId}"]`);
    
    if (!input || !input.value) {
      toast.warning('Please provide a response before saving');
      return;
    }

    let responseData = input.value;
    if (input.type === 'radio') {
      const checked = questionCard.querySelector(`[name="q_${questionId}"]:checked`);
      responseData = checked ? checked.value : null;
    }

    if (!responseData) {
      toast.warning('Please provide a response before saving');
      return;
    }

    submitResponseMutation.mutate({
      assessment: currentAssessment.id,
      question: questionId,
      response_data: responseData,
      confidence_level: 5
    });
  };

  const handleEvidenceUpload = (data) => {
    if (!data.file || data.file.length === 0) {
      toast.warning('Please select a file to upload');
      return;
    }

    // Find or create response for the question
    const existingResponse = responses[selectedQuestionId];
    if (existingResponse) {
      uploadEvidenceMutation.mutate({
        responseId: existingResponse.id,
        fileData: {
          file: data.file[0],
          title: data.title,
          description: data.description
        }
      });
    } else {
      // Create placeholder response first
      submitResponseMutation.mutate({
        assessment: currentAssessment.id,
        question: selectedQuestionId,
        response_data: 'Evidence provided',
        confidence_level: 5
      }, {
        onSuccess: (response) => {
          uploadEvidenceMutation.mutate({
            responseId: response.id,
            fileData: {
              file: data.file[0],
              title: data.title,
              description: data.description
            }
          });
        }
      });
    }
  };

  const renderQuestionInput = (question) => {
    const existingResponse = responses[question.id];
    const value = existingResponse ? existingResponse.response_data : '';

    switch (question.question_type) {
      case 'yes_no':
        return (
          <div className="space-y-2">
            <label className="flex items-center space-x-3">
              <input 
                type="radio" 
                name={`q_${question.id}`} 
                value="yes"
                defaultChecked={value === 'yes'}
                className="text-brand-green focus:ring-brand-green"
              />
              <span className="text-text-high">Yes</span>
            </label>
            <label className="flex items-center space-x-3">
              <input 
                type="radio" 
                name={`q_${question.id}`} 
                value="no"
                defaultChecked={value === 'no'}
                className="text-brand-green focus:ring-brand-green"
              />
              <span className="text-text-high">No</span>
            </label>
          </div>
        );

      case 'multiple_choice':
        return (
          <select 
            name={`q_${question.id}`}
            defaultValue={value}
            className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-text-high focus:outline-none focus:border-brand-green focus:ring-1 focus:ring-brand-green transition-colors"
          >
            <option value="" className="bg-[#131A2C] text-text-high">Select an option...</option>
            {question.options?.map(option => (
              <option key={option} value={option} className="bg-[#131A2C] text-text-high">{option}</option>
            ))}
          </select>
        );

      case 'text':
        return (
          <textarea
            name={`q_${question.id}`}
            placeholder={question.placeholder || 'Enter your response...'}
            defaultValue={value}
            rows="4"
            className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-text-high placeholder-text-muted focus:outline-none focus:border-brand-green focus:ring-1 focus:ring-brand-green transition-colors resize-none"
          />
        );

      case 'number':
        return (
          <input
            type="number"
            name={`q_${question.id}`}
            placeholder={question.placeholder || 'Enter a number...'}
            defaultValue={value}
            className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-text-high placeholder-text-muted focus:outline-none focus:border-brand-green focus:ring-1 focus:ring-brand-green transition-colors"
          />
        );

      case 'date':
        return (
          <input
            type="date"
            name={`q_${question.id}`}
            defaultValue={value}
            className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-text-high focus:outline-none focus:border-brand-green focus:ring-1 focus:ring-brand-green transition-colors"
          />
        );

      case 'rating':
        return (
          <div className="flex items-center space-x-2">
            {[1, 2, 3, 4, 5].map(rating => (
              <label key={rating} className="flex items-center">
                <input 
                  type="radio" 
                  name={`q_${question.id}`} 
                  value={rating}
                  defaultChecked={parseInt(value) === rating}
                  className="sr-only"
                />
                <i className={`fas fa-star text-2xl cursor-pointer transition-colors ${
                  parseInt(value) >= rating ? 'text-yellow-400' : 'text-white/20'
                }`}></i>
              </label>
            ))}
            <span className="ml-4 text-text-muted text-sm">Rate from 1 to 5</span>
          </div>
        );

      default:
        return (
          <input
            type="text"
            name={`q_${question.id}`}
            placeholder={question.placeholder || 'Enter your response...'}
            defaultValue={value}
            className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-text-high placeholder-text-muted focus:outline-none focus:border-brand-green focus:ring-1 focus:ring-brand-green transition-colors"
          />
        );
    }
  };

  if (assessmentsLoading || questionsLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-text-high font-bold text-3xl mb-2">ESG Assessment</h1>
              <p className="text-text-muted">Complete your comprehensive ESG evaluation</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="secondary"
                onClick={() => {/* Save progress logic */}}
              >
                <i className="fas fa-save mr-2"></i>Save Progress
              </Button>
              <Button
                variant="primary"
                onClick={() => setShowNewAssessmentModal(true)}
              >
                <i className="fas fa-plus mr-2"></i>New Assessment
              </Button>
            </div>
          </div>

          {/* Assessment Selection */}
          <Card className="mb-6">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-text-high font-medium mb-2">Current Assessment</label>
                <select
                  value={currentAssessment?.id || ''}
                  onChange={handleAssessmentChange}
                  className="px-4 py-2 bg-white/5 border border-white/20 rounded-lg text-text-high focus:outline-none focus:border-brand-green focus:ring-1 focus:ring-brand-green transition-colors"
                >
                  <option value="" className="bg-[#131A2C] text-text-high">Select an assessment...</option>
                  {assessments?.map(assessment => (
                    <option key={assessment.id} value={assessment.id} className="bg-[#131A2C] text-text-high">
                      {assessment.name} ({assessment.status})
                    </option>
                  ))}
                </select>
              </div>
              <div className="text-right">
                <div className="text-text-muted text-sm">Overall Progress</div>
                <div className="text-2xl font-bold text-brand-green">
                  {Math.round(currentAssessment?.progress_percentage || 0)}%
                </div>
              </div>
            </div>

            <div className="mt-4">
              <div className="bg-white/10 rounded-full h-2">
                <div 
                  className="h-full bg-brand-green rounded-full transition-all duration-500"
                  style={{ width: `${currentAssessment?.progress_percentage || 0}%` }}
                ></div>
              </div>
            </div>
          </Card>
        </div>

        {/* Category Tabs */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-white/5 p-1 rounded-lg">
            {categories.map(category => (
              <button
                key={category.id}
                onClick={() => handleCategoryChange(category.id)}
                className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                  currentCategory === category.id 
                    ? 'text-white' 
                    : 'text-text-muted hover:text-text-high'
                }`}
                style={{
                  backgroundColor: currentCategory === category.id ? category.color : 'transparent'
                }}
              >
                <i className={`${category.icon} mr-2`}></i>
                {category.label}
              </button>
            ))}
          </div>
        </div>

        {/* Questions Container */}
        <div className="space-y-6">
          {!currentAssessment ? (
            <Card className="text-center py-12">
              <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4">
                <i className="fas fa-clipboard-check text-2xl text-text-muted"></i>
              </div>
              <h3 className="text-text-high font-semibold text-lg mb-2">No Assessment Selected</h3>
              <p className="text-text-muted mb-4">Create a new assessment or select an existing one to begin</p>
              <Button
                variant="primary"
                onClick={() => setShowNewAssessmentModal(true)}
              >
                <i className="fas fa-plus mr-2"></i>Create New Assessment
              </Button>
            </Card>
          ) : !questions || questions.length === 0 ? (
            <Card className="text-center py-12">
              <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4">
                <i className="fas fa-question-circle text-2xl text-text-muted"></i>
              </div>
              <h3 className="text-text-high font-semibold text-lg mb-2">No Questions Available</h3>
              <p className="text-text-muted">Questions for this category will be loaded here</p>
            </Card>
          ) : (
            questions.map((question, index) => (
              <Card key={question.id} className="question-card" data-question-id={question.id}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-sm font-medium text-text-muted">Question {index + 1}</span>
                      {question.is_required && (
                        <span className="text-xs bg-red-500 text-white px-2 py-1 rounded">Required</span>
                      )}
                      <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">
                        {question.question_type}
                      </span>
                    </div>
                    <h3 className="text-text-high font-semibold text-lg mb-2">{question.question_text}</h3>
                    {question.help_text && (
                      <p className="text-text-muted text-sm mb-4">{question.help_text}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    {responses[question.id] ? (
                      <i className="fas fa-check-circle text-brand-green"></i>
                    ) : (
                      <i className="far fa-circle text-text-muted"></i>
                    )}
                  </div>
                </div>

                <div className="mb-4">
                  {renderQuestionInput(question)}
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                  <div className="flex items-center space-x-4">
                    <Button
                      variant="tertiary"
                      size="small"
                      onClick={() => {
                        setSelectedQuestionId(question.id);
                        setShowEvidenceModal(true);
                      }}
                    >
                      <i className="fas fa-paperclip mr-2"></i>Add Evidence
                    </Button>
                    {question.compliance_context && (
                      <div className="text-xs text-text-muted max-w-xs">
                        {question.compliance_context}
                      </div>
                    )}
                  </div>
                  <Button
                    variant="primary"
                    size="small"
                    loading={submitResponseMutation.isLoading}
                    onClick={() => handleResponseSave(question.id)}
                  >
                    Save Response
                  </Button>
                </div>
              </Card>
            ))
          )}
        </div>

        {/* New Assessment Modal */}
        <Modal
          isOpen={showNewAssessmentModal}
          onClose={() => setShowNewAssessmentModal(false)}
          title="Create New Assessment"
        >
          <form onSubmit={handleAssessmentSubmit(handleNewAssessment)} className="space-y-4">
            <Input
              label="Assessment Name"
              placeholder="e.g., Q1 2024 Assessment"
              required
              error={assessmentErrors.name?.message}
              {...registerAssessment('name', {
                required: 'Assessment name is required'
              })}
            />

            <div>
              <label className="block text-text-high font-medium mb-2">Description</label>
              <textarea
                placeholder="Optional description"
                rows="3"
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-text-high placeholder-text-muted focus:outline-none focus:border-brand-green focus:ring-1 focus:ring-brand-green transition-colors resize-none"
                {...registerAssessment('description')}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Start Date"
                type="date"
                required
                error={assessmentErrors.assessment_period_start?.message}
                {...registerAssessment('assessment_period_start', {
                  required: 'Start date is required'
                })}
              />
              <Input
                label="End Date"
                type="date"
                required
                error={assessmentErrors.assessment_period_end?.message}
                {...registerAssessment('assessment_period_end', {
                  required: 'End date is required'
                })}
              />
            </div>

            <div className="flex space-x-4 pt-4">
              <Button
                type="submit"
                variant="primary"
                loading={createAssessmentMutation.isLoading}
                className="flex-1"
              >
                Create Assessment
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowNewAssessmentModal(false)}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Modal>

        {/* Evidence Upload Modal */}
        <Modal
          isOpen={showEvidenceModal}
          onClose={() => setShowEvidenceModal(false)}
          title="Upload Evidence"
        >
          <form onSubmit={handleEvidenceSubmit(handleEvidenceUpload)} className="space-y-4">
            <Input
              label="Title"
              placeholder="Evidence title"
              {...registerEvidence('title')}
            />

            <div>
              <label className="block text-text-high font-medium mb-2">Description</label>
              <textarea
                placeholder="Describe the evidence"
                rows="3"
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-text-high placeholder-text-muted focus:outline-none focus:border-brand-green focus:ring-1 focus:ring-brand-green transition-colors resize-none"
                {...registerEvidence('description')}
              />
            </div>

            <div>
              <label className="block text-text-high font-medium mb-2">File</label>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-text-high file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-brand-green file:text-white hover:file:bg-green-600 transition-colors"
                {...registerEvidence('file', {
                  required: 'File is required'
                })}
              />
            </div>

            <div className="flex space-x-4 pt-4">
              <Button
                type="submit"
                variant="primary"
                loading={uploadEvidenceMutation.isLoading}
                className="flex-1"
              >
                Upload Evidence
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowEvidenceModal(false)}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </Layout>
  );
};

export default Assessment;