import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { esgAPI } from '../../services/api';

/**
 * TaskMonitor - Permanent monitoring system to prevent task loading failures
 * This component runs in the background and ensures tasks are always available
 */
const TaskMonitor = () => {
  const [monitoringData, setMonitoringData] = useState({
    lastCheck: null,
    checksPerformed: 0,
    issuesFound: 0,
    autoFixesApplied: 0,
    status: 'initializing'
  });

  const runHealthCheck = async () => {
    try {
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      if (!currentUser.company_id) {
        console.warn('⚠️ TaskMonitor: No user company_id found');
        return;
      }

      console.log('🏥 TaskMonitor: Running health check...');
      
      // Check 1: API connectivity
      const apiHealthy = await checkAPIHealth();
      
      // Check 2: Task availability
      const tasksAvailable = await checkTaskAvailability();
      
      // Check 3: User authentication
      const authValid = await checkAuthenticationStatus();
      
      // Check 4: Company onboarding status
      const onboardingComplete = await checkOnboardingStatus();
      
      const allChecks = [apiHealthy, tasksAvailable, authValid, onboardingComplete];
      const failedChecks = allChecks.filter(check => !check).length;
      
      setMonitoringData(prev => ({
        ...prev,
        lastCheck: new Date().toISOString(),
        checksPerformed: prev.checksPerformed + 1,
        issuesFound: prev.issuesFound + failedChecks,
        status: failedChecks === 0 ? 'healthy' : 'issues_detected'
      }));
      
      if (failedChecks > 0) {
        console.warn(`⚠️ TaskMonitor: ${failedChecks} issues detected`);
        await attemptAutoFix();
      } else {
        console.log('✅ TaskMonitor: All systems healthy');
      }
      
    } catch (error) {
      console.error('❌ TaskMonitor: Health check failed:', error);
      setMonitoringData(prev => ({
        ...prev,
        status: 'error',
        issuesFound: prev.issuesFound + 1
      }));
    }
  };

  const checkAPIHealth = async () => {
    try {
      await esgAPI.getTasks({ limit: 1 });
      console.log('✅ TaskMonitor: API healthy');
      return true;
    } catch (error) {
      console.error('❌ TaskMonitor: API unhealthy:', error.response?.status);
      return false;
    }
  };

  const checkTaskAvailability = async () => {
    try {
      const tasks = await esgAPI.getTasks();
      const tasksList = Array.isArray(tasks) ? tasks : tasks.results || [];
      
      if (tasksList.length === 0) {
        console.warn('⚠️ TaskMonitor: No tasks found');
        return false;
      }
      
      console.log(`✅ TaskMonitor: ${tasksList.length} tasks available`);
      return true;
    } catch (error) {
      console.error('❌ TaskMonitor: Task check failed:', error);
      return false;
    }
  };

  const checkAuthenticationStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn('⚠️ TaskMonitor: No auth token found');
        return false;
      }
      
      const user = await esgAPI.getCurrentUser();
      if (!user.company_id) {
        console.warn('⚠️ TaskMonitor: User missing company_id');
        return false;
      }
      
      console.log('✅ TaskMonitor: Authentication valid');
      return true;
    } catch (error) {
      console.error('❌ TaskMonitor: Auth check failed:', error);
      return false;
    }
  };

  const checkOnboardingStatus = async () => {
    try {
      const company = await esgAPI.getCompany();
      
      if (!company.onboarding_completed) {
        console.warn('⚠️ TaskMonitor: Onboarding not completed');
        return false;
      }
      
      if (company.setup_step < 4) {
        console.warn('⚠️ TaskMonitor: Setup not complete');
        return false;
      }
      
      console.log('✅ TaskMonitor: Onboarding complete');
      return true;
    } catch (error) {
      console.error('❌ TaskMonitor: Onboarding check failed:', error);
      return false;
    }
  };

  const attemptAutoFix = async () => {
    console.log('🔧 TaskMonitor: Attempting automatic fixes...');
    
    try {
      // Fix 1: Refresh authentication
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('🔧 TaskMonitor: No token found, user needs to re-login');
        toast.warn('Session expired. Please log in again.');
        window.location.href = '/login';
        return;
      }
      
      // Fix 2: Force refresh user data
      try {
        const userData = await esgAPI.getCurrentUser();
        localStorage.setItem('user', JSON.stringify(userData));
        console.log('🔧 TaskMonitor: User data refreshed');
      } catch (error) {
        console.error('🔧 TaskMonitor: User refresh failed:', error);
      }
      
      // Fix 3: Check if onboarding needs completion
      try {
        const company = await esgAPI.getCompany();
        if (!company.onboarding_completed || company.setup_step < 4) {
          console.log('🔧 TaskMonitor: Redirecting to complete onboarding');
          toast.info('Please complete your onboarding to generate tasks.');
          window.location.href = '/onboard';
          return;
        }
      } catch (error) {
        console.error('🔧 TaskMonitor: Company check failed:', error);
      }
      
      // Fix 4: Force task list refresh
      try {
        // Clear React Query cache
        const queryClient = window.__REACT_QUERY_CLIENT__;
        if (queryClient) {
          queryClient.invalidateQueries('tasks');
          console.log('🔧 TaskMonitor: Task cache cleared');
        }
        
        // Force page refresh as last resort
        setTimeout(() => {
          console.log('🔧 TaskMonitor: Forcing page refresh');
          window.location.reload();
        }, 2000);
        
      } catch (error) {
        console.error('🔧 TaskMonitor: Cache clear failed:', error);
      }
      
      setMonitoringData(prev => ({
        ...prev,
        autoFixesApplied: prev.autoFixesApplied + 1
      }));
      
    } catch (error) {
      console.error('❌ TaskMonitor: Auto-fix failed:', error);
    }
  };

  // Run health checks periodically
  useEffect(() => {
    // Initial check after component mounts
    const initialTimeout = setTimeout(runHealthCheck, 2000);
    
    // Periodic checks every 5 minutes
    const interval = setInterval(runHealthCheck, 5 * 60 * 1000);
    
    return () => {
      clearTimeout(initialTimeout);
      clearInterval(interval);
    };
  }, []);

  // Run check when page becomes visible (user returns to tab)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        runHealthCheck();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  // Development mode: Show monitoring data
  if (process.env.NODE_ENV === 'development') {
    return (
      <div className="fixed bottom-4 right-4 bg-black/80 text-white p-3 rounded-lg text-xs font-mono z-50">
        <div className="font-semibold mb-1">TaskMonitor</div>
        <div>Status: <span className={monitoringData.status === 'healthy' ? 'text-green-400' : 'text-red-400'}>{monitoringData.status}</span></div>
        <div>Checks: {monitoringData.checksPerformed}</div>
        <div>Issues: {monitoringData.issuesFound}</div>
        <div>Fixes: {monitoringData.autoFixesApplied}</div>
        {monitoringData.lastCheck && (
          <div>Last: {new Date(monitoringData.lastCheck).toLocaleTimeString()}</div>
        )}
      </div>
    );
  }

  // Production mode: No visible UI
  return null;
};

export default TaskMonitor;