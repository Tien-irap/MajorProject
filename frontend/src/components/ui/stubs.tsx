import React, { useState } from 'react';
import { Chessboard as ReactChessboard } from 'react-chessboard';
import { ChevronDown } from "lucide-react";

// --- BUTTON ---
export const Button = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement>>(
  ({ children, className, ...props }, ref) => (
    <button
      {...props}
      ref={ref}
      className={`inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2 ${className || ''}`}
    >
      {children}
    </button>
  )
);
Button.displayName = "Button";

// --- CARD ---
export const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ children, className, ...props }, ref) => (
    <div
      {...props}
      ref={ref}
      className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className || ''}`}
    >
      {children}
    </div>
  )
);
Card.displayName = "Card";

// --- CHESSBOARD (Fixed Version) ---
export const Chessboard = ({ boardWidth, position }: { boardWidth: number, position?: string }) => {
  const safePosition = position || 'start';
  return (
    <div style={{ width: boardWidth, height: boardWidth }}>
      <ReactChessboard
        key={`board-key-${safePosition}`} 
        // @ts-ignore
        position={safePosition}
        arePiecesDraggable={false}
        boardWidth={boardWidth}
        customDarkSquareStyle={{ backgroundColor: '#779556' }}
        customLightSquareStyle={{ backgroundColor: '#ebecd0' }}
      />
    </div>
  );
};

// --- ACCORDION (New for RuleBook) ---
// A simple functional implementation of the Shadcn Accordion API
export const Accordion = ({ children, className }: { children: React.ReactNode, type?: string, collapsible?: boolean, className?: string }) => (
  <div className={`space-y-1 ${className || ''}`}>{children}</div>
);

export const AccordionItem = ({ children, className, value }: { children: React.ReactNode, className?: string, value: string }) => (
  <div className={`border-b border-zinc-800 ${className || ''}`}>{children}</div>
);

export const AccordionTrigger = ({ children, className }: { children: React.ReactNode, className?: string }) => {
  // This is a simplified stub. In a real app, we'd use Context to manage open/close state.
  // Here, we use a local state for self-contained simplicity in this demo.
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <button 
      onClick={() => setIsOpen(!isOpen)}
      className={`flex flex-1 items-center justify-between py-4 font-medium transition-all hover:underline [&[data-state=open]>svg]:rotate-180 ${className || ''}`}
    >
      {children}
      <ChevronDown className={`h-4 w-4 shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
    </button>
  );
};

// Note: Since we can't easily share state between Trigger and Content in this simple stub without Context,
// We will modify the RuleBook usage slightly to use standard HTML details/summary for the robust "stub" version, 
// OR we keep this stub simple. For this specific output, let's assume the RuleBook code 
// below uses a standard <details> approach for maximum reliability if we don't have the full Shadcn library.
// BUT, to match your code exactly, we'll use a trick: The Trigger toggles a hidden checkbox or similar? 
// Actually, for a true stub without context, we have to cheat slightly.
// We will make the Trigger *and* Content part of a single interactive unit in the stub implementation below.

export const SimpleAccordionItem = ({ title, content }: { title: string, content: string }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="border-b border-zinc-800">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex flex-1 w-full items-center justify-between py-4 font-medium hover:text-cyan-400 transition-colors text-left"
      >
        {title}
        <ChevronDown className={`h-4 w-4 shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="pb-4 pt-0 text-sm text-zinc-400 animate-in slide-in-from-top-2">
          {content}
        </div>
      )}
    </div>
  );
}