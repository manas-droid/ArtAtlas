
export type SearchModel = {
    query:string;
    explanationBlocks: ExplanationBlock[]
    metadata: MetaData
}


export type ExplanationBlock = {
    concept : Concept
    evidence:Evidence
}

export type Evidence = {
    overallStrengthLabel : string
    overallStrengthValue : number
    artworks : Artwork[]
}


export type Artwork = {
    artworkId : number
    supportStrengthLabel:string
    supportStrengthValue : number    
    provenance:string
    whyThisArtwork:string
}

export type Concept = {
    id : number 
    label: string
    confidenceLabel:string
    confidenceValue:number
  
}



export type MetaData = {
    unexplainedResultsHidden:boolean
    explanationComplete:boolean
}





/**
 * 

 * 
 * 
 * 
 * 
 * 
 */

