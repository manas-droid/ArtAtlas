import type { ArtworkResultModel, EssayResultModel } from '../full-result/full.result.response'

type ArtworkCardProps = {
  artwork: ArtworkResultModel
}

export function ArtworkResultCard({ artwork }: ArtworkCardProps) {
  const hasImage = Boolean(artwork.imageUrl)
  const score = Number.isFinite(artwork.confidenceValue) ? artwork.confidenceValue : 0

  return (
    <article className="artwork-card">
      <div className="artwork-thumb" aria-hidden="true">
        {hasImage ? (
          <img src={artwork.imageUrl} alt={artwork.artworkTitle || 'Artwork'} loading="lazy" />
        ) : (
          <span>{artwork.artworkTitle || 'Artwork'}</span>
        )}
      </div>
      <div className="card-section">
        <p className="eyebrow">{artwork.confidenceLabel} match</p>
        <p className="lead">{artwork.artworkTitle || 'Untitled artwork'}</p>
        <p className="body">{artwork.artistName || 'Unknown artist'}</p>
        <p className="meta">Score: {score.toFixed(2)}</p>
      </div>
    </article>
  )
}

type EssayCardProps = {
  essay: EssayResultModel
}

export function EssayResultCard({ essay }: EssayCardProps) {
  const score = Number.isFinite(essay.confidenceValue) ? essay.confidenceValue : 0
  return (
    <article className="concept-card">
      <div className="card-section">
        <p className="eyebrow">{essay.confidenceLabel} relevance</p>
        <p className="lead">{essay.essayTitle}</p>
        <p className="body">{essay.essayText}</p>
        <p className="meta">
          Source: {essay.source} · Score: {score.toFixed(2)}
        </p>
      </div>
    </article>
  )
}
