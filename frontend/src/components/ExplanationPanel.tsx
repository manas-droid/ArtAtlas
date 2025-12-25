import type { ExplanationBlock, MetaData } from '../explanation/explanation.model'
import { ConceptCard } from './cards/ConceptCard'

type PanelProps = {
  blocks: ExplanationBlock[]
  metadata?: MetaData
  showEmptyMessage?: boolean
}

export function ExplanationPanel({ blocks, metadata, showEmptyMessage }: PanelProps) {
  const hasBlocks = blocks.length > 0

  return (
    <section className="concepts">
      <h2>Key ideas related to your search</h2>
      {hasBlocks ? (
        <div className="concept-grid">
          {blocks.map((block, index) => (
            <ConceptCard
              key={`${block.concept.id ?? 'concept'}-${index}`}
              block={block}
              highlight={index === 0}
            />
          ))}
        </div>
      ) : (
        showEmptyMessage && (
          <div className="empty-state">
            <p>No explainable ideas found yet. Try refining your search.</p>
          </div>
        )
      )}

      {metadata?.unexplainedResultsHidden && (
        <footer className="footer-note">
          Some retrieved artworks are not shown because they could not be confidently explained using visual evidence.
        </footer>
      )}
    </section>
  )
}
