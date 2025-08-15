/**
 * Sample task generator with enhanced meter information
 * This demonstrates the v1-style meter enhancement feature
 */

export const generateSampleTasksWithMeters = (companyId = 'temp') => {
  // Sample meter information (simulating what would come from backend)
  const sampleMeters = [
    {
      id: 'ELE001',
      number: 'ELE001',
      type: 'electricity',
      provider: 'DEWA',
      location: 'Main Building',
      location_id: '1'
    },
    {
      id: 'WAT001', 
      number: 'WAT001',
      type: 'water',
      provider: 'DEWA',
      location: 'Main Building',
      location_id: '1'
    },
    {
      id: 'ELE002',
      number: 'ELE002', 
      type: 'electricity',
      provider: 'DEWA',
      location: 'Warehouse',
      location_id: '2'
    }
  ];

  const tasksWithMeters = [
    {
      id: `task_meter_${Date.now()}_001`,
      title: 'Track electricity consumption monthly (Meter: ELE001)',
      description: 'Establish monthly energy consumption tracking for all facilities\n\nSpecific Meters to Track:\n• Electricity Meter ELE001 at Main Building (DEWA)\n',
      compliance_context: 'UAE Climate Law: Energy efficiency reporting requirement',
      action_required: 'Monthly utility bills\n\nSpecific Action: Read meter ELE001 (electricity) at Main Building and record monthly consumption from DEWA bills.',
      category: 'environmental',
      priority: 'high',
      status: 'todo',
      due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      estimated_hours: 8,
      framework_tags: ['UAE Climate Law', 'Dubai Sustainable Tourism'],
      sector: 'manufacturing',
      task_type: 'evidence_upload',
      created_at: new Date().toISOString(),
      company_id: companyId,
      progress_percentage: 0
    },
    {
      id: `task_meter_${Date.now()}_002`,
      title: 'Monitor water usage monthly (Meter: WAT001)',
      description: 'Document current water consumption and identify conservation opportunities\n\nSpecific Meters to Track:\n• Water Meter WAT001 at Main Building (DEWA)\n',
      compliance_context: 'UAE Water Security Strategy 2036',
      action_required: 'Review water bills and conduct facility water audit\n\nSpecific Action: Read meter WAT001 (water) at Main Building and record monthly consumption from DEWA bills.',
      category: 'environmental',
      priority: 'medium', 
      status: 'in_progress',
      due_date: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000).toISOString(),
      estimated_hours: 6,
      framework_tags: ['UAE Water Security Strategy'],
      sector: 'manufacturing',
      task_type: 'evidence_upload',
      created_at: new Date().toISOString(),
      company_id: companyId,
      progress_percentage: 25,
      assigned_user: {
        id: 1,
        full_name: 'John Smith',
        email: 'john.smith@company.com'
      }
    },
    {
      id: `task_meter_${Date.now()}_003`,
      title: 'Track warehouse electricity consumption (Meters: ELE001, ELE002)',
      description: 'Monitor electricity usage across multiple facilities\n\nSpecific Meters to Track:\n• Electricity Meter ELE001 at Main Building (DEWA)\n• Electricity Meter ELE002 at Warehouse (DEWA)\n',
      compliance_context: 'Federal Energy Management Regulation in Industrial Facilities',
      action_required: 'Monthly electricity bills\n\nSpecific Meters to Track:\n- ELE001 (electricity) at Main Building\n- ELE002 (electricity) at Warehouse\n\nRecord monthly consumption from provider bills for each meter.',
      category: 'environmental',
      priority: 'high',
      status: 'todo',
      due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      estimated_hours: 12,
      framework_tags: ['Federal Energy Management Regulation'],
      sector: 'manufacturing',
      task_type: 'evidence_upload',
      created_at: new Date().toISOString(),
      company_id: companyId,
      progress_percentage: 0
    }
  ];

  return tasksWithMeters;
};

// Function to replace existing tasks with meter-enhanced versions
export const replaceTasksWithMeterVersions = () => {
  try {
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    const companyId = currentUser.company_id || 'temp';
    
    // Get existing tasks
    const existingTasks = JSON.parse(localStorage.getItem(`generatedTasks_${companyId}`) || '[]');
    
    // Generate new meter-enhanced tasks
    const meterTasks = generateSampleTasksWithMeters(companyId);
    
    // Keep non-electricity/water tasks and replace the relevant ones
    const filteredTasks = existingTasks.filter(task => 
      !task.title.toLowerCase().includes('electricity') && 
      !task.title.toLowerCase().includes('water') &&
      !task.title.toLowerCase().includes('track') &&
      !task.title.toLowerCase().includes('monitor')
    );
    
    // Combine with meter-enhanced tasks
    const updatedTasks = [...filteredTasks, ...meterTasks];
    
    // Save back to localStorage
    localStorage.setItem(`generatedTasks_${companyId}`, JSON.stringify(updatedTasks));
    
    console.log('✅ Tasks updated with meter information');
    console.log(`📊 Total tasks: ${updatedTasks.length}`);
    console.log(`🔌 Meter-enhanced tasks: ${meterTasks.length}`);
    
    return updatedTasks;
    
  } catch (error) {
    console.error('❌ Error updating tasks with meter info:', error);
    return [];
  }
};

export default {
  generateSampleTasksWithMeters,
  replaceTasksWithMeterVersions
};