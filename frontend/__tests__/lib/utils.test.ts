/**
 * Utils Tests
 */

import { cn } from '@/lib/utils';

describe('cn (className merger)', () => {
  it('merges basic class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('handles conditional classes', () => {
    expect(cn('base', true && 'conditional')).toBe('base conditional');
    expect(cn('base', false && 'conditional')).toBe('base');
  });

  it('handles undefined and null values', () => {
    expect(cn('base', undefined, null, 'end')).toBe('base end');
  });

  it('handles arrays', () => {
    expect(cn(['foo', 'bar'], 'baz')).toBe('foo bar baz');
  });

  it('handles objects', () => {
    expect(cn({ foo: true, bar: false })).toBe('foo');
  });

  it('resolves Tailwind conflicts', () => {
    // Later classes should override earlier ones
    expect(cn('px-2', 'px-4')).toBe('px-4');
    expect(cn('text-red-500', 'text-blue-500')).toBe('text-blue-500');
  });

  it('handles complex merging', () => {
    expect(cn('p-4', 'px-2')).toBe('p-4 px-2');
    expect(cn('bg-red-500 p-4', 'bg-blue-500')).toBe('p-4 bg-blue-500');
  });

  it('returns empty string for no inputs', () => {
    expect(cn()).toBe('');
  });
});
