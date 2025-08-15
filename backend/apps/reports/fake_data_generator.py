"""
Fake Data Generator for ESG Reports
Generates realistic sample data to demonstrate report capabilities
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid


class ESGFakeDataGenerator:
    """Generates realistic fake data for ESG reports"""
    
    def __init__(self, company_name="Demo Company Ltd", seed=None):
        self.company_name = company_name
        # Set random seed for consistent but unique data per report
        if seed:
            import hashlib
            # Create numeric seed from string
            seed_hash = int(hashlib.md5(str(seed).encode()).hexdigest()[:8], 16)
            random.seed(seed_hash)
        
        # Sample environmental initiatives
        self.environmental_initiatives = [
            "Solar panel installation across main facilities",
            "LED lighting conversion program",
            "Waste reduction and recycling enhancement",
            "Water conservation system implementation",
            "Electric vehicle fleet transition",
            "Green building certification pursuit",
            "Carbon offset program launch",
            "Sustainable packaging adoption"
        ]
        
        # Sample social programs
        self.social_programs = [
            "Employee wellness and mental health support",
            "Diversity and inclusion training programs",
            "Local community partnership initiatives",
            "Skills development and education support",
            "Flexible work arrangements implementation",
            "Health and safety protocol enhancements",
            "Employee volunteer program expansion",
            "Local supplier preference program"
        ]
        
        # Sample governance improvements
        self.governance_improvements = [
            "Board diversity and independence enhancement",
            "Ethics and compliance training rollout",
            "Risk management framework update",
            "Stakeholder engagement process improvement",
            "Transparency and reporting standards upgrade",
            "Data privacy and security measures strengthening",
            "Audit and oversight mechanism enhancement",
            "Corporate governance policy revision"
        ]
    
    def generate_comprehensive_data(self) -> Dict[str, Any]:
        """Generate comprehensive fake ESG data"""
        return {
            'company_profile': self._generate_company_profile(),
            'esg_scores': self._generate_esg_scores(),
            'environmental_data': self._generate_environmental_data(),
            'social_data': self._generate_social_data(),
            'governance_data': self._generate_governance_data(),
            'compliance_status': self._generate_compliance_status(),
            'task_progress': self._generate_task_progress(),
            'evidence_summary': self._generate_evidence_summary(),
            'key_achievements': self._generate_key_achievements(),
            'recommendations': self._generate_recommendations(),
            'trends': self._generate_trends(),
            'benchmarks': self._generate_benchmark_data(),
            'data_quality': self._generate_data_quality()
        }
    
    def _generate_company_profile(self) -> Dict[str, Any]:
        """Generate realistic company profile"""
        return {
            'name': self.company_name,
            'business_sector': random.choice(['Technology', 'Manufacturing', 'Services', 'Healthcare', 'Education']),
            'employee_size': random.choice(['50-100', '100-500', '500-1000', '1000+']),
            'main_location': 'Dubai, UAE',
            'emirate': 'Dubai',
            'license_type': 'Commercial',
            'setup_completed': True,
            'created_date': datetime.now() - timedelta(days=random.randint(200, 800)),
            'annual_revenue': f"AED {random.randint(10, 500)} Million",
            'market_presence': random.choice(['Local', 'Regional', 'International']),
            'certifications': random.sample([
                'ISO 14001 (Environmental Management)',
                'ISO 45001 (Occupational Health & Safety)',
                'ISO 26000 (Social Responsibility)',
                'Dubai Chamber CSR Label',
                'Green Key Certification'
            ], k=random.randint(2, 4))
        }
    
    def _generate_esg_scores(self) -> Dict[str, Any]:
        """Generate realistic ESG scores with trends"""
        # Create DRAMATICALLY different score ranges based on seed
        score_categories = [
            (45, 65, "struggling"),   # Struggling companies
            (65, 80, "developing"),   # Developing companies
            (80, 95, "advanced"),     # Advanced companies
            (95, 100, "exceptional")  # Exceptional companies
        ]
        category = random.choice(score_categories)
        score_range = (category[0], category[1])
        performance_level = category[2]
        
        # Generate dramatically different scores based on performance level
        if performance_level == "struggling":
            base_scores = {
                'environmental_score': random.randint(40, 60),
                'social_score': random.randint(45, 65),
                'governance_score': random.randint(50, 70)
            }
            industry_ranking = f"Bottom {random.randint(60, 80)}%"
            peer_comparison = random.choice(['Below Average', 'Needs Improvement', 'Developing'])
            improvement = f"+{random.randint(15, 25)} points YoY"
        elif performance_level == "developing":
            base_scores = {
                'environmental_score': random.randint(60, 75),
                'social_score': random.randint(65, 80),
                'governance_score': random.randint(70, 85)
            }
            industry_ranking = f"Top {random.randint(40, 60)}%"
            peer_comparison = random.choice(['Average', 'Above Average', 'Good'])
            improvement = f"+{random.randint(8, 18)} points YoY"
        elif performance_level == "advanced":
            base_scores = {
                'environmental_score': random.randint(75, 90),
                'social_score': random.randint(80, 95),
                'governance_score': random.randint(85, 98)
            }
            industry_ranking = f"Top {random.randint(15, 35)}%"
            peer_comparison = random.choice(['Above Average', 'Excellent', 'Strong'])
            improvement = f"+{random.randint(3, 12)} points YoY"
        else:  # exceptional
            base_scores = {
                'environmental_score': random.randint(90, 100),
                'social_score': random.randint(92, 100),
                'governance_score': random.randint(95, 100)
            }
            industry_ranking = f"Top {random.randint(1, 10)}%"
            peer_comparison = random.choice(['Outstanding', 'Exceptional', 'Industry Leader'])
            improvement = f"+{random.randint(1, 8)} points YoY"
        
        overall_score = sum(base_scores.values()) / len(base_scores)
        
        return {
            'overall_score': round(overall_score, 1),
            'environmental_score': base_scores['environmental_score'],
            'social_score': base_scores['social_score'],
            'governance_score': base_scores['governance_score'],
            'performance_level': performance_level,  # Add performance level for more content variation
            'data_completion': random.randint(70 if performance_level == "struggling" else 85, 
                                            90 if performance_level == "struggling" else 98),
            'score_trends': {
                'last_quarter': round(overall_score - random.uniform(1, 12), 1),
                'last_year': round(overall_score - random.uniform(3, 20), 1),
                'improvement': improvement
            },
            'industry_ranking': industry_ranking,
            'peer_comparison': peer_comparison
        }
    
    def _generate_environmental_data(self) -> Dict[str, Any]:
        """Generate environmental performance data"""
        # Create EXTREMELY dramatic variation based on company size and performance
        company_profiles = [
            (5000, 25000, 25, 150, "micro"),      # Micro companies
            (25000, 100000, 100, 500, "small"),   # Small companies  
            (100000, 400000, 500, 1500, "medium"), # Medium companies
            (400000, 1000000, 1500, 5000, "large"), # Large companies
            (1000000, 3000000, 5000, 15000, "enterprise"), # Enterprise companies
        ]
        profile = random.choice(company_profiles)
        kwh_min, kwh_max, co2_min, co2_max, company_size = profile
        
        return {
            'company_size_category': company_size,  # Add size info for more variation
            'energy_consumption': {
                'total_kwh': random.randint(kwh_min, kwh_max),
                'renewable_percentage': random.randint(5, 95),  # Much wider range
                'reduction_target': f"{random.randint(5, 50)}% by 2025",
                'monthly_trend': [random.randint(int(kwh_min/15), int(kwh_max/10)) for _ in range(12)]
            },
            'carbon_emissions': {
                'total_co2_tonnes': random.randint(co2_min, co2_max),
                'scope1': random.randint(int(co2_min * 0.2), int(co2_max * 0.4)),
                'scope2': random.randint(int(co2_min * 0.3), int(co2_max * 0.6)),
                'scope3': random.randint(int(co2_min * 0.1), int(co2_max * 0.3)),
                'reduction_achieved': f"{random.randint(5, 40)}%",
                'offset_programs': random.randint(1, 12)
            },
            'waste_management': {
                'total_waste_tonnes': random.randint(20, 150),
                'recycling_rate': random.randint(60, 90),
                'landfill_diversion': random.randint(70, 95),
                'waste_streams': random.randint(3, 8)
            },
            'water_usage': {
                'total_liters': random.randint(10000, 50000),
                'conservation_measures': random.randint(3, 7),
                'reduction_achieved': f"{random.randint(10, 30)}%"
            },
            'initiatives': random.sample(self.environmental_initiatives, k=random.randint(3, 6)),
            'certifications': random.sample([
                'ISO 14001', 'LEED Gold', 'Energy Star', 'Carbon Trust Standard'
            ], k=random.randint(1, 3))
        }
    
    def _generate_social_data(self) -> Dict[str, Any]:
        """Generate social performance data"""
        # Create dramatically different employee profiles
        employee_profiles = [
            (10, 50, "startup"),      # Startup
            (50, 200, "small"),       # Small company
            (200, 500, "medium"),     # Medium company  
            (500, 2000, "large"),     # Large company
            (2000, 10000, "enterprise") # Enterprise
        ]
        profile = random.choice(employee_profiles)
        emp_min, emp_max, company_type = profile
        
        # Vary metrics dramatically based on company performance
        performance_multiplier = random.choice([0.6, 0.8, 1.0, 1.2, 1.4])  # Poor to excellent
        
        return {
            'company_type': company_type,  # Add for more variation
            'employee_metrics': {
                'total_employees': random.randint(emp_min, emp_max),
                'diversity_ratio': f"{random.randint(20, 65)}% women",
                'retention_rate': f"{random.randint(int(60 * performance_multiplier), int(98 * performance_multiplier))}%",
                'satisfaction_score': f"{random.randint(int(40 * performance_multiplier), int(95 * performance_multiplier))}/100",
                'training_hours': random.randint(int(10 * performance_multiplier), int(80 * performance_multiplier)),
                'promotion_rate': f"{random.randint(int(3 * performance_multiplier), int(25 * performance_multiplier))}%"
            },
            'health_safety': {
                'incidents': random.randint(0, 3),
                'safety_training_completion': random.randint(95, 100),
                'wellness_programs': random.randint(3, 8),
                'mental_health_support': True,
                'safety_certifications': random.randint(1, 4)
            },
            'community_impact': {
                'volunteer_hours': random.randint(200, 1000),
                'local_partnerships': random.randint(3, 12),
                'community_investment': f"AED {random.randint(50, 300)}K",
                'beneficiaries_reached': random.randint(500, 5000)
            },
            'supply_chain': {
                'local_suppliers': f"{random.randint(40, 80)}%",
                'supplier_assessments': random.randint(10, 50),
                'ethical_sourcing_policy': True,
                'supplier_diversity_program': True
            },
            'programs': random.sample(self.social_programs, k=random.randint(4, 7))
        }
    
    def _generate_governance_data(self) -> Dict[str, Any]:
        """Generate governance performance data"""
        return {
            'board_composition': {
                'total_members': random.randint(5, 12),
                'independent_directors': f"{random.randint(40, 70)}%",
                'women_representation': f"{random.randint(20, 50)}%",
                'average_tenure': f"{random.randint(3, 8)} years",
                'diversity_score': random.randint(75, 95)
            },
            'ethics_compliance': {
                'code_of_conduct': True,
                'ethics_training_completion': random.randint(95, 100),
                'whistleblower_policy': True,
                'compliance_violations': random.randint(0, 2),
                'audit_findings': random.randint(0, 5)
            },
            'risk_management': {
                'risk_assessment_frequency': 'Quarterly',
                'risk_categories_covered': random.randint(8, 15),
                'mitigation_plans_active': random.randint(5, 20),
                'insurance_coverage': random.randint(85, 98)
            },
            'transparency': {
                'sustainability_reporting': True,
                'stakeholder_engagement_score': random.randint(80, 95),
                'disclosure_rating': random.choice(['A', 'A-', 'B+']),
                'external_audits': random.randint(2, 5)
            },
            'improvements': random.sample(self.governance_improvements, k=random.randint(3, 6))
        }
    
    def _generate_compliance_status(self) -> List[Dict[str, Any]]:
        """Generate compliance framework status"""
        frameworks = [
            {
                'name': 'Dubai Sustainable Tourism',
                'compliance_percentage': random.randint(80, 95),
                'status': 'Compliant',
                'last_assessment': datetime.now() - timedelta(days=random.randint(30, 90)),
                'next_review': datetime.now() + timedelta(days=random.randint(60, 120)),
                'requirements_met': random.randint(15, 25),
                'total_requirements': random.randint(20, 30)
            },
            {
                'name': 'Green Key Certification',
                'compliance_percentage': random.randint(70, 90),
                'status': random.choice(['Compliant', 'In Progress']),
                'last_assessment': datetime.now() - timedelta(days=random.randint(20, 60)),
                'next_review': datetime.now() + timedelta(days=random.randint(30, 90)),
                'requirements_met': random.randint(12, 20),
                'total_requirements': random.randint(18, 25)
            },
            {
                'name': 'UAE Federal Climate Law',
                'compliance_percentage': random.randint(65, 85),
                'status': random.choice(['In Progress', 'Compliant']),
                'last_assessment': datetime.now() - timedelta(days=random.randint(40, 80)),
                'next_review': datetime.now() + timedelta(days=random.randint(45, 100)),
                'requirements_met': random.randint(10, 18),
                'total_requirements': random.randint(16, 22)
            }
        ]
        return frameworks
    
    def _generate_task_progress(self) -> Dict[str, Any]:
        """Generate task completion statistics"""
        total_tasks = random.randint(50, 150)
        completed = random.randint(int(total_tasks * 0.6), int(total_tasks * 0.9))
        
        return {
            'total_tasks': total_tasks,
            'completed': completed,
            'in_progress': random.randint(5, 15),
            'pending': total_tasks - completed,
            'completion_rate': round((completed / total_tasks) * 100, 1),
            'categories': {
                'Environmental': random.randint(15, 30),
                'Social': random.randint(20, 40),
                'Governance': random.randint(10, 25),
                'Compliance': random.randint(8, 20)
            }
        }
    
    def _generate_evidence_summary(self) -> Dict[str, Any]:
        """Generate evidence collection summary"""
        return {
            'total_documents': random.randint(100, 300),
            'verified_documents': random.randint(80, 250),
            'categories': {
                'Policies & Procedures': random.randint(15, 40),
                'Certificates & Licenses': random.randint(10, 25),
                'Training Records': random.randint(20, 60),
                'Performance Data': random.randint(25, 80),
                'Audit Reports': random.randint(5, 15),
                'Stakeholder Feedback': random.randint(10, 30)
            },
            'quality_score': random.randint(85, 98)
        }
    
    def _generate_key_achievements(self) -> List[str]:
        """Generate list of key achievements"""
        achievements = [
            f"Achieved {random.randint(15, 35)}% reduction in carbon emissions",
            f"Increased employee satisfaction score to {random.randint(85, 95)}/100",
            f"Implemented {random.randint(3, 8)} new sustainability initiatives",
            f"Obtained {random.randint(2, 5)} new environmental certifications",
            f"Diverted {random.randint(70, 90)}% of waste from landfills",
            f"Increased renewable energy usage to {random.randint(20, 45)}%",
            f"Enhanced board diversity to {random.randint(35, 55)}%",
            f"Completed {random.randint(95, 100)}% of planned ESG tasks",
            f"Engaged with {random.randint(500, 3000)} community members",
            f"Reduced water consumption by {random.randint(15, 30)}%"
        ]
        return random.sample(achievements, k=random.randint(5, 8))
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations"""
        recommendations = [
            {
                'category': 'Environmental',
                'priority': 'High',
                'title': 'Expand Renewable Energy Adoption',
                'description': 'Consider increasing solar panel coverage to achieve 50% renewable energy by 2025',
                'impact': 'Potential 20% reduction in carbon footprint',
                'timeline': '6-12 months'
            },
            {
                'category': 'Social',
                'priority': 'Medium',
                'title': 'Enhance Diversity & Inclusion Programs',
                'description': 'Implement targeted recruitment and mentorship programs for underrepresented groups',
                'impact': 'Improved workplace culture and innovation',
                'timeline': '3-6 months'
            },
            {
                'category': 'Governance',
                'priority': 'High',
                'title': 'Strengthen Risk Management Framework',
                'description': 'Update risk assessment procedures to include climate-related financial risks',
                'impact': 'Better preparedness for future challenges',
                'timeline': '2-4 months'
            },
            {
                'category': 'Compliance',
                'priority': 'Medium',
                'title': 'Pursue Additional Certifications',
                'description': 'Consider obtaining ISO 26000 certification for social responsibility',
                'impact': 'Enhanced credibility and market positioning',
                'timeline': '8-12 months'
            }
        ]
        return random.sample(recommendations, k=random.randint(3, 4))
    
    def _generate_trends(self) -> Dict[str, List[float]]:
        """Generate performance trends over time"""
        def generate_trend(start_value, trend_direction='up'):
            values = [start_value]
            for i in range(11):  # 12 months total
                if trend_direction == 'up':
                    change = random.uniform(0.5, 3.0)
                    values.append(min(100, values[-1] + change))
                else:
                    change = random.uniform(0.2, 2.0)
                    values.append(max(0, values[-1] - change))
            return [round(v, 1) for v in values]
        
        return {
            'esg_score': generate_trend(random.randint(65, 75), 'up'),
            'environmental_score': generate_trend(random.randint(60, 70), 'up'),
            'social_score': generate_trend(random.randint(70, 80), 'up'),
            'governance_score': generate_trend(random.randint(75, 85), 'up'),
            'energy_consumption': generate_trend(random.randint(8000, 12000), 'down'),
            'carbon_emissions': generate_trend(random.randint(80, 120), 'down')
        }
    
    def _generate_benchmark_data(self) -> Dict[str, Any]:
        """Generate industry benchmark comparisons"""
        return {
            'industry_average': {
                'environmental_score': random.randint(60, 75),
                'social_score': random.randint(65, 80),
                'governance_score': random.randint(70, 85),
                'overall_score': random.randint(65, 80)
            },
            'top_quartile': {
                'environmental_score': random.randint(85, 95),
                'social_score': random.randint(88, 98),
                'governance_score': random.randint(90, 98),
                'overall_score': random.randint(88, 97)
            },
            'regional_comparison': {
                'uae_average': random.randint(70, 85),
                'gcc_average': random.randint(65, 80),
                'mena_average': random.randint(60, 75)
            },
            'ranking': {
                'industry_rank': f"{random.randint(15, 45)} out of {random.randint(200, 500)}",
                'regional_rank': f"Top {random.randint(10, 30)}%",
                'percentile': f"{random.randint(70, 95)}th percentile"
            }
        }
    
    def _generate_data_quality(self) -> Dict[str, Any]:
        """Generate data quality assessment"""
        return {
            'overall_quality': random.randint(85, 98),
            'completeness': random.randint(90, 100),
            'accuracy': random.randint(85, 95),
            'timeliness': random.randint(80, 95),
            'consistency': random.randint(88, 98),
            'data_sources': random.randint(15, 35),
            'automated_collection': f"{random.randint(60, 85)}%",
            'manual_verification': f"{random.randint(95, 100)}%"
        }


# Utility function to inject fake data
def enhance_data_with_fake_content(real_data: Dict[str, Any], company_name: str = None, seed: str = None) -> Dict[str, Any]:
    """Enhance real data with fake content where data is missing or minimal"""
    generator = ESGFakeDataGenerator(company_name or "Demo Company Ltd", seed=seed)
    fake_data = generator.generate_comprehensive_data()
    
    # Merge real data with fake data, preferring real data where it exists
    enhanced_data = fake_data.copy()
    for key, value in real_data.items():
        if value:  # Only override if real data has meaningful content
            enhanced_data[key] = value
    
    return enhanced_data