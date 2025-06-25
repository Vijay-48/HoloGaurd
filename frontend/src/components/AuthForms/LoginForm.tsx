
import React from 'react';
import { SignIn } from '@clerk/clerk-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import SpiderIcon from '../SpiderIcon';

interface LoginFormProps {
  onSubmit?: (email: string, password: string) => Promise<void>;
  onSwitchToSignup: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSwitchToSignup }) => {
  return (
    <Card className="w-full max-w-md mx-auto bg-card web-border">
      <CardHeader className="text-center">
        <div className="mx-auto w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
          <SpiderIcon size={32} />
        </div>
        <CardTitle className="text-2xl">Welcome Back</CardTitle>
        <p className="text-muted-foreground">Sign in to your HaloGuard account</p>
      </CardHeader>
      
      <CardContent>
        <SignIn 
          routing="hash"
          signUpUrl="#"
          afterSignInUrl="/"
        />
        
        <div className="mt-6 text-center">
          <p className="text-sm text-muted-foreground">
            Don't have an account?{' '}
            <button
              onClick={onSwitchToSignup}
              className="text-primary hover:underline font-medium"
            >
              Sign up
            </button>
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default LoginForm;
