'use client';

import { useMemo } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

import { cn } from "@/shared/lib/utils";

interface Segment {
  type: "text" | "math";
  value: string;
  display: boolean;
}

// Split text into plain and math segments. Supports block `$$...$$` and inline
// `$...$`; a literal `\$` is treated as an escaped dollar, not a delimiter.
function parse(input: string): Segment[] {
  const segments: Segment[] = [];
  const regex = /\$\$([\s\S]+?)\$\$|(?<!\\)\$([^$\n]+?)(?<!\\)\$/g;
  let last = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(input)) !== null) {
    if (match.index > last) {
      segments.push({
        type: "text",
        value: input.slice(last, match.index),
        display: false,
      });
    }
    const display = match[1] !== undefined;
    segments.push({
      type: "math",
      value: (display ? match[1] : match[2]).trim(),
      display,
    });
    last = regex.lastIndex;
  }

  if (last < input.length) {
    segments.push({ type: "text", value: input.slice(last), display: false });
  }
  return segments;
}

function renderMath(value: string, display: boolean): string {
  try {
    return katex.renderToString(value, {
      displayMode: display,
      throwOnError: false,
      strict: false,
    });
  } catch {
    return value;
  }
}

/**
 * Renders text that may contain LaTeX math delimited by `$...$` (inline) or
 * `$$...$$` (block). Plain segments render as text; math segments render via
 * KaTeX. Falls back to the raw source if a formula fails to parse.
 */
export function MathText({
  children,
  className,
}: {
  children: string | null | undefined;
  className?: string;
}) {
  const segments = useMemo(() => parse(children ?? ""), [children]);

  return (
    <span className={cn(className)}>
      {segments.map((seg, i) =>
        seg.type === "text" ? (
          <span key={i}>{seg.value}</span>
        ) : (
          <span
            key={i}
            dangerouslySetInnerHTML={{
              __html: renderMath(seg.value, seg.display),
            }}
          />
        ),
      )}
    </span>
  );
}
