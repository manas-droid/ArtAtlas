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
        <details className="why-section">
          <summary>Why do I see this result?</summary>
          <WhyTrace trace={artwork.retrievalTrace} fallbackLabel={artwork.confidenceLabel} />
        </details>
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
        <details className="why-section">
          <summary>Why do I see this result?</summary>
          <WhyTrace trace={essay.retrievalTrace} fallbackLabel={essay.confidenceLabel} />
        </details>
      </div>
    </article>
  )
}

type WhyTraceProps = {
  trace: ArtworkResultModel['retrievalTrace'] | EssayResultModel['retrievalTrace']
  fallbackLabel: string
}

function WhyTrace({ trace, fallbackLabel }: WhyTraceProps) {
  const lexical = trace?.lexicalMatch
  const semantic = trace?.semanticalMatch

  if (!lexical && !semantic) {
    return (
      <p className="body">
        This result aligns with your query with {fallbackLabel.toLowerCase()} confidence.
      </p>
    )
  }

  return (
    <div className="body">
      {lexical && (
        <div className="meta">
          <p className="lead">Lexical match</p>
          <p className="meta">• <b>Matched Lexemes</b>: {lexical.matchedLexemes?.join(', ') || 'N/A'}</p>
          <p className="meta">• <b>Matched fields</b>: {lexical.matchedFields?.join(', ') || 'N/A'}</p>
          <p className="meta">• <b>Source</b>: {lexical.source || 'N/A'}</p>
        </div>
      )}
      {semantic && (
        <div className="meta" style={{ marginTop: '6px' }}>
          <p className="lead">Semantic similarity</p>
          <p className="meta">• <b>Similarity score</b>: {semantic.similarityValue.toFixed(2)} ({semantic.similarityLable})</p>
          <p className="meta">• <b>Embedding source</b>: {semantic.source || 'N/A'}</p>
        </div>
      )}
    </div>
  )
}
