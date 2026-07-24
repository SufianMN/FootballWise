import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Search, ChevronDown } from 'lucide-react';

export interface Player {
  id: string;
  name: string;
  team: string;
  position: string;
}

export interface SearchablePlayerSelectProps {
  players: Player[];
  value: string;
  onChange: (id: string) => void;
  placeholder?: string;
}

const SearchablePlayerSelect: React.FC<SearchablePlayerSelectProps> = ({ 
  players, 
  value, 
  onChange, 
  placeholder = 'Select a player...' 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const listboxRef = useRef<HTMLDivElement>(null);

  const selectedPlayer = players.find(p => p.id === value);

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

  // Filter players based on search string
  // For performance with potentially thousands of players, useMemo is critical
  const filteredPlayers = useMemo(() => {
    if (!search.trim()) return players.slice(0, 100); // Show top 100 max when not searching
    const lowerSearch = search.toLowerCase().trim();
    // Allow matching on name or team
    return players
      .filter(p => p.name.toLowerCase().includes(lowerSearch) || p.team.toLowerCase().includes(lowerSearch))
      .slice(0, 100); // Limit results to prevent DOM lag
  }, [players, search]);

  // Reset highlight when search changes
  useEffect(() => {
    setHighlightedIndex(0);
  }, [search, isOpen]);

  // Scroll highlighted item into view
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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === 'ArrowDown' || e.key === ' ') {
        setIsOpen(true);
        e.preventDefault();
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      setHighlightedIndex(prev => Math.min(prev + 1, filteredPlayers.length - 1));
      e.preventDefault();
    } else if (e.key === 'ArrowUp') {
      setHighlightedIndex(prev => Math.max(prev - 1, 0));
      e.preventDefault();
    } else if (e.key === 'Enter') {
      if (filteredPlayers[highlightedIndex]) {
        handleSelect(filteredPlayers[highlightedIndex].id);
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
          placeholder={isOpen ? "Type name or team..." : placeholder}
          value={isOpen ? search : (selectedPlayer ? selectedPlayer.name : '')}
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
          aria-controls="player-listbox"
        />
        
        <ChevronDown size={18} className={`absolute right-3 ${isOpen ? 'text-primary transform rotate-180' : 'text-slate-400 group-hover:text-slate-300'} pointer-events-none transition-all`} />
      </div>

      {isOpen && (
        <div 
          ref={listboxRef}
          id="player-listbox"
          role="listbox"
          className="absolute z-50 w-full mt-2 bg-slate-800 border border-slate-600 rounded-lg shadow-2xl max-h-72 overflow-y-auto custom-scrollbar animate-fade-in"
        >
          {filteredPlayers.length === 0 ? (
            <div className="p-4 text-slate-400 text-center italic">No players found matching "{search}"</div>
          ) : (
            filteredPlayers.map((player, index) => (
              <div
                key={player.id}
                role="option"
                aria-selected={index === highlightedIndex}
                className={`p-3 cursor-pointer transition-colors flex items-center justify-between ${
                  index === highlightedIndex ? 'bg-primary/20 text-white border-l-2 border-primary' : 'text-slate-300 hover:bg-slate-700 border-l-2 border-transparent'
                }`}
                onClick={() => handleSelect(player.id)}
                onMouseEnter={() => setHighlightedIndex(index)}
              >
                <div>
                  <div className={player.id === value ? 'font-bold text-white' : 'font-medium'}>
                    {player.name}
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5 flex items-center gap-2">
                    <span>{player.team}</span>
                    <span className="w-1 h-1 rounded-full bg-slate-600"></span>
                    <span>{player.position}</span>
                  </div>
                </div>
                {player.id === value && (
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

export default SearchablePlayerSelect;
