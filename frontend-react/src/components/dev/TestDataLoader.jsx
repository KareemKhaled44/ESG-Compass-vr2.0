import React from 'react';
import { toast } from 'react-toastify';
import { useQueryClient } from 'react-query';
import Button from '../ui/Button';
import { loadTestTasks, clearTestData } from '../../utils/testData';
import { replaceTasksWithMeterVersions } from '../../utils/generateSampleTasksWithMeters';
import { taskService } from '../../services/taskService';

const TestDataLoader = () => {
  const queryClient = useQueryClient();

  const handleLoadTestTasks = () => {
    try {
      const tasks = loadTestTasks();
      queryClient.invalidateQueries('tasks');
      toast.success(`Loaded ${tasks.length} test tasks for evidence collection testing!`, {
        autoClose: 3000
      });
    } catch (error) {
      console.error('Error loading test tasks:', error);
      toast.error('Failed to load test tasks');
    }
  };

  const handleClearTestData = () => {
    try {
      clearTestData();
      queryClient.invalidateQueries('tasks');
      toast.info('Test data cleared', { autoClose: 2000 });
    } catch (error) {
      console.error('Error clearing test data:', error);
      toast.error('Failed to clear test data');
    }
  };

  const handleAddMeterEnhancements = () => {
    try {
      const updatedTasks = replaceTasksWithMeterVersions();
      queryClient.invalidateQueries('tasks');
      toast.success(`✅ Enhanced tasks with meter information! ${updatedTasks.length} total tasks`, {
        autoClose: 4000
      });
    } catch (error) {
      console.error('Error enhancing tasks with meters:', error);
      toast.error('Failed to enhance tasks with meter info');
    }
  };

  const handleBackendTaskRegeneration = async () => {
    try {
      toast.info('🔄 Regenerating tasks with meters via backend...', { autoClose: 2000 });
      
      const result = await taskService.regenerateTasksWithMeters(true); // Clear existing
      queryClient.invalidateQueries('tasks');
      
      toast.success(`✅ Backend regenerated ${result.tasks_created} tasks with meter info!`, {
        autoClose: 5000
      });
    } catch (error) {
      console.error('Error regenerating backend tasks:', error);
      toast.error('Failed to regenerate tasks via backend - check console for details');
    }
  };

  const handleSyncBackendTasks = async () => {
    try {
      toast.info('🔄 Syncing backend tasks to frontend...', { autoClose: 2000 });
      
      // Try to fetch tasks from backend API
      const backendTasks = await taskService.getTasks();
      
      if (backendTasks && backendTasks.length > 0) {
        // Save to localStorage so they display immediately
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        const companyId = currentUser.company_id || 'temp';
        localStorage.setItem(`generatedTasks_${companyId}`, JSON.stringify(backendTasks));
        
        queryClient.invalidateQueries('tasks');
        toast.success(`✅ Synced ${backendTasks.length} backend tasks to frontend!`, {
          autoClose: 4000
        });
      } else {
        toast.warn('No tasks found in backend to sync');
      }
    } catch (error) {
      console.error('Error syncing backend tasks:', error);
      toast.error('Failed to sync backend tasks - check console for details');
    }
  };

  // Only show in development
  if (process.env.NODE_ENV === 'production') {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg p-4 space-y-2">
      <div className="text-xs text-text-muted font-medium mb-2">🧪 DEV TOOLS</div>
      <div className="flex flex-col space-y-2">
        <Button
          size="small"
          variant="outline"
          onClick={handleLoadTestTasks}
          className="text-xs"
        >
          Load Test Tasks
        </Button>
        <Button
          size="small"
          variant="outline" 
          onClick={handleClearTestData}
          className="text-xs"
        >
          Clear Test Data
        </Button>
        <Button
          size="small"
          variant="primary"
          onClick={handleAddMeterEnhancements}
          className="text-xs"
        >
          🔌 Add Meter Info
        </Button>
        <Button
          size="small"
          variant="secondary"
          onClick={handleBackendTaskRegeneration}
          className="text-xs"
        >
          🏭 Backend Regen
        </Button>
        <Button
          size="small"
          variant="outline"
          onClick={handleSyncBackendTasks}
          className="text-xs"
        >
          🔄 Sync Backend
        </Button>
      </div>
      <div className="text-xs text-text-muted">
        Sync/Generate tasks from backend
      </div>
    </div>
  );
};

export default TestDataLoader;