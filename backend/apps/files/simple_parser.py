"""
Simple fallback file parser that works without external dependencies
"""

import json
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SimpleExtractedData:
    """Simple version of extracted data without dataclass dependencies"""
    
    def __init__(self, file_name: str, file_type: str):
        self.file_name = file_name
        self.file_type = file_type
        self.extraction_date = datetime.now().isoformat()
        self.extraction_method = 'simple_text_extraction'
        self.confidence_score = 50.0
        
        # Environmental metrics
        self.energy_consumption_kwh = None
        self.water_usage_liters = None
        self.waste_generated_kg = None
        self.carbon_emissions_tco2 = None
        self.renewable_energy_percentage = None
        
        # Social metrics
        self.total_employees = None
        self.training_hours = None
        self.safety_incidents = None
        self.employee_satisfaction_score = None
        
        # Governance metrics
        self.board_meetings = None
        self.compliance_score = None
        
        # Additional data
        self.raw_text = None
        self.tables = []
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        data = {
            'file_name': self.file_name,
            'file_type': self.file_type,
            'extraction_date': self.extraction_date,
            'extraction_method': self.extraction_method,
            'confidence_score': self.confidence_score,
            'energy_consumption_kwh': self.energy_consumption_kwh,
            'water_usage_liters': self.water_usage_liters,
            'waste_generated_kg': self.waste_generated_kg,
            'carbon_emissions_tco2': self.carbon_emissions_tco2,
            'renewable_energy_percentage': self.renewable_energy_percentage,
            'total_employees': self.total_employees,
            'training_hours': self.training_hours,
            'safety_incidents': self.safety_incidents,
            'employee_satisfaction_score': self.employee_satisfaction_score,
            'board_meetings': self.board_meetings,
            'compliance_score': self.compliance_score,
            'raw_text': self.raw_text,
            'tables': self.tables,
        }
        return json.dumps(data, default=str, indent=2)


class SimpleFileParser:
    """Simple file parser that only handles text extraction"""
    
    def __init__(self):
        self.esg_patterns = {
            'energy': r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:kwh|mwh|kilowatt)',
            'water': r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:liters?|gallons?|m³|cubic meters?)',
            'waste': r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:kg|tons?|metric tons?)',
            'carbon': r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:tco2|tons? co2|metric tons?)',
            'employees': r'(?:total\s+)?(?:employees?|staff|workforce)[:\s]+(\d+)',
            'training': r'training\s+hours?[:\s]+(\d+(?:,\d{3})*(?:\.\d+)?)',
        }
    
    def parse_file(self, file_path: str, file_obj=None) -> SimpleExtractedData:
        """Parse file and extract basic text"""
        file_name = file_path.split('/')[-1] if '/' in file_path else file_path
        file_extension = file_name.split('.')[-1].lower() if '.' in file_name else 'unknown'
        
        extracted_data = SimpleExtractedData(file_name, file_extension)
        
        try:
            # Try to read as text
            if file_obj and hasattr(file_obj, 'read'):
                content = file_obj.read()
                if isinstance(content, bytes):
                    text = content.decode('utf-8', errors='ignore')
                else:
                    text = str(content)
            else:
                text = f"Simple parser - file: {file_name}"
            
            extracted_data.raw_text = text
            
            # Extract basic metrics from text
            self._extract_simple_metrics(extracted_data, text)
            
            # Calculate confidence based on found metrics
            extracted_data.confidence_score = self._calculate_simple_confidence(extracted_data)
            
        except Exception as e:
            logger.error(f"Error in simple parser for {file_name}: {e}")
            extracted_data.raw_text = f"Error: {str(e)}"
        
        return extracted_data
    
    def _extract_simple_metrics(self, data: SimpleExtractedData, text: str):
        """Extract basic ESG metrics from text"""
        if not text:
            return
        
        text_lower = text.lower()
        
        # Extract energy
        energy_match = re.search(self.esg_patterns['energy'], text_lower)
        if energy_match:
            data.energy_consumption_kwh = self._parse_number(energy_match.group(1))
        
        # Extract water
        water_match = re.search(self.esg_patterns['water'], text_lower)
        if water_match:
            data.water_usage_liters = self._parse_number(water_match.group(1))
        
        # Extract waste
        waste_match = re.search(self.esg_patterns['waste'], text_lower)
        if waste_match:
            data.waste_generated_kg = self._parse_number(waste_match.group(1))
        
        # Extract carbon
        carbon_match = re.search(self.esg_patterns['carbon'], text_lower)
        if carbon_match:
            data.carbon_emissions_tco2 = self._parse_number(carbon_match.group(1))
        
        # Extract employees
        employee_match = re.search(self.esg_patterns['employees'], text_lower)
        if employee_match:
            data.total_employees = int(self._parse_number(employee_match.group(1)) or 0)
        
        # Extract training
        training_match = re.search(self.esg_patterns['training'], text_lower)
        if training_match:
            data.training_hours = self._parse_number(training_match.group(1))
        
        # Extract percentages for scores
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
        percentages = re.findall(percentage_pattern, text)
        
        if percentages and 'renewable' in text_lower:
            for pct in percentages:
                value = float(pct)
                if 0 <= value <= 100:
                    data.renewable_energy_percentage = value
                    break
        
        if percentages and 'satisfaction' in text_lower:
            for pct in percentages:
                value = float(pct)
                if 50 <= value <= 100:
                    data.employee_satisfaction_score = value
                    break
        
        if percentages and 'compliance' in text_lower:
            for pct in percentages:
                value = float(pct)
                if 0 <= value <= 100:
                    data.compliance_score = value
                    break
    
    def _parse_number(self, value_str: str) -> Optional[float]:
        """Parse number from string"""
        if not value_str:
            return None
        
        # Clean the string
        clean_str = value_str.replace(',', '').strip()
        
        try:
            return float(clean_str)
        except:
            return None
    
    def _calculate_simple_confidence(self, data: SimpleExtractedData) -> float:
        """Calculate simple confidence score"""
        metrics_found = 0
        total_metrics = 11
        
        if data.energy_consumption_kwh is not None:
            metrics_found += 1
        if data.water_usage_liters is not None:
            metrics_found += 1
        if data.waste_generated_kg is not None:
            metrics_found += 1
        if data.carbon_emissions_tco2 is not None:
            metrics_found += 1
        if data.renewable_energy_percentage is not None:
            metrics_found += 1
        if data.total_employees is not None:
            metrics_found += 1
        if data.training_hours is not None:
            metrics_found += 1
        if data.safety_incidents is not None:
            metrics_found += 1
        if data.employee_satisfaction_score is not None:
            metrics_found += 1
        if data.board_meetings is not None:
            metrics_found += 1
        if data.compliance_score is not None:
            metrics_found += 1
        
        # Basic confidence calculation
        if data.raw_text and len(data.raw_text) > 50:
            base_confidence = 30
        else:
            base_confidence = 10
        
        metric_confidence = (metrics_found / total_metrics) * 70
        
        return min(base_confidence + metric_confidence, 100.0)