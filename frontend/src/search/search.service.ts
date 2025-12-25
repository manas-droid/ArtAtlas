import type { SearchModel } from "./search.model"
import { transformResponseToUIModel } from "./transform.response"

const URL:string = 'http://localhost:8080/api/search'

export const getQueryResponse = async (query:string):Promise<SearchModel>=>{

   const response =  await fetch(`${URL}?q=${query}`)

    const searchResponse = await response.json()

    return transformResponseToUIModel(searchResponse);
}