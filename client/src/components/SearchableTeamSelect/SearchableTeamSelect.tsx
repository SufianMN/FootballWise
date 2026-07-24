import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Search, ChevronDown } from 'lucide-react';

export interface Team {
  id: string;
  name: string;
}

export interface SearchableTeamSelectProps {
  teams: Team[];
  value: string;
  onChange: (id: string) => void;
  placeholder?: string;
}

const SearchableTeamSelect: React.FC<SearchableTeamSelectProps> = ({ 
  teams, 
  value, 
  onChange, 
  placeholder = 'Select a team...' 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  
  const containerRef = useRef<HTMLDivElement>(null);

  const selectedTeam = teams.find(t => t.id === value);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearch(''); // Reset search when closing without selection
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter teams based on search string
  const filteredTeams = useMemo(() => {
    if (!search.trim()) return teams;
    const lowerSearch = search.toLowerCase().trim();
    return teams.filter(t => t.name.toLowerCase().includes(lowerSearch));
  }, [teams, search]);

  // Reset highlight when search changes
  useEffect(() => {
    setHighlightedIndex(0);
  }, [search, isOpen]);

  // Scroll highlighted item into view if it is not visible
  const listboxRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (isOpen && listboxRef.current) {
      const highlightedEl = listboxRef.current.children[highlightedIndex] as HTMLElement;
      if (highlightedEl) {
        const listbox = listboxRef.current;
        if (highlightedEl.offsetTop < listbox.scrollTop) {
          listbox.scrollTop = highlightedEl.offsetTop;
        } else if (highlightedEl.offsetTop + highlightedEl.clientHeight > listbox.scrollTop + listbox.clientHeight) {
          listbox.scrollTop = highlightedEl.offsetTop + highlightedEl.clientHeight - listbox.clientHeight;
        }
      }
    }
  }, [highlightedIndex, isOpen]);

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === 'ArrowDown' || e.key === ' ') {
        setIsOpen(true);
        e.preventDefault();
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      setHighlightedIndex(prev => Math.min(prev + 1, filteredTeams.length - 1));
      e.preventDefault();
    } else if (e.key === 'ArrowUp') {
      setHighlightedIndex(prev => Math.max(prev - 1, 0));
      e.preventDefault();
    } else if (e.key === 'Enter') {
      if (filteredTeams[highlightedIndex]) {
        onChange(filteredTeams[highlightedIndex].id);
        setIsOpen(false);
        setSearch('');
      }
      e.preventDefault();
    } else if (e.key === 'Escape' || e.key === 'Tab') {
      setIsOpen(false);
      setSearch('');
    }
  };

  const handleSelect = (id: string) => {
    onChange(id);
    setIsOpen(false);
    setSearch('');
  };

  return (
    <div className="relative w-full text-white" ref={containerRef}>
      <div 
        className={`relative flex items-center w-full bg-background border ${isOpen ? 'border-primary ring-1 ring-primary' : 'border-slate-600'} rounded-lg transition-all shadow-sm group`}
      >
        <Search size={18} className={`absolute left-3 ${isOpen ? 'text-primary' : 'text-slate-400 group-hover:text-slate-300'} pointer-events-none transition-colors`} />
        
        <input
          type="text"
          className="w-full bg-transparent outline-none text-white p-3 pl-10 pr-10 rounded-lg cursor-text"
          placeholder={isOpen ? "Type to search..." : placeholder}
          value={isOpen ? search : (selectedTeam ? selectedTeam.name : '')}
          onChange={(e) => {
            if (!isOpen) setIsOpen(true);
            setSearch(e.target.value);
          }}
          onFocus={() => {
            setIsOpen(true);
            setSearch('');
          }}
          onKeyDown={handleKeyDown}
          role="combobox"
          aria-expanded={isOpen}
          aria-controls="team-listbox"
        />
        
        <ChevronDown size={18} className={`absolute right-3 ${isOpen ? 'text-primary transform rotate-180' : 'text-slate-400 group-hover:text-slate-300'} pointer-events-none transition-all`} />
      </div>

      {/* Dropdown list */}
      {isOpen && (
        <div 
          ref={listboxRef}
          id="team-listbox"
          role="listbox"
          className="absolute z-50 w-full mt-2 bg-slate-800 border border-slate-600 rounded-lg shadow-2xl max-h-60 overflow-y-auto custom-scrollbar animate-fade-in"
        >
          {filteredTeams.length === 0 ? (
            <div className="p-4 text-slate-400 text-center italic">No teams found matching "{search}"</div>
          ) : (
            filteredTeams.map((team, index) => (
              <div
                key={team.id}
                role="option"
                aria-selected={index === highlightedIndex}
                className={`p-3 cursor-pointer transition-colors flex items-center justify-between ${
                  index === highlightedIndex ? 'bg-primary/20 text-white border-l-2 border-primary' : 'text-slate-300 hover:bg-slate-700 border-l-2 border-transparent'
                }`}
                onClick={() => handleSelect(team.id)}
                onMouseEnter={() => setHighlightedIndex(index)}
              >
                <span className={team.id === value ? 'font-bold text-white' : ''}>{team.name}</span>
                {team.id === value && (
                  <span className="text-primary text-xs font-bold bg-primary/10 px-2 py-1 rounded">Selected</span>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default SearchableTeamSelect;
