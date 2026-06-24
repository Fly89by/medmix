import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const inputId = id || label?.replace(/\s+/g, '-').toLowerCase();
    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-gray-700">
            {label}
          </label>
        )}
        <input
          id={inputId}
          className={cn(
            'w-full rounded-lg border px-3 py-2 text-sm bg-white transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary',
            'placeholder:text-gray-400',
            '[dir="rtl"]&:text-right',
            error ? 'border-red-500' : 'border-gray-300',
            className
          )}
          ref={ref}
          dir="auto"
          {...props}
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>
    );
  }
);
Input.displayName = 'Input';

export { Input };
