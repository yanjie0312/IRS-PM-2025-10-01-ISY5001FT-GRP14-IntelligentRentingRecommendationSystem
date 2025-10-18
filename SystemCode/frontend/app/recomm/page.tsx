"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { api, type Property, type RecommendationsResponse } from "@/lib/api"
import RentBlock from "@/components/RentBlock"
import { Loader2, Home, AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

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

        const historyState = (window.history.state as any)?.state

        if (historyState?.properties) {
          // Use data passed from user input page
          const data: RecommendationsResponse = historyState.properties
          setProperties(data.properties)
          setTotalCount(data.total_count)
        } else {
          // No data passed, fetch recommendations without submit
          const response = await api.getRecommendationsWithoutSubmit()
          const data: RecommendationsResponse = response.data
          setProperties(data.properties)
          setTotalCount(data.total_count)
        }
      } catch (err: any) {
        console.error("[v0] Failed to fetch recommendations:", err)
        setError(err.response?.data?.message || "获取推荐房源失败，请稍后重试")
      } finally {
        setLoading(false)
      }
    }

    fetchRecommendations()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
          <p className="text-lg text-muted-foreground">正在为您寻找理想住所...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-50 p-4">
        <Alert variant="destructive" className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>加载失败</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
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
              <h1 className="text-3xl font-bold text-foreground">为您推荐的房源</h1>
              <p className="text-muted-foreground">
                根据您的需求，我们为您找到了 <span className="font-semibold text-primary">{totalCount}</span>{" "}
                个匹配的房源
              </p>
            </div>
          </div>
        </div>

        {properties.length === 0 ? (
          <div className="text-center py-16">
            <Home className="h-16 w-16 text-muted-foreground/50 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">暂无推荐房源</h3>
            <p className="text-muted-foreground">请尝试调整您的筛选条件</p>
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
