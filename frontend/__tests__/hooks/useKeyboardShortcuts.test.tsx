/**
 * useKeyboardShortcuts Hook Tests
 */

import React from 'react';
import { renderHook, act } from '@testing-library/react';
import {
  useKeyboardShortcuts,
  getModifierKey,
  formatShortcut,
} from '@/hooks/useKeyboardShortcuts';

describe('useKeyboardShortcuts', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('calls action when matching shortcut is pressed', () => {
    const action = jest.fn();
    renderHook(() =>
      useKeyboardShortcuts({
        shortcuts: [{ key: 'k', metaKey: true, action }],
      })
    );

    act(() => {
      const event = new KeyboardEvent('keydown', {
        key: 'k',
        metaKey: true,
        bubbles: true,
      });
      window.dispatchEvent(event);
    });

    expect(action).toHaveBeenCalledTimes(1);
  });

  it('does not call action when different key is pressed', () => {
    const action = jest.fn();
    renderHook(() =>
      useKeyboardShortcuts({
        shortcuts: [{ key: 'k', metaKey: true, action }],
      })
    );

    act(() => {
      const event = new KeyboardEvent('keydown', {
        key: 'j',
        metaKey: true,
        bubbles: true,
      });
      window.dispatchEvent(event);
    });

    expect(action).not.toHaveBeenCalled();
  });

  it('does not call action when modifier key does not match', () => {
    const action = jest.fn();
    renderHook(() =>
      useKeyboardShortcuts({
        shortcuts: [{ key: 'k', metaKey: true, action }],
      })
    );

    act(() => {
      const event = new KeyboardEvent('keydown', {
        key: 'k',
        metaKey: false,
        bubbles: true,
      });
      window.dispatchEvent(event);
    });

    expect(action).not.toHaveBeenCalled();
  });

  it('handles multiple shortcuts', () => {
    const action1 = jest.fn();
    const action2 = jest.fn();
    renderHook(() =>
      useKeyboardShortcuts({
        shortcuts: [
          { key: 'k', metaKey: true, action: action1 },
          { key: 's', metaKey: true, action: action2 },
        ],
      })
    );

    act(() => {
      window.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true })
      );
    });
    expect(action1).toHaveBeenCalledTimes(1);
    expect(action2).not.toHaveBeenCalled();

    act(() => {
      window.dispatchEvent(
        new KeyboardEvent('keydown', { key: 's', metaKey: true, bubbles: true })
      );
    });
    expect(action2).toHaveBeenCalledTimes(1);
  });

  it('respects enabled option', () => {
    const action = jest.fn();
    renderHook(() =>
      useKeyboardShortcuts({
        shortcuts: [{ key: 'k', metaKey: true, action }],
        enabled: false,
      })
    );

    act(() => {
      window.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true })
      );
    });

    expect(action).not.toHaveBeenCalled();
  });

  it('respects individual shortcut enabled option', () => {
    const action = jest.fn();
    renderHook(() =>
      useKeyboardShortcuts({
        shortcuts: [{ key: 'k', metaKey: true, action, enabled: false }],
      })
    );

    act(() => {
      window.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true })
      );
    });

    expect(action).not.toHaveBeenCalled();
  });

  it('handles shift modifier correctly', () => {
    const action = jest.fn();
    renderHook(() =>
      useKeyboardShortcuts({
        shortcuts: [{ key: 'k', metaKey: true, shiftKey: true, action }],
      })
    );

    // Without shift - should not trigger
    act(() => {
      window.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true })
      );
    });
    expect(action).not.toHaveBeenCalled();

    // With shift - should trigger
    act(() => {
      window.dispatchEvent(
        new KeyboardEvent('keydown', {
          key: 'k',
          metaKey: true,
          shiftKey: true,
          bubbles: true,
        })
      );
    });
    expect(action).toHaveBeenCalledTimes(1);
  });

  it('cleans up event listener on unmount', () => {
    const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener');
    
    const { unmount } = renderHook(() =>
      useKeyboardShortcuts({
        shortcuts: [{ key: 'k', metaKey: true, action: jest.fn() }],
      })
    );

    unmount();

    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'keydown',
      expect.any(Function),
      true
    );
  });
});

describe('getModifierKey', () => {
  const originalPlatform = navigator.platform;

  afterEach(() => {
    Object.defineProperty(navigator, 'platform', {
      value: originalPlatform,
      writable: true,
    });
  });

  it('returns ⌘ for Mac', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'MacIntel',
      writable: true,
    });
    expect(getModifierKey()).toBe('⌘');
  });

  it('returns Ctrl for Windows', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'Win32',
      writable: true,
    });
    expect(getModifierKey()).toBe('Ctrl');
  });
});

describe('formatShortcut', () => {
  it('formats basic shortcut', () => {
    expect(formatShortcut({ key: 'k', action: jest.fn() })).toBe('K');
  });

  it('formats shortcut with meta key', () => {
    const result = formatShortcut({ key: 'k', metaKey: true, action: jest.fn() });
    expect(result).toMatch(/^(⌘|Ctrl) \+ K$/);
  });

  it('formats shortcut with shift key', () => {
    const result = formatShortcut({ key: 'k', shiftKey: true, action: jest.fn() });
    expect(result).toBe('Shift + K');
  });

  it('formats shortcut with multiple modifiers', () => {
    const result = formatShortcut({
      key: 's',
      metaKey: true,
      shiftKey: true,
      action: jest.fn(),
    });
    expect(result).toMatch(/^(⌘|Ctrl) \+ Shift \+ S$/);
  });
});
