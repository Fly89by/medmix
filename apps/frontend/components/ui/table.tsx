import { HTMLAttributes, TdHTMLAttributes, ThHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

const Table = forwardRef<HTMLTableElement, HTMLAttributes<HTMLTableElement>>(
  ({ className, ...props }, ref) => (
    <div className="overflow-x-auto">
      <table ref={ref} className={cn('w-full text-sm', className)} {...props} />
    </div>
  )
);
Table.displayName = 'Table';

const Thead = forwardRef<HTMLTableSectionElement, HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => (
    <thead ref={ref} className={cn('border-b bg-gray-50', className)} {...props} />
  )
);
Thead.displayName = 'Thead';

const Tbody = forwardRef<HTMLTableSectionElement, HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => (
    <tbody ref={ref} className={cn('divide-y', className)} {...props} />
  )
);
Tbody.displayName = 'Tbody';

const Tr = forwardRef<HTMLTableRowElement, HTMLAttributes<HTMLTableRowElement>>(
  ({ className, ...props }, ref) => (
    <tr ref={ref} className={cn('hover:bg-gray-50', className)} {...props} />
  )
);
Tr.displayName = 'Tr';

const Th = forwardRef<HTMLTableCellElement, ThHTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => (
    <th
      ref={ref}
      className={cn('px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider', className)}
      {...props}
    />
  )
);
Th.displayName = 'Th';

const Td = forwardRef<HTMLTableCellElement, TdHTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => (
    <td ref={ref} className={cn('px-4 py-3 whitespace-nowrap', className)} {...props} />
  )
);
Td.displayName = 'Td';

export { Table, Thead, Tbody, Tr, Th, Td };
