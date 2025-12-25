import type { ExplanationModel } from "./explanation/explanation.model"
import { transformResponseToExplanation } from "./explanation/transform.response"
import { transformResponseToFullResult, type FullResultModel } from "./full-result/full.result.response"



export type UIModel = {
    explanationModel : ExplanationModel,
    fullResultModel  : FullResultModel
} 



export const transformApiResponse = (searchResponse:any):UIModel=>{
    const explanationModel: ExplanationModel  =  transformResponseToExplanation(searchResponse)
    const fullResultModel : FullResultModel   = transformResponseToFullResult(searchResponse.results); 
  return {
    explanationModel,
    fullResultModel
  }
}