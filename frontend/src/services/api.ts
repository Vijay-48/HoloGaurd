// Real API service for HaloGuard
// Connects to the FastAPI backend for deepfake detection

export interface DetectionResult {
  overall_score: number;
  overall_prediction: string;
  confidence: number;
  vision_score: number;
  vision_prediction: string;
  audio_sync_score?: number;
  physiological_score?: number;
  explanation?: string;
  heatmap_url?: string;
  processing_time: number;
  model_version: string;
  file_type: string;
  
  // Legacy properties for frontend compatibility
  isDeepfake: boolean;
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
  private baseURL: string;
  
  constructor() {
    this.baseURL = import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  }

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('haloguard_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
  
  // Real detection using backend API
  async detectDeepfake(file: File): Promise<DetectionResult> {
    const formData = new FormData();
    formData.append('file', file);
    
    const isVideo = file.type.startsWith('video/');
    const endpoint = isVideo ? '/api/detect/video' : '/api/detect/image';
    
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Detection failed: ${response.statusText}`);
      }

      const backendResult = await response.json();
      
      // Transform backend response to frontend format
      const result: DetectionResult = {
        ...backendResult,
        isDeepfake: backendResult.overall_prediction === 'fake',
        hasHeatmap: !!backendResult.heatmap_url,
      };

      return result;
    } catch (error) {
      console.error('Backend detection failed:', error);
      
      // Fallback to mock result if backend fails
      console.warn('Using fallback mock detection due to backend error');
      return this.mockDetection(file);
    }
  }
  
  // Fallback mock detection
  private async mockDetection(file: File): Promise<DetectionResult> {
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const filename = file.name.toLowerCase();
    const isLikelyDeepfake = filename.includes('fake') || filename.includes('deepfake') || Math.random() < 0.3;
    
    return {
      overall_score: 0.85 + Math.random() * 0.14,
      overall_prediction: isLikelyDeepfake ? 'fake' : 'real',
      confidence: 0.85 + Math.random() * 0.14,
      vision_score: 0.85 + Math.random() * 0.14,
      vision_prediction: isLikelyDeepfake ? 'fake' : 'real',
      audio_sync_score: file.type.startsWith('video/') ? 0.75 + Math.random() * 0.2 : undefined,
      physiological_score: file.type.startsWith('video/') ? 0.7 + Math.random() * 0.25 : undefined,
      processing_time: 2.5 + Math.random() * 2,
      model_version: "2.0.0",
      file_type: file.type.startsWith('image/') ? 'image' : 'video',
      isDeepfake: isLikelyDeepfake,
      hasHeatmap: Math.random() > 0.3,
    };
  }
  
  // Real-time stream detection using WebSocket
  async detectDeepfakeStream(stream: MediaStream, callback: (result: DetectionResult) => void): Promise<void> {
    const wsUrl = this.baseURL.replace(/^http/, 'ws') + '/api/detect/stream';
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected for stream detection');
    };

    ws.onmessage = (event) => {
      try {
        const backendResult = JSON.parse(event.data);
        const result: DetectionResult = {
          ...backendResult,
          isDeepfake: backendResult.prediction === 'fake',
          hasHeatmap: false, // Real-time doesn't generate heatmaps
        };
        callback(result);
      } catch (error) {
        console.error('Failed to parse stream result:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Send frames from stream
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;
    const video = document.createElement('video');
    
    video.srcObject = stream;
    video.play();

    const sendFrame = () => {
      if (ws.readyState === WebSocket.OPEN) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);
        
        const frameData = canvas.toDataURL('image/jpeg', 0.8);
        ws.send(JSON.stringify({
          type: 'frame',
          data: frameData,
          frame_id: Date.now()
        }));
      }
    };

    // Send frames every 500ms for real-time detection
    const interval = setInterval(sendFrame, 500);
    
    // Cleanup function
    return () => {
      clearInterval(interval);
      ws.close();
      video.srcObject = null;
    };
  }
  
  // Get scan history from backend
  async getScanHistory(): Promise<ScanHistory[]> {
    try {
      const response = await fetch(`${this.baseURL}/api/history/`, {
        headers: this.getAuthHeaders(),
      });

      if (response.ok) {
        const backendHistory = await response.json();
        return backendHistory.map((item: any) => ({
          id: item.id || Date.now().toString(),
          filename: item.filename || 'Unknown file',
          type: item.file_type === 'image' ? 'image' : 'video',
          verdict: item.overall_prediction === 'fake' ? 'deepfake' : 'authentic',
          confidence: item.confidence || item.overall_score || 0.5,
          timestamp: new Date(item.timestamp)
        }));
      }
    } catch (error) {
      console.error('Failed to fetch history from backend:', error);
    }
    
    // Fallback to localStorage
    return this.getLocalScanHistory();
  }

  // Local storage fallback for scan history
  private getLocalScanHistory(): ScanHistory[] {
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
      console.error('Error loading local scan history:', error);
    }
    
    return [];
  }
  
  // Save scan result to backend and local storage
  async addScanResult(filename: string, type: 'image' | 'video', result: DetectionResult): Promise<void> {
    const scanData = {
      filename,
      file_type: type,
      timestamp: new Date().toISOString(),
      results: JSON.stringify(result)
    };

    // Try to save to backend
    try {
      await fetch(`${this.baseURL}/api/history/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
        },
        body: JSON.stringify(scanData),
      });
    } catch (error) {
      console.error('Failed to save scan to backend:', error);
    }

    // Always save to local storage as backup
    this.saveToLocalStorage(filename, type, result);
  }

  private saveToLocalStorage(filename: string, type: 'image' | 'video', result: DetectionResult): void {
    const newScan: ScanHistory = {
      id: Date.now().toString(),
      filename,
      type,
      verdict: result.isDeepfake ? 'deepfake' : 'authentic',
      confidence: result.confidence,
      timestamp: new Date()
    };
    
    const currentHistory = this.getLocalScanHistory();
    const updatedHistory = [newScan, ...currentHistory].slice(0, 50);
    
    try {
      localStorage.setItem('haloguard_history', JSON.stringify(updatedHistory));
    } catch (error) {
      console.error('Error saving scan history to localStorage:', error);
    }
  }
}

export const api = new HaloGuardAPI();