import React, { useState } from 'react';
import { Shield, LogIn, History, Menu, X, User } from 'lucide-react';

import { Button } from '@/components/ui/button';
import UploadForm from '@/components/UploadForm';
import ResultDisplay from '@/components/ResultDisplay';
import HistoryList from '@/components/HistoryList';
import LoginForm from '@/components/AuthForms/LoginForm';
import SignupForm from '@/components/AuthForms/SignupForm';
import SpiderIcon from '@/components/SpiderIcon';
import { useAuth } from '@/hooks/useAuth';
import { api, DetectionResult } from '@/services/api';

type ViewState = 'scanner' | 'history' | 'auth';
type AuthMode = 'login' | 'signup';

const Index = () => {
  const { user, logout } = useAuth();
  const [currentView, setCurrentView] = useState<ViewState>('scanner');
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleFileAnalysis = async (file: File) => {
    setIsAnalyzing(true);
    try {
      const analysisResult = await api.detectDeepfake(file);
      setResult(analysisResult);
      
      // Add to scan history
      const fileType = file.type.startsWith('image/') ? 'image' : 'video';
      api.addScanResult(file.name, fileType, analysisResult);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleNewScan = () => {
    setResult(null);
  };

  const handleRescan = (id: string) => {
    console.log('Rescanning item:', id);
    // In a real app, this would trigger a new scan
  };

  const handleViewHeatmap = () => {
    console.log('Viewing heatmap...');
    // In a real app, this would show the heatmap overlay
  };

  const renderHeader = () => (
    <header className="bg-card web-border border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <SpiderIcon size={32} className="text-white" animate />
            <h1 className="text-2xl font-bold text-shadow-glow">HALOGUARD</h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Button
              variant={currentView === 'scanner' ? 'default' : 'ghost'}
              onClick={() => setCurrentView('scanner')}
              className="web-ripple"
            >
              <Shield className="w-4 h-4 mr-2" />
              Scanner
            </Button>
            
            {user && (
              <Button
                variant={currentView === 'history' ? 'default' : 'ghost'}
                onClick={() => setCurrentView('history')}
                className="web-ripple"
              >
                <History className="w-4 h-4 mr-2" />
                History
              </Button>
            )}
            
            {!user && (
              <Button
                variant={currentView === 'auth' ? 'default' : 'outline'}
                onClick={() => setCurrentView('auth')}
                className="web-ripple"
              >
                <LogIn className="w-4 h-4 mr-2" />
                Sign In
              </Button>
            )}
            
            <SignedIn>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </nav>

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-border pt-4 pb-4">
            <div className="space-y-2">
              <Button
                variant={currentView === 'scanner' ? 'default' : 'ghost'}
                onClick={() => {
                  setCurrentView('scanner');
                  setMobileMenuOpen(false);
                }}
                className="w-full justify-start web-ripple"
              >
                <Shield className="w-4 h-4 mr-2" />
                Scanner
              </Button>
              
              <SignedIn>
                <Button
                  variant={currentView === 'history' ? 'default' : 'ghost'}
                  onClick={() => {
                    setCurrentView('history');
                    setMobileMenuOpen(false);
                  }}
                  className="w-full justify-start web-ripple"
                >
                  <History className="w-4 h-4 mr-2" />
                  History
                </Button>
              </SignedIn>
              
              <SignedOut>
                <Button
                  variant={currentView === 'auth' ? 'default' : 'ghost'}
                  onClick={() => {
                    setCurrentView('auth');
                    setMobileMenuOpen(false);
                  }}
                  className="w-full justify-start web-ripple"
                >
                  <LogIn className="w-4 h-4 mr-2" />
                  Sign In
                </Button>
              </SignedOut>
              
              <SignedIn>
                <div className="px-4 py-2">
                  <UserButton afterSignOutUrl="/" />
                </div>
              </SignedIn>
            </div>
          </div>
        )}
      </div>
    </header>
  );

  const renderContent = () => {
    if (currentView === 'auth' && !user) {
      return (
        <div className="min-h-screen bg-web-pattern flex items-center justify-center p-4">
          {authMode === 'login' ? (
            <LoginForm
              onSwitchToSignup={() => setAuthMode('signup')}
            />
          ) : (
            <SignupForm
              onSwitchToLogin={() => setAuthMode('login')}
            />
          )}
        </div>
      );
    }

    if (currentView === 'history' && user) {
      const history = api.getScanHistory();
      return (
        <div className="min-h-screen bg-web-pattern">
          {renderHeader()}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <HistoryList history={history} onRescan={handleRescan} />
          </main>
        </div>
      );
    }

    // Default scanner view
    return (
      <div className="min-h-screen bg-web-pattern">
        {renderHeader()}
        <main className="flex-1 flex items-center justify-center p-4">
          <div className="w-full max-w-4xl">
            {/* Hero Section */}
            {!isAnalyzing && !result && (
              <div className="text-center mb-12">
                <div className="mb-8">
                  <SpiderIcon size={80} className="mx-auto mb-4 text-white" animate />
                  <h1 className="text-6xl font-bold mb-4 text-shadow-glow">
                    HALOGUARD
                  </h1>
                  <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                    Advanced deepfake detection powered by neural networks. 
                    Upload images or videos to verify their authenticity.
                  </p>
                </div>
              </div>
            )}

            {/* Main Content */}
            {result ? (
              <ResultDisplay
                result={result}
                onNewScan={handleNewScan}
                onViewHeatmap={result.hasHeatmap ? handleViewHeatmap : undefined}
              />
            ) : (
              <UploadForm onSubmit={handleFileAnalysis} isLoading={isAnalyzing} />
            )}
          </div>
        </main>
      </div>
    );
  };

  return renderContent();
};

export default Index;
