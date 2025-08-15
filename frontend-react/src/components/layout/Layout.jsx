import React from 'react';
import Header from './Header';
// import TaskMonitor from '../monitoring/TaskMonitor'; // Hidden for production

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen text-text-high font-inter bg-gradient-to-br from-[#131A2C] via-[#1C1330] to-[#131A2C]">
      <Header />
      <main className="px-6 lg:px-20 py-8">
        {children}
      </main>
      {/* TaskMonitor - Hidden for production */}
      {process.env.NODE_ENV === 'development' && false && (
        <TaskMonitor />
      )}
    </div>
  );
};

export default Layout;