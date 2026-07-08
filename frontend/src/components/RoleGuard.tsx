import type { ReactNode } from "react";

import { useAuth } from "@/hooks/useAuth";
import type { UserRole } from "@/types";

interface RoleGuardProps {
  allow: UserRole[];
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Renders `children` only if the current user's role is in `allow`.
 * This is a UX convenience, not a security boundary — every mutating
 * endpoint re-checks permissions server-side regardless of what the
 * UI shows.
 */
export function RoleGuard({ allow, children, fallback = null }: RoleGuardProps) {
  const { user } = useAuth();
  if (!user || !allow.includes(user.role)) {
    return <>{fallback}</>;
  }
  return <>{children}</>;
}
