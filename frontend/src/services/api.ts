
// Mock API service for HaloGuard
// In a real implementation, this would connect to actual deepfake detection APIs

export interface DetectionResult {
  isDeepfake: boolean;
  confidence: number;
  processing_time: number;
  hasHeatmap?: boolean;
}

export interface ScanHistory {
  id: string;
  filename: string;
  type: 'image' | 'video';
  verdict: 'authentic' | 'deepfake';
  confidence: number;
  timestamp: Date;
}

class HaloGuardAPI {
  private baseURL = '/api'; // This would be your actual API endpoint
  
  // Mock detection - simulates AI analysis
  async detectDeepfake(file: File): Promise<DetectionResult> {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 3000 + Math.random() * 2000));
    
    // Mock result based on filename patterns for demo
    const filename = file.name.toLowerCase();
    const isLikelyDeepfake = filename.includes('fake') || filename.includes('deepfake') || Math.random() < 0.3;
    
    return {
      isDeepfake: isLikelyDeepfake,
      confidence: 0.85 + Math.random() * 0.14, // 85-99% confidence
      processing_time: 2.5 + Math.random() * 2, // 2.5-4.5 seconds
      hasHeatmap: Math.random() > 0.3 // 70% chance of heatmap
    };
  }
  
  // Mock video stream detection
  async detectDeepfakeStream(stream: MediaStream): Promise<DetectionResult> {
    // Simulate real-time processing
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return {
      isDeepfake: Math.random() < 0.2, // 20% chance for demo
      confidence: 0.75 + Math.random() * 0.2,
      processing_time: 1.2,
      hasHeatmap: false // Real-time doesn't generate heatmaps
    };
  }
  
  // Get scan history - now uses localStorage for demo purposes
  getScanHistory(): ScanHistory[] {
    try {
      const stored = localStorage.getItem('haloguard_history');
      if (stored) {
        const parsed = JSON.parse(stored);
        return parsed.map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }));
      }
    } catch (error) {
      console.error('Error loading scan history:', error);
    }
    
    // Return mock data if nothing in localStorage
    const mockHistory: ScanHistory[] = [
      {
        id: '1',
        filename: 'profile_photo.jpg',
        type: 'image',
        verdict: 'authentic',
        confidence: 0.94,
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
      },
      {
        id: '2',
        filename: 'suspicious_video.mp4',
        type: 'video',
        verdict: 'deepfake',
        confidence: 0.87,
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000) // 1 day ago
      },
      {
        id: '3',
        filename: 'family_reunion.jpg',
        type: 'image',
        verdict: 'authentic',
        confidence: 0.98,
        timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) // 3 days ago
      }
    ];
    
    // Store mock data for future use
    this.saveScanHistory(mockHistory);
    return mockHistory;
  }
  
  // Save scan history to localStorage
  private saveScanHistory(history: ScanHistory[]): void {
    try {
      localStorage.setItem('haloguard_history', JSON.stringify(history));
    } catch (error) {
      console.error('Error saving scan history:', error);
    }
  }
  
  // Add new scan result to history
  addScanResult(filename: string, type: 'image' | 'video', result: DetectionResult): void {
    const newScan: ScanHistory = {
      id: Date.now().toString(),
      filename,
      type,
      verdict: result.isDeepfake ? 'deepfake' : 'authentic',
      confidence: result.confidence,
      timestamp: new Date()
    };
    
    const currentHistory = this.getScanHistory();
    const updatedHistory = [newScan, ...currentHistory].slice(0, 50); // Keep last 50 scans
    this.saveScanHistory(updatedHistory);
  }
}

export const api = new HaloGuardAPI();
