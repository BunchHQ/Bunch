import { ReactNode } from "react"
import { ArrowRight } from "@phosphor-icons/react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const BentoGrid = ({
    children,
    className,
}: {
    children: ReactNode
    className?: string
}) => {
    return (
        <div
            className={cn(
                "grid w-full auto-rows-[40rem] grid-cols-1 gap-3 md:grid-cols-3",
                className
            )}
        >
            {children}
        </div>
    )
}

const BentoCard = ({
    name,
    className,
    background,
    Icon,
    description,
    href,
    cta,
    graphic,
}: {
    name: string
    className?: string
    background?: ReactNode
    Icon?: any
    description: string
    href: string
    cta: string
    graphic?: ReactNode
}) => (
    <div
        key={name}
        className={cn(
            "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl h-[25rem]",
            // light styles
            "bg-background/50 border backdrop-blur-sm [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
            // dark styles
            "dark:bg-background/20 dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]",
            className
        )}
    >
        <div className="absolute inset-0 z-0 transition-opacity group-hover:opacity-100 opacity-50">{background}</div>

        {graphic && (
            <div className="relative flex-1 w-full opacity-100 group-hover:opacity-100 transition-opacity duration-500">
                {graphic}
            </div>
        )}

        <div className="pointer-events-none z-10 flex transform-gpu flex-col gap-1 p-6 transition-all duration-300 group-hover:-translate-y-10 group-hover:bg-background/20 group-hover:backdrop-blur-none bg-transparent justify-end">
            <h3 className="text-xl font-semibold text-foreground backdrop-blur-sm py-1 rounded w-fit">
                {name}
            </h3>
            <p className="max-w-lg text-muted-foreground backdrop-blur-sm py-1 rounded">{description}</p>
        </div>

        <div
            className={cn(
                "pointer-events-none absolute bottom-0 flex w-full translate-y-10 transform-gpu flex-row items-center p-4 opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100"
            )}
        >
            <Button variant="ghost" asChild size="sm" className="pointer-events-auto">
                <a href={href}>
                    {cta}
                    <ArrowRight className="ml-2 h-4 w-4" />
                </a>
            </Button>
        </div>
        <div className="pointer-events-none absolute inset-0 transform-gpu transition-all duration-300 group-hover:bg-primary/[.03]" />
    </div>
)

export { BentoCard, BentoGrid }
