import { Spinner } from "@/shared/components/ui/spinner";

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center h-[75vh]">
      <Spinner className="w-8 h-8" />
    </div>
  )
}