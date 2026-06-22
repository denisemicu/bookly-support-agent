import Image from "next/image"
import { Quote } from "lucide-react"

export function StorySection() {
  return (
    <section id="story" className="scroll-mt-20 bg-primary py-16 text-primary-foreground md:py-24">
      <div className="mx-auto grid max-w-6xl items-center gap-12 px-4 md:px-6 lg:grid-cols-2">
        <div className="relative order-2 lg:order-1">
          <div className="overflow-hidden rounded-[2rem] border-4 border-primary-foreground/10 shadow-2xl">
            <Image
              src="/images/bookstore-hero.png"
              alt="A cozy reading corner inside the Bookly bookshop"
              width={640}
              height={720}
              className="h-full w-full object-cover"
            />
          </div>
        </div>

        <div className="order-1 flex flex-col gap-6 text-balance lg:order-2">
          <p className="font-serif text-lg italic text-accent">
            Once upon a shopfront
          </p>
          <h2 className="font-serif text-4xl font-semibold leading-tight tracking-tight md:text-5xl">
            A bookshop built from curiosity and candlelight
          </h2>
          <p className="text-pretty leading-relaxed text-primary-foreground/85">
            Bookly opened its little green door forty years ago, when our
            founder traded a rainy commute for a roomful of stories. We&apos;ve
            been hand-picking books, brewing pots of tea, and matching readers
            with their next favorite ever since.
          </p>
          <p className="text-pretty leading-relaxed text-primary-foreground/85">
            We believe a bookshop should feel like a warm hug — a place to
            linger, to discover, and to wander without a list. No algorithms
            here, just real people who love a good yarn.
          </p>

          <figure className="mt-2 rounded-2xl border border-primary-foreground/15 bg-primary-foreground/5 p-6">
            <Quote className="size-6 text-accent" />
            <blockquote className="mt-3 font-serif text-xl italic leading-relaxed">
              &ldquo;I came in for one book and left with three and a new friend
              behind the counter. Pure magic.&rdquo;
            </blockquote>
            <figcaption className="mt-3 text-sm text-primary-foreground/70">
              — Marguerite, regular since 2014
            </figcaption>
          </figure>
        </div>
      </div>
    </section>
  )
}
