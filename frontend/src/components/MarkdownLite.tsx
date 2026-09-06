import type { ReactNode } from "react";

type Block =
  | { type: "h3" | "h4"; text: string }
  | { type: "ul"; items: string[] }
  | { type: "p"; text: string };

function parseBlocks(content: string): Block[] {
  const blocks: Block[] = [];
  let list: string[] | null = null;
  let para: string[] | null = null;

  const flushList = () => {
    if (list) {
      blocks.push({ type: "ul", items: list });
      list = null;
    }
  };
  const flushPara = () => {
    if (para && para.length) {
      blocks.push({ type: "p", text: para.join(" ") });
    }
    para = null;
  };

  for (const rawLine of content.split("\n")) {
    const line = rawLine.trim();
    if (line.startsWith("### ")) {
      flushList();
      flushPara();
      blocks.push({ type: "h4", text: line.slice(4) });
    } else if (line.startsWith("## ")) {
      flushList();
      flushPara();
      blocks.push({ type: "h3", text: line.slice(3) });
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      flushPara();
      (list ??= []).push(line.slice(2));
    } else if (line === "") {
      flushList();
      flushPara();
    } else {
      flushList();
      (para ??= []).push(line);
    }
  }
  flushList();
  flushPara();
  return blocks;
}

function parseInline(text: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={i}>{part.slice(1, -1)}</code>;
    }
    return part;
  });
}

export function MarkdownLite({ content }: { content: string }) {
  const blocks = parseBlocks(content);
  return (
    <>
      {blocks.map((block, i) => {
        if (block.type === "h3") {
          return (
            <h3 className="chat-md-heading" key={i}>
              {parseInline(block.text)}
            </h3>
          );
        }
        if (block.type === "h4") {
          return (
            <h4 className="chat-md-heading" key={i}>
              {parseInline(block.text)}
            </h4>
          );
        }
        if (block.type === "ul") {
          return (
            <ul className="chat-md-list" key={i}>
              {block.items.map((item, j) => (
                <li key={j}>{parseInline(item)}</li>
              ))}
            </ul>
          );
        }
        return (
          <p className="chat-md-p" key={i}>
            {parseInline(block.text)}
          </p>
        );
      })}
    </>
  );
}
