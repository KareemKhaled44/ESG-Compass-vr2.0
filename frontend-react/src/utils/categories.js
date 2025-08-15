// Central category management system
// This ensures all parts of the application use consistent categories

export const TASK_CATEGORIES = {
  ENVIRONMENTAL: 'environmental',
  SOCIAL: 'social',
  GOVERNANCE: 'governance',
  GENERAL: 'general'
};

// Standardized category configuration
export const CATEGORY_CONFIG = [
  {
    id: TASK_CATEGORIES.ENVIRONMENTAL,
    label: 'Environmental',
    icon: 'fa-solid fa-leaf',
    color: '#2EC57D', // brand-green
    description: 'Environmental sustainability and conservation tasks'
  },
  {
    id: TASK_CATEGORIES.SOCIAL,
    label: 'Social',
    icon: 'fa-solid fa-users',
    color: '#3DAEFF', // brand-blue
    description: 'Social responsibility and community engagement tasks'
  },
  {
    id: TASK_CATEGORIES.GOVERNANCE,
    label: 'Governance',
    icon: 'fa-solid fa-shield-halved',
    color: '#20C5C5', // brand-teal
    description: 'Corporate governance and compliance tasks'
  },
  {
    id: TASK_CATEGORIES.GENERAL,
    label: 'General',
    icon: 'fa-solid fa-tasks',
    color: '#9CA3AF', // gray
    description: 'General ESG and administrative tasks'
  }
];

// Helper functions
export const getCategoryConfig = (categoryId) => {
  return CATEGORY_CONFIG.find(cat => cat.id === categoryId) || CATEGORY_CONFIG.find(cat => cat.id === TASK_CATEGORIES.GENERAL);
};

export const getCategoryIcon = (categoryId) => {
  const config = getCategoryConfig(categoryId);
  return config.icon;
};

export const getCategoryColor = (categoryId) => {
  const config = getCategoryConfig(categoryId);
  return config.color;
};

export const getCategoryLabel = (categoryId) => {
  const config = getCategoryConfig(categoryId);
  return config.label;
};

// Options for form selects
export const getCategoryOptions = (includeAll = false) => {
  const options = CATEGORY_CONFIG.map(cat => ({
    value: cat.id,
    label: cat.label
  }));
  
  if (includeAll) {
    options.unshift({ value: 'all', label: 'All Categories' });
  }
  
  return options;
};

// Auto-categorize task based on title/description
export const suggestTaskCategory = (title = '', description = '', actionRequired = '') => {
  const text = `${title} ${description} ${actionRequired}`.toLowerCase();
  
  // Environmental keywords
  const environmentalKeywords = [
    'environment', 'environmental', 'energy', 'water', 'waste', 'recycling',
    'carbon', 'emissions', 'sustainability', 'green', 'eco', 'climate',
    'pollution', 'renewable', 'conservation', 'biodiversity', 'air quality',
    'utilities', 'electricity', 'dewa', 'addc', 'meter', 'kwh', 'm³'
  ];
  
  // Social keywords
  const socialKeywords = [
    'social', 'community', 'employee', 'workers', 'safety', 'health',
    'diversity', 'inclusion', 'equity', 'training', 'education', 'welfare',
    'human rights', 'labor', 'workplace', 'culture', 'engagement',
    'food policy', 'curriculum', 'wellness', 'uniform'
  ];
  
  // Governance keywords
  const governanceKeywords = [
    'governance', 'compliance', 'policy', 'regulation', 'audit', 'risk',
    'ethics', 'transparency', 'accountability', 'board', 'management',
    'reporting', 'disclosure', 'framework', 'standard', 'certification',
    'signed', 'approved', 'document'
  ];
  
  // Count keyword matches
  const environmentalScore = environmentalKeywords.filter(keyword => text.includes(keyword)).length;
  const socialScore = socialKeywords.filter(keyword => text.includes(keyword)).length;
  const governanceScore = governanceKeywords.filter(keyword => text.includes(keyword)).length;
  
  // Return category with highest score
  if (environmentalScore >= socialScore && environmentalScore >= governanceScore && environmentalScore > 0) {
    return TASK_CATEGORIES.ENVIRONMENTAL;
  } else if (socialScore >= governanceScore && socialScore > 0) {
    return TASK_CATEGORIES.SOCIAL;
  } else if (governanceScore > 0) {
    return TASK_CATEGORIES.GOVERNANCE;
  }
  
  // Default fallback
  return TASK_CATEGORIES.GENERAL;
};

// Validate category
export const isValidCategory = (categoryId) => {
  return Object.values(TASK_CATEGORIES).includes(categoryId);
};

// Normalize category (fix common variations)
export const normalizeCategory = (categoryId) => {
  if (!categoryId) return TASK_CATEGORIES.GENERAL;
  
  const normalized = categoryId.toLowerCase().trim();
  
  // Handle common variations
  const categoryMap = {
    'compliance': TASK_CATEGORIES.GOVERNANCE,
    'reporting': TASK_CATEGORIES.GOVERNANCE,
    'admin': TASK_CATEGORIES.GENERAL,
    'administrative': TASK_CATEGORIES.GENERAL,
    'env': TASK_CATEGORIES.ENVIRONMENTAL,
    'soc': TASK_CATEGORIES.SOCIAL,
    'gov': TASK_CATEGORIES.GOVERNANCE
  };
  
  if (categoryMap[normalized]) {
    return categoryMap[normalized];
  }
  
  // Check if it's a valid category
  if (isValidCategory(normalized)) {
    return normalized;
  }
  
  // Try to auto-categorize
  return suggestTaskCategory(categoryId);
};