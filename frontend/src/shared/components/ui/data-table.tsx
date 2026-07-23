'use client';

import { ColumnDef, flexRender, getCoreRowModel, useReactTable } from '@tanstack/react-table';
import { cn } from '@/shared/lib/utils';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './table';

interface DataTableProps<TData> {
  data: TData[];
  columns: ColumnDef<TData>[];
  onRowClick?: (row: TData) => void;
  noDataMessage?: string;
  className?: string;
}

export function DataTable<TData>({
  data,
  columns,
  onRowClick,
  noDataMessage = '—',
  className,
}: DataTableProps<TData>) {
  // eslint-disable-next-line react-hooks/incompatible-library
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div className={cn(
      'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm',
      className
    )}>
      <Table className="w-full table-fixed text-left border-collapse">
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow
              key={headerGroup.id}
              className="border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50"
            >
              {headerGroup.headers.map((header) => (
                <TableHead
                  key={header.id}
                  className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider"
                  style={header.column.columnDef.size !== undefined ? { width: header.column.columnDef.size } : undefined}
                >
                  {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody className="divide-y divide-slate-100 dark:divide-slate-800">
          {table.getRowModel().rows.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                className={cn(
                  'hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors',
                  onRowClick && 'cursor-pointer'
                )}
                onClick={onRowClick ? () => onRowClick(row.original) : undefined}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell
                    key={cell.id}
                    className="px-6 py-4 text-sm overflow-hidden"
                    style={cell.column.columnDef.size !== undefined ? { width: cell.column.columnDef.size } : undefined}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell className="text-center text-slate-500 p-12" colSpan={columns.length}>
                {noDataMessage}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
