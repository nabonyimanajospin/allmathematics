/** Injects server-rendered lesson HTML. The HTML is produced only by renderRich/renderInline/KaTeX on the server. */
export function Rich({ html, className = "" }: { html: string; className?: string }) {
  return <div className={`rich min-w-0 ${className}`} dangerouslySetInnerHTML={{ __html: html }} />;
}

export function RichInline({ html, className = "" }: { html: string; className?: string }) {
  return <span className={className} dangerouslySetInnerHTML={{ __html: html }} />;
}
