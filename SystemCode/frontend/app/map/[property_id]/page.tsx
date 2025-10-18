"use client"

import { useEffect, useState } from "react"
import { useParams, useSearchParams } from "next/navigation"
import { api } from "@/lib/api"
import { Loader2, AlertCircle, ArrowLeft } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"

export default function MapPage() {
  const params = useParams()
  const searchParams = useSearchParams()

  const propertyId = params.property_id as string
  const latitude = searchParams.get("lat")
  const longitude = searchParams.get("lng")

  const [mapHtml, setMapHtml] = useState<string>("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMapData = async () => {
      if (!propertyId || !latitude || !longitude) {
        setError("缺少必要的地图参数")
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)
        const response = await api.getPropertyMap(Number(propertyId), Number(latitude), Number(longitude))
        setMapHtml(response.data.html)
      } catch (err: any) {
        console.error("[v0] Error fetching map data:", err)
        setError(err.message || "无法加载地图数据，请稍后重试")
      } finally {
        setLoading(false)
      }
    }

    fetchMapData()
  }, [propertyId, latitude, longitude])

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
          <p className="text-muted-foreground">加载地图中...</p>
        </div>
      </div>
    )
  }

  if (error || !mapHtml) {
    return (
      <div className="h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full space-y-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error || "地图数据不存在"}</AlertDescription>
          </Alert>
          <Button onClick={() => window.close()} className="w-full">
            <ArrowLeft className="h-4 w-4 mr-2" />
            关闭窗口
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-card border-b border-border p-4 shadow-sm">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-xl font-semibold text-foreground">房源地图</h1>
          <Button variant="outline" onClick={() => window.close()}>
            关闭
          </Button>
        </div>
      </div>

      <div className="flex-1">
        <iframe
          srcDoc={mapHtml}
          className="w-full h-full border-0"
          title="Property Map"
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
    </div>
  )
}
