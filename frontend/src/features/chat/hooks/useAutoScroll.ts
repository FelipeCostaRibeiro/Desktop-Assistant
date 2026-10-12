import { useEffect, useRef } from 'react'

export function useAutoScroll(dependency: unknown) {
  const sentinelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    sentinelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [dependency])

  return sentinelRef
}
