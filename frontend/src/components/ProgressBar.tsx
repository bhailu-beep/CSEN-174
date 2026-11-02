// A thin bar that fills up as exercises are solved.
export default function ProgressBar({ done, total, label }: { done: number; total: number; label: string }) {
  const percent = total ? (done / total) * 100 : 0;
  return (
    <div className="progressBar" role="progressbar" aria-label={label} aria-valuenow={done} aria-valuemin={0} aria-valuemax={total}>
      <div style={{ width: `${percent}%` }} />
    </div>
  );
}
