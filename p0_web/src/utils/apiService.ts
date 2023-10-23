import {notify} from "@/utils/utils";

function getOptions(method: string, body: Object | null = null) {
  const options: any = {
      method: method,
      mode: 'cors',
      headers: {
        "Content-Type": "application/json",
      },
    }

    if (body) {
        options["body"] = JSON.stringify(body)
    }

    return options
}

class APIService {
  private readonly baseURL = 'http://localhost:8000'

  async get(path: string) {
    const url = `${this.baseURL}${path}`
    const response = await fetch(url)
    return await response.json()
  }

  async put(path: string, data: Object) {
    const url = `${this.baseURL}${path}`
    try {
      const response = await fetch(url, getOptions("PUT", data))
      return await response.json()
    } catch (e: any) {
      notify(e)
      throw e
    }
  }

  async delete(path: string) {
    const url = `${this.baseURL}${path}`
    const response = await fetch(url, getOptions("DELETE"))
    return await response.json()
  }
}

export const apiService = new APIService()
