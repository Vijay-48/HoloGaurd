
import { useUser, useAuth as useClerkAuth } from '@clerk/clerk-react';

interface AuthUser {
  id: string;
  email: string;
  name: string;
}

export const useAuth = () => {
  const { user, isLoaded } = useUser();
  const { signOut } = useClerkAuth();

  const authUser: AuthUser | null = user ? {
    id: user.id,
    email: user.emailAddresses[0]?.emailAddress || '',
    name: user.fullName || user.firstName || 'User'
  } : null;

  return {
    user: authUser,
    session: user ? { user: authUser } : null,
    login: async () => {
      // Clerk handles login through SignIn component
      throw new Error('Use SignIn component for login');
    },
    signup: async () => {
      // Clerk handles signup through SignUp component
      throw new Error('Use SignUp component for signup');
    },
    logout: signOut,
    isLoading: !isLoaded
  };
};
