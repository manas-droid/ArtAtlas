import type { ExplanationBlock } from '../../explanation/explanation.model'
import { ArtworkCard } from './ArtworkCard'

function conceptReason(label: string) {
  return `Your query relates to ${label}${label ? '' : ' this idea'}.`
}

type ConceptCardProps = {
  block: ExplanationBlock
  highlight?: boolean
}

export function ConceptCard({ block, highlight }: ConceptCardProps) {
  const { concept, evidence } = block
  return (
    <article className="concept-card">
      {highlight && <span className="pill strongest-pill">Strongest supporting idea</span>}
      <div className="card-section">
        <p className="eyebrow">Why this idea appears</p>
        <p className="lead">{conceptReason(concept.label)}</p>
        {concept.confidenceLabel && <span className="pill">{concept.confidenceLabel} confidence</span>}
      </div>

      <div className="card-section">
        <p className="eyebrow">Visual examples supporting this idea</p>
        <p className="body">Overall strength: {evidence.overallStrengthLabel}</p>
        <div className="artworks">
          {evidence.artworks.map((artwork, index) => (
            <ArtworkCard key={`${artwork.artworkId ?? 'art'}-${index}`} artwork={artwork} conceptLabel={concept.label} />
          ))}
        </div>
      </div>
    </article>
  )
}
