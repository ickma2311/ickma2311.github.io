-- Keep the same reader links at the end of every HTML page, before comments.
function Pandoc(doc)
  if not quarto.doc.is_format("html") then
    return doc
  end

  doc.blocks:insert(pandoc.RawBlock("html", [[
<nav class="reader-links" aria-label="Stay connected with Chao">
  <p class="reader-links-eyebrow">Beyond the blog</p>
  <p class="reader-links-title">Stay connected with Chao</p>
  <p class="reader-links-intro">Follow my ideas, say hello, or explore what I’m building.</p>
  <div class="reader-links-items">
    <a class="reader-card reader-card-x" href="https://x.com/ickma2311" target="_blank" rel="noopener noreferrer">
      <span class="reader-card-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.9 2H22l-6.8 7.8L23.2 22h-6.3L12 14.6 5.5 22H2.3l8.2-9.4L.8 2h6.5l5.8 7.6L18.9 2Zm-1.1 18h1.7L6.4 3.9H4.6L17.8 20Z"/></svg></span>
      <span class="reader-card-arrow" aria-hidden="true">↗</span>
      <span class="reader-card-name">X / Twitter</span>
      <span class="reader-card-description">Notes, ideas &amp; things I’m learning.</span>
      <span class="reader-card-action">Follow @ickma2311</span>
    </a>
    <a class="reader-card reader-card-linkedin" href="https://www.linkedin.com/in/chao-ma-929839241/" target="_blank" rel="noopener noreferrer">
      <span class="reader-card-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.45 2H3.55C2.69 2 2 2.68 2 3.52v16.96c0 .84.69 1.52 1.55 1.52h16.9c.86 0 1.55-.68 1.55-1.52V3.52c0-.84-.69-1.52-1.55-1.52ZM7.93 18.75H4.98V9.2h2.95v9.55ZM6.45 7.89a1.71 1.71 0 1 1 0-3.42 1.71 1.71 0 0 1 0 3.42Zm12.3 10.86H15.8V14.1c0-1.11-.02-2.54-1.55-2.54-1.55 0-1.79 1.21-1.79 2.46v4.73H9.51V9.2h2.83v1.3h.04c.39-.74 1.36-1.52 2.79-1.52 2.98 0 3.58 1.96 3.58 4.5v5.27Z"/></svg></span>
      <span class="reader-card-arrow" aria-hidden="true">↗</span>
      <span class="reader-card-name">LinkedIn</span>
      <span class="reader-card-description">Let’s connect over AI, learning &amp; work.</span>
      <span class="reader-card-action">Connect with me</span>
    </a>
    <a class="reader-card reader-card-daily" href="https://dailychat.net/" target="_blank" rel="noopener noreferrer">
      <span class="reader-card-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-5 3v-3a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z"/><path d="m13 7-4 5h4l-2 3 5-5h-4l1-3Z"/></svg></span>
      <span class="reader-card-arrow" aria-hidden="true">↗</span>
      <span class="reader-card-name">DailyChat</span>
      <span class="reader-card-description">Your quick read on AI &amp; tech.</span>
      <span class="reader-card-action">Explore DailyChat</span>
    </a>
  </div>
</nav>
]]))
  return doc
end
