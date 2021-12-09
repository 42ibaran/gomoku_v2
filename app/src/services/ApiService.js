const API_URL = "http://localhost:5000"

export class ApiService {
    static async post(path, data, queryParams={}) {
        let url = new URL(API_URL + path)
        Object.keys(queryParams).forEach(key => url.searchParams.append(key, queryParams[key]))
        try {
            const response = await fetch(url, {
                method : 'POST',
                headers : {
                    'Content-Type': 'application/json'
                },
                body : data ? JSON.stringify(data) : ''
            })
            return await response.json() ?? {}
        } catch(e) {
            return e
        }
    }
}
