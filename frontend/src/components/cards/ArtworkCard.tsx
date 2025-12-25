import type { Artwork } from '../../explanation/explanation.model'

type ArtworkCardProps = {
  artwork: Artwork
  conceptLabel: string
}

export function ArtworkCard({ artwork, conceptLabel }: ArtworkCardProps) {
  const hasImage = Boolean(artwork.imageUrl)
  return (
    <div className="artwork-card">
      <div className="artwork-thumb" aria-hidden="true">
        {hasImage ? (
          <img src={artwork.imageUrl} alt={artwork.title || conceptLabel} loading="lazy" />
        ) : (
          <span>{artwork.title || conceptLabel}</span>
        )}
      </div>
      <div className="artwork-copy">
        <p className="eyebrow">{artwork.supportStrengthLabel} support</p>
        <p className="lead">{artwork.title || 'Untitled artwork'}</p>
        <p className="body">{artwork.whyThisArtwork}</p>
      </div>
    </div>
  )
}
