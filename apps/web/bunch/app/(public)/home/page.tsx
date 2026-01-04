"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, Chat, Shield, Lightning, Globe, Users, Command } from "@phosphor-icons/react"
import HeroInterface from "@/components/landing/HeroInterface"
import { SunIcon } from "lucide-react"
import { GlitchText } from "@/components/landing/GlitchText"

export default function HomePage() {
    return (
        <div className="flex flex-col min-h-screen">
            <section className="relative pt-32 pb-20 px-6 text-center lg:pt-48 lg:pb-32 overflow-hidden">

                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-primary/10 blur-[120px] rounded-full -z-10 opacity-50" />
                {/* <div className="absolute bottom-0 right-0 w-[800px] h-[600px] bg-primary/5 blur-[100px] rounded-full -z-10" /> */}

                <div className="mx-auto max-w-5xl space-y-8 relative z-10">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-muted/50 border backdrop-blur-sm text-sm font-medium mb-4 hover:bg-muted transition-colors cursor-default">
                        <SunIcon className="w-4 h-4 text-yellow-500" />
                        <span>Public Beta Now Live!</span>
                    </div>

                    <h1 className="text-5xl md:text-6xl lg:text-8xl font-extrabold tracking-tight text-foreground">
                        Your <GlitchText text="Team" hoverText="Bunch" /><br />
                        <span className="text-primary">Supercharged</span>
                    </h1>

                    <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                        The modern communication platform designed for teams that move fast.
                        Real-time messaging, threads, and powerful integrations in one place.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
                        <Button size="lg" className="h-14 px-8 text-lg rounded-full shadow-lg shadow-primary/20 transition-transform hover:scale-105" asChild>
                            <Link href="/auth/sign-up">Get Started Free <ArrowRight className="ml-2 w-5 h-5" /></Link>
                        </Button>
                        <Button size="lg" variant="outline" className="h-14 px-8 text-lg rounded-full bg-background/50 backdrop-blur-sm hover:bg-background transition-transform hover:scale-105" asChild>
                            <Link href="/browse">Browse Bunches</Link>
                        </Button>
                    </div>
                </div>

                <div className="mt-16 mx-auto w-full max-w-6xl">
                    <HeroInterface />
                </div>
            </section>



            {/* Features Grid */}
            <section className="py-32 px-6">
                <div className="mx-auto max-w-6xl">
                    <div className="text-center mb-20 space-y-4">
                        <h2 className="text-3xl md:text-5xl font-bold">Everything you need to sync</h2>
                        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                            Bunch provides all the tools your team needs to stay aligned and move forward efficiently.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        <FeatureCard
                            icon={Lightning}
                            title="Real-time Speed"
                            description="Engineered for zero-latency messaging. Your team stays in sync, instantly."
                        />
                        <FeatureCard
                            icon={Shield}
                            title="Secure Encrypted"
                            description="Enterprise-grade security standards with end-to-end encryption for private channels."
                        />
                        <FeatureCard
                            icon={Globe}
                            title="Universal Access"
                            description="Available on Web, iOS, and Android. Your conversations sync seamlessly across devices."
                        />
                        <FeatureCard
                            icon={Chat}
                            title="Smart Threads"
                            description="Keep discussions focused. Reply in threads to declutter your main channel view."
                        />
                        <FeatureCard
                            icon={Users}
                            title="Team Roles"
                            description="Granular permission controls for admins, moderators, and guests."
                        />
                        <FeatureCard
                            icon={Command}
                            title="Keyboard First"
                            description="Navigate the entire app without lifting your hands from the keyboard."
                        />
                    </div>
                </div>
            </section>

            {/* Stats/Big Numbers Section */}
            <section className="py-24 bg-primary text-primary-foreground">
                <div className="mx-auto max-w-7xl px-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                        <div>
                            <div className="text-5xl font-bold mb-2">10k+</div>
                            <div className="text-primary-foreground/80">Active Users</div>
                        </div>
                        <div>
                            <div className="text-5xl font-bold mb-2">50M+</div>
                            <div className="text-primary-foreground/80">Messages Sent</div>
                        </div>
                        <div>
                            <div className="text-5xl font-bold mb-2">99.9%</div>
                            <div className="text-primary-foreground/80">Uptime</div>
                        </div>
                        <div>
                            <div className="text-5xl font-bold mb-2">24/7</div>
                            <div className="text-primary-foreground/80">Support</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-32 px-6 text-center relative overflow-hidden">
                <div className="absolute inset-0 bg-muted/30 -z-10"></div>
                <div className="max-w-4xl mx-auto space-y-8">
                    <h2 className="text-4xl md:text-6xl font-bold">Ready to bunch up?</h2>
                    <p className="text-muted-foreground text-xl max-w-2xl mx-auto">
                        Join thousands of forward-thinking teams using Bunch to communicate better and ship faster.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
                        <Button size="lg" className="h-14 px-10 text-lg rounded-full" asChild>
                            <Link href="/auth/sign-up">Start for Free</Link>
                        </Button>
                        <Button size="lg" variant="ghost" className="h-14 px-10 text-lg rounded-full" asChild>
                            <Link href="/contact">Contact Sales</Link>
                        </Button>
                    </div>
                </div>
            </section>

            <footer className="py-12 px-6 border-t bg-muted/10">
                <div className="max-w-7xl mx-auto grid grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
                    <div>
                        <h3 className="font-bold mb-4">Product</h3>
                        <ul className="space-y-2 text-muted-foreground text-sm">
                            <li><Link href="#" className="hover:text-foreground">Features</Link></li>
                            <li><Link href="#" className="hover:text-foreground">Pricing</Link></li>
                            <li><Link href="#" className="hover:text-foreground">Changelog</Link></li>
                            <li><Link href="#" className="hover:text-foreground">Docs</Link></li>
                        </ul>
                    </div>
                    <div>
                        <h3 className="font-bold mb-4">Company</h3>
                        <ul className="space-y-2 text-muted-foreground text-sm">
                            <li><Link href="#" className="hover:text-foreground">About</Link></li>
                            <li><Link href="#" className="hover:text-foreground">Careers</Link></li>
                            <li><Link href="#" className="hover:text-foreground">Blog</Link></li>
                            <li><Link href="#" className="hover:text-foreground">Contact</Link></li>
                        </ul>
                    </div>
                    <div>
                        <h3 className="font-bold mb-4">Legal</h3>
                        <ul className="space-y-2 text-muted-foreground text-sm">
                            <li><Link href="#" className="hover:text-foreground">Privacy</Link></li>
                            <li><Link href="#" className="hover:text-foreground">Terms</Link></li>
                        </ul>
                    </div>
                    <div>
                        <h3 className="font-bold mb-4">Social</h3>
                        <ul className="space-y-2 text-muted-foreground text-sm">
                            <li><Link href="#" className="hover:text-foreground">Twitter</Link></li>
                            <li><Link href="#" className="hover:text-foreground">GitHub</Link></li>
                            <li><Link href="#" className="hover:text-foreground">Discord</Link></li>
                        </ul>
                    </div>
                </div>
                <div className="text-center text-muted-foreground text-sm">
                    © {new Date().getFullYear()} Bunch HQ. All rights reserved.
                </div>
            </footer>
        </div>
    )
}

function FeatureCard({ icon: Icon, title, description }: { icon: any, title: string, description: string }) {
    return (
        <div className="group p-8 rounded-2xl bg-card border hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300">
            <div className="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center text-primary mb-6 group-hover:scale-110 transition-transform">
                <Icon className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-bold mb-3">{title}</h3>
            <p className="text-muted-foreground leading-relaxed">{description}</p>
        </div>
    )
}
