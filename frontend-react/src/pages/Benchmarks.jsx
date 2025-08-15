import React, { useState } from 'react';
import Layout from '../components/layout/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const Benchmarks = () => {
  const [selectedSector, setSelectedSector] = useState('hospitality');
  const [selectedMetric, setSelectedMetric] = useState('carbon_intensity');

  // Mock benchmark data
  const benchmarkData = {
    hospitality: {
      carbon_intensity: {
        industry_average: 45.8,
        your_performance: 38.2,
        top_quartile: 32.1,
        unit: 'kg CO2e/room night',
        trend: 'improving'
      },
      energy_intensity: {
        industry_average: 125.5,
        your_performance: 110.3,
        top_quartile: 95.7,
        unit: 'kWh/room night',
        trend: 'stable'
      },
      water_intensity: {
        industry_average: 285.2,
        your_performance: 320.1,
        top_quartile: 210.8,
        unit: 'liters/room night',
        trend: 'declining'
      },
      waste_diversion: {
        industry_average: 42.5,
        your_performance: 55.8,
        top_quartile: 68.3,
        unit: '% diverted',
        trend: 'improving'
      }
    }
  };

  const sectors = [
    { value: 'hospitality', label: 'Hospitality & Tourism' },
    { value: 'construction', label: 'Construction & Real Estate' },
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'logistics', label: 'Logistics & Transportation' },
    { value: 'education', label: 'Education' },
    { value: 'health', label: 'Healthcare' }
  ];

  const metrics = [
    { value: 'carbon_intensity', label: 'Carbon Intensity', icon: 'fa-solid fa-leaf' },
    { value: 'energy_intensity', label: 'Energy Intensity', icon: 'fa-solid fa-bolt' },
    { value: 'water_intensity', label: 'Water Intensity', icon: 'fa-solid fa-tint' },
    { value: 'waste_diversion', label: 'Waste Diversion', icon: 'fa-solid fa-recycle' }
  ];

  const currentData = benchmarkData[selectedSector]?.[selectedMetric];

  const getPerformanceColor = (yourValue, industryAvg, isHigherBetter = false) => {
    const ratio = yourValue / industryAvg;
    if (isHigherBetter) {
      return ratio >= 1.1 ? 'text-green-400' : ratio >= 0.9 ? 'text-yellow-400' : 'text-red-400';
    } else {
      return ratio <= 0.9 ? 'text-green-400' : ratio <= 1.1 ? 'text-yellow-400' : 'text-red-400';
    }
  };

  const getPerformanceMessage = (yourValue, industryAvg, topQuartile, isHigherBetter = false) => {
    if (isHigherBetter) {
      if (yourValue >= topQuartile) return "Excellent - Top quartile performance";
      if (yourValue >= industryAvg) return "Good - Above industry average";
      return "Below average - Room for improvement";
    } else {
      if (yourValue <= topQuartile) return "Excellent - Top quartile performance";
      if (yourValue <= industryAvg) return "Good - Below industry average";
      return "Above average - Room for improvement";
    }
  };

  const getTrendIcon = (trend) => {
    const icons = {
      'improving': 'fa-solid fa-arrow-trend-up text-green-400',
      'stable': 'fa-solid fa-minus text-yellow-400',
      'declining': 'fa-solid fa-arrow-trend-down text-red-400'
    };
    return icons[trend] || 'fa-solid fa-minus text-gray-400';
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-text-high mb-2">ESG Benchmarks</h1>
            <p className="text-text-muted">Compare your sustainability performance with industry standards</p>
          </div>
          <Button variant="outline">
            <i className="fa-solid fa-download mr-2"></i>
            Export Report
          </Button>
        </div>

        {/* Sector Selection */}
        <Card className="mb-8">
          <h3 className="text-lg font-semibold text-text-high mb-4">Select Industry Sector</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {sectors.map((sector) => (
              <button
                key={sector.value}
                onClick={() => setSelectedSector(sector.value)}
                className={`p-3 rounded-lg text-sm font-medium transition-colors ${
                  selectedSector === sector.value
                    ? 'bg-brand-green text-white'
                    : 'bg-white/5 text-text-muted hover:bg-white/10 hover:text-text-high'
                }`}
              >
                {sector.label}
              </button>
            ))}
          </div>
        </Card>

        {/* Metrics Selection */}
        <Card className="mb-8">
          <h3 className="text-lg font-semibold text-text-high mb-4">Performance Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {metrics.map((metric) => (
              <button
                key={metric.value}
                onClick={() => setSelectedMetric(metric.value)}
                className={`p-4 rounded-lg text-left transition-colors ${
                  selectedMetric === metric.value
                    ? 'bg-brand-green/20 border-2 border-brand-green'
                    : 'bg-white/5 border-2 border-white/10 hover:border-white/20'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <i className={`${metric.icon} text-lg ${
                    selectedMetric === metric.value ? 'text-brand-green' : 'text-text-muted'
                  }`}></i>
                  <span className={`font-medium ${
                    selectedMetric === metric.value ? 'text-brand-green' : 'text-text-high'
                  }`}>
                    {metric.label}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </Card>

        {/* Benchmark Results */}
        {currentData ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Performance Overview */}
            <Card>
              <h3 className="text-lg font-semibold text-text-high mb-6 flex items-center">
                <i className="fa-solid fa-chart-bar mr-2 text-brand-green"></i>
                Performance Comparison
              </h3>
              
              <div className="space-y-6">
                {/* Your Performance */}
                <div className="bg-white/5 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-text-muted text-sm">Your Performance</span>
                    <i className={getTrendIcon(currentData.trend)}></i>
                  </div>
                  <div className={`text-2xl font-bold ${getPerformanceColor(
                    currentData.your_performance, 
                    currentData.industry_average,
                    selectedMetric === 'waste_diversion'
                  )}`}>
                    {currentData.your_performance} {currentData.unit}
                  </div>
                </div>

                {/* Industry Average */}
                <div className="bg-white/5 rounded-lg p-4">
                  <div className="text-text-muted text-sm mb-2">Industry Average</div>
                  <div className="text-xl font-semibold text-text-high">
                    {currentData.industry_average} {currentData.unit}
                  </div>
                </div>

                {/* Top Quartile */}
                <div className="bg-white/5 rounded-lg p-4">
                  <div className="text-text-muted text-sm mb-2">Top Quartile</div>
                  <div className="text-xl font-semibold text-green-400">
                    {currentData.top_quartile} {currentData.unit}
                  </div>
                </div>

                {/* Performance Message */}
                <div className="bg-brand-blue/10 border border-brand-blue/20 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <i className="fa-solid fa-info-circle text-brand-blue mt-1"></i>
                    <div>
                      <h4 className="text-brand-blue font-medium mb-1">Performance Insight</h4>
                      <p className="text-text-muted text-sm">
                        {getPerformanceMessage(
                          currentData.your_performance,
                          currentData.industry_average,
                          currentData.top_quartile,
                          selectedMetric === 'waste_diversion'
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Visualization */}
            <Card>
              <h3 className="text-lg font-semibold text-text-high mb-6 flex items-center">
                <i className="fa-solid fa-chart-column mr-2 text-brand-green"></i>
                Benchmark Visualization
              </h3>

              <div className="space-y-4">
                {/* Bar Chart Simulation */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-muted">Top Quartile</span>
                    <span className="text-sm font-medium">{currentData.top_quartile}</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-3">
                    <div 
                      className="bg-green-400 h-3 rounded-full" 
                      style={{ width: '100%' }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-muted">Your Performance</span>
                  <span className="text-sm font-medium">{currentData.your_performance}</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-3">
                  <div 
                    className={`h-3 rounded-full ${
                      getPerformanceColor(currentData.your_performance, currentData.industry_average, selectedMetric === 'waste_diversion')
                        .includes('green') ? 'bg-green-400' :
                      getPerformanceColor(currentData.your_performance, currentData.industry_average, selectedMetric === 'waste_diversion')
                        .includes('yellow') ? 'bg-yellow-400' : 'bg-red-400'
                    }`}
                    style={{ 
                      width: `${Math.min((currentData.your_performance / Math.max(currentData.top_quartile, currentData.industry_average, currentData.your_performance)) * 100, 100)}%` 
                    }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-muted">Industry Average</span>
                  <span className="text-sm font-medium">{currentData.industry_average}</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-3">
                  <div 
                    className="bg-gray-400 h-3 rounded-full" 
                    style={{ 
                      width: `${Math.min((currentData.industry_average / Math.max(currentData.top_quartile, currentData.industry_average, currentData.your_performance)) * 100, 100)}%` 
                    }}
                  />
                </div>
              </div>

              {/* Recommendations */}
              <div className="mt-8 bg-brand-green/10 border border-brand-green/20 rounded-lg p-4">
                <h4 className="text-brand-green font-medium mb-2 flex items-center">
                  <i className="fa-solid fa-lightbulb mr-2"></i>
                  Improvement Recommendations
                </h4>
                <ul className="text-text-muted text-sm space-y-1">
                  <li>• Review best practices from top-performing companies in your sector</li>
                  <li>• Focus on the key metrics where you have the largest gaps</li>
                  <li>• Set specific targets to reach industry average within 12 months</li>
                  <li>• Consider implementing proven sustainability technologies</li>
                </ul>
              </div>
            </Card>
          </div>
        ) : (
          <Card>
            <div className="text-center py-12">
              <i className="fa-solid fa-chart-bar text-4xl text-text-muted mb-4"></i>
              <h3 className="text-text-high font-medium mb-2">No Benchmark Data Available</h3>
              <p className="text-text-muted">Benchmark data for this sector and metric combination is not available yet.</p>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default Benchmarks;