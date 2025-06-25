
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Shield, ShieldAlert, RotateCcw, Calendar, FileImage, FileVideo } from 'lucide-react';
import SpiderIcon from './SpiderIcon';

interface ScanHistory {
  id: string;
  filename: string;
  type: 'image' | 'video';
  verdict: 'authentic' | 'deepfake';
  confidence: number;
  timestamp: Date;
}

interface HistoryListProps {
  history: ScanHistory[];
  onRescan: (id: string) => void;
}

const HistoryList: React.FC<HistoryListProps> = ({ history, onRescan }) => {
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  if (history.length === 0) {
    return (
      <Card className="bg-card web-border">
        <CardContent className="text-center py-12">
          <SpiderIcon size={48} className="mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">No Scans Yet</h3>
          <p className="text-muted-foreground">
            Your deepfake detection history will appear here
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card web-border">
      <CardHeader>
        <CardTitle className="flex items-center">
          <SpiderIcon size={20} className="mr-2" />
          Scan History
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {history.map((scan) => {
            const isDeepfake = scan.verdict === 'deepfake';
            const VerdictIcon = isDeepfake ? ShieldAlert : Shield;
            const TypeIcon = scan.type === 'image' ? FileImage : FileVideo;
            
            return (
              <div
                key={scan.id}
                className="flex items-center justify-between p-4 bg-muted rounded-lg web-border hover:bg-accent transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-background rounded-full flex items-center justify-center">
                    <TypeIcon className="w-5 h-5 text-muted-foreground" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium truncate">{scan.filename}</h4>
                    <div className="flex items-center space-x-3 text-sm text-muted-foreground">
                      <span className="flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        {formatDate(scan.timestamp)}
                      </span>
                      <span className="flex items-center">
                        <VerdictIcon className={`w-3 h-3 mr-1 ${
                          isDeepfake ? 'text-red-400' : 'text-green-400'
                        }`} />
                        {Math.round(scan.confidence * 100)}% confidence
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Badge
                    variant={isDeepfake ? 'destructive' : 'secondary'}
                    className={isDeepfake ? 'bg-red-900 text-red-100' : 'bg-green-900 text-green-100'}
                  >
                    {isDeepfake ? 'Deepfake' : 'Authentic'}
                  </Badge>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onRescan(scan.id)}
                    className="web-ripple"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default HistoryList;
