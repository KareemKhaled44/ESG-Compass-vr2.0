import React, { useState, useEffect } from 'react';
import Button from '../ui/Button';
import Card from '../ui/Card';

const DataDebugger = () => {
  const [debugData, setDebugData] = useState({});
  const [isVisible, setIsVisible] = useState(false);

  const collectDebugData = () => {
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    const companyId = currentUser.company_id || 'temp';
    
    // Collect all localStorage data related to tasks
    const allLocalStorageKeys = Object.keys(localStorage);
    const taskRelatedKeys = allLocalStorageKeys.filter(key => 
      key.includes('task') || 
      key.includes('evidence') || 
      key.includes('generatedTasks') ||
      key.includes('onboarding')
    );

    const debugInfo = {
      currentUser: {
        id: currentUser.id,
        email: currentUser.email,
        company_id: currentUser.company_id,
        fullUser: currentUser
      },
      companyId,
      taskRelatedData: {},
      allTaskKeys: taskRelatedKeys,
      evidenceKeys: [],
      totalLocalStorageKeys: allLocalStorageKeys.length
    };

    // Get all task evidence keys
    const evidenceKeys = allLocalStorageKeys.filter(key => key.includes('task_evidence'));
    debugInfo.evidenceKeys = evidenceKeys;

    // Collect actual data for each key
    taskRelatedKeys.forEach(key => {
      try {
        const data = localStorage.getItem(key);
        if (data) {
          try {
            const parsed = JSON.parse(data);
            debugInfo.taskRelatedData[key] = {
              type: 'JSON',
              length: Array.isArray(parsed) ? parsed.length : Object.keys(parsed).length,
              sample: Array.isArray(parsed) ? parsed.slice(0, 2) : parsed,
              raw: data.length > 500 ? `${data.substring(0, 500)}...` : data
            };
          } catch {
            debugInfo.taskRelatedData[key] = {
              type: 'String',
              length: data.length,
              raw: data.length > 200 ? `${data.substring(0, 200)}...` : data
            };
          }
        }
      } catch (error) {
        debugInfo.taskRelatedData[key] = { error: error.message };
      }
    });

    // Check specific keys
    debugInfo.specificChecks = {
      generatedTasks: localStorage.getItem(`generatedTasks_${companyId}`),
      onboardingCompleted: localStorage.getItem('onboardingCompleted'),
      user: localStorage.getItem('user'),
      access_token: localStorage.getItem('access_token') ? 'Present' : 'Missing',
      refresh_token: localStorage.getItem('refresh_token') ? 'Present' : 'Missing',
      authToken: localStorage.getItem('authToken') ? 'Present' : 'Missing'
    };

    setDebugData(debugInfo);
  };

  const copyDebugData = () => {
    const debugText = JSON.stringify(debugData, null, 2);
    navigator.clipboard.writeText(debugText).then(() => {
      alert('Debug data copied to clipboard!');
    });
  };

  const clearAllTaskData = () => {
    if (window.confirm('Are you sure you want to clear ALL task-related data? This cannot be undone!')) {
      const taskKeys = Object.keys(localStorage).filter(key => 
        key.includes('task') || 
        key.includes('evidence') || 
        key.includes('generatedTasks')
      );
      
      taskKeys.forEach(key => localStorage.removeItem(key));
      alert(`Cleared ${taskKeys.length} task-related keys`);
      collectDebugData();
    }
  };

  useEffect(() => {
    collectDebugData();
  }, []);

  if (!isVisible) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <Button 
          variant="outline" 
          size="small"
          onClick={() => setIsVisible(true)}
          className="bg-red-500 text-white border-red-600"
        >
          🐛 Debug Data
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <Card className="max-w-4xl w-full max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-text-high">🐛 Data Debugger</h2>
          <div className="flex space-x-2">
            <Button variant="outline" size="small" onClick={collectDebugData}>
              Refresh
            </Button>
            <Button variant="outline" size="small" onClick={copyDebugData}>
              Copy Data
            </Button>
            <Button variant="outline" size="small" onClick={() => setIsVisible(false)}>
              Close
            </Button>
          </div>
        </div>

        <div className="space-y-4">
          {/* Current User Info */}
          <div className="bg-white/5 p-4 rounded">
            <h3 className="font-semibold text-text-high mb-2">👤 Current User</h3>
            <div className="text-sm space-y-1">
              <div><span className="text-text-muted">ID:</span> {debugData.currentUser?.id || 'N/A'}</div>
              <div><span className="text-text-muted">Email:</span> {debugData.currentUser?.email || 'N/A'}</div>
              <div><span className="text-text-muted">Company ID:</span> {debugData.currentUser?.company_id || 'N/A'}</div>
            </div>
          </div>

          {/* Task Keys */}
          <div className="bg-white/5 p-4 rounded">
            <h3 className="font-semibold text-text-high mb-2">🔑 Task-Related Keys ({debugData.allTaskKeys?.length || 0})</h3>
            <div className="text-sm space-y-1 max-h-40 overflow-y-auto">
              {debugData.allTaskKeys?.map((key, index) => (
                <div key={index} className="text-text-muted font-mono">{key}</div>
              ))}
            </div>
          </div>

          {/* Evidence Keys */}
          <div className="bg-white/5 p-4 rounded">
            <h3 className="font-semibold text-text-high mb-2">📎 Evidence Keys ({debugData.evidenceKeys?.length || 0})</h3>
            <div className="text-sm space-y-1 max-h-40 overflow-y-auto">
              {debugData.evidenceKeys?.map((key, index) => (
                <div key={index} className="text-text-muted font-mono">{key}</div>
              ))}
            </div>
          </div>

          {/* Task Data Details */}
          <div className="bg-white/5 p-4 rounded">
            <h3 className="font-semibold text-text-high mb-2">📋 Task Data Details</h3>
            <div className="text-sm space-y-2 max-h-60 overflow-y-auto">
              {Object.entries(debugData.taskRelatedData || {}).map(([key, data]) => (
                <div key={key} className="border-l-2 border-brand-green pl-2">
                  <div className="text-text-high font-mono text-xs">{key}</div>
                  <div className="text-text-muted">
                    Type: {data.type}, Length: {data.length}
                  </div>
                  {data.sample && (
                    <div className="text-text-muted text-xs mt-1">
                      Sample: {JSON.stringify(data.sample)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="bg-red-500/10 border border-red-500/20 p-4 rounded">
            <h3 className="font-semibold text-red-400 mb-2">⚠️ Danger Zone</h3>
            <Button 
              variant="outline" 
              size="small"
              onClick={clearAllTaskData}
              className="border-red-500 text-red-400"
            >
              Clear All Task Data
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default DataDebugger;