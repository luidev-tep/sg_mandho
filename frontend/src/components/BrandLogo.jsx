import { communityConfig } from '../config/communityConfig';

export default function BrandLogo({ size = 40 }) {
  return <svg width={size} height={size} viewBox="0 0 48 48" role="img" aria-label={communityConfig.branding.shortName}>
    <rect width="48" height="48" rx="13" fill="var(--brand-primary)" />
    <path d="M9 18 24 8l15 10v3H9z" fill="white" opacity=".75" />
    <text x="24" y="35" textAnchor="middle" fill="white" fontFamily="Inter, sans-serif" fontWeight="700" fontSize="16">{communityConfig.branding.logoInitials}</text>
  </svg>;
}
