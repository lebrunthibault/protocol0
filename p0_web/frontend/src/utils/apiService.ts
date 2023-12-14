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

const baseURL = 'http://localhost:8000'

const makeRequest = async (path: string, method: string, data: Object | null = null) => {
    const url = `${baseURL}${path}`
    let response = null;
    try {
      response = await fetch(url, getOptions(method, data))
    } catch (e: any) {
      notify(e)
      throw e
    }

    const r = response.clone()
    try {
        data = await response.json()
    } catch (e) {

        const error = await r.text()
          notify(r.statusText,{body: error, badge: url})
          throw new Error(error)
    }

    if (!response.ok) {
      notify(response.statusText)
      throw new Error(response.statusText)
    } else {
      return data
    }
}

class APIService {
  async get(path: string) {
    return await makeRequest(path, "GET")
    // const url = `${this.baseURL}${path}`
    // const response = await fetch(url)
    // return await response.json()
  }

  async post(path: string, data: Object) {
    return await makeRequest(path, "POST", data)
  }

  async put(path: string, data: Object) {
    return await makeRequest(path, "PUT", data)
  }

  async delete(path: string) {
    return await makeRequest(path, "DELETE")
  }
}

export const apiService = new APIService()
