'use client';

import { useRef } from "react";
import { Upload } from "lucide-react";
import toast from "react-hot-toast";

import { Button } from "@/shared/components/ui/button";
import { useImportQuestionsMutation } from "../api/tests-api";

const DOCX_MIME =
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document";

export function ImportQuestionsButton({ testId }: { testId: number }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const { mutateAsync, isPending } = useImportQuestionsMutation();

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = ""; // allow re-selecting the same file
    if (!file) return;

    if (!file.name.endsWith(".docx") && file.type !== DOCX_MIME) {
      toast.error("Please select a .docx file");
      return;
    }

    try {
      const result = await mutateAsync({ testId, data: { file } });
      toast.success(`Imported ${result.imported_count} question(s)`);
    } catch {
      toast.error("Failed to import the file");
    }
  };

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept=".docx"
        className="hidden"
        onChange={handleFile}
      />
      <Button
        variant="outline"
        onClick={() => inputRef.current?.click()}
        isLoading={isPending}
      >
        <Upload className="size-4" /> Import .docx
      </Button>
    </>
  );
}
