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
import { getDeviceId } from "@/lib/device"
import { Loader2, AlertCircle, DollarSign } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

const FLAT_TYPES = ["HDB", "Condo", "Landed", "Apartment", "Executive Condo"]

export default function UserInputPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [activeTab, setActiveTab] = useState("form")

  const [formData, setFormData] = useState<FormData>({
    min_monthly_rent: 0,
    max_monthly_rent: 0,
    school_id: 0,
    target_district_id: undefined,
    max_school_limit: undefined, // Changed from max_school_distance
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
      alert("Please select a target school")
      return
    }

    if (!formData.min_monthly_rent || !formData.max_monthly_rent) {
      alert("Please enter rent range")
      return
    }

    if (formData.min_monthly_rent > formData.max_monthly_rent) {
      alert("Minimum rent cannot be greater than maximum rent")
      return
    }

    setIsSubmitting(true)

    try {
      const submitData = {
        ...formData,
        device_id: getDeviceId(),
      }
      const response = await api.submitForm(submitData)
      router.push("/recomm", { state: { properties: response.data } } as any)
    } catch (error: any) {
      console.error("Failed to submit form:", error)
      alert(error.message || "Submission failed, please try again")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleNLPSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!nlpInput.trim()) {
      alert("Please enter your requirements description")
      return
    }

    if (nlpInput.length > maxChars) {
      alert(`Description cannot exceed ${maxChars} characters`)
      return
    }

    setIsSubmitting(true)
    setNlpError(false)

    try {
      const response = await api.submitDescription(nlpInput)
      router.push("/recomm", { state: { properties: response.data } } as any)
    } catch (error: any) {
      console.error("Failed to submit NLP input:", error)
      if (error.code === 40003) {
        setNlpError(true)
      }
      alert(error.message || "Submission failed, please try again")
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
    <div className="min-h-screen bg-gradient-to-b from-blue-50/30 via-background to-blue-50/20 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent mb-4">
            Tell Us Your Requirements
          </h1>
          <p className="text-lg text-muted-foreground">Choose your preferred way to describe your ideal home</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-8 h-12">
            <TabsTrigger value="form" className="text-base">
              Detailed Form
            </TabsTrigger>
            <TabsTrigger value="nlp" className="text-base">
              Natural Language Description
            </TabsTrigger>
          </TabsList>

          {/* Form Mode */}
          <TabsContent value="form">
            <form onSubmit={handleFormSubmit}>
              <div className="space-y-6">
                <Card className="border-2 border-blue-100 shadow-sm hover:shadow-md transition-shadow">
                  <CardHeader className="bg-gradient-to-r from-blue-50 to-transparent">
                    <CardTitle className="flex items-center gap-2">
                      <DollarSign className="h-5 w-5 text-blue-600" />
                      Rent Budget <span className="text-red-500">*</span>
                    </CardTitle>
                    <CardDescription>Set your monthly rent range (required)</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4 pt-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="min_rent" className="text-base font-medium">
                          Minimum Monthly Rent (S$) <span className="text-red-500">*</span>
                        </Label>
                        <div className="relative">
                          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">S$</span>
                          <Input
                            id="min_rent"
                            type="number"
                            placeholder="e.g.: 800"
                            value={formData.min_monthly_rent || ""}
                            onChange={(e) =>
                              setFormData({ ...formData, min_monthly_rent: Number(e.target.value) || 0 })
                            }
                            className="pl-10 h-11"
                            min={0}
                            required
                          />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="max_rent" className="text-base font-medium">
                          Maximum Monthly Rent (S$) <span className="text-red-500">*</span>
                        </Label>
                        <div className="relative">
                          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">S$</span>
                          <Input
                            id="max_rent"
                            type="number"
                            placeholder="e.g.: 1500"
                            value={formData.max_monthly_rent || ""}
                            onChange={(e) =>
                              setFormData({ ...formData, max_monthly_rent: Number(e.target.value) || 0 })
                            }
                            className="pl-10 h-11"
                            min={0}
                            required
                          />
                        </div>
                      </div>
                    </div>
                    <StarRating
                      label="Rent Importance"
                      value={formData.importance_rent || 3}
                      onChange={(value) => setFormData({ ...formData, importance_rent: value })}
                    />
                  </CardContent>
                </Card>

                <Card className="border-2 border-blue-100 shadow-sm hover:shadow-md transition-shadow">
                  <CardHeader className="bg-gradient-to-r from-blue-50 to-transparent">
                    <CardTitle>School & Location Preferences</CardTitle>
                    <CardDescription>Select your target school and ideal location</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-5 pt-6">
                    <div className="space-y-2">
                      <Label htmlFor="school" className="text-base font-medium">
                        Target School <span className="text-red-500">*</span>
                      </Label>
                      <Select
                        value={formData.school_id?.toString() || ""}
                        onValueChange={(value) => setFormData({ ...formData, school_id: Number(value) })}
                        required
                      >
                        <SelectTrigger id="school" className="h-11">
                          <SelectValue placeholder="Please select target school" className="text-muted-foreground" />
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
                      <Label htmlFor="district" className="text-base font-medium">
                        Target District (Optional)
                      </Label>
                      <Select
                        value={formData.target_district_id?.toString() || ""}
                        onValueChange={(value) =>
                          setFormData({ ...formData, target_district_id: value ? Number(value) : undefined })
                        }
                      >
                        <SelectTrigger id="district" className="h-11">
                          <SelectValue placeholder="Select district (optional)" />
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
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="school_limit" className="text-base font-medium">
                          Max Commute Time (minutes)
                        </Label>
                        <Input
                          id="school_limit"
                          type="number"
                          placeholder="e.g.: 30 (means 30 minutes)"
                          value={formData.max_school_limit || ""}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              max_school_limit: e.target.value ? Number(e.target.value) : undefined,
                            })
                          }
                          className="h-11"
                          min={0}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="mrt_distance" className="text-base font-medium">
                          Max MRT Distance (meters)
                        </Label>
                        <Input
                          id="mrt_distance"
                          type="number"
                          placeholder="e.g.: 500"
                          value={formData.max_mrt_distance || ""}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              max_mrt_distance: e.target.value ? Number(e.target.value) : undefined,
                            })
                          }
                          className="h-11"
                          min={0}
                        />
                      </div>
                    </div>
                    <StarRating
                      label="Location Importance"
                      value={formData.importance_location || 3}
                      onChange={(value) => setFormData({ ...formData, importance_location: value })}
                    />
                  </CardContent>
                </Card>

                <Card className="border-2 border-blue-100 shadow-sm hover:shadow-md transition-shadow">
                  <CardHeader className="bg-gradient-to-r from-blue-50 to-transparent">
                    <CardTitle>Property Type & Facilities Preferences</CardTitle>
                    <CardDescription>Select your preferred property types</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-5 pt-6">
                    <div className="space-y-3">
                      <Label className="text-base font-medium">Property Type Preferences (Optional)</Label>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {FLAT_TYPES.map((type) => (
                          <div
                            key={type}
                            className="flex items-center space-x-3 p-3 rounded-lg border-2 border-muted hover:border-blue-200 hover:bg-blue-50/50 transition-colors"
                          >
                            <Checkbox
                              id={type}
                              checked={formData.flat_type_preference?.includes(type)}
                              onCheckedChange={() => handleFlatTypeToggle(type)}
                            />
                            <label
                              htmlFor={type}
                              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex-1"
                            >
                              {type}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                    <StarRating
                      label="Facilities Importance"
                      value={formData.importance_facility || 3}
                      onChange={(value) => setFormData({ ...formData, importance_facility: value })}
                    />
                  </CardContent>
                </Card>

                {/* Submit Button */}
                <Button
                  type="submit"
                  size="lg"
                  className="w-full h-12 text-base font-semibold shadow-lg hover:shadow-xl transition-shadow"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    "Get Recommendations"
                  )}
                </Button>
              </div>
            </form>
          </TabsContent>

          <TabsContent value="nlp">
            <form onSubmit={handleNLPSubmit}>
              <Card className="border-2 border-blue-100 shadow-sm">
                <CardHeader className="bg-gradient-to-r from-blue-50 to-transparent">
                  <CardTitle>Describe Your Requirements in Natural Language</CardTitle>
                  <CardDescription>Tell us in your own words what kind of house you want</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-6">
                  {nlpError && (
                    <Alert variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>
                        Incomplete information, please ensure price range and target school are included
                      </AlertDescription>
                    </Alert>
                  )}
                  <div className="space-y-2">
                    <Label htmlFor="nlp_input" className="text-base font-medium">
                      Requirements Description <span className="text-red-500">*</span>
                    </Label>
                    <div className="bg-blue-50/50 p-3 rounded-lg mb-3">
                      <p className="text-sm text-blue-900 font-medium">
                        Please describe your rental requirements, must include price range and target school
                      </p>
                    </div>
                    <Textarea
                      id="nlp_input"
                      placeholder="e.g.: I want to find a room near NUS, monthly rent 1000-1500 SGD, preferably with gym and kitchen facilities, no more than 500 meters from MRT station..."
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
                      <span>Please ensure price range and target school are included</span>
                      <span className={nlpInput.length >= maxChars ? "text-red-500 font-medium" : ""}>
                        {nlpInput.length}/{maxChars}
                      </span>
                    </div>
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg border border-muted">
                    <p className="text-sm font-semibold mb-2">Tips: You can include the following information</p>
                    <ul className="text-sm text-muted-foreground space-y-1.5 list-disc list-inside">
                      <li>
                        <span className="text-red-500 font-medium">Budget range (required)</span>
                      </li>
                      <li>
                        <span className="text-red-500 font-medium">Target school (required)</span>
                      </li>
                      <li>Ideal location or district</li>
                      <li>Property type preferences</li>
                      <li>Transportation convenience requirements</li>
                      <li>Other special requirements</li>
                    </ul>
                  </div>
                  <Button
                    type="submit"
                    size="lg"
                    className="w-full h-12 text-base font-semibold shadow-lg hover:shadow-xl transition-shadow"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      "Get Recommendations"
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
