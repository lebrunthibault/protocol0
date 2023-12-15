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

const makeRequest = async (baseUrl: string, path: string, method: string, optional: boolean, data: Object | null = null) => {
    const url = `${baseUrl}${path}`

    let response = null;
    try {
      response = await fetch(url, getOptions(method, data))
    } catch (e: any) {
        if (optional) {
            notify("This feature is not available")
        } else {
            notify(e)
        }
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

class ApiService {
    constructor(private readonly baseUrl: string, private readonly optional: boolean = false) {}

  async get(path: string) {
    return await makeRequest(this.baseUrl, path, "GET", this.optional)
  }

  async post(path: string, data: Object) {
    return await makeRequest(this.baseUrl, path, "POST", this.optional, data)
  }

  async put(path: string, data: Object) {
    return await makeRequest(this.baseUrl, path, "PUT", this.optional, data)
  }

  async delete(path: string) {
    return await makeRequest(this.baseUrl, path, "DELETE", this.optional)
  }
}

export default ApiService
