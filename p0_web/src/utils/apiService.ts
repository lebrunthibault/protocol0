class APIService {
  private readonly baseURL = 'http://localhost:8000'

  async get(path: string) {
    const url = `${this.baseURL}${path}`
    const response = await fetch(url)
    return await response.json()
  }

  async post(path: string, data: Object) {
    const url = `${this.baseURL}${path}`
    const response = await fetch(url, {
      method: 'POST',
      mode: 'cors',
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data)
    })

    return await response.json()
  }
}

export const apiService = new APIService()
