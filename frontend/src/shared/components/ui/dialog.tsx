"use client"

import * as React from "react"
import { XIcon } from "lucide-react"
import { OverlayTriggerStateContext } from "react-aria-components"
import {
  Modal,
  useOverlayState,
  type ModalDialogProps,
  type ModalHeaderProps,
  type ModalFooterProps,
  type ModalHeadingProps,
  type ModalTriggerProps,
} from "@heroui/react"
import { cn } from "@/shared/lib/utils"

function Dialog({
  open,
  onOpenChange,
  children,
}: {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children?: React.ReactNode
}) {
  const state = useOverlayState({ isOpen: open, onOpenChange })
  return <Modal state={state}>{children}</Modal>
}

function DialogContent({
  className,
  children,
  showCloseButton = true,
}: Omit<ModalDialogProps, "children"> & { children?: React.ReactNode; showCloseButton?: boolean }) {
  return (
    <Modal.Backdrop isDismissable>
      <Modal.Container placement="center" size="lg">
        <Modal.Dialog
          className={cn(
            "p-0 overflow-hidden bg-white dark:bg-slate-900 border-none shadow-2xl rounded-xl flex flex-col",
            className
          )}
        >
          {showCloseButton && (
            <Modal.CloseTrigger className="absolute top-4 right-4 p-1 bg-gray-400 hover:bg-gray-500 transition-colors rounded-full">
              <XIcon size={16} />
            </Modal.CloseTrigger>
          )}
          {children}
        </Modal.Dialog>
      </Modal.Container>
    </Modal.Backdrop>
  )
}

function DialogHeader({ className, ...props }: ModalHeaderProps) {
  return (
    <Modal.Header
      className={cn(
        "flex flex-col gap-2 px-6 py-4 border-b border-slate-100 dark:border-slate-800",
        className
      )}
      {...props}
    />
  )
}

function DialogFooter({ className, ...props }: ModalFooterProps) {
  return (
    <Modal.Footer
      className={cn(
        "px-6 py-4 bg-slate-50 dark:bg-slate-800/30 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3",
        className
      )}
      {...props}
    />
  )
}

function DialogTitle({ className, ...props }: ModalHeadingProps) {
  return (
    <Modal.Heading
      className={cn("text-lg leading-none font-semibold text-slate-900 dark:text-slate-100", className)}
      {...props}
    />
  )
}

function DialogDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn("text-muted-foreground text-sm", className)}
      {...props}
    />
  )
}

function DialogClose({
  children,
  asChild,
  ...props
}: React.HTMLAttributes<HTMLElement> & { asChild?: boolean; children?: React.ReactNode }) {
  const overlayState = React.useContext(OverlayTriggerStateContext)

  if (asChild && React.isValidElement(children)) {
    const child = children as React.ReactElement<React.HTMLAttributes<HTMLElement>>
    return React.cloneElement(child, {
      ...props,
      onClick: (e: React.MouseEvent<HTMLElement>) => {
        child.props.onClick?.(e)
        overlayState?.close()
      },
    })
  }

  return (
    <button type="button" onClick={() => overlayState?.close()} {...props}>
      {children}
    </button>
  )
}

function DialogTrigger({ children, ...props }: ModalTriggerProps) {
  return (
    <Modal.Trigger {...props}>
      {children}
    </Modal.Trigger>
  )
}

function DialogPortal({ children }: { children?: React.ReactNode }) {
  return <>{children}</>
}

function DialogOverlay() {
  return null
}

export {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogOverlay,
  DialogPortal,
  DialogTitle,
  DialogTrigger,
}
