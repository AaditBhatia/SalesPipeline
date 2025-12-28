import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { leadsAPI } from '../api/client';

function LeadDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [showRescoreModal, setShowRescoreModal] = useState(false);
  const [rescoreComment, setRescoreComment] = useState('');
  const [showScoringResultModal, setShowScoringResultModal] = useState(false);
  const [scoringResult, setScoringResult] = useState(null);
  const [scoringStatus, setScoringStatus] = useState(null); // 'loading', 'success', 'error'
  const [isEvaluating, setIsEvaluating] = useState(false);

  const fetchLead = async () => {
    try {
      setLoading(true);
      const response = await leadsAPI.getById(id);
      setLead(response.data);
    } catch (error) {
      console.error('Error fetching lead:', error);
      alert('Lead not found');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const autoScore = async () => {
    setIsEvaluating(true);
    setScoringStatus('loading');
    
    try {
      const response = await fetch(`http://localhost:8000/api/leads/${id}/score`, {
        method: 'POST',
      });
      
      if (response.ok) {
        const data = await response.json();
        setScoringResult(data.ai_analysis);
        setScoringStatus('success');
        
        // Refresh lead data
        await fetchLead();
        
        // Show the result modal
        setShowScoringResultModal(true);
        
        // Continue with qualification after a brief delay
        setTimeout(async () => {
          try {
            await fetch(`http://localhost:8000/api/leads/${id}/qualify`, {
              method: 'POST',
            });
            await fetchLead();
          } catch (error) {
            console.error('Auto-qualify error:', error);
          }
        }, 1000);
      } else {
        setScoringStatus('error');
      }
    } catch (error) {
      console.error('Auto-scoring error:', error);
      setScoringStatus('error');
    } finally {
      setIsEvaluating(false);
    }
  };

  useEffect(() => {
    fetchLead();
    
    // Check if we should auto-trigger scoring
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('autoScore') === 'true') {
      // Remove the parameter from URL
      window.history.replaceState({}, '', `/leads/${id}`);
      // Trigger auto-scoring after a short delay to ensure lead is loaded
      setTimeout(() => {
        autoScore();
      }, 500);
    }
  }, [id]);

  const handleWorkflow = async (workflowType) => {
    setProcessing(true);
    try {
      let response;
      
      switch (workflowType) {
        case 'qualify':
          response = await fetch(`http://localhost:8000/api/leads/${id}/qualify`, {
            method: 'POST',
          });
          break;
        
        case 'score':
          response = await fetch(`http://localhost:8000/api/leads/${id}/score`, {
            method: 'POST',
          });
          if (response.ok) {
            const data = await response.json();
            setScoringResult(data.ai_analysis);
            setShowScoringResultModal(true);
          }
          break;
        
        case 'contact':
          await leadsAPI.update(id, { status: 'contacted' });
          break;
        
        case 'qualified':
          await leadsAPI.update(id, { status: 'qualified' });
          break;
        
        case 'demo':
          await leadsAPI.update(id, { status: 'demo' });
          break;
      }
      
      await fetchLead();
      if (workflowType !== 'score') {
        alert('Workflow completed successfully!');
      }
    } catch (error) {
      console.error('Workflow error:', error);
      alert('Error processing workflow');
    } finally {
      setProcessing(false);
    }
  };

  const handleRescore = async () => {
    if (!rescoreComment.trim()) {
      alert('Please enter a comment explaining why you want to rescore');
      return;
    }

    setProcessing(true);
    try {
      const response = await fetch(`http://localhost:8000/api/leads/${id}/rescore`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comment: rescoreComment }),
      });

      if (!response.ok) {
        throw new Error('Failed to rescore lead');
      }

      await fetchLead();
      setShowRescoreModal(false);
      setRescoreComment('');
      alert('Lead rescored successfully!');
    } catch (error) {
      console.error('Rescore error:', error);
      alert('Error rescoring lead');
    } finally {
      setProcessing(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      new: 'bg-blue-100 text-blue-800',
      contacted: 'bg-yellow-100 text-yellow-800',
      qualified: 'bg-green-100 text-green-800',
      demo: 'bg-purple-100 text-purple-800',
      closed_won: 'bg-green-200 text-green-900',
      closed_lost: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getWorkflowSteps = () => {
    const allSteps = [
      { id: 'new', label: 'New Lead', icon: '📥', activityTypes: ['lead_created'] },
      { id: 'scored', label: 'Scored', icon: '📊', scoreRequired: true, activityTypes: ['ai_scoring', 'score_updated'] },
      { id: 'contacted', label: 'Contacted', icon: '📞', activityTypes: ['status_changed', 'email_sent', 'email_failed'] },
      { id: 'qualified', label: 'Qualified', icon: '✅', activityTypes: ['ai_qualification', 'status_changed'] },
      { id: 'demo', label: 'Demo Scheduled', icon: '📅', activityTypes: ['status_changed', 'workflow_completed'] },
      { id: 'closed_won', label: 'Closed Won', icon: '🎉', activityTypes: ['status_changed'] },
    ];

    const statusOrder = ['new', 'contacted', 'qualified', 'demo', 'closed_won', 'closed_lost'];
    const currentIndex = statusOrder.indexOf(lead?.status || 'new');

    return allSteps.map((step, index) => {
      let status = 'pending';
      
      if (step.id === 'scored') {
        status = lead?.score > 0 ? 'completed' : 'pending';
      } else if (step.id === 'new') {
        status = 'completed';
      } else {
        const stepIndex = statusOrder.indexOf(step.id);
        if (stepIndex <= currentIndex) {
          status = 'completed';
        } else if (stepIndex === currentIndex + 1) {
          status = 'next';
        }
      }

      // Get activities for this step
      const stepActivities = (lead?.activities || []).filter(activity => 
        step.activityTypes.includes(activity.type)
      );

      return { ...step, status, activities: stepActivities };
    });
  };

  const handleStepClick = (step) => {
    if (step.activities && step.activities.length > 0) {
      setSelectedActivity({ step, activities: step.activities });
      setShowActivityModal(true);
    }
  };

  const formatTimestamp = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
      </div>
    );
  }

  if (!lead) {
    return null;
  }

  const workflowSteps = getWorkflowSteps();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/')}
            className="text-blue-600 hover:text-blue-800 font-medium flex items-center mb-4"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Leads
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {lead.first_name} {lead.last_name}
              </h1>
              <p className="text-gray-600 mt-1">{lead.company_name}</p>
            </div>
            <span className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full ${getStatusColor(lead.status)}`}>
              {lead.status}
            </span>
          </div>
        </div>

        {/* Workflow Progress Timeline */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Workflow Progress</h2>
            <p className="text-sm text-gray-500">Click on completed steps to view details</p>
          </div>
          
          <div className="relative">
            {/* Progress Line */}
            <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200" style={{ width: 'calc(100% - 2rem)' }}></div>
            <div 
              className="absolute top-5 left-0 h-0.5 bg-blue-600 transition-all duration-500" 
              style={{ 
                width: `${(workflowSteps.filter(s => s.status === 'completed').length / workflowSteps.length) * 100}%` 
              }}
            ></div>

            {/* Steps */}
            <div className="relative flex justify-between">
              {workflowSteps.map((step, index) => (
                <div 
                  key={step.id} 
                  className="flex flex-col items-center cursor-pointer group"
                  style={{ width: '120px' }}
                  onClick={() => handleStepClick(step)}
                >
                  {/* Icon Circle */}
                  <div className={`
                    w-10 h-10 rounded-full flex items-center justify-center text-lg z-10 transition-all
                    ${step.status === 'completed' 
                      ? 'bg-blue-600 text-white group-hover:bg-blue-700 group-hover:scale-110' 
                      : step.status === 'next'
                      ? 'bg-yellow-400 text-white animate-pulse'
                      : 'bg-gray-200 text-gray-400'
                    }
                    ${step.activities && step.activities.length > 0 ? 'cursor-pointer' : 'cursor-default'}
                  `}>
                    {step.status === 'completed' ? '✓' : step.icon}
                  </div>

                  {/* Label */}
                  <div className="mt-2 text-center">
                    <p className={`text-xs font-medium ${
                      step.status === 'completed' ? 'text-blue-600 group-hover:text-blue-700' : 
                      step.status === 'next' ? 'text-yellow-600' : 
                      'text-gray-500'
                    }`}>
                      {step.label}
                    </p>
                    {step.scoreRequired && lead.score > 0 && (
                      <p className="text-xs text-gray-500 mt-1">
                        {lead.score}/100
                      </p>
                    )}
                    {step.activities && step.activities.length > 0 && step.status === 'completed' && (
                      <p className="text-xs text-blue-500 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        View details →
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Next Step Recommendation */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-gray-900">Next Step</h3>
                <div className="mt-1 text-sm text-gray-600">
                  {lead.status === 'new' && (
                    <p>Run the automated workflow to score and qualify this lead.</p>
                  )}
                  {lead.status === 'contacted' && (
                    <p>Follow up with the lead and move to qualified status if they show interest.</p>
                  )}
                  {lead.status === 'qualified' && (
                    <p>Schedule a product demo to showcase the solution.</p>
                  )}
                  {lead.status === 'demo' && (
                    <p>Follow up after demo and work towards closing the deal.</p>
                  )}
                  {lead.status === 'closed_won' && (
                    <p>🎉 Deal closed! Begin onboarding process.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Activity Details Modal */}
{showActivityModal && selectedActivity && (
  <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50" onClick={() => setShowActivityModal(false)}>
    <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">
          {selectedActivity.step.icon} {selectedActivity.step.label} - Activity Details
        </h2>
        <button
          onClick={() => setShowActivityModal(false)}
          className="text-gray-400 hover:text-gray-600"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div className="px-6 py-4 space-y-4">
        {selectedActivity.activities.map((activity, index) => (
          <div key={activity.id || index} className="border-l-4 border-blue-500 pl-4 py-2">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-gray-900">{activity.details}</h3>
              <span className="text-xs text-gray-500 whitespace-nowrap ml-4">{formatTimestamp(activity.timestamp)}</span>
            </div>
            
            {/* AI SCORING - DETAILED BREAKDOWN */}
            {activity.type === 'ai_scoring' && activity.metadata && activity.metadata.breakdown && (
              <div className="mt-3 space-y-4">
                {/* Check if breakdown has the new detailed format */}
                {typeof Object.values(activity.metadata.breakdown)[0] === 'object' && 
                 Object.values(activity.metadata.breakdown)[0].reasoning ? (
                  <>
                    {/* New detailed format */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
                        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                          <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd"/>
                        </svg>
                        AI Scoring Breakdown
                      </h4>
                      
                      <div className="space-y-3">
                        {Object.entries(activity.metadata.breakdown).map(([category, details]) => (
                          <div key={category} className="bg-white rounded-lg p-3 border border-blue-100">
                            <div className="flex justify-between items-start mb-2">
                              <h5 className="font-semibold text-gray-900 capitalize">
                                {category.replace('_', ' ')}
                              </h5>
                              <span className="text-lg font-bold text-blue-600">
                                {details.score} pts
                              </span>
                            </div>
                            
                            <p className="text-sm text-gray-700 mb-2">
                              <span className="font-medium">Reasoning:</span> {details.reasoning}
                            </p>
                            
                            {details.evidence && details.evidence.length > 0 && (
                              <div className="mt-2">
                                <p className="text-xs font-semibold text-gray-600 mb-1">Evidence:</p>
                                <ul className="list-disc list-inside space-y-1">
                                  {details.evidence.map((ev, idx) => (
                                    <li key={idx} className="text-xs text-gray-600">{ev}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                      
                      <div className="mt-4 pt-3 border-t border-blue-200">
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <p className="text-xs font-semibold text-gray-600">Total Score</p>
                            <p className="text-2xl font-bold text-blue-600">{activity.metadata.score}/100</p>
                          </div>
                          <div>
                            <p className="text-xs font-semibold text-gray-600">Priority</p>
                            <p className={`text-lg font-bold ${
                              activity.metadata.priority === 'hot' ? 'text-red-600' :
                              activity.metadata.priority === 'warm' ? 'text-yellow-600' :
                              'text-blue-600'
                            }`}>
                              {activity.metadata.priority?.toUpperCase() || 'N/A'}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Key Insights */}
                    {activity.metadata.insights && activity.metadata.insights.length > 0 && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <h4 className="font-semibold text-green-900 mb-2 flex items-center">
                          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                          </svg>
                          Key Insights
                        </h4>
                        <ul className="space-y-1">
                          {activity.metadata.insights.map((insight, idx) => (
                            <li key={idx} className="text-sm text-green-800 flex items-start">
                              <span className="mr-2">•</span>
                              <span>{insight}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Strengths */}
                    {activity.metadata.strengths && activity.metadata.strengths.length > 0 && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <h5 className="font-semibold text-green-900 text-sm mb-2">💪 Strengths</h5>
                        <ul className="space-y-1">
                          {activity.metadata.strengths.map((strength, idx) => (
                            <li key={idx} className="text-xs text-green-800">✓ {strength}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Red Flags */}
                    {activity.metadata.red_flags && activity.metadata.red_flags.length > 0 && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                        <h5 className="font-semibold text-yellow-900 text-sm mb-2">⚠️ Red Flags</h5>
                        <ul className="space-y-1">
                          {activity.metadata.red_flags.map((flag, idx) => (
                            <li key={idx} className="text-xs text-yellow-800">• {flag}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Recommended Action */}
                    {activity.metadata.recommended_action && (
                      <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                        <h5 className="font-semibold text-purple-900 text-sm mb-1">🎯 Recommended Action</h5>
                        <p className="text-sm text-purple-800">{activity.metadata.recommended_action}</p>
                      </div>
                    )}
                    
                    {/* Deal Size Estimate */}
                    {activity.metadata.deal_size && (
                      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
                        <h5 className="font-semibold text-indigo-900 text-sm mb-1">💰 Estimated Deal Size</h5>
                        <p className="text-sm text-indigo-800 capitalize font-semibold">{activity.metadata.deal_size}</p>
                        {activity.metadata.deal_size_reasoning && (
                          <p className="text-xs text-indigo-700 mt-1">{activity.metadata.deal_size_reasoning}</p>
                        )}
                      </div>
                    )}
                  </>
                ) : (
                  /* Old simple format - show as table */
                  <div className="bg-gray-50 rounded p-3">
                    <p className="text-xs font-semibold text-gray-600 mb-2">Score Breakdown:</p>
                    {Object.entries(activity.metadata.breakdown).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm py-1">
                        <span className="text-gray-600 capitalize">{key.replace('_', ' ')}:</span>
                        <span className="font-medium text-gray-900">
                          {typeof value === 'object' ? `+${value.points} pts - ${value.reason}` : value}
                        </span>
                      </div>
                    ))}
                    <div className="pt-2 border-t border-gray-200 flex justify-between text-sm font-semibold mt-2">
                      <span>Total Score:</span>
                      <span className="text-blue-600">{activity.metadata.score}/100</span>
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {/* STATUS CHANGED */}
            {activity.type === 'status_changed' && activity.metadata && (
              <div className="mt-2 bg-gray-50 rounded p-3">
                <div className="text-sm">
                  <p className="text-gray-700">
                    <span className="font-medium">From:</span> 
                    <span className={`ml-2 px-2 py-0.5 rounded ${getStatusColor(activity.metadata.old_status)}`}>
                      {activity.metadata.old_status}
                    </span>
                  </p>
                  <p className="text-gray-700 mt-1">
                    <span className="font-medium">To:</span> 
                    <span className={`ml-2 px-2 py-0.5 rounded ${getStatusColor(activity.metadata.new_status)}`}>
                      {activity.metadata.new_status}
                    </span>
                  </p>
                </div>
              </div>
            )}
            
            {/* OTHER METADATA */}
            {activity.metadata && !['ai_scoring', 'status_changed'].includes(activity.type) && Object.keys(activity.metadata).length > 0 && (
              <div className="mt-2 bg-gray-50 rounded p-3">
                <p className="text-xs font-semibold text-gray-600 mb-2">Additional Details:</p>
                <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                  {JSON.stringify(activity.metadata, null, 2)}
                </pre>
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
        <button
          onClick={() => setShowActivityModal(false)}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
        >
          Close
        </button>
      </div>
    </div>
  </div>
)}

        <div className="grid grid-cols-3 gap-6">
          {/* Left Column - Lead Info */}
          <div className="col-span-2 space-y-6">
            {/* Contact Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h2>
              <dl className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Email</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.email}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Phone</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.phone || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Job Title</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.job_title || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Source</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.source || '-'}</dd>
                </div>
              </dl>
            </div>

            {/* Company Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Company Information</h2>
              <dl className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Company Name</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.company_name}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Company Size</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.company_size || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Industry</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.industry || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Lead Score</dt>
                  <dd className="mt-1">
                    <span className="text-2xl font-bold text-blue-600">{lead.score}</span>
                    <span className="text-sm text-gray-500">/100</span>
                  </dd>
                </div>
              </dl>
            </div>

            {/* Notes */}
            {lead.notes && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Notes</h2>
                <p className="text-sm text-gray-700">{lead.notes}</p>
              </div>
            )}
          </div>

          {/* Right Column - Actions */}
          <div className="col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
              
              <div className="space-y-3">
                {/* AI Workflows */}
                <div className="border-b border-gray-200 pb-3 mb-3">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">AI Workflows</p>
                  
                  <button
                    onClick={() => handleWorkflow('qualify')}
                    disabled={processing}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium mb-2 disabled:opacity-50 flex items-center justify-center"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                    Qualify Lead (AI)
                  </button>
                  
                  <button
                    onClick={() => handleWorkflow('score')}
                    disabled={processing}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium mb-2 disabled:opacity-50 flex items-center justify-center"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Score Lead (AI)
                  </button>
                  
                  {lead.score > 0 && (
                    <button
                      onClick={() => setShowRescoreModal(true)}
                      disabled={processing}
                      className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50 flex items-center justify-center"
                    >
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Rescore with Comment
                    </button>
                  )}
                </div>

                {/* Status Updates */}
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Update Status</p>
                  
                  {lead.status === 'new' && (
                    <button
                      onClick={() => handleWorkflow('contact')}
                      disabled={processing}
                      className="w-full bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-medium mb-2 disabled:opacity-50"
                    >
                      Mark as Contacted
                    </button>
                  )}
                  
                  {lead.status === 'contacted' && (
                    <button
                      onClick={() => handleWorkflow('qualified')}
                      disabled={processing}
                      className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium mb-2 disabled:opacity-50"
                    >
                      Mark as Qualified
                    </button>
                  )}
                  
                  {lead.status === 'qualified' && (
                    <button
                      onClick={() => handleWorkflow('demo')}
                      disabled={processing}
                      className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium mb-2 disabled:opacity-50"
                    >
                      Schedule Demo
                    </button>
                  )}
                </div>

                {/* Generate Message */}
                <div className="border-t border-gray-200 pt-3">
                  <button
                    onClick={() => alert('Message generation coming soon!')}
                    className="w-full bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium flex items-center justify-center"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Generate Message (AI)
                  </button>
                </div>
              </div>

              {processing && (
                <div className="mt-4 text-center">
                  <div className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-solid border-blue-600 border-r-transparent"></div>
                  <p className="text-sm text-gray-600 mt-2">Processing...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Rescore Modal */}
      {showRescoreModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50" onClick={() => setShowRescoreModal(false)}>
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Rescore Lead with Additional Context</h2>
              <p className="text-sm text-gray-600 mt-1">Add comments or context to help AI rescore this lead more accurately</p>
            </div>
            
            <div className="px-6 py-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Comment / Additional Context *
              </label>
              <textarea
                value={rescoreComment}
                onChange={(e) => setRescoreComment(e.target.value)}
                rows="4"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Example: This lead just mentioned they have a $500k budget and need to implement by Q2. They're also evaluating 2 competitors..."
              />
              <p className="text-xs text-gray-500 mt-2">
                💡 Tip: Include information about budget, timeline, competitors, or any recent conversations that might affect the score.
              </p>
            </div>
            
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowRescoreModal(false);
                  setRescoreComment('');
                }}
                disabled={processing}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleRescore}
                disabled={processing || !rescoreComment.trim()}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium disabled:opacity-50 flex items-center"
              >
                {processing ? (
                  <>
                    <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-white border-r-transparent mr-2"></div>
                    Rescoring...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Rescore Lead
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LeadDetail;