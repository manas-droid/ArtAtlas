import { transformConfidenceToString } from "../explanation/transform.response"

export type FullResultModel = {
    artwork: ArtworkResultModel[]
    essay: EssayResultModel[]

}


export type ArtworkResultModel = {
    artworkId: number
    artistName: string | null | undefined
    artworkTitle: string | null | undefined
    imageUrl : string 
    confidenceValue: number // final_score
    confidenceLabel: string 
}


export type EssayResultModel = {
    essayId:number
    essayTitle:string
    essayText:string
    source:string
    confidenceValue:number
    confidenceLabel: string
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
            confidenceLabel: transformConfidenceToString(essay.score.final_score)
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
            imageUrl: artwork.image_url
        }

    });

}