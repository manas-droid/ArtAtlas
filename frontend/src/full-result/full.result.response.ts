import { transformConfidenceToString } from "../explanation/transform.response"

export type FullResultModel = {
    artwork: ArtworkResultModel[]
    essay: EssayResultModel[]

}

export type RetrievalTrace = {
    lexicalMatch ?: {
        matchedLexemes : string[],
        source : string
    },
    semanticalMatch ?: {
        similarityValue : number, 
        similarityLable : string,
        source : string
    }
}

export type ArtworkResultModel = {
    artworkId: number
    artistName: string | null | undefined
    artworkTitle: string | null | undefined
    imageUrl : string 
    confidenceValue: number // final_score
    confidenceLabel: string 
    retrievalTrace: RetrievalTrace
}


export type EssayResultModel = {
    essayId:number
    essayTitle:string
    essayText:string
    source:string
    confidenceValue:number
    confidenceLabel: string,
    retrievalTrace: RetrievalTrace
}




export const transformResponseToFullResult = (results:any[]):FullResultModel=>{
    if(results.length == 0) 
        return {
            artwork: [],
            essay : []
        }

    
    const artworkResponses:any[] = results.filter((result)=>result.result_type === "artwork");
    const essayResponses:any[] = results.filter((result)=> result.result_type === "essay");

    const artworkModel: ArtworkResultModel[] = getArtworkModel(artworkResponses);
    const essayModel : EssayResultModel[]  = getEssayModel(essayResponses);

    return {
        artwork : artworkModel,
        essay : essayModel
    }
}



export const getEssayModel = (essayResponses: any[]): EssayResultModel[]=>{


    return essayResponses.map((essay)=>{

        return {
            essayId : essay.id, 
            essayText: essay.text,
            essayTitle: essay.title,
            source: essay.source, 
            confidenceValue: essay.score.final_score,
            confidenceLabel: transformConfidenceToString(essay.score.final_score),
            retrievalTrace : {
                lexicalMatch : (essay.retrieval_trace.lexical_match) ? {
                    matchedLexemes: essay.retrieval_trace.lexical_match.matched_lexemes,
                    source : transformLexicalSource(essay.retrieval_trace.lexical_match.source)
                } : undefined,
                semanticalMatch : (essay.retrieval_trace.semantic_match)  ? {
                    similarityLable : transformConfidenceToString(essay.retrieval_trace.semantic_match.similarity),
                    similarityValue : essay.retrieval_trace.semantic_match.similarity,
                    source: transformSemanticSource(essay.retrieval_trace.semantic_match.source)
                } : undefined

            }

        }
    })

}


export const getArtworkModel = (artworkResponses:any[]):ArtworkResultModel[]=>{

    return artworkResponses.map((artwork:any)=>{
        return {
            artistName: artwork.artist,
            artworkId: artwork.id, 
            artworkTitle: artwork.title,
            confidenceLabel: transformConfidenceToString(artwork.score.final_score),
            confidenceValue: artwork.score.final_score,
            imageUrl: artwork.image_url,
            retrievalTrace : {
                lexicalMatch : (artwork.retrieval_trace.lexical_match) ? {
                    matchedLexemes: artwork.retrieval_trace.lexical_match.matched_lexemes,
                    source : transformLexicalSource(artwork.retrieval_trace.lexical_match.source)
                } : undefined,
                semanticalMatch : (artwork.retrieval_trace.semantic_match)  ? {
                    similarityLable : transformConfidenceToString(artwork.retrieval_trace.semantic_match.similarity),
                    similarityValue : artwork.retrieval_trace.semantic_match.similarity,
                    source: transformSemanticSource(artwork.retrieval_trace.semantic_match.source)
                } : undefined

            }
        }

    });

}


function transformLexicalSource(source : string):string {

    if(source ===  "aggregated_metadata") return "aggregated artwork metadata"

    if(source === "essay_text") return "essay text";


    return source;
}


function transformSemanticSource(source:string):string{

    if(source === "artwork_embedding") return "artwork metadata";

    if(source === "essay_chunk") return "essay chunk";

    return source;

}