"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { StarRating } from "@/components/StarRating"
import { api, type FormData } from "@/lib/api"
import { SCHOOLS } from "@/lib/constants/schools"
import { DISTRICTS } from "@/lib/constants/districts"
import { Loader2, AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

const FLAT_TYPES = ["HDB", "Condo", "Landed", "Apartment", "Executive Condo"]

export default function UserInputPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [activeTab, setActiveTab] = useState("form")

  const [formData, setFormData] = useState<FormData>({
    min_monthly_rent: 1000,
    max_monthly_rent: 2000,
    school_id: 0,
    target_district_id: undefined,
    max_school_distance: undefined,
    flat_type_preference: [],
    max_mrt_distance: undefined,
    importance_rent: 3,
    importance_location: 3,
    importance_facility: 3,
  })

  const [nlpInput, setNlpInput] = useState("")
  const [nlpError, setNlpError] = useState(false)
  const maxChars = 500

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.school_id) {
      alert("请选择目标学校")
      return
    }

    setIsSubmitting(true)

    try {
      const response = await api.submitForm(formData)
      // Pass the returned property data to recommendations page
      router.push("/recomm", { state: { properties: response.data } } as any)
    } catch (error: any) {
      console.error("Failed to submit form:", error)
      alert(error.message || "提交失败，请重试")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleNLPSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!nlpInput.trim()) {
      alert("请输入您的需求描述")
      return
    }

    if (nlpInput.length > maxChars) {
      alert(`描述不能超过 ${maxChars} 字`)
      return
    }

    setIsSubmitting(true)
    setNlpError(false)

    try {
      const response = await api.submitDescription(nlpInput)
      // Pass the returned property data to recommendations page
      router.push("/recomm", { state: { properties: response.data } } as any)
    } catch (error: any) {
      console.error("Failed to submit NLP input:", error)
      if (error.code === 40003) {
        setNlpError(true)
      }
      alert(error.message || "提交失败，请重试")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleFlatTypeToggle = (flatType: string) => {
    setFormData((prev) => ({
      ...prev,
      flat_type_preference: prev.flat_type_preference?.includes(flatType)
        ? prev.flat_type_preference.filter((type) => type !== flatType)
        : [...(prev.flat_type_preference || []), flatType],
    }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-3">告诉我们您的需求</h1>
          <p className="text-lg text-muted-foreground">选择您喜欢的方式来描述理想住所</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-8">
            <TabsTrigger value="form">详细表单</TabsTrigger>
            <TabsTrigger value="nlp">自然语言描述</TabsTrigger>
          </TabsList>

          {/* Form Mode */}
          <TabsContent value="form">
            <form onSubmit={handleFormSubmit}>
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>租金预算 *</CardTitle>
                    <CardDescription>设置您的月租金范围（必填）</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="min_rent">最低月租 (SGD) *</Label>
                        <Input
                          id="min_rent"
                          type="number"
                          value={formData.min_monthly_rent}
                          onChange={(e) => setFormData({ ...formData, min_monthly_rent: Number(e.target.value) })}
                          min={0}
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="max_rent">最高月租 (SGD) *</Label>
                        <Input
                          id="max_rent"
                          type="number"
                          value={formData.max_monthly_rent}
                          onChange={(e) => setFormData({ ...formData, max_monthly_rent: Number(e.target.value) })}
                          min={0}
                          required
                        />
                      </div>
                    </div>
                    <StarRating
                      label="租金重要性"
                      value={formData.importance_rent || 3}
                      onChange={(value) => setFormData({ ...formData, importance_rent: value })}
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>学校与位置偏好</CardTitle>
                    <CardDescription>选择您的目标学校和理想位置</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="school">目标学校 *</Label>
                      <Select
                        value={formData.school_id?.toString()}
                        onValueChange={(value) => setFormData({ ...formData, school_id: Number(value) })}
                        required
                      >
                        <SelectTrigger id="school">
                          <SelectValue placeholder="请选择学校" />
                        </SelectTrigger>
                        <SelectContent>
                          {SCHOOLS.map((school) => (
                            <SelectItem key={school.id} value={school.id.toString()}>
                              {school.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="district">目标区域（可选）</Label>
                      <Select
                        value={formData.target_district_id?.toString() || ""}
                        onValueChange={(value) =>
                          setFormData({ ...formData, target_district_id: value ? Number(value) : undefined })
                        }
                      >
                        <SelectTrigger id="district">
                          <SelectValue placeholder="选择区域（可选）" />
                        </SelectTrigger>
                        <SelectContent>
                          {DISTRICTS.map((district) => (
                            <SelectItem key={district.id} value={district.id.toString()}>
                              {district.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="school_distance">最大学校距离 (米)</Label>
                        <Input
                          id="school_distance"
                          type="number"
                          placeholder="例如：1000"
                          value={formData.max_school_distance || ""}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              max_school_distance: e.target.value ? Number(e.target.value) : undefined,
                            })
                          }
                          min={0}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="mrt_distance">最大地铁站距离 (米)</Label>
                        <Input
                          id="mrt_distance"
                          type="number"
                          placeholder="例如：500"
                          value={formData.max_mrt_distance || ""}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              max_mrt_distance: e.target.value ? Number(e.target.value) : undefined,
                            })
                          }
                          min={0}
                        />
                      </div>
                    </div>
                    <StarRating
                      label="位置重要性"
                      value={formData.importance_location || 3}
                      onChange={(value) => setFormData({ ...formData, importance_location: value })}
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>房型与设施偏好</CardTitle>
                    <CardDescription>选择您偏好的房屋类型</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <Label>房屋类型偏好（可选）</Label>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {FLAT_TYPES.map((type) => (
                          <div key={type} className="flex items-center space-x-2">
                            <Checkbox
                              id={type}
                              checked={formData.flat_type_preference?.includes(type)}
                              onCheckedChange={() => handleFlatTypeToggle(type)}
                            />
                            <label
                              htmlFor={type}
                              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                            >
                              {type}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                    <StarRating
                      label="设施重要性"
                      value={formData.importance_facility || 3}
                      onChange={(value) => setFormData({ ...formData, importance_facility: value })}
                    />
                  </CardContent>
                </Card>

                {/* Submit Button */}
                <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      提交中...
                    </>
                  ) : (
                    "获取推荐"
                  )}
                </Button>
              </div>
            </form>
          </TabsContent>

          <TabsContent value="nlp">
            <form onSubmit={handleNLPSubmit}>
              <Card>
                <CardHeader>
                  <CardTitle>用自然语言描述您的需求</CardTitle>
                  <CardDescription>用您自己的话告诉我们您想要什么样的房子</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {nlpError && (
                    <Alert variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>必要信息不全，请确保包含价格范围和目标学校</AlertDescription>
                    </Alert>
                  )}
                  <div className="space-y-2">
                    <Label htmlFor="nlp_input">需求描述 *</Label>
                    <Textarea
                      id="nlp_input"
                      placeholder="例如：我想在 NUS 附近找一个房间，月租 1000-1500 新币，最好有健身房和厨房设施，离地铁站不超过 500 米..."
                      value={nlpInput}
                      onChange={(e) => {
                        setNlpInput(e.target.value)
                        setNlpError(false)
                      }}
                      rows={10}
                      className={`resize-none ${nlpError ? "border-red-500 focus-visible:ring-red-500" : ""}`}
                      required
                      maxLength={maxChars}
                    />
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <span>请确保包含价格范围和目标学校</span>
                      <span>
                        {nlpInput.length}/{maxChars}
                      </span>
                    </div>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground">
                      <strong>提示：</strong>您可以包含以下信息：
                    </p>
                    <ul className="text-sm text-muted-foreground mt-2 space-y-1 list-disc list-inside">
                      <li>预算范围（必填）</li>
                      <li>目标学校（必填）</li>
                      <li>理想位置或区域</li>
                      <li>房屋类型偏好</li>
                      <li>交通便利性需求</li>
                      <li>其他特殊要求</li>
                    </ul>
                  </div>
                  <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
                    {isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        分析中...
                      </>
                    ) : (
                      "获取推荐"
                    )}
                  </Button>
                </CardContent>
              </Card>
            </form>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
