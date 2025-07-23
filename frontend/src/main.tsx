
import { createRoot } from 'react-dom/client';

import App from './App.tsx';
import './index.css';





}

createRoot(document.getElementById("root")!).render(
  <ClerkProvider publishableKey={PUBLISHABLE_KEY} afterSignOutUrl="/">
    <App />
  </ClerkProvider>
);
