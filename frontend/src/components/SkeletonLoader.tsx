'use client';

import { cn } from '@/utils/styling';

interface SkeletonLoaderProps {
  height?: string;
  width?: string;
  count?: number;
}

export default function SkeletonLoader({
  height = 'h-12',
  width = 'w-full',
  count = 1,
}: SkeletonLoaderProps) {
  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, idx) => (
        <div
          key={idx}
          className={cn(
            'skeleton rounded',
            height,
            width
          )}
        />
      ))}
    </div>
  );
}
