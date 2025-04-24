/**
 * Agency table component for displaying and interacting with agency data.
 * Provides sorting, filtering, and pagination functionality.
 * Renders agency metrics in a responsive grid layout.
 * 
 * @author Sepehr Rafiei
 */

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { ChevronUp, ChevronDown, Search, ArrowUpDown } from "lucide-react";

interface Agency {
  name: string;
  word_count: number;
  section_count: number;
}

const ITEMS_PER_PAGE = 12;

function formatNumber(num: number): string {
  if (num >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(2)}M`;
  }
  if (num >= 1_000) {
    return `${(num / 1_000).toFixed(2)}K`;
  }
  return num.toLocaleString();
}

export default function AgencyTable() {
  const [agencies, setAgencies] = useState<Agency[]>([]);
  const [filtered, setFiltered] = useState<Agency[]>([]);
  const [sort, setSort] = useState<"words" | "regulations" | "agency">("words");
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    const fetchAgencies = async () => {
      try {
        setIsLoading(true);
        const response = await fetch("http://localhost:8000/api/agencies");
        if (!response.ok) throw new Error("Failed to fetch agencies");
        const data = await response.json();
        setAgencies(data);
        setFiltered(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setIsLoading(false);
      }
    };

    fetchAgencies();
  }, []);

  useEffect(() => {
    let sorted = [...agencies];
    
    if (sort === "words") {
      sorted.sort((a, b) => 
        sortDirection === "desc" 
          ? b.word_count - a.word_count 
          : a.word_count - b.word_count
      );
    } else if (sort === "regulations") {
      sorted.sort((a, b) => 
        sortDirection === "desc" 
          ? b.section_count - a.section_count 
          : a.section_count - b.section_count
      );
    } else if (sort === "agency") {
      sorted.sort((a, b) => 
        sortDirection === "desc" 
          ? b.name.localeCompare(a.name) 
          : a.name.localeCompare(b.name)
      );
    }

    if (search) {
      sorted = sorted.filter((a) =>
        a.name.toLowerCase().includes(search.toLowerCase())
      );
    }

    setFiltered(sorted);
    setCurrentPage(1);
  }, [sort, search, agencies, sortDirection]);

  const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE);
  const paginatedAgencies = filtered.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const handleSort = (newSort: "words" | "regulations" | "agency") => {
    if (sort === newSort) {
      setSortDirection(sortDirection === "desc" ? "asc" : "desc");
    } else {
      setSort(newSort);
      setSortDirection("desc");
    }
  };

  if (error) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-semibold text-red-600">Error</h2>
        <p className="text-gray-600 mt-2">{error}</p>
        <Button 
          onClick={() => window.location.reload()} 
          className="mt-4"
        >
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col items-center gap-6">
        <div className="relative w-full" style={{ maxWidth: "calc(160px * 3 + 1rem * 2)" }}>
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search agencies..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 bg-white shadow-[0_2px_8px_rgba(0,0,0,0.1)] border-none h-11 transition-all duration-200 hover:shadow-[0_4px_12px_rgba(0,0,0,0.15)] focus-visible:ring-0 focus-visible:ring-offset-0 w-full"
          />
        </div>

        <div className="flex justify-center gap-4">
          <Button
            variant="ghost"
            onClick={() => handleSort("words")}
            className={`min-w-[160px] flex items-center gap-2 transition-all duration-200 ${
              sort === "words" 
                ? "bg-white shadow-[0_2px_8px_rgba(0,0,0,0.1)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.15)]" 
                : "hover:bg-gray-50 hover:shadow-[0_2px_8px_rgba(0,0,0,0.1)]"
            }`}
          >
            Sort by Words
            {sort === "words" && <ArrowUpDown className="h-4 w-4" />}
          </Button>
          <Button
            variant="ghost"
            onClick={() => handleSort("regulations")}
            className={`min-w-[160px] flex items-center gap-2 transition-all duration-200 ${
              sort === "regulations" 
                ? "bg-white shadow-[0_2px_8px_rgba(0,0,0,0.1)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.15)]" 
                : "hover:bg-gray-50 hover:shadow-[0_2px_8px_rgba(0,0,0,0.1)]"
            }`}
          >
            Sort by Regulations
            {sort === "regulations" && <ArrowUpDown className="h-4 w-4" />}
          </Button>
          <Button
            variant="ghost"
            onClick={() => handleSort("agency")}
            className={`min-w-[160px] flex items-center gap-2 transition-all duration-200 ${
              sort === "agency" 
                ? "bg-white shadow-[0_2px_8px_rgba(0,0,0,0.1)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.15)]" 
                : "hover:bg-gray-50 hover:shadow-[0_2px_8px_rgba(0,0,0,0.1)]"
            }`}
          >
            Sort by Agency
            {sort === "agency" && <ArrowUpDown className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg p-6 shadow-[0_2px_8px_rgba(0,0,0,0.1)] animate-pulse">
              <div className="h-7 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="space-y-2">
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                <div className="h-6 bg-gray-200 rounded w-2/3"></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {paginatedAgencies.map((agency) => (
            <div
              key={agency.name}
              className="bg-white rounded-lg p-6 shadow-[0_2px_8px_rgba(0,0,0,0.1)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.15)] transition-shadow duration-200"
            >
              <h2 className="text-xl font-semibold mb-4 text-gray-900">
                {agency.name}
              </h2>
              <div className="space-y-2">
                <div className="flex items-baseline justify-between">
                  <span className="text-blue-600 text-2xl font-bold">
                    {formatNumber(agency.word_count)}
                  </span>
                  <span className="text-gray-500">Words</span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="text-gray-900 text-xl">
                    {formatNumber(agency.section_count)}
                  </span>
                  <span className="text-gray-500">Sections of regulation</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {filtered.length > ITEMS_PER_PAGE && (
        <div className="flex justify-center gap-2 mt-8">
          <Button
            variant="ghost"
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="transition-all duration-200 hover:bg-gray-50 hover:shadow-[0_2px_8px_rgba(0,0,0,0.1)] disabled:opacity-50 disabled:hover:shadow-none"
          >
            Previous
          </Button>
          <div className="flex items-center gap-2">
            {[...Array(Math.ceil(filtered.length / ITEMS_PER_PAGE))].map((_, i) => (
              <Button
                key={i}
                variant="ghost"
                onClick={() => setCurrentPage(i + 1)}
                className={`w-10 transition-all duration-200 ${
                  currentPage === i + 1
                    ? "bg-white shadow-[0_2px_8px_rgba(0,0,0,0.1)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.15)]"
                    : "hover:bg-gray-50 hover:shadow-[0_2px_8px_rgba(0,0,0,0.1)]"
                }`}
              >
                {i + 1}
              </Button>
            ))}
          </div>
          <Button
            variant="ghost"
            onClick={() => setCurrentPage(p => Math.min(Math.ceil(filtered.length / ITEMS_PER_PAGE), p + 1))}
            disabled={currentPage === Math.ceil(filtered.length / ITEMS_PER_PAGE)}
            className="transition-all duration-200 hover:bg-gray-50 hover:shadow-[0_2px_8px_rgba(0,0,0,0.1)] disabled:opacity-50 disabled:hover:shadow-none"
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
