'use client';

/**
 * CaseMembersDropdown Component
 * Displays case team members as an avatar stack with dropdown.
 *
 * Used in case detail header instead of a separate tab.
 */

import { useState, useRef, useEffect } from 'react';
import { Users, ChevronDown } from 'lucide-react';

interface CaseMember {
  userId: string;
  userName?: string;
  role: string;
}

interface CaseMembersDropdownProps {
  /** List of case members */
  members: CaseMember[];
  /** Maximum number of avatars to show before +N */
  maxAvatars?: number;
}

const ROLE_COLORS: Record<string, string> = {
  OWNER: 'bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300',
  MEMBER: 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300',
  VIEWER: 'bg-gray-100 text-gray-800 dark:bg-neutral-700 dark:text-neutral-300',
};

const ROLE_LABELS: Record<string, string> = {
  OWNER: '담당자',
  MEMBER: '팀원',
  VIEWER: '열람자',
};

/**
 * Get initials from a name
 */
function getInitials(name?: string): string {
  if (!name) return '?';
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

/**
 * Generate a consistent color based on user ID
 */
function getAvatarColor(userId?: string): string {
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-yellow-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-teal-500',
    'bg-orange-500',
  ];
  if (!userId) return colors[0];
  const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
}

/**
 * Avatar component for a single member
 */
function MemberAvatar({
  member,
  size = 'md',
  showBorder = true,
}: {
  member: CaseMember;
  size?: 'sm' | 'md';
  showBorder?: boolean;
}) {
  const sizeClasses = size === 'sm' ? 'w-6 h-6 text-xs' : 'w-8 h-8 text-sm';
  const borderClasses = showBorder ? 'ring-2 ring-white dark:ring-neutral-800' : '';

  return (
    <div
      className={`${sizeClasses} ${borderClasses} ${getAvatarColor(member.userId)} rounded-full flex items-center justify-center text-white font-medium`}
      title={member.userName || member.userId}
    >
      {getInitials(member.userName)}
    </div>
  );
}

/**
 * Case members dropdown with avatar stack
 */
export function CaseMembersDropdown({ members, maxAvatars = 3 }: CaseMembersDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (members.length === 0) {
    return (
      <div className="flex items-center text-sm text-[var(--color-text-secondary)]">
        <Users className="w-4 h-4 mr-1" />
        팀원 없음
      </div>
    );
  }

  const visibleMembers = members.slice(0, maxAvatars);
  const hiddenCount = members.length - maxAvatars;

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger: Avatar Stack */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center hover:opacity-80 transition-opacity"
      >
        <div className="flex -space-x-2">
          {visibleMembers.map((member) => (
            <MemberAvatar key={member.userId} member={member} />
          ))}
          {hiddenCount > 0 && (
            <div className="w-8 h-8 rounded-full bg-gray-300 dark:bg-neutral-600 flex items-center justify-center text-xs font-medium text-gray-700 dark:text-neutral-200 ring-2 ring-white dark:ring-neutral-800">
              +{hiddenCount}
            </div>
          )}
        </div>
        <ChevronDown className={`w-4 h-4 ml-1 text-[var(--color-text-secondary)] transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-lg shadow-lg z-20 py-2">
          <div className="px-3 py-1 text-xs font-medium text-[var(--color-text-secondary)] border-b border-gray-100 dark:border-neutral-700">
            팀원 ({members.length})
          </div>
          <div className="max-h-64 overflow-y-auto">
            {members.map((member) => (
              <div
                key={member.userId}
                className="px-3 py-2 hover:bg-gray-50 dark:hover:bg-neutral-700/50 flex items-center justify-between"
              >
                <div className="flex items-center space-x-2">
                  <MemberAvatar member={member} size="sm" showBorder={false} />
                  <div>
                    <div className="text-sm font-medium text-[var(--color-text-primary)]">
                      {member.userName || '이름 없음'}
                    </div>
                  </div>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded ${ROLE_COLORS[member.role] || ROLE_COLORS.VIEWER}`}>
                  {ROLE_LABELS[member.role] || member.role}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
