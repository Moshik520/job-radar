import { formatPostedDate } from './posted-date';

describe('formatPostedDate', () => {
  const now = new Date(2026, 9, 14, 15, 0); // Oct 14, 2026, 15:00 local time

  it.each([
    [new Date(2026, 9, 14, 8, 0), 'Today'],
    [new Date(2026, 9, 13, 23, 59), 'Yesterday'],
    [new Date(2026, 9, 9, 12, 0), '5 days ago'],
    [new Date(2026, 9, 1, 12, 0), '13 days ago'],
    [new Date(2026, 8, 30, 12, 0), '2 weeks ago'],
    [new Date(2026, 7, 20, 12, 0), '7 weeks ago'],
    [new Date(2026, 7, 4, 12, 0), 'Aug 4, 2026'],
  ])('%s is shown as "%s"', (posted, expected) => {
    expect(formatPostedDate(posted.toISOString(), now)).toBe(expected);
  });

  it('shows nothing when there is no date', () => {
    expect(formatPostedDate(null, now)).toBe('');
  });

  it('shows nothing for a date it cannot read', () => {
    expect(formatPostedDate('not a date', now)).toBe('');
  });

  it('treats a date slightly in the future (clock skew) as today', () => {
    expect(formatPostedDate(new Date(2026, 9, 14, 16, 0).toISOString(), now)).toBe('Today');
  });
});
