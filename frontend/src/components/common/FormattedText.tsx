import React from 'react';

interface Props {
  text: string | null | undefined;
  className?: string;
}

// Simple formatter: builds paragraphs and bullet/numbered lists from plain text
// - Detects list items starting with -, *, • or numbers like "1.", "1)"
// - Groups consecutive list items into a single <ul> or <ol>
// - Renders other text as <p>
// No HTML is injected; this is safe for scraped text.
export const FormattedText: React.FC<Props> = ({ text, className = '' }) => {
  const content = (text || '').replace(/\r\n/g, '\n').trim();
  if (!content) return <div className={className}></div>;

  const lines = content.split('\n').map(l => l.trim());

  type Block =
    | { type: 'p'; text: string }
    | { type: 'ul'; items: string[] }
    | { type: 'ol'; items: string[] };

  const blocks: Block[] = [];

  const bulletRegex = /^[-*•]\s+/; // -, *, •
  const orderedRegex = /^(\d+)[.)]\s+/; // 1.  or  1)

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];

    // skip empty lines (paragraph breaks)
    if (!line) { i++; continue; }

    if (bulletRegex.test(line)) {
      const items: string[] = [];
      while (i < lines.length && bulletRegex.test(lines[i])) {
        items.push(lines[i].replace(bulletRegex, '').trim());
        i++;
      }
      blocks.push({ type: 'ul', items });
      continue;
    }

    if (orderedRegex.test(line)) {
      const items: string[] = [];
      while (i < lines.length && orderedRegex.test(lines[i])) {
        items.push(lines[i].replace(orderedRegex, '').trim());
        i++;
      }
      blocks.push({ type: 'ol', items });
      continue;
    }

    // Accumulate paragraph until blank line or next list
    const para: string[] = [line];
    i++;
    while (i < lines.length && lines[i] && !bulletRegex.test(lines[i]) && !orderedRegex.test(lines[i])) {
      para.push(lines[i]);
      i++;
    }
    blocks.push({ type: 'p', text: para.join(' ') });
  }

  return (
    <div className={className}>
      {blocks.map((b, idx) => {
        if (b.type === 'p') {
          return (
            <p key={idx} className="mb-3">
              {b.text}
            </p>
          );
        }
        if (b.type === 'ul') {
          return (
            <ul key={idx} className="list-disc pl-6 mb-3 space-y-1">
              {b.items.map((it, i2) => <li key={i2}>{it}</li>)}
            </ul>
          );
        }
        // ordered list
        return (
          <ol key={idx} className="list-decimal pl-6 mb-3 space-y-1">
            {b.items.map((it, i2) => <li key={i2}>{it}</li>)}
          </ol>
        );
      })}
    </div>
  );
};

export default FormattedText;
