import { SiteHeader } from "@/components/site-header"
import { HeroSection } from "@/components/hero-section"
import { FeaturedBooks } from "@/components/featured-books"
import { CategoriesSection } from "@/components/categories-section"
import { StorySection } from "@/components/story-section"
import { NewsletterSection } from "@/components/newsletter-section"
import { SiteFooter } from "@/components/site-footer"

export default function Page() {
  return (
    <main className="min-h-screen bg-background">
      <SiteHeader />
      <HeroSection />
      <FeaturedBooks />
      <CategoriesSection />
      <StorySection />
      <NewsletterSection />
      <SiteFooter />
    </main>
  )
}
