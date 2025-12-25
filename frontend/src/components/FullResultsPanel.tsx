import type { FullResultModel } from '../full-result/full.result.response'
import { ArtworkResultCard, EssayResultCard } from './FullResultCard'

type PanelProps = {
  model: FullResultModel
}

export function FullResultsPanel({ model }: PanelProps) {
  const combined = [
    ...(model.artwork || []).map((artwork) => ({
      kind: 'artwork' as const,
      score: artwork.confidenceValue ?? 0,
      item: artwork,
    })),
    ...(model.essay || []).map((essay) => ({
      kind: 'essay' as const,
      score: essay.confidenceValue ?? 0,
      item: essay,
    })),
  ].sort((a, b) => b.score - a.score)

  const hasResults = combined.length > 0

  return (
    <section className="artworks">
      <h2>Full results</h2>

      {hasResults ? (
        <div className="concept-grid">
          {combined.map((entry, index) =>
            entry.kind === 'artwork' ? (
              <ArtworkResultCard key={`art-${entry.item.artworkId ?? index}`} artwork={entry.item} />
            ) : (
              <EssayResultCard key={`essay-${entry.item.essayId ?? index}`} essay={entry.item} />
            ),
          )}
        </div>
      ) : (
        <p className="subtle">No full results available.</p>
      )}
    </section>
  )
}
