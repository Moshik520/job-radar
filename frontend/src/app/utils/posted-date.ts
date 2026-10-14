const DAY_MS = 24 * 60 * 60 * 1000;

/** "Today", "Yesterday", "5 days ago", "3 weeks ago", or "Aug 4, 2026" for older posts. */
export function formatPostedDate(iso: string | null, now: Date = new Date()): string {
  if (!iso) {
    return '';
  }
  const posted = new Date(iso);
  if (Number.isNaN(posted.getTime())) {
    return '';
  }
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const startOfPostedDay = new Date(posted.getFullYear(), posted.getMonth(), posted.getDate()).getTime();
  const days = Math.round((startOfToday - startOfPostedDay) / DAY_MS);

  if (days <= 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 14) return `${days} days ago`;
  if (days < 56) return `${Math.floor(days / 7)} weeks ago`;
  return posted.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
