import React from 'react';
import { useLocation, Link } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  
  // SessionDetail page has its own full-width layout
  const isDetailPage = location.pathname.includes('/sessions/') && location.pathname !== '/sessions';

  return (
    <div className="min-h-screen bg-surface-100 flex flex-col safe-area-inset">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-20 flex-shrink-0">
        <div className="max-w-screen-2xl mx-auto px-3 sm:px-6 lg:px-8 py-2.5 sm:py-3">
          <Link 
            to="/sessions" 
            className="flex items-center gap-2 sm:gap-3 hover:opacity-80 transition-opacity"
          >
            {/* Logo/Icon */}
            <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-sm flex-shrink-0">
              <svg className="w-4 h-4 sm:w-5 sm:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div className="min-w-0">
              <h1 className="text-sm sm:text-base font-semibold text-gray-900 leading-tight truncate">
                Cerina Protocol Foundry
              </h1>
              <p className="text-[10px] sm:text-xs text-gray-400 hidden xs:block">
                CBT Exercise Design System
              </p>
            </div>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className={`flex-1 ${isDetailPage ? '' : 'py-4 sm:py-6 lg:py-8'}`}>
        {children}
      </main>

      {/* Footer - hide on detail page and mobile for cleaner look */}
      {!isDetailPage && (
        <footer className="hidden sm:block border-t border-gray-200 bg-white flex-shrink-0">
          <div className="content-container py-4">
            <p className="text-xs text-gray-400 text-center">
              Cerina Protocol Foundry — Multi-Agent CBT Protocol Designer
            </p>
          </div>
        </footer>
      )}
    </div>
  );
};
