class APIService {
  private readonly baseURL = 'http://localhost:8000'

  async fetch(path: string) {
    const url = `${this.baseURL}${path}`
    const response = await fetch(url)
    return await response.json()
  }
}

export const apiService = new APIService()
