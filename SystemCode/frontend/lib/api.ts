import axios, { type AxiosInstance, type AxiosRequestConfig } from "axios"
import type Decimal from "decimal.js"
import { convertPropertiesCoordinates } from "./utils/decimal"

// 使用环境变量或默认值
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "https://vault-arbitration-incentive-sharp.trycloudflare.com"

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
})

// 扩展 AxiosRequestConfig 接口以添加自定义属性
interface CustomAxiosRequestConfig extends AxiosRequestConfig {
  isMapRequest?: boolean
}

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

    // **[修改点 1]：识别并标记地图 API 请求**
    if (config.url && config.url.includes("/api/v1/properties/map")) {
      // 设置一个自定义标记，告知响应拦截器这个请求返回的是原始 HTML
      (config as CustomAxiosRequestConfig).isMapRequest = true
      // 强制 Axios 将响应体视为原始字符串，防止 JSON 或其他类型解析错误
      config.responseType = 'text'
      // 后端返回 HTML，修改 Accept 头，但 'application/json' 仍然用于 POST body
      config.headers.Accept = 'text/html'
    } else {
      // 确保非地图请求使用 JSON
      config.headers.Accept = 'application/json, text/plain, */*'
    }

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
      // isHTML: typeof response.data === "string" && response.data.trim().startsWith("<!DOCTYPE"), // 移除不稳定的判断
    })

    // **[修改点 2]：地图请求特殊处理**
    // 如果是地图请求，config.responseType 已经被设置为 'text'，response.data 应该是 HTML 字符串
    if ((response.config as CustomAxiosRequestConfig).isMapRequest) {
      console.log("[v0] Received HTML response (Map Request), returning raw data.")
      // 直接返回原始 response，response.data 即为 HTML 字符串
      return response
    }

    // Original JSON processing logic (for standard API responses)
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
    } else if (typeof response.data === "string" && response.data.trim().startsWith("<!DOCTYPE")) {
      // [原先的特殊处理，现在应该被 Map Request 标记取代，但可以保留作为一般页面的防护]
      console.log("[v0] Received HTML response (likely map HTML/error page) without map tag.")
      return response
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

  getRecommendationsNoSubmit: async () => {
    console.log("[v0] Fetching recommendations without submit (default)")
    // 注意：根据您的 API 响应，这里使用 /api/v1/properties/recommendation-no-submit
    const response = await apiClient.get<RecommendationsResponse>("/api/v1/properties/recommendation-no-submit")
    console.log("[v0] Default recommendations response:", response.data)
    if (response.data && response.data.properties) {
      // 转换坐标
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

  // 修复: 改为 POST 请求，并发送 JSON body，并确保返回 HTML 字符串
  getPropertyMap: async (propertyId: number, latitude: number | Decimal | string, longitude: number | Decimal | string) => {
    // 转换为数字
    const lat = typeof latitude === 'string' ? parseFloat(latitude) : Number(latitude)
    const lng = typeof longitude === 'string' ? parseFloat(longitude) : Number(longitude)

    console.log("[v0] Fetching property map:", { propertyId, latitude: lat, longitude: lng })

    // 使用 POST 请求，发送 JSON body
    // 泛型改为 string，因为拦截器会确保返回原始 HTML 字符串
    const response = await apiClient.post<string>("/api/v1/properties/map", {
      property_id: propertyId,
      latitude: lat,
      longitude: lng
    })

    // 返回 HTML 字符串
    return {
      ...response,
      data: {
        html: response.data // response.data 此时应是纯 HTML 字符串
      }
    }
  },
}

export default apiClient