// services/dataExtractionService.js

class DataExtractionService {
  constructor() {
    this.extractionRules = {
      // Define patterns for different types of data extraction
      utilityBills: {
        patterns: [
          { regex: /electricity.*?(\d+\.?\d*)\s*kwh/i, metric: 'energy_consumption', unit: 'kWh' },
          { regex: /water.*?(\d+\.?\d*)\s*(gallons|liters|m3)/i, metric: 'water_usage', unit: 'L' },
          { regex: /total.*?amount.*?(\d+\.?\d*)/i, metric: 'utility_cost', unit: 'AED' },
          { regex: /carbon.*?(\d+\.?\d*)\s*kg/i, metric: 'carbon_emissions', unit: 'kg' }
        ]
      },
      employeeReports: {
        patterns: [
          { regex: /satisfaction.*?(\d+\.?\d*)%/i, metric: 'employee_satisfaction', unit: '%' },
          { regex: /training.*?hours.*?(\d+\.?\d*)/i, metric: 'training_hours', unit: 'hours' },
          { regex: /diversity.*?(\d+\.?\d*)%/i, metric: 'diversity_ratio', unit: '%' },
          { regex: /incidents.*?(\d+)/i, metric: 'safety_incidents', unit: 'count' }
        ]
      },
      wasteReports: {
        patterns: [
          { regex: /recycled.*?(\d+\.?\d*)\s*kg/i, metric: 'waste_recycled', unit: 'kg' },
          { regex: /landfill.*?(\d+\.?\d*)\s*kg/i, metric: 'waste_landfill', unit: 'kg' },
          { regex: /composted.*?(\d+\.?\d*)\s*kg/i, metric: 'waste_composted', unit: 'kg' }
        ]
      }
    };
  }

  // Main extraction method
  async extractDataFromTaskEvidence(taskId) {
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    const companyId = currentUser.company_id || 'temp';
    
    // Log user isolation details
    console.log(`👤 Current user: ${currentUser.username || 'unknown'}`);
    console.log(`🏢 Company ID: ${companyId}`);
    
    // Get evidence from localStorage with proper isolation
    const evidenceKey = `task_evidence_${companyId}_${taskId}`;
    const evidence = JSON.parse(localStorage.getItem(evidenceKey) || '[]');
    
    console.log(`🔍 Task ${taskId} - Evidence key: ${evidenceKey}`);
    console.log(`🔍 Task ${taskId} - Processing ${evidence.length} evidence items for user: ${currentUser.username}`);
    
    const extractedData = [];
    
    for (const item of evidence) {
      console.log(`📄 Processing item:`, item);
      
      if (item.type === 'file') {
        const data = await this.extractFromFile(item, taskId);
        if (data && data.length > 0) {
          console.log(`✅ Extracted ${data.length} data points from file:`, data);
          extractedData.push(...data);
        } else {
          console.log(`⚠️ No data extracted from file: ${item.fileName}`);
        }
      } else if (item.type === 'data') {
        // Direct data entry
        const dataPoint = {
          taskId,
          metric: this.inferMetricFromTask(taskId),
          value: parseFloat(item.value),
          unit: this.inferUnitFromTask(taskId),
          source: 'manual_entry',
          timestamp: item.uploaded_at || new Date().toISOString(),
          confidence: 1.0
        };
        console.log(`📊 Direct data entry:`, dataPoint);
        extractedData.push(dataPoint);
      }
    }
    
    console.log(`🎯 Task ${taskId} - Total extracted: ${extractedData.length} data points for user: ${currentUser.username}`);
    return extractedData;
  }

  // Extract data from different file types
  async extractFromFile(fileItem, taskId) {
    const { fileName, fileData, fileType } = fileItem;
    
    if (!fileData) return null;
    
    try {
      if (fileName?.endsWith('.csv')) {
        return await this.extractFromCSV(fileData, taskId);
      } else if (fileType?.startsWith('text/')) {
        return await this.extractFromText(fileData, taskId);
      }
      // Note: PDF and Excel extraction would require additional libraries
      // For now, we'll focus on text-based extraction
    } catch (error) {
      console.error('Error extracting data from file:', error);
      return null;
    }
  }

