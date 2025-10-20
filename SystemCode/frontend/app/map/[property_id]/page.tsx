"use client"

import { useEffect, useState } from "react"
import { useParams, useSearchParams } from "next/navigation"
import { api } from "@/lib/api"
import { FALLBACK_MAP_HTML } from "@/lib/constants/fallback-map"
import { Loader2, AlertCircle } from "lucide-react"
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
  const [usingFallback, setUsingFallback] = useState(false)

  useEffect(() => {
    const fetchMapData = async () => {
      if (!propertyId || !latitude || !longitude) {
        setError("Missing required map parameters")
        setLoading(false)
        setMapHtml(FALLBACK_MAP_HTML)
        setUsingFallback(true)
        return
      }

      try {
        setLoading(true)
        setError(null)
        const response = await api.getPropertyMap(Number(propertyId), Number(latitude), Number(longitude))
        if (response.data && response.data.html) {
          setMapHtml(response.data.html)
          setUsingFallback(false)
        } else {
          // Use fallback if no HTML returned
          setMapHtml(FALLBACK_MAP_HTML)
          setUsingFallback(true)
        }
      } catch (err: any) {
        console.error("[v0] Error fetching map data:", err)
        setMapHtml(FALLBACK_MAP_HTML)
        setUsingFallback(true)
        setError("Unable to load property map, showing default Singapore location")
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
          <p className="text-muted-foreground">Loading map...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-card border-b border-border p-4 shadow-sm">
        <div className="container mx-auto flex items-center justify-between">
          <div className="space-y-1">
            <h1 className="text-xl font-semibold text-foreground">Property Map</h1>
            {usingFallback && <p className="text-sm text-muted-foreground">Showing default Singapore location</p>}
          </div>
          <Button variant="outline" onClick={() => window.close()}>
            Close
          </Button>
        </div>
      </div>

      {error && usingFallback && (
        <div className="container mx-auto px-4 pt-4">
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      )}

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
