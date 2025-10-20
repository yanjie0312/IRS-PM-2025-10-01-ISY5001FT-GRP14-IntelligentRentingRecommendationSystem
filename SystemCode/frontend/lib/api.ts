import axios, { type AxiosInstance } from "axios"

// Base API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

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
    // Add auth token if available
    const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

apiClient.interceptors.response.use(
  (response) => {
    // Extract data from unified response format
    if (response.data && typeof response.data === "object" && "code" in response.data) {
      const apiResponse = response.data as ApiResponse
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
      console.error("[v0] API Error:", error.response.status, error.response.data)
    } else if (error.request) {
      // Request made but no response received
      console.error("[v0] Network Error:", error.message)
    } else {
      // Error in request setup
      console.error("[v0] Request Error:", error.message)
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
  distance_to_school: number // Changed to number
  distance_to_mrt: number // Changed to number
  latitude: number
  longitude: number
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
  max_school_limit?: number // Maximum acceptable commute time to school in minutes
  flat_type_preference?: string[]
  max_mrt_distance?: number
  importance_rent?: number
  importance_location?: number
  importance_facility?: number
  device_id?: string
}

export interface DescriptionInput {
  description: string
}


export interface MapData {
  html: string
}

export const api = {
  // Navigation data
  getNavigation: () => apiClient.get("/api/nav"),

  submitForm: (data: FormData) => apiClient.post<RecommendationsResponse>("/api/v1/properties/submit-form", data),

  submitDescription: (description: string) =>
    apiClient.post<RecommendationsResponse>("/api/v1/properties/submit-description", { description }),

  // Get recommendations
  getRecommendations: () => apiClient.get<RecommendationsResponse>("/api/recommendations"),

  getRecommendationsWithoutSubmit: () =>
    apiClient.get<RecommendationsResponse>("/api/v1/properties/recommendation-no-submit"),

  getPropertyMap: (propertyId: number, latitude: number, longitude: number) =>
    apiClient.get<MapData>("/api/v1/properties/map", {
      params: { property_id: propertyId, latitude, longitude },
    }),


}

export default apiClient