  // Extract from text content
  async extractFromText(fileData, taskId) {
    try {
      const text = typeof fileData === 'string' ? fileData : atob(fileData.split(',')[1]);
      return this.extractMetricsFromText(text, taskId);
    } catch (error) {
      console.error('Text extraction error:', error);
      return null;
    }
  }

  // Extract metrics from text using patterns
  extractMetricsFromText(text, taskId) {
    const extractedData = [];
    const taskType = this.getTaskType(taskId);
    const patterns = this.extractionRules[taskType] || this.extractionRules.utilityBills;
    
    patterns.patterns.forEach(pattern => {
      const matches = text.match(pattern.regex);
      if (matches && matches[1]) {
        extractedData.push({
          taskId,
          metric: pattern.metric,
          value: parseFloat(matches[1]),
          unit: pattern.unit,
          source: 'text_extraction',
          timestamp: new Date().toISOString(),
          confidence: 0.7
        });
      }
    });
    
    return extractedData;
  }

  // Extract from CSV files
  async extractFromCSV(fileData, taskId) {
    try {
      console.log('🔍 Starting CSV extraction for task:', taskId);
      
      // Decode base64 CSV data
      const csvText = typeof fileData === 'string' ? fileData : atob(fileData.split(',')[1]);
      console.log('📄 CSV content preview:', csvText.substring(0, 200));
      
      const lines = csvText.split('\n').filter(line => line.trim().length > 0);
      if (lines.length < 2) {
        console.log('⚠️ CSV has insufficient data (needs header + at least 1 row)');
        return [];
      }
      
      const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
      console.log('📋 CSV headers:', headers);
      
      const extractedData = [];
      
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        const row = {};
        headers.forEach((header, index) => {
          row[header] = values[index]?.trim();
        });
        
        console.log(`📊 Row ${i}:`, row);
        
        // Extract based on column names (more flexible matching)
        const energyHeaders = ['energy', 'kwh', 'electricity', 'power', 'electric'];
        const waterHeaders = ['water', 'water usage', 'water (l)', 'liters', 'gallons'];
        const wasteHeaders = ['waste', 'waste (kg)', 'waste generated', 'garbage', 'trash'];
        
        // Check for energy data
        for (const header of headers) {
          if (energyHeaders.some(eh => header.includes(eh))) {
            const value = parseFloat(row[header]);
            if (!isNaN(value)) {
              extractedData.push({
                taskId,
                metric: 'energy_consumption',
                value: value,
                unit: 'kWh',
                source: 'csv',
                timestamp: row['date'] || row['time'] || new Date().toISOString(),
                confidence: 0.95
              });
              console.log('⚡ Energy data extracted:', value);
            }
          }
          
          // Check for water data
          if (waterHeaders.some(wh => header.includes(wh))) {
            const value = parseFloat(row[header]);
            if (!isNaN(value)) {
              extractedData.push({
                taskId,
                metric: 'water_usage',
                value: value,
                unit: 'L',
                source: 'csv',
                timestamp: row['date'] || row['time'] || new Date().toISOString(),
                confidence: 0.95
              });
              console.log('💧 Water data extracted:', value);
            }
          }
          
          // Check for waste data
          if (wasteHeaders.some(wst => header.includes(wst))) {
            const value = parseFloat(row[header]);
            if (!isNaN(value)) {
              extractedData.push({
                taskId,
                metric: 'waste_generated',
                value: value,
                unit: 'kg',
                source: 'csv',
                timestamp: row['date'] || row['time'] || new Date().toISOString(),
                confidence: 0.95
              });
              console.log('🗑️ Waste data extracted:', value);
            }
          }
        }
      }
      
      console.log('✅ CSV extraction complete:', extractedData);
      return extractedData;
    } catch (error) {
      console.error('❌ CSV extraction error:', error);
      return [];
    }
  }

  // Infer metric type from task ID
  inferMetricFromTask(taskId) {
    const taskMetricMap = {
      '1': 'air_quality_index',
      '2': 'food_waste',
      '3': 'recycling_rate',
      '4': 'energy_consumption',
      '5': 'student_participation',
      '6': 'uniform_reuse_rate',
      '7': 'curriculum_integration',
      '8': 'policy_compliance'
    };
    return taskMetricMap[taskId] || 'general_metric';
  }

  // Infer unit from task ID
  inferUnitFromTask(taskId) {
    const taskUnitMap = {
      '1': 'AQI',
      '2': 'kg',
      '3': '%',
      '4': 'kWh',
      '5': '%',
      '6': '%',
      '7': 'score',
      '8': 'score'
    };
    return taskUnitMap[taskId] || 'units';
  }

  // Get task type for extraction rules
  getTaskType(taskId) {
    const taskTypeMap = {
      '1': 'employeeReports',
      '2': 'wasteReports',
      '3': 'wasteReports',
      '4': 'utilityBills',
      '5': 'employeeReports',
      '6': 'wasteReports',
      '7': 'employeeReports',
      '8': 'employeeReports'
    };
    return taskTypeMap[taskId] || 'utilityBills';
  }

  // Aggregate data for dashboard
  async aggregateDataForDashboard() {
    const allData = [];
    
    // Extract data from all tasks
    for (let taskId = 1; taskId <= 8; taskId++) {
      const taskData = await this.extractDataFromTaskEvidence(taskId.toString());
      if (taskData && taskData.length > 0) {
        allData.push(...taskData);
      }
    }
    
    // Group by metric and calculate aggregates
    const aggregated = {};
    
    allData.forEach(item => {
      if (!aggregated[item.metric]) {
        aggregated[item.metric] = {
          metric: item.metric,
          values: [],
          latest: null,
          average: 0,
          total: 0,
          unit: item.unit,
          trend: []
        };
      }
      
      aggregated[item.metric].values.push(item.value);
      aggregated[item.metric].trend.push({
        date: item.timestamp,
        value: item.value,
        source: item.source
      });
    });
    
    // Calculate statistics
    Object.keys(aggregated).forEach(metric => {
      const data = aggregated[metric];
      data.total = data.values.reduce((sum, val) => sum + val, 0);
      data.average = data.total / data.values.length;
      data.latest = data.values[data.values.length - 1];
      
      // Sort trend by date
      data.trend.sort((a, b) => new Date(a.date) - new Date(b.date));
      
      // Calculate percentage change
      if (data.values.length > 1) {
        const previous = data.values[data.values.length - 2];
        data.change = ((data.latest - previous) / previous) * 100;
      }
    });
    
    // Store in localStorage for dashboard
    localStorage.setItem('dashboard_extracted_metrics', JSON.stringify(aggregated));
    
    return aggregated;
  }

  // Helper method to add sample data for demonstration
  generateSampleData() {
    const sampleMetrics = {
      energy_consumption: {
        metric: 'energy_consumption',
        values: [1200, 1150, 1100, 1050],
        latest: 1050,
        average: 1125,
        total: 4500,
        unit: 'kWh',
        trend: [
          { date: '2024-01-01', value: 1200, source: 'csv' },
          { date: '2024-02-01', value: 1150, source: 'csv' },
          { date: '2024-03-01', value: 1100, source: 'manual_entry' },
          { date: '2024-04-01', value: 1050, source: 'csv' }
        ],
        change: -4.5
      },
      water_usage: {
        metric: 'water_usage',
        values: [2500, 2400, 2300, 2200],
        latest: 2200,
        average: 2350,
        total: 9400,
        unit: 'L',
        trend: [
          { date: '2024-01-01', value: 2500, source: 'csv' },
          { date: '2024-02-01', value: 2400, source: 'csv' },
          { date: '2024-03-01', value: 2300, source: 'manual_entry' },
          { date: '2024-04-01', value: 2200, source: 'csv' }
        ],
        change: -4.3
      },
      employee_satisfaction: {
        metric: 'employee_satisfaction',
        values: [78, 82, 85, 87],
        latest: 87,
        average: 83,
        total: 332,
        unit: '%',
        trend: [
          { date: '2024-01-01', value: 78, source: 'manual_entry' },
          { date: '2024-02-01', value: 82, source: 'csv' },
          { date: '2024-03-01', value: 85, source: 'csv' },
          { date: '2024-04-01', value: 87, source: 'manual_entry' }
        ],
        change: 2.4
      }
    };

    localStorage.setItem('dashboard_extracted_metrics', JSON.stringify(sampleMetrics));
    return sampleMetrics;
  }
}

export const dataExtractionService = new DataExtractionService();