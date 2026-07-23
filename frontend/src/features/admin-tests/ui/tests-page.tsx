'use client';

import { useState } from "react";
import { useRouter } from "next/navigation";
import { format } from "date-fns";
import { Pencil, Plus, Trash2 } from "lucide-react";
import toast from "react-hot-toast";

import type { TestResponse } from "@/shared/api/generated/model";
import { ROUTES } from "@/shared/constants/routes";
import { useDebouncedSearch } from "@/shared/hooks/use-debounced-search";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { Spinner } from "@/shared/components/ui/spinner";
import { TablePagination } from "@/shared/components/pagination";
import { ConfirmDialog } from "@/shared/components/confirm-dialog";
import { useTestsQuery, useDeleteTestMutation } from "../api/tests-api";
import { TestFormDialog } from "./test-form-dialog";

export function AdminTestsPage() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<TestResponse | null>(null);
  const [deleting, setDeleting] = useState<TestResponse | null>(null);

  const search = useDebouncedSearch("", (value) => {
    setQuery(value);
    setPage(1);
  });

  const { data, isLoading } = useTestsQuery({
    page,
    limit: 10,
    query: query || undefined,
  });
  const deleteMutation = useDeleteTestMutation();

  const openCreate = () => {
    setEditing(null);
    setFormOpen(true);
  };

  const openEdit = (test: TestResponse) => {
    setEditing(test);
    setFormOpen(true);
  };

  const confirmDelete = async () => {
    if (!deleting) return;
    try {
      await deleteMutation.mutateAsync({ testId: deleting.id });
      toast.success("Test deleted");
      setDeleting(null);
    } catch {
      toast.error("Failed to delete test");
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">Tests</h1>
        <Button onClick={openCreate}>
          <Plus className="size-4" /> Create test
        </Button>
      </div>

      <div className="max-w-sm">
        <Input
          placeholder="Search tests..."
          value={search.value}
          onChange={search.onChange}
        />
      </div>

      <div className="rounded-lg border bg-background">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead className="w-32">Mode</TableHead>
              <TableHead className="w-32">Questions</TableHead>
              <TableHead className="w-40">Created</TableHead>
              <TableHead className="w-28 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="h-32 text-center">
                  <Spinner className="mx-auto size-6" />
                </TableCell>
              </TableRow>
            ) : data && data.items.length > 0 ? (
              data.items.map((test) => (
                <TableRow
                  key={test.id}
                  className="cursor-pointer"
                  onClick={() => router.push(ROUTES.ADMIN_TEST(test.id))}
                >
                  <TableCell className="font-medium">{test.name}</TableCell>
                  <TableCell>{test.mode} q</TableCell>
                  <TableCell>{test.question_count}</TableCell>
                  <TableCell>
                    {format(new Date(test.created_at), "dd MMM yyyy")}
                  </TableCell>
                  <TableCell
                    className="text-right"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => openEdit(test)}
                      >
                        <Pencil className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => setDeleting(test)}
                      >
                        <Trash2 className="size-4 text-destructive" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} className="h-32 text-center text-muted-foreground">
                  No tests yet. Create your first test.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {data && data.page_count > 1 ? (
        <TablePagination
          page={page}
          pageCount={data.page_count}
          onPageChange={setPage}
        />
      ) : null}

      <TestFormDialog open={formOpen} onOpenChange={setFormOpen} test={editing} />

      <ConfirmDialog
        open={!!deleting}
        onOpenChange={(open) => !open && setDeleting(null)}
        title="Delete test?"
        description={
          deleting
            ? `"${deleting.name}" and all its questions will be permanently removed.`
            : undefined
        }
        isLoading={deleteMutation.isPending}
        onConfirm={confirmDelete}
      />
    </div>
  );
}
