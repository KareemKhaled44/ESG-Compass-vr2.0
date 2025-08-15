"""
Management command to seed report templates
"""
from django.core.management.base import BaseCommand
from apps.reports.models import ReportTemplate, ReportSection


class Command(BaseCommand):
    help = 'Seed database with report templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing templates before seeding',
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('Cleaning existing templates...')
            ReportTemplate.objects.all().delete()

        self.stdout.write('Creating report templates...')
        
        # ESG Comprehensive Report
        esg_comprehensive = ReportTemplate.objects.create(
            name='esg_comprehensive',
            display_name='ESG Comprehensive Report',
            description='Complete overview of Environmental, Social, and Governance performance with detailed metrics, trends, and recommendations.',
            report_type='esg_comprehensive',
            template_config={
                'layout': 'professional',
                'include_charts': True,
                'include_recommendations': True,
                'color_scheme': 'brand'
            },
            required_frameworks=['GRI', 'SASB'],
            required_categories=['environmental', 'social', 'governance'],
            supported_formats=['pdf', 'xlsx'],
            compliance_standards=['GRI Standards', 'SASB Standards'],
            applicable_sectors=['hospitality', 'construction', 'retail', 'manufacturing', 'technology', 'finance'],
            is_framework_official=False,
            requires_verification=False,
            status='active'
        )
        
        # ESG Comprehensive Sections
        sections_esg = [
            ('cover', 'Cover Page', 'Report title and company information', 0),
            ('executive_summary', 'Executive Summary', 'Key findings and performance overview', 1),
            ('methodology', 'Methodology', 'Data collection and calculation methods', 2),
            ('environmental', 'Environmental Performance', 'Energy, water, waste, and emissions metrics', 3),
            ('social', 'Social Performance', 'Employee, community, and stakeholder metrics', 4),
            ('governance', 'Governance Performance', 'Board structure, policies, and compliance', 5),
            ('compliance', 'Compliance Status', 'Framework adherence and certification status', 6),
            ('recommendations', 'Recommendations', 'Priority actions and improvement opportunities', 7),
            ('appendix', 'Appendix', 'Detailed data tables and supporting information', 8)
        ]
        
        for section_type, title, description, order in sections_esg:
            ReportSection.objects.create(
                template=esg_comprehensive,
                name=section_type,
                title=title,
                description=description,
                section_type=section_type,
                order=order,
                is_required=True,
                is_active=True
            )

        # Dubai Sustainable Tourism Report
        dst_compliance = ReportTemplate.objects.create(
            name='dst_compliance',
            display_name='Dubai Sustainable Tourism Compliance',
            description='Official DST compliance report for Dubai Department of Tourism & Commerce Marketing certification.',
            report_type='dst_compliance',
            template_config={
                'layout': 'compliance',
                'include_checklist': True,
                'dst_version': '2024',
                'official_format': True
            },
            required_frameworks=['DST'],
            required_categories=['environmental', 'social'],
            supported_formats=['pdf', 'xlsx'],
            compliance_standards=['Dubai Sustainable Tourism 2024'],
            applicable_sectors=['hospitality'],
            is_framework_official=True,
            requires_verification=True,
            status='active'
        )

        # DST Sections
        sections_dst = [
            ('cover', 'Cover Page', 'DST certification report cover', 0),
            ('compliance', 'Compliance Status', 'Current DST compliance level and status', 1),
            ('environmental', 'Environmental Criteria', 'Environmental management and performance', 2),
            ('social', 'Social Responsibility', 'Community engagement and employee welfare', 3),
            ('custom', 'Requirements Checklist', 'Detailed DST requirements assessment', 4),
            ('recommendations', 'Action Plan', 'Steps to achieve full DST compliance', 5)
        ]
        
        for section_type, title, description, order in sections_dst:
            ReportSection.objects.create(
                template=dst_compliance,
                name=section_type.lower().replace(' ', '_'),
                title=title,
                description=description,
                section_type=section_type,
                order=order,
                is_required=True,
                is_active=True
            )

        # Green Key Certification Report
        green_key = ReportTemplate.objects.create(
            name='green_key',
            display_name='Green Key Certification Assessment',
            description='International eco-label assessment for hospitality industry focusing on environmental responsibility.',
            report_type='green_key',
            template_config={
                'layout': 'certification',
                'green_key_version': '2024',
                'include_criteria_checklist': True
            },
            required_frameworks=['GREEN_KEY'],
            required_categories=['environmental'],
            supported_formats=['pdf', 'xlsx'],
            compliance_standards=['Green Key International Standards'],
            applicable_sectors=['hospitality'],
            is_framework_official=True,
            requires_verification=True,
            status='active'
        )

        # Custom Export Template
        custom_export = ReportTemplate.objects.create(
            name='custom_export',
            display_name='Custom Export',
            description='Create tailored reports with specific metrics, timeframes, and formats for stakeholders.',
            report_type='custom_export',
            template_config={
                'layout': 'flexible',
                'customizable_sections': True,
                'multiple_formats': True
            },
            required_frameworks=[],
            required_categories=[],
            supported_formats=['pdf', 'xlsx', 'csv', 'json'],
            compliance_standards=[],
            applicable_sectors=[],
            is_framework_official=False,
            requires_verification=False,
            status='active'
        )

        # Quarterly Summary Report
        quarterly_summary = ReportTemplate.objects.create(
            name='quarterly_summary',
            display_name='Quarterly ESG Summary',
            description='Quarterly performance summary with key metrics, achievements, and action items.',
            report_type='quarterly_summary',
            template_config={
                'layout': 'summary',
                'period': 'quarterly',
                'include_trends': True,
                'include_targets': True
            },
            required_frameworks=[],
            required_categories=['environmental', 'social', 'governance'],
            supported_formats=['pdf', 'xlsx'],
            compliance_standards=[],
            applicable_sectors=['hospitality', 'construction', 'retail', 'manufacturing', 'technology', 'finance'],
            is_framework_official=False,
            requires_verification=False,
            status='active'
        )

        # UAE Compliance Tracker
        compliance_tracker = ReportTemplate.objects.create(
            name='compliance_tracker',
            display_name='UAE Compliance Tracker',
            description='Comprehensive tracking of UAE federal and emirate-level environmental and climate regulations.',
            report_type='compliance_tracker',
            template_config={
                'layout': 'compliance',
                'include_federal_laws': True,
                'include_emirate_laws': True,
                'traffic_light_system': True
            },
            required_frameworks=['UAE_FEDERAL', 'NET_ZERO_2050'],
            required_categories=['environmental', 'governance'],
            supported_formats=['pdf', 'xlsx'],
            compliance_standards=['UAE Federal Climate Law', 'UAE Net Zero 2050'],
            applicable_sectors=['hospitality', 'construction', 'retail', 'manufacturing', 'technology', 'finance'],
            is_framework_official=True,
            requires_verification=False,
            status='active'
        )

        # Annual ESG Report
        annual_report = ReportTemplate.objects.create(
            name='annual_report',
            display_name='Annual ESG Report',
            description='Comprehensive annual sustainability report suitable for stakeholders and regulatory filing.',
            report_type='annual_report',
            template_config={
                'layout': 'annual',
                'include_ceo_message': True,
                'include_materiality_matrix': True,
                'include_targets': True,
                'professional_design': True
            },
            required_frameworks=['GRI', 'SASB', 'TCFD'],
            required_categories=['environmental', 'social', 'governance'],
            supported_formats=['pdf'],
            compliance_standards=['GRI Standards', 'SASB Standards', 'TCFD Recommendations'],
            applicable_sectors=['hospitality', 'construction', 'retail', 'manufacturing', 'technology', 'finance'],
            is_framework_official=False,
            requires_verification=True,
            status='active'
        )

        # Benchmark Analysis Report
        benchmark_analysis = ReportTemplate.objects.create(
            name='benchmark_analysis',
            display_name='ESG Benchmark Analysis',
            description='Comparative analysis against industry peers and best practices with actionable insights.',
            report_type='benchmark_analysis',
            template_config={
                'layout': 'analytical',
                'include_peer_comparison': True,
                'include_best_practices': True,
                'include_gap_analysis': True
            },
            required_frameworks=[],
            required_categories=['environmental', 'social', 'governance'],
            supported_formats=['pdf', 'xlsx'],
            compliance_standards=[],
            applicable_sectors=['hospitality', 'construction', 'retail', 'manufacturing', 'technology', 'finance'],
            is_framework_official=False,
            requires_verification=False,
            status='active'
        )

        templates_created = ReportTemplate.objects.count()
        sections_created = ReportSection.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {templates_created} report templates and {sections_created} sections'
            )
        )
        
        # Display created templates
        self.stdout.write('\nCreated templates:')
        for template in ReportTemplate.objects.all():
            self.stdout.write(f'  • {template.display_name} ({template.report_type})')