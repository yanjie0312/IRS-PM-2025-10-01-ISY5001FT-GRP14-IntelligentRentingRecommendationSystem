"use client"

import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { Home, MapPin, Shield, TrendingUp } from "lucide-react"

export default function WelcomePage() {
  const router = useRouter()

  const handleGetStarted = () => {
    router.push("/userin")
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-accent/10">
        <div className="container mx-auto px-4 py-20 md:py-32">
          <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
            {/* Left Content */}
            <div className="space-y-8 text-center lg:text-left">
              <div className="space-y-4">
                <h1 className="font-serif text-4xl md:text-5xl lg:text-6xl font-bold text-balance leading-tight">
                  找到你的
                  <span className="text-primary block mt-2">理想住所</span>
                </h1>
                <p className="text-lg md:text-xl text-muted-foreground text-pretty max-w-2xl mx-auto lg:mx-0">
                  智能推荐系统帮您快速找到最适合的租房选择，让找房变得简单高效
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Button
                  size="lg"
                  onClick={handleGetStarted}
                  className="text-lg px-8 py-6 shadow-lg hover:shadow-xl transition-all"
                >
                  <Home className="mr-2 h-5 w-5" />
                  开始找房
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  onClick={() => router.push("/recomm")}
                  className="text-lg px-8 py-6"
                >
                  浏览推荐
                </Button>
              </div>

              {/* Feature Stats */}
              <div className="grid grid-cols-3 gap-4 pt-8 border-t border-border">
                <div className="text-center lg:text-left">
                  <div className="text-2xl md:text-3xl font-bold text-primary">1000+</div>
                  <div className="text-sm text-muted-foreground">优质房源</div>
                </div>
                <div className="text-center lg:text-left">
                  <div className="text-2xl md:text-3xl font-bold text-primary">95%</div>
                  <div className="text-sm text-muted-foreground">满意度</div>
                </div>
                <div className="text-center lg:text-left">
                  <div className="text-2xl md:text-3xl font-bold text-primary">24h</div>
                  <div className="text-sm text-muted-foreground">快速响应</div>
                </div>
              </div>
            </div>

            {/* Right Image/Visual */}
            <div className="relative">
              <div className="relative aspect-[4/3] rounded-2xl overflow-hidden shadow-2xl">
                <img
                  src="/modern-apartment-building-exterior-with-blue-sky.jpg"
                  alt="Modern apartment building"
                  className="object-cover w-full h-full"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-primary/20 to-transparent" />
              </div>

              {/* Floating Cards */}
              <div className="absolute -bottom-6 -left-6 bg-card p-4 rounded-xl shadow-lg border border-border hidden md:block">
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <Shield className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <div className="font-semibold">安全保障</div>
                    <div className="text-sm text-muted-foreground">实名认证</div>
                  </div>
                </div>
              </div>

              <div className="absolute -top-6 -right-6 bg-card p-4 rounded-xl shadow-lg border border-border hidden md:block">
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <TrendingUp className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <div className="font-semibold">智能匹配</div>
                    <div className="text-sm text-muted-foreground">AI推荐</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Decorative Elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl -z-10" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl -z-10" />
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="font-serif text-3xl md:text-4xl font-bold mb-4">为什么选择 HouseFinder</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              我们提供最专业的租房服务，让您的找房之旅更加轻松愉快
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-card p-8 rounded-xl shadow-sm border border-border hover:shadow-md transition-shadow">
              <div className="h-14 w-14 rounded-lg bg-primary/10 flex items-center justify-center mb-6">
                <MapPin className="h-7 w-7 text-primary" />
              </div>
              <h3 className="font-semibold text-xl mb-3">精准定位</h3>
              <p className="text-muted-foreground leading-relaxed">
                根据您的工作地点、学校位置等需求，智能推荐最合适的房源位置
              </p>
            </div>

            <div className="bg-card p-8 rounded-xl shadow-sm border border-border hover:shadow-md transition-shadow">
              <div className="h-14 w-14 rounded-lg bg-primary/10 flex items-center justify-center mb-6">
                <Shield className="h-7 w-7 text-primary" />
              </div>
              <h3 className="font-semibold text-xl mb-3">安全可靠</h3>
              <p className="text-muted-foreground leading-relaxed">
                所有房源经过严格审核，房东实名认证，保障您的租房安全
              </p>
            </div>

            <div className="bg-card p-8 rounded-xl shadow-sm border border-border hover:shadow-md transition-shadow">
              <div className="h-14 w-14 rounded-lg bg-primary/10 flex items-center justify-center mb-6">
                <TrendingUp className="h-7 w-7 text-primary" />
              </div>
              <h3 className="font-semibold text-xl mb-3">智能推荐</h3>
              <p className="text-muted-foreground leading-relaxed">
                AI算法分析您的需求，为您推荐最匹配的房源，节省找房时间
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
