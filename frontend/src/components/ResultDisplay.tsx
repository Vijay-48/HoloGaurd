
import React from 'react';
import { Shield, ShieldAlert, Eye, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import SpiderIcon from './SpiderIcon';

interface AnalysisResult {
  isDeepfake: boolean;
  confidence: number;
  processing_time: number;
  hasHeatmap?: boolean;
}

interface ResultDisplayProps {
  result: AnalysisResult;
  onNewScan: () => void;
  onViewHeatmap?: () => void;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ 
  result, 
  onNewScan, 
  onViewHeatmap 
}) => {
  const confidencePercentage = Math.round(result.confidence * 100);
  const verdictColor = result.isDeepfake ? 'text-red-400' : 'text-green-400';
  const verdictIcon = result.isDeepfake ? ShieldAlert : Shield;
  const VerdictIcon = verdictIcon;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Main Result Card */}
      <Card className="bg-card web-border">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto w-20 h-20 rounded-full bg-muted flex items-center justify-center mb-4">
            <VerdictIcon className={`w-10 h-10 ${verdictColor}`} />
          </div>
          <CardTitle className="text-2xl">
            <span className={verdictColor}>
              {result.isDeepfake ? 'DEEPFAKE DETECTED' : 'AUTHENTIC MEDIA'}
            </span>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Confidence Gauge */}
          <div className="text-center space-y-4">
            <div className="relative w-32 h-32 mx-auto">
              {/* Background circle */}
              <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="8"
                  fill="transparent"
                />
                {/* Progress circle */}
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  stroke={result.isDeepfake ? '#ef4444' : '#22c55e'}
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray={`${confidencePercentage * 2.83} 283`}
                  strokeLinecap="round"
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              
              {/* Center content */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-2xl font-bold">{confidencePercentage}%</span>
                <span className="text-sm text-muted-foreground">Confidence</span>
              </div>
            </div>
            
            <p className="text-muted-foreground">
              Analysis completed in {result.processing_time.toFixed(2)}s
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={onNewScan}
              variant="outline"
              className="flex-1 web-ripple"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              New Scan
            </Button>
            
            {result.hasHeatmap && onViewHeatmap && (
              <Button
                onClick={onViewHeatmap}
                variant="secondary"
                className="flex-1 web-ripple"
              >
                <Eye className="w-4 h-4 mr-2" />
                View Heatmap
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Technical Details */}
      <Card className="bg-card web-border">
        <CardHeader>
          <CardTitle className="flex items-center text-lg">
            <SpiderIcon size={20} className="mr-2" />
            Detection Details
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Algorithm:</span>
              <p className="font-medium">Neural Network Analysis</p>
            </div>
            <div>
              <span className="text-muted-foreground">Model Version:</span>
              <p className="font-medium">HaloGuard v2.1</p>
            </div>
            <div>
              <span className="text-muted-foreground">Scan Type:</span>
              <p className="font-medium">Deep Learning Detection</p>
            </div>
            <div>
              <span className="text-muted-foreground">Risk Level:</span>
              <p className={`font-medium ${result.isDeepfake ? 'text-red-400' : 'text-green-400'}`}>
                {result.isDeepfake ? 'HIGH' : 'LOW'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ResultDisplay;
