"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
// 确保从 api.ts 导入 api 对象
import { type Property, type RecommendationsResponse, api } from "@/lib/api" // <-- 假设 api.ts 路径是 @/lib/api
import RentBlock from "@/components/RentBlock"
import { Loader2, Home, AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"

export default function RecommendationsPage() {
  const router = useRouter()
  const [properties, setProperties] = useState<Property[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true)
        setError(null)

        // Read from localStorage
        const savedData = localStorage.getItem('recommendations_data')
        let data: RecommendationsResponse | null = null

        if (savedData) {
          // 尝试解析 localStorage 中的数据
          try {
            data = JSON.parse(savedData)
            console.log("[v0] Loaded recommendations from localStorage.")
          } catch (e) {
            console.warn("[v0] Failed to parse localStorage data, treating as missing.", e)
            data = null // 解析失败，视为数据不存在
          }
        }

        if (data && data.properties && data.properties.length > 0) {
          // **情况 1: 从 localStorage 读取数据成功**
          setProperties(data.properties || [])
          setTotalCount(data.total_count || 0)
        } else {
          // **情况 2: localStorage 数据不存在或无效，调用默认推荐 API**
          console.log("[v0] No valid recommendations in localStorage, fetching default recommendations...")
          const response = await api.getRecommendationsNoSubmit() // 调用新的 API
          const apiData = response.data

          if (apiData && apiData.properties) {
            setProperties(apiData.properties)
            setTotalCount(apiData.total_count)
          } else {
            // API 返回数据结构异常
            throw new Error("API returned no properties.")
          }
        }
      } catch (err: any) {
        // 捕获所有错误（包括 API 错误和 JSON 解析错误）
        console.error("[v0] Failed to fetch recommendations:", err)

        // 尝试从 API 错误对象中提取 message，否则使用通用错误信息
        const errorMessage =
          err.message ||
          err.response?.data?.message ||
          "Failed to fetch recommended properties, please try again later."

        setError(errorMessage)
        setProperties([])
        setTotalCount(0)
      } finally {
        setLoading(false)
      }
    }

    fetchRecommendations()
  }, [])

  // ... (剩余的渲染逻辑保持不变)
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
          <p className="text-lg text-muted-foreground">Finding your ideal home...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-50 p-4">
        <div className="max-w-md space-y-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>No Recommendations Available</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <Button
            onClick={() => router.push("/")}
            className="w-full"
          >
            Go to Home Page
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8 space-y-2">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Home className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Recommended Properties for You</h1>
              <p className="text-muted-foreground">
                Based on your requirements, we found <span className="font-semibold text-primary">{totalCount}</span>{" "}
                matching properties
              </p>
            </div>
          </div>
        </div>

        {properties.length === 0 ? (
          <div className="text-center py-16">
            <Home className="h-16 w-16 text-muted-foreground/50 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">No Recommended Properties</h3>
            <p className="text-muted-foreground">Please try adjusting your filter criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {properties.map((property) => (
              <RentBlock key={property.property_id} property={property} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}