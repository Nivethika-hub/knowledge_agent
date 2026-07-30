import { AlertCircle, RefreshCw } from 'lucide-react'

export function LoadingCards({ count = 3 }: { count?: number }) {
  return (
    <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: count }, (_, index) => (
        <div className="h-36 animate-pulse rounded-2xl bg-slate-200" key={index} />
      ))}
    </div>
  )
}

export function ErrorCard({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-start gap-4 rounded-2xl border border-rose-200 bg-rose-50 p-6 text-rose-950">
      <AlertCircle className="size-6 text-rose-600" />
      <div>
        <h2 className="font-semibold">We could not load this data</h2>
        <p className="mt-1 text-sm text-rose-800">{message}</p>
      </div>
      {onRetry && (
        <button className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-semibold shadow-sm" onClick={onRetry}>
          <RefreshCw className="size-4" /> Retry
        </button>
      )}
    </div>
  )
}
