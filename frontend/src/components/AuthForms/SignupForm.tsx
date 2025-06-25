
import React from 'react';
import { SignUp } from '@clerk/clerk-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import SpiderIcon from '../SpiderIcon';

interface SignupFormProps {
  onSubmit?: (name: string, email: string, password: string) => Promise<void>;
  onSwitchToLogin: () => void;
}

const SignupForm: React.FC<SignupFormProps> = ({ onSwitchToLogin }) => {
  return (
    <Card className="w-full max-w-md mx-auto bg-card web-border">
      <CardHeader className="text-center">
        <div className="mx-auto w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
          <SpiderIcon size={32} />
        </div>
        <CardTitle className="text-2xl">Join HaloGuard</CardTitle>
        <p className="text-muted-foreground">Create your account to start detecting deepfakes</p>
      </CardHeader>
      
      <CardContent>
        <SignUp 
          routing="hash"
          signInUrl="#"
          afterSignUpUrl="/"
        />
        
        <div className="mt-6 text-center">
          <p className="text-sm text-muted-foreground">
            Already have an account?{' '}
            <button
              onClick={onSwitchToLogin}
              className="text-primary hover:underline font-medium"
            >
              Sign in
            </button>
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default SignupForm;
