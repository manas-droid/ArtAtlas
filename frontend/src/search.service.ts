import { transformApiResponse, type UIModel } from "./transform.api.response"

const URL:string = 'http://localhost:8080/api/search'

export const getQueryResponse = async (query:string):Promise<UIModel>=>{

   const response =  await fetch(`${URL}?q=${query}`)

    const searchResponse = await response.json()
    console.log(searchResponse)
    return transformApiResponse(searchResponse);
}