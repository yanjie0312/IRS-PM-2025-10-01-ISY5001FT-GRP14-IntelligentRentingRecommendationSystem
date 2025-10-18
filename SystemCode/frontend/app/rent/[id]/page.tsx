"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { api, type Property } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  ArrowLeft,
  MapPin,
  Home,
  Bed,
  Bath,
  Maximize,
  Calendar,
  School,
  Train,
  Star,
  Loader2,
  AlertCircle,
} from "lucide-react"
import Image from "next/image"

export default function RentDetailPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string

  const [property, setProperty] = useState<Property | null>(null)
  const [mapHtml, setMapHtml] = useState<string>("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const historyState = (window.history.state as any)?.state

    if (historyState?.property) {
      setProperty(historyState.property)
      setLoading(false)

      // Fetch map HTML using the new API
      const fetchMap = async () => {
        try {
          const mapResponse = await api.getPropertyMap(
            historyState.property.property_id,
            historyState.property.latitude,
            historyState.property.longitude,
          )
          setMapHtml(mapResponse.data.html)
        } catch (mapErr) {
          console.error("[v0] Error fetching map HTML:", mapErr)
        }
      }
      fetchMap()
    } else {
      // No property data in state, redirect to recommendations
      setError("请从推荐列表访问房源详情")
      setLoading(false)
    }
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
          <p className="text-muted-foreground">加载房源详情中...</p>
        </div>
      </div>
    )
  }

  if (error || !property) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full space-y-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error || "房源不存在"}</AlertDescription>
          </Alert>
          <Button onClick={() => router.push("/recomm")} className="w-full">
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回推荐列表
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50/50 to-background">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <Button variant="ghost" onClick={() => router.push("/recomm")} className="mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          返回推荐列表
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card className="overflow-hidden">
              <div className="relative h-96 w-full bg-muted">
                <Image
                  src={property.img_src || "/placeholder.svg"}
                  alt={property.name}
                  fill
                  className="object-cover"
                  priority
                />
                <Badge className="absolute top-4 right-4 bg-primary text-primary-foreground text-base px-4 py-2">
                  {property.facility_type}
                </Badge>
              </div>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <CardTitle className="text-3xl">{property.name}</CardTitle>
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <MapPin className="h-4 w-4" />
                      <span>{property.location}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-primary">{property.price}</div>
                    <div className="text-sm text-muted-foreground">每月</div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <Bed className="h-5 w-5 text-primary" />
                    <div>
                      <div className="text-sm text-muted-foreground">卧室</div>
                      <div className="font-semibold">{property.beds}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <Bath className="h-5 w-5 text-primary" />
                    <div>
                      <div className="text-sm text-muted-foreground">浴室</div>
                      <div className="font-semibold">{property.baths}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <Maximize className="h-5 w-5 text-primary" />
                    <div>
                      <div className="text-sm text-muted-foreground">面积</div>
                      <div className="font-semibold">{property.area} m²</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <Calendar className="h-5 w-5 text-primary" />
                    <div>
                      <div className="text-sm text-muted-foreground">建造年份</div>
                      <div className="font-semibold">{property.build_time}</div>
                    </div>
                  </div>
                </div>

                <Separator />

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-primary" />
                    位置信息
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="text-sm text-muted-foreground">区域</div>
                      <div className="font-medium">{property.district}</div>
                    </div>
                    <div className="space-y-2">
                      <div className="text-sm text-muted-foreground">详细地址</div>
                      <div className="font-medium">{property.location}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <School className="h-4 w-4 text-primary" />
                      <div>
                        <span className="text-sm text-muted-foreground">距学校：</span>
                        <span className="font-medium ml-2">{property.distance_to_school}m</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Train className="h-4 w-4 text-primary" />
                      <div>
                        <span className="text-sm text-muted-foreground">距地铁站：</span>
                        <span className="font-medium ml-2">{property.distance_to_mrt}m</span>
                      </div>
                    </div>
                  </div>
                </div>

                {property.public_facilities && property.public_facilities.length > 0 && (
                  <>
                    <Separator />
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Home className="h-5 w-5 text-primary" />
                        附近设施
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {property.public_facilities.map((facility, index) => (
                          <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                            <span className="font-medium">{facility.name}</span>
                            <Badge variant="secondary">{facility.distance}m</Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {mapHtml && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-primary" />
                    地图位置
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-96 rounded-lg overflow-hidden">
                    <iframe
                      srcDoc={mapHtml}
                      className="w-full h-full border-0"
                      title="Property Map"
                      sandbox="allow-scripts allow-same-origin"
                    />
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="space-y-6">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="h-5 w-5 text-primary" />
                  推荐理由
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground leading-relaxed">{property.recommend_reason}</p>
                <Separator />
                <div className="space-y-3">
                  <Button className="w-full" size="lg">
                    联系房东
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full bg-transparent"
                    size="lg"
                    onClick={() =>
                      window.open(
                        `/map/${property.property_id}?lat=${property.latitude}&lng=${property.longitude}`,
                        "_blank",
                      )
                    }
                  >
                    <MapPin className="h-4 w-4 mr-2" />
                    在新窗口查看地图
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
