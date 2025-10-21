import axios, { type AxiosInstance } from "axios"
import type Decimal from "decimal.js"
import { convertPropertiesCoordinates } from "./utils/decimal"

// 使用环境变量或默认值
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "https://base-sessions-nearest-regardless.trycloudflare.com"

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
})

export interface ApiResponse<T = any> {
  code: number // 200 = success, others = error codes
  message: string
  data: T
}

// Request interceptor for adding auth tokens or logging
apiClient.interceptors.request.use(
  (config) => {
    console.log("[v0] API Request:", {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      data: config.data,
      params: config.params,
    })
    // Add auth token if available
    const token = typeof window !== "undefined" ? sessionStorage.getItem("auth_token") : null
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error("[v0] Request setup error:", error)
    return Promise.reject(error)
  },
)

apiClient.interceptors.response.use(
  (response) => {
    console.log("[v0] API Response:", {
      status: response.status,
      statusText: response.statusText,
      data: response.data,
      dataType: typeof response.data,
      isHTML: typeof response.data === "string" && response.data.trim().startsWith("<!DOCTYPE"),
    })

    // Check if response is HTML instead of JSON
    if (typeof response.data === "string" && response.data.trim().startsWith("<!DOCTYPE")) {
      console.error("[v0] Received HTML instead of JSON. This usually means the API endpoint doesn't exist.")
      return Promise.reject({
        message: "API endpoint not found or returned HTML instead of JSON",
        response: response,
        isHTMLResponse: true,
      })
    }

    // Extract data from unified response format
    if (response.data && typeof response.data === "object" && "code" in response.data) {
      const apiResponse = response.data as ApiResponse
      console.log("[v0] API Response Code:", apiResponse.code, "Message:", apiResponse.message)
      if (apiResponse.code === 200) {
        // Success: return the data field
        response.data = apiResponse.data
      } else {
        // Error code in response: reject with error info
        return Promise.reject({
          code: apiResponse.code,
          message: apiResponse.message,
          response: response,
        })
      }
    }
    return response
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error("[v0] API Error Response:", {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers,
      })
    } else if (error.request) {
      console.error("[v0] Network Error - No response received:", {
        message: error.message,
        url: error.config?.url,
        baseURL: error.config?.baseURL,
      })

      const corsError = new Error(
        "Unable to connect to the API server. Please check your network connection and ensure the backend server is running.",
      )
      corsError.name = "NetworkError"
      return Promise.reject(corsError)
    } else {
      // Error in request setup
      console.error("[v0] Request Setup Error:", error.message)
    }
    return Promise.reject(error)
  },
)

export interface Property {
  property_id: number
  img_src: string
  name: string
  district: string
  price: string
  beds: number
  baths: number
  area: number
  build_time: string
  location: string
  time_to_school: number
  distance_to_mrt: number
  latitude: Decimal
  longitude: Decimal
  public_facilities: Array<{
    name: string
    distance: number
  }>
  facility_type: string
  recommend_reason: string
}

// Recommendations response interface
export interface RecommendationsResponse {
  properties: Property[]
  total_count: number
}

export interface FormData {
  min_monthly_rent: number
  max_monthly_rent: number
  school_id: number
  target_district_id?: number
  max_school_limit?: number
  flat_type_preference?: string[]
  max_mrt_distance?: number
  importance_rent?: number
  importance_location?: number
  importance_facility?: number
  device_id?: string
}

export interface MapData {
  html: string
}

export const api = {
  // Navigation data
  getNavigation: () => apiClient.get("/api/nav"),

  submitForm: async (data: FormData) => {
    console.log("[v0] Submitting form data:", data)
    const response = await apiClient.post<RecommendationsResponse>("/api/v1/properties/submit-form", data)
    console.log("[v0] Form submission response:", response.data)
    if (response.data && response.data.properties) {
      response.data.properties = convertPropertiesCoordinates(response.data.properties)
    }
    return response
  },

  submitDescription: async (description: string) => {
    console.log("[v0] Submitting description:", description)
    const response = await apiClient.post<RecommendationsResponse>("/api/v1/properties/submit-description", {
      description,
    })
    console.log("[v0] Description submission response:", response.data)
    if (response.data && response.data.properties) {
      response.data.properties = convertPropertiesCoordinates(response.data.properties)
    }
    return response
  },

  getRecommendationsWithoutSubmit: async () => {
    console.log("[v0] Fetching recommendations without submit")
    const response = await apiClient.get<RecommendationsResponse>("/api/v1/properties/recommendations")
    console.log("[v0] Recommendations response:", response.data)
    if (response.data && response.data.properties) {
      response.data.properties = convertPropertiesCoordinates(response.data.properties)
    }
    return response
  },

  getPropertyDetail: async (propertyId: number) => {
    console.log("[v0] Fetching property detail:", propertyId)
    const response = await apiClient.get<Property>(`/api/v1/properties/${propertyId}`)
    console.log("[v0] Property detail response:", response.data)
    if (response.data) {
      const properties = convertPropertiesCoordinates([response.data])
      return { ...response, data: properties[0] }
    }
    return response
  },

  // 修复：使用正确的参数名称和格式
  getPropertyMap: (propertyId: number, latitude: number | Decimal | string, longitude: number | Decimal | string) => {
    // 转换为数字字符串，确保精度
    const lat = typeof latitude === 'string' ? latitude : String(latitude)
    const lng = typeof longitude === 'string' ? longitude : String(longitude)

    console.log("[v0] Fetching property map:", { propertyId, latitude: lat, longitude: lng })

    return apiClient.get<MapData>(`/api/v1/properties/${propertyId}/map`, {
      params: {
        latitude: lat,
        longitude: lng
      },
    })
  },
}

export default apiClient