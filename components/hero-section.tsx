import Image from "next/image"
import { Sparkles, ArrowRight, Flame } from "lucide-react"
import { Button } from "@/components/ui/button"

export function HeroSection() {
  return (
    <section id="top" className="relative overflow-hidden">
      <div className="mx-auto grid max-w-6xl items-center gap-10 px-4 pb-16 pt-12 md:px-6 md:pb-24 md:pt-16 lg:grid-cols-2 lg:gap-12">
        <div className="flex flex-col items-start gap-6 text-balance">
          <span className="inline-flex items-center gap-2 rounded-full border border-accent/40 bg-accent/15 px-4 py-1.5 text-sm font-semibold text-accent-foreground">
            <Sparkles className="size-4" />
            A little shop full of wonder
          </span>

          <h1 className="font-serif text-5xl font-semibold leading-[1.05] tracking-tight text-foreground md:text-6xl lg:text-7xl">
            Where every book{" "}
            <span className="italic text-primary">begins a little</span> bit of
            magic
          </h1>

          <p className="max-w-md text-lg leading-relaxed text-muted-foreground">
            Welcome to Bookly — a cozy, old-fashioned bookstore tucked between
            the everyday and the extraordinary. Pull up a chair, breathe in that
            paper smell, and let us help you find your next great story.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Button
              size="lg"
              className="group rounded-full bg-primary px-7 text-base text-primary-foreground hover:bg-primary/90"
              nativeButton={false}
              render={<a href="#featured" />}
            >
              Wander the shelves
              <ArrowRight className="ml-1 size-4 transition-transform group-hover:translate-x-0.5" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="rounded-full border-primary/30 bg-transparent px-7 text-base text-primary hover:bg-secondary"
              nativeButton={false}
              render={<a href="#story" />}
            >
              Our story
            </Button>
          </div>

          <dl className="flex gap-8 pt-6">
            <div>
              <dt className="font-serif text-3xl font-semibold text-primary">
                12k+
              </dt>
              <dd className="text-sm text-muted-foreground">Stories rehomed</dd>
            </div>
            <div>
              <dt className="font-serif text-3xl font-semibold text-primary">
                40 yrs
              </dt>
              <dd className="text-sm text-muted-foreground">On Maple Lane</dd>
            </div>
            <div>
              <dt className="font-serif text-3xl font-semibold text-primary">
                ∞
              </dt>
              <dd className="text-sm text-muted-foreground">Cups of tea</dd>
            </div>
          </dl>
        </div>

        <div className="relative">
          <div className="absolute -left-6 -top-6 hidden size-24 rounded-full bg-accent/30 blur-2xl lg:block" />
          <div className="relative overflow-hidden rounded-[2rem] border-4 border-card shadow-2xl shadow-primary/20">
            <Image
              src="/images/bookstore-hero.png"
              alt="The warm, lamplit interior of the Bookly bookstore with towering shelves of books"
              width={720}
              height={820}
              priority
              className="h-full w-full object-cover"
            />
          </div>
          <div className="absolute -bottom-5 left-6 flex items-center gap-3 rounded-2xl border border-border bg-card px-4 py-3 shadow-xl md:left-10">
            <span className="flex size-9 items-center justify-center rounded-full bg-accent/20 text-accent-foreground">
              <Flame className="size-5" />
            </span>
            <p className="text-sm font-medium text-foreground">
              Open till dusk,
              <br />
              <span className="text-muted-foreground">every single day</span>
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
