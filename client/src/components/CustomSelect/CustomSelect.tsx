import React, { useState, useEffect, useRef, useMemo } from 'react';
import { ChevronDown, Search, Check } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
}

export interface CustomSelectProps {
  options: SelectOption[];
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
  searchable?: boolean;
  className?: string;
}

const CustomSelect: React.FC<CustomSelectProps> = ({
  options,
  value,
  onChange,
  placeholder = 'Select option...',
  searchable = false,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const listboxRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find(o => o.value === value);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearch('');
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredOptions = useMemo(() => {
    if (!searchable || !search.trim()) return options;
    const lower = search.toLowerCase().trim();
    return options.filter(o => o.label.toLowerCase().includes(lower));
  }, [options, search, searchable]);

  useEffect(() => {
    setHighlightedIndex(0);
  }, [search, isOpen]);

  // Scroll highlighted item into view
  useEffect(() => {
    if (isOpen && listboxRef.current) {
      const highlightedEl = listboxRef.current.children[searchable ? highlightedIndex + 1 : highlightedIndex] as HTMLElement;
      if (highlightedEl) {
        const listbox = listboxRef.current;
        if (highlightedEl.offsetTop < listbox.scrollTop) {
          listbox.scrollTop = highlightedEl.offsetTop;
        } else if (highlightedEl.offsetTop + highlightedEl.clientHeight > listbox.scrollTop + listbox.clientHeight) {
          listbox.scrollTop = highlightedEl.offsetTop + highlightedEl.clientHeight - listbox.clientHeight;
        }
      }
    }
  }, [highlightedIndex, isOpen, searchable]);

  const handleSelect = (val: string) => {
    onChange(val);
    setIsOpen(false);
    setSearch('');
  };

  return (
    <div className={`relative text-white ${isOpen ? 'z-50' : 'z-10'} ${className}`} ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full flex items-center justify-between bg-slate-950/80 backdrop-blur-md border ${
          isOpen ? 'border-blue-500 ring-2 ring-blue-500/30 shadow-lg shadow-blue-500/10' : 'border-slate-700/80 hover:border-slate-600'
        } rounded-xl p-3.5 text-white transition-all shadow-inner text-sm font-semibold cursor-pointer gap-3`}
      >
        <span className="truncate">
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <ChevronDown 
          size={18} 
          className={`text-slate-400 shrink-0 transition-transform ${isOpen ? 'rotate-180 text-blue-400' : ''}`} 
        />
      </button>

      {isOpen && (
        <div
          ref={listboxRef}
          role="listbox"
          className="absolute z-[100] top-full left-0 w-full mt-2 bg-slate-900/95 backdrop-blur-xl border border-slate-700/90 rounded-xl shadow-2xl shadow-slate-950/90 max-h-64 overflow-y-auto custom-scrollbar animate-fade-in divide-y divide-slate-800/50"
        >
          {searchable && (
            <div className="p-2 sticky top-0 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 z-10">
              <div className="relative flex items-center">
                <Search size={16} className="absolute left-3 text-slate-400 pointer-events-none" />
                <input
                  type="text"
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-lg p-2 pl-9 text-xs text-white outline-none focus:border-blue-500"
                  placeholder="Search..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  autoFocus
                />
              </div>
            </div>
          )}

          {filteredOptions.length === 0 ? (
            <div className="p-4 text-slate-400 text-center italic text-xs">No options found</div>
          ) : (
            filteredOptions.map((opt, index) => {
              const isSelected = opt.value === value;
              const isHighlighted = index === highlightedIndex;
              return (
                <div
                  key={opt.value}
                  role="option"
                  aria-selected={isSelected}
                  className={`p-3.5 cursor-pointer transition-all flex items-center justify-between text-sm ${
                    isHighlighted 
                      ? 'bg-gradient-to-r from-blue-600/30 to-indigo-600/30 text-white border-l-4 border-blue-500 font-semibold' 
                      : 'text-slate-300 hover:bg-slate-800/80 border-l-4 border-transparent'
                  }`}
                  onClick={() => handleSelect(opt.value)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                >
                  <span className={isSelected ? 'font-bold text-white' : ''}>{opt.label}</span>
                  {isSelected && (
                    <span className="text-xs font-bold text-indigo-300 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 border border-indigo-500/40 px-2.5 py-0.5 rounded-full shadow-sm flex items-center gap-1">
                      <Check size={12} className="text-indigo-300" /> Selected
                    </span>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};

export default CustomSelect;
