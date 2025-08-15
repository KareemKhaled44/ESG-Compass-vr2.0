/**
 * ESG Sector-Specific Questions and Frameworks
 * Parsed from "2jul-Sector-Specific ESG Scoping for UAE SMEs.md"
 * 
 * IMPORTANT: This data structure follows the EXACT categorization from the official document
 * Each sector has its own specific category structure, not generic ESG categories
 */

export const esgSectorData = {
  hospitality: {
    name: 'Hospitality & Tourism',
    categories: ['Governance & Management', 'Energy', 'Water', 'Waste', 'Supply Chain'],
    frameworks: [
      'Dubai Sustainable Tourism (DST)',
      'Green Key Global', 
      'UAE Climate Law',
      'UAE Waste Management Law',
      'Public Health & Hygiene Regulations'
    ],
    questions: [
      // Governance & Management
      {
        id: 'hosp_gov_1',
        question: 'Do you have a designated person or team responsible for your hotel\'s sustainability efforts?',
        rationale: 'Management Structure',
        frameworks: 'Green Key: 1.1 Environmental Manager, DST: 1.3 Establish a committee',
        data_source: 'Job description, Committee meeting minutes',
        category: 'Governance & Management',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'hosp_gov_2',
        question: 'Do you have a written sustainability policy signed by senior management?',
        rationale: 'Formal Commitment',
        frameworks: 'Green Key: 1.2 Sustainability Policy, DST: 1.3 (Implied foundation for committee)',
        data_source: 'Signed policy document',
        category: 'Governance & Management',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'hosp_gov_3',
        question: 'Do you provide regular training for all staff on your sustainability goals and their specific roles?',
        rationale: 'Employee Engagement',
        frameworks: 'DST: 1.4 Train employees, Green Key: 2.1 Staff training',
        data_source: 'Training records, materials',
        category: 'Governance & Management',
        required: true,
        type: 'yes_no'
      },
      
      // Energy
      {
        id: 'hosp_energy_1',
        question: 'Do you track your total monthly electricity consumption from the public grid (e.g., DEWA) in kilowatt-hours (kWh)?',
        rationale: 'Scope 2 Emissions',
        frameworks: 'DST Carbon Calculator: Mandatory Input, Green Key: 7.1 Monthly energy registration',
        data_source: 'Monthly utility bills',
        category: 'Energy',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'hosp_energy_2',
        question: 'Do you use any fuel (like diesel or petrol) for on-site power generators?',
        rationale: 'Scope 1 Emissions',
        frameworks: 'DST Carbon Calculator: Mandatory Input (Petrol, Diesel)',
        data_source: 'Fuel purchase receipts/logs',
        category: 'Energy',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'hosp_energy_3',
        question: 'Do you use district cooling services?',
        rationale: 'Scope 2 Emissions',
        frameworks: 'DST Carbon Calculator: Mandatory Input',
        data_source: 'Monthly district cooling bills',
        category: 'Energy',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'hosp_energy_4',
        question: 'Do you use Liquefied Petroleum Gas (LPG) for cooking or heating?',
        rationale: 'Scope 1 Emissions',
        frameworks: 'DST Carbon Calculator: Mandatory Input',
        data_source: 'LPG purchase invoices/logs',
        category: 'Energy',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'hosp_energy_5',
        question: 'Are at least 75% of your light bulbs energy-efficient models (like LED)?',
        rationale: 'Energy Efficiency',
        frameworks: 'Green Key: 7.3 Energy-efficient bulbs, DST: 2.1 Energy efficiency plan',
        data_source: 'Purchase invoices, lighting inventory',
        category: 'Energy',
        required: false,
        type: 'yes_no'
      },
      
      // Water
      {
        id: 'hosp_water_1',
        question: 'Do you track your total monthly water consumption in cubic meters (m³)?',
        rationale: 'Water Consumption',
        frameworks: 'DST Carbon Calculator: Mandatory Input, Green Key: 4.1 Monthly water registration',
        data_source: 'Monthly water utility bills',
        category: 'Water',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'hosp_water_2',
        question: 'Do the showers in your guest rooms have a flow rate of 9 litres per minute or less?',
        rationale: 'Water Efficiency',
        frameworks: 'Green Key: 4.4 Shower water flow, DST: 3.1 Water conservation plan',
        data_source: 'Technical specifications for showerheads',
        category: 'Water',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'hosp_water_3',
        question: 'Do you have a program that encourages guests to reuse their towels and linens?',
        rationale: 'Guest Engagement',
        frameworks: 'DST: 3.2 Reuse guest towels/linens, Green Key: 5.1 & 5.2 Guest information',
        data_source: 'Photos of in-room signage',
        category: 'Water',
        required: false,
        type: 'yes_no'
      },
      
      // Waste
      {
        id: 'hosp_waste_1',
        question: 'Do you measure the total amount of waste sent to landfill each month (in kg or tonnes)?',
        rationale: 'Waste to Landfill',
        frameworks: 'DST Carbon Calculator: Mandatory Input',
        data_source: 'Waste contractor invoices/reports',
        category: 'Waste',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'hosp_waste_2',
        question: 'Do you separate waste for recycling (e.g., paper, plastic, glass) and track the amounts recycled?',
        rationale: 'Recycling Rate',
        frameworks: 'DST Carbon Calculator: Mandatory Input, Green Key: 6.1 Waste separation',
        data_source: 'Waste contractor invoices/reports',
        category: 'Waste',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'hosp_waste_3',
        question: 'Do you use bulk, refillable dispensers for toiletries (soap, shampoo) in guest bathrooms?',
        rationale: 'Plastic Waste Reduction',
        frameworks: 'Green Key: 6.11 Toiletries in dispensers, DST: 4.2 Reduce waste from toiletries',
        data_source: 'Photos of dispensers in bathrooms',
        category: 'Waste',
        required: false,
        type: 'yes_no'
      },
      
      // Supply Chain
      {
        id: 'hosp_supply_1',
        question: 'Do you have a policy to give preference to local, organic, or fair-trade suppliers?',
        rationale: 'Sustainable Procurement',
        frameworks: 'DST: 6.1 Sustainable purchasing plan, Green Key: 8.1 Purchase from sustainable categories',
        data_source: 'Purchasing policy, sample invoices',
        category: 'Supply Chain',
        required: false,
        type: 'yes_no'
      }
    ]
  },

  construction: {
    name: 'Construction & Real Estate',
    categories: ['Project Planning & Design', 'Construction Phase', 'Operational Phase'],
    frameworks: [
      'Al Sa\'fat Dubai',
      'Estidama Pearl Rating System',
      'LEED',
      'BREEAM', 
      'UAE Climate Law',
      'UAE Waste Management Law',
      'UAE Environment Law'
    ],
    questions: [
      // Project Planning & Design
      {
        id: 'const_design_1',
        question: 'Are you pursuing a green building certification for this project (e.g., Al Sa\'fat, Estidama, LEED)?',
        rationale: 'Sustainable Design',
        frameworks: 'Al Sa\'fat: Mandatory for all new Dubai buildings, Estidama: Mandatory for all new Abu Dhabi buildings, LEED: Voluntary international standard',
        data_source: 'Project design brief, registration with certification body',
        category: 'Project Planning & Design',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'const_design_2',
        question: 'Have you conducted an Environmental Impact Assessment (EIA) for this project?',
        rationale: 'Risk Assessment',
        frameworks: 'Dubai Municipality: Required for projects with potential environmental impact, JAFZA: Required for projects in the free zone',
        data_source: 'EIA Report',
        category: 'Project Planning & Design',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'const_design_3',
        question: 'Does your building design incorporate features to reduce energy use, such as high-performance insulation or window glazing?',
        rationale: 'Passive Design & Energy Efficiency',
        frameworks: 'Al Sa\'fat / Dubai Regulations: Mandates high-performance insulation and lighting, Estidama (Resourceful Energy): Targets energy conservation',
        data_source: 'Building design specifications, material data sheets',
        category: 'Project Planning & Design',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'const_design_4',
        question: 'Does the project plan include installing on-site renewable energy, like solar panels?',
        rationale: 'Renewable Energy Generation',
        frameworks: 'Dubai Clean Energy Strategy 2050: Aims for 75% clean energy, Al Sa\'fat / Estidama: Provide credits for renewable energy',
        data_source: 'Project plans, supplier contracts',
        category: 'Project Planning & Design',
        required: false,
        type: 'yes_no'
      },

      // Construction Phase
      {
        id: 'const_phase_1',
        question: 'Do you have a Construction and Demolition (C&D) Waste Management Plan in place?',
        rationale: 'Waste Management',
        frameworks: 'Federal Law No. 12 of 2018: Mandates waste management, Al Sa\'fat / Estidama: Mandatory credits for C&D waste management',
        data_source: 'C&D Waste Management Plan document',
        category: 'Construction Phase',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'const_phase_2',
        question: 'Do you segregate construction waste on-site for recycling (e.g., concrete, steel, wood)?',
        rationale: 'Waste Diversion',
        frameworks: 'Al Sa\'fat / Estidama: Credits for diverting waste from landfill, Dubai Municipality: Requires waste segregation',
        data_source: 'Waste transfer notes from recycling facilities',
        category: 'Construction Phase',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'const_phase_3',
        question: 'Do you use locally sourced or recycled materials in your construction?',
        rationale: 'Sustainable Materials',
        frameworks: 'Al Sa\'fat / Estidama (Stewarding Materials): Credits for using local and recycled content',
        data_source: 'Material procurement records, supplier certificates',
        category: 'Construction Phase',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'const_phase_4',
        question: 'Do you have measures to control dust and air pollution from the construction site?',
        rationale: 'Air Quality',
        frameworks: 'Dubai Municipality: Requires air quality monitoring and control',
        data_source: 'Air quality monitoring plan/reports',
        category: 'Construction Phase',
        required: true,
        type: 'yes_no'
      },

      // Operational Phase (for Real Estate)
      {
        id: 'const_ops_1',
        question: 'Does the building have separate meters to track electricity and water consumption for different areas (e.g., common areas, individual units)?',
        rationale: 'Sub-metering & Monitoring',
        frameworks: 'Al Sa\'fat / Estidama: Credits for energy and water metering',
        data_source: 'Building management system (BMS) specifications',
        category: 'Operational Phase',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'const_ops_2',
        question: 'Are water-efficient fixtures (low-flow taps, toilets) installed in the building?',
        rationale: 'Water Conservation',
        frameworks: 'Al Sa\'fat / Dubai Regulations: Mandates water-efficient fixtures, Estidama (Precious Water): Requires reduction in water demand',
        data_source: 'Fixture specification sheets',
        category: 'Operational Phase',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'const_ops_3',
        question: 'Does the building have dedicated recycling bins for tenants/occupants?',
        rationale: 'Occupant Waste Management',
        frameworks: 'Al Sa\'fat / Estidama: Credits for operational waste management',
        data_source: 'Photos of recycling facilities',
        category: 'Operational Phase',
        required: false,
        type: 'yes_no'
      }
    ]
  },

  manufacturing: {
    name: 'Manufacturing',
    categories: ['Governance & Systems', 'Energy & Emissions', 'Waste & Materials', 'Water'],
    frameworks: [
      'Federal Energy Management Regulation in Industrial Facilities',
      'UAE Policy for Advanced Industries', 
      'ISO 14001 Environmental Management System',
      'UAE Climate Law',
      'UAE Waste Management Law',
      'Free Zone Regulations'
    ],
    questions: [
      // Governance & Systems
      {
        id: 'mfg_gov_1',
        question: 'Do you have a certified Environmental Management System, such as ISO 14001?',
        rationale: 'Formalized System',
        frameworks: 'ISO 14001: A voluntary but widely recognized standard for EMS',
        data_source: 'ISO 14001 Certificate',
        category: 'Governance & Systems',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'mfg_gov_2',
        question: 'Have you conducted an Environmental Impact Assessment (EIA) for your facility?',
        rationale: 'Risk Assessment',
        frameworks: 'Dubai Municipality: Required for industrial projects',
        data_source: 'EIA Report',
        category: 'Governance & Systems',
        required: true,
        type: 'yes_no'
      },

      // Energy & Emissions
      {
        id: 'mfg_energy_1',
        question: 'Do you track your facility\'s monthly consumption of all energy sources (electricity, natural gas, diesel)?',
        rationale: 'Scope 1 & 2 Emissions',
        frameworks: 'Federal Energy Management Regulation: Mandates energy management, Climate Law: Requires GHG reporting',
        data_source: 'Utility bills, fuel purchase logs',
        category: 'Energy & Emissions',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'mfg_energy_2',
        question: 'Have you implemented any projects to improve energy efficiency (e.g., upgrading machinery, installing LED lighting)?',
        rationale: 'Energy Conservation',
        frameworks: 'Federal Energy Management Regulation: Targets 33% energy reduction, Policy for Advanced Industries: Promotes energy efficiency',
        data_source: 'Project reports, equipment specifications',
        category: 'Energy & Emissions',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'mfg_energy_3',
        question: 'Do you monitor air emissions from your stacks or vents?',
        rationale: 'Air Quality',
        frameworks: 'Federal Energy Management Regulation: Targets 32% air quality improvement, Dubai Municipality: Requires air emission permits',
        data_source: 'Emissions monitoring reports',
        category: 'Energy & Emissions',
        required: true,
        type: 'yes_no'
      },

      // Waste & Materials
      {
        id: 'mfg_waste_1',
        question: 'Do you track the types and quantities of industrial waste your facility generates?',
        rationale: 'Waste Generation',
        frameworks: 'Federal Law No. 12 of 2018: Regulates industrial waste',
        data_source: 'Waste inventory, disposal records',
        category: 'Waste & Materials',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'mfg_waste_2',
        question: 'Do you have a licensed contractor for disposing of hazardous waste?',
        rationale: 'Hazardous Waste Management',
        frameworks: 'Federal Law No. 12 of 2018: Regulates hazardous waste, JAFZA EHS Regulations: Covers hazardous waste disposal',
        data_source: 'Contractor license, waste transfer notes',
        category: 'Waste & Materials',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'mfg_waste_3',
        question: 'Do you have any programs to reduce, reuse, or recycle waste materials within your production process?',
        rationale: 'Circular Economy',
        frameworks: 'Policy for Advanced Industries: Promotes circular economy principles',
        data_source: 'Process flow diagrams, recycling records',
        category: 'Waste & Materials',
        required: false,
        type: 'yes_no'
      },

      // Water
      {
        id: 'mfg_water_1',
        question: 'Do you treat your industrial wastewater before discharging it?',
        rationale: 'Water Pollution',
        frameworks: 'Federal Law No. 24 of 1999: Prohibits water pollution, Water Security Strategy 2036: Aims to reduce pollution',
        data_source: 'Wastewater treatment plant specifications, discharge quality reports',
        category: 'Water',
        required: true,
        type: 'yes_no'
      }
    ]
  },

  logistics: {
    name: 'Logistics & Transportation',
    categories: ['Fleet & Transportation', 'Warehousing & Operations', 'Packaging & Waste'],
    frameworks: [
      'Green Logistics & Supply Chain Initiatives',
      'UAE Green Agenda 2030',
      'UAE Energy Strategy 2050',
      'UAE Climate Law',
      'UAE Waste Management Law',
      'Maritime Law'
    ],
    questions: [
      // Fleet & Transportation
      {
        id: 'log_fleet_1',
        question: 'Do you track the total amount and type of fuel (petrol, diesel) consumed by your vehicle fleet each month?',
        rationale: 'Scope 1 Emissions',
        frameworks: 'Climate Law: Requires GHG reporting',
        data_source: 'Fuel purchase records, fleet management system data',
        category: 'Fleet & Transportation',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'log_fleet_2',
        question: 'Does your fleet include any electric or hybrid vehicles?',
        rationale: 'Green Transport',
        frameworks: 'UAE Green Agenda 2030: Promotes green transport, Government Incentives: Encourage EV adoption',
        data_source: 'Vehicle registration documents',
        category: 'Fleet & Transportation',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'log_fleet_3',
        question: 'Do you use software or other methods to optimize delivery routes to save fuel?',
        rationale: 'Fuel Efficiency',
        frameworks: 'Green Logistics Practices: Key strategy for reducing emissions and costs',
        data_source: 'Description of route optimization system/process',
        category: 'Fleet & Transportation',
        required: false,
        type: 'yes_no'
      },

      // Warehousing & Operations
      {
        id: 'log_warehouse_1',
        question: 'Do you track the monthly electricity consumption of your warehouses and distribution centers?',
        rationale: 'Scope 2 Emissions',
        frameworks: 'Climate Law: Requires GHG reporting',
        data_source: 'Monthly electricity bills',
        category: 'Warehousing & Operations',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'log_warehouse_2',
        question: 'Have you installed energy-saving features in your warehouses, such as LED lighting or solar panels?',
        rationale: 'Energy Efficiency',
        frameworks: 'Green Logistics Practices: Promotes sustainable warehousing',
        data_source: 'Photos, purchase invoices for equipment',
        category: 'Warehousing & Operations',
        required: false,
        type: 'yes_no'
      },

      // Packaging & Waste
      {
        id: 'log_packaging_1',
        question: 'Do you use packaging made from recycled or biodegradable materials?',
        rationale: 'Sustainable Packaging',
        frameworks: 'Green Logistics Practices: Key strategy for waste reduction',
        data_source: 'Packaging supplier specifications',
        category: 'Packaging & Waste',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'log_packaging_2',
        question: 'Do you have a program to take back and reuse packaging materials (e.g., pallets, containers) from your customers?',
        rationale: 'Reverse Logistics / Circular Economy',
        frameworks: 'Green Logistics Practices: Promotes a circular economy',
        data_source: 'Description of take-back program',
        category: 'Packaging & Waste',
        required: false,
        type: 'yes_no'
      }
    ]
  },

  education: {
    name: 'Education',
    categories: ['Policy & Management', 'Resource Management', 'Health & Environment'],
    frameworks: [
      'Sustainable Schools Initiative (SSI)',
      'Emirates Coalition for Green Schools',
      'ADEK Sustainability Policy',
      'Green Building Regulations',
      'Federal Law on Public Health'
    ],
    questions: [
      // Policy & Management
      {
        id: 'edu_policy_1',
        question: 'Does your school have a formal, written sustainability strategy or policy?',
        rationale: 'Governance',
        frameworks: 'ADEK Sustainability Policy: 1.1 Sustainability Strategy (Mandatory)',
        data_source: 'Signed policy document',
        category: 'Policy & Management',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'edu_policy_2',
        question: 'Do you have a student-led "Eco Club" or sustainability committee?',
        rationale: 'Student Engagement',
        frameworks: 'Sustainable Schools Initiative (SSI): Key component, Emirates Coalition for Green Schools: Recommends a Student Sustainability Committee',
        data_source: 'Club charter, list of activities',
        category: 'Policy & Management',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'edu_policy_3',
        question: 'Is sustainability integrated into the curriculum in any subjects?',
        rationale: 'Environmental Education',
        frameworks: 'ADEK Sustainability Policy: 2.1 Curriculum Integration (Mandatory), Emirates Coalition for Green Schools: Recommends integration',
        data_source: 'Curriculum maps, lesson plan examples',
        category: 'Policy & Management',
        required: true,
        type: 'yes_no'
      },

      // Resource Management
      {
        id: 'edu_resource_1',
        question: 'Does your school track its monthly electricity and water consumption?',
        rationale: 'Resource Consumption',
        frameworks: 'SSI Green School Audit: Core component of assessing environmental impact',
        data_source: 'Utility bills',
        category: 'Resource Management',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'edu_resource_2',
        question: 'Does your school have a program for recycling paper, plastic, and other materials?',
        rationale: 'Waste Management',
        frameworks: 'Emirates Coalition for Green Schools: Recommends waste reduction programs',
        data_source: 'Photos of recycling bins, waste contractor agreement',
        category: 'Resource Management',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'edu_resource_3',
        question: 'Does the school have a program for reusing or donating old uniforms and textbooks?',
        rationale: 'Resource Reuse',
        frameworks: 'ADEK Sustainability Policy: 2.5 & 2.6 Reuse of Uniforms & Resources (Mandatory)',
        data_source: 'Description of donation/resale program',
        category: 'Resource Management',
        required: true,
        type: 'yes_no'
      },

      // Health & Environment
      {
        id: 'edu_health_1',
        question: 'Do you monitor the indoor air quality in your classrooms and facilities?',
        rationale: 'Indoor Environmental Quality',
        frameworks: 'Emirates Coalition for Green Schools: Recommends IAQ monitoring systems',
        data_source: 'IAQ monitoring plan or reports',
        category: 'Health & Environment',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'edu_health_2',
        question: 'Does your school cafeteria or food service have a policy to promote healthy or locally sourced food?',
        rationale: 'Sustainable Food',
        frameworks: 'Emirates Coalition for Green Schools: Recommends sustainable food practices, Federal Law on Public Health: Sets healthy food requirements for schools',
        data_source: 'Cafeteria menu, supplier information',
        category: 'Health & Environment',
        required: false,
        type: 'yes_no'
      }
    ]
  },

  health: {
    name: 'Health',
    categories: ['Governance & Infrastructure', 'Waste Management', 'Resource Management'],
    frameworks: [
      'DoH Sustainability Goals',
      'MOHAP Hospital Regulation',
      'Dubai Health Authority Guidelines',
      'UAE Waste Management Law',
      'Federal Law on Public Health',
      'Green Building Regulations'
    ],
    questions: [
      // Governance & Infrastructure
      {
        id: 'health_gov_1',
        question: 'Does your facility have a sustainability plan to reduce energy, water, and waste?',
        rationale: 'Management System',
        frameworks: 'DoH Sustainability Goals: Requires facilities to have a sustainability roadmap, American Hospital Dubai Policy: Example of a facility-level policy',
        data_source: 'Sustainability plan document',
        category: 'Governance & Infrastructure',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'health_gov_2',
        question: 'Was your facility built or retrofitted according to green building standards (e.g., Al Sa\'fat, Estidama, LEED)?',
        rationale: 'Green Infrastructure',
        frameworks: 'DoH Sustainability Goals: Infrastructure pillar focuses on green building, Al Sa\'fat / Estidama: Mandatory for new builds',
        data_source: 'Building certification documents',
        category: 'Governance & Infrastructure',
        required: false,
        type: 'yes_no'
      },

      // Waste Management
      {
        id: 'health_waste_1',
        question: 'Do you segregate different types of medical waste at the point of generation (e.g., sharps, infectious, general)?',
        rationale: 'Medical Waste Segregation',
        frameworks: 'MOHAP Hospital Regulation: Requires proper handling of hazardous/medical waste, Dubai Municipality Guidelines: Mandate separation at source',
        data_source: 'Waste management policy, photos of segregation bins',
        category: 'Waste Management',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'health_waste_2',
        question: 'Do you have a contract with a licensed company for the safe treatment and disposal of biomedical waste?',
        rationale: 'Hazardous Waste Disposal',
        frameworks: 'Federal Law No. 12 of 2018: Governs waste disposal, MOHAP/DHA Regulations: Require safe disposal',
        data_source: 'Contractor license and agreement',
        category: 'Waste Management',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'health_waste_3',
        question: 'Have you implemented measures to reduce single-use plastics in non-clinical areas?',
        rationale: 'Plastic Waste Reduction',
        frameworks: 'DoH Sustainability Goals: Operations pillar includes waste reduction, General Trend: Many hospitals are eliminating plastic bags/bottles',
        data_source: 'Policy on single-use plastics',
        category: 'Waste Management',
        required: false,
        type: 'yes_no'
      },

      // Resource Management
      {
        id: 'health_resource_1',
        question: 'Do you track your facility\'s monthly electricity and water consumption?',
        rationale: 'Resource Consumption',
        frameworks: 'DoH Sustainability Goals: Operations pillar includes energy/water management',
        data_source: 'Utility bills',
        category: 'Resource Management',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'health_resource_2',
        question: 'Have you installed energy-efficient equipment (e.g., LED lighting, efficient HVAC systems)?',
        rationale: 'Energy Efficiency',
        frameworks: 'DoH Sustainability Goals: Infrastructure pillar promotes efficiency, General Trend: Hospitals are adopting LEDs, efficient chillers',
        data_source: 'Equipment specification sheets',
        category: 'Resource Management',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'health_resource_3',
        question: 'Do you have a program to reduce paper use by transitioning to electronic health records and digital communications?',
        rationale: 'Paper Waste Reduction',
        frameworks: 'General Trend: A key sustainability initiative adopted by UAE hospitals',
        data_source: 'Policy on paperless operations, EMR system details',
        category: 'Resource Management',
        required: false,
        type: 'yes_no'
      }
    ]
  },

  retail: {
    name: 'Retail & Trading',
    frameworks: [
      'UAE Climate Law',
      'UAE Waste Management Law',
      'Dubai Municipality Regulations',
      'Green Building Regulations'
    ],
    questions: [
      // Energy Management
      {
        id: 'retail_energy_1',
        question: 'Do you track your store\'s monthly electricity consumption?',
        rationale: 'Energy Monitoring',
        frameworks: 'UAE Climate Law: Requires energy tracking',
        data_source: 'Monthly electricity bills',
        category: 'Energy',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'retail_energy_2',
        question: 'Have you upgraded to energy-efficient lighting (LED) throughout your store?',
        rationale: 'Energy Efficiency',
        frameworks: 'Dubai Municipality: Promotes energy efficiency',
        data_source: 'Lighting upgrade receipts',
        category: 'Energy',
        required: false,
        type: 'yes_no'
      },

      // Waste Management
      {
        id: 'retail_waste_1',
        question: 'Do you have separate bins for different types of waste (general, recyclable, organic)?',
        rationale: 'Waste Segregation',
        frameworks: 'UAE Waste Management Law: Requires waste separation',
        data_source: 'Photos of waste segregation setup',
        category: 'Waste',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'retail_waste_2',
        question: 'Do you have a policy to reduce single-use plastic bags or charge customers for them?',
        rationale: 'Plastic Waste Reduction',
        frameworks: 'Dubai Municipality: Plastic reduction initiatives',
        data_source: 'Store policy document',
        category: 'Waste',
        required: false,
        type: 'yes_no'
      },

      // Supply Chain
      {
        id: 'retail_supply_1',
        question: 'Do you prioritize suppliers who provide environmentally certified or sustainable products?',
        rationale: 'Sustainable Procurement',
        frameworks: 'UAE Climate Strategy: Promotes sustainable supply chains',
        data_source: 'Supplier certification documents',
        category: 'Supply Chain',
        required: false,
        type: 'yes_no'
      }
    ]
  },

  technology: {
    name: 'Technology & Software',
    frameworks: [
      'UAE Climate Law',
      'Dubai Smart City Initiative',
      'UAE Digital Government Strategy'
    ],
    questions: [
      // Energy & Infrastructure
      {
        id: 'tech_energy_1',
        question: 'Do you measure the energy consumption of your data centers or server rooms?',
        rationale: 'IT Infrastructure Energy Use',
        frameworks: 'UAE Climate Law: Requires energy tracking',
        data_source: 'Energy monitoring systems, utility bills',
        category: 'Energy',
        required: true,
        type: 'yes_no'
      },
      {
        id: 'tech_energy_2',
        question: 'Do you use cloud services to reduce on-premise hardware requirements?',
        rationale: 'Energy Efficiency through Cloud',
        frameworks: 'Dubai Smart City Initiative: Promotes cloud adoption',
        data_source: 'Cloud service contracts',
        category: 'Energy',
        required: false,
        type: 'yes_no'
      },

      // Digital Sustainability
      {
        id: 'tech_digital_1',
        question: 'Do you have policies to promote paperless operations and digital document management?',
        rationale: 'Digital Transformation',
        frameworks: 'UAE Digital Government Strategy: Promotes digitization',
        data_source: 'Digital policy documents',
        category: 'Social',
        required: false,
        type: 'yes_no'
      },
      {
        id: 'tech_digital_2',
        question: 'Do you track and optimize the carbon footprint of your software applications?',
        rationale: 'Software Carbon Footprint',
        frameworks: 'UAE Climate Law: Comprehensive emissions tracking',
        data_source: 'Carbon tracking tools, optimization reports',
        category: 'Environmental',
        required: false,
        type: 'yes_no'
      }
    ]
  }
};