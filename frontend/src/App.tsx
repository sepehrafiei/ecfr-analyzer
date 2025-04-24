/**
 * Main application component for the eCFR Analyzer frontend.
 * Renders the agency table and handles loading states.
 * Provides the main layout and structure for the application.
 * 
 * @author Sepehr Rafiei
 */

import { Suspense } from "react";
import AgencyTable from "@/components/AgencyTable";

function App() {
  return (
    <div className="min-h-screen bg-white">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-center mb-12">Federal Regulations by Agency</h1>
        <Suspense fallback={<div>Loading...</div>}>
          <AgencyTable />
        </Suspense>
      </main>
    </div>
  );
}

export default App;
