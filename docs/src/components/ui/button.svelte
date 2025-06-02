<script lang="ts">
import type { Snippet } from "svelte"
import type { ClassValue } from "svelte/elements"

interface ButtonProps {
  border?: "primary" | "dotted" | "none"
  bg?: "creme" | "primary" | "none"
  color?: "primary" | "white" | "creme" | "light"
  children: Snippet
  class?: ClassValue
}
let props: ButtonProps = $props()
let {
  border = "primary",
  bg = "primary",
  color = "creme",
  children,
}: ButtonProps = props
</script>

<span
  class={[
    "h-min w-min text-nowrap rounded-xl",
    {
      "border-6 border-bunch-primary-dark": border === "primary",
    },
    props.class,
  ]}
>
  <button
    class={[
      "font-bunch h-full rounded-[calc(theme(borderRadius.xl)-6px)] px-6 py-1 pb-2 font-medium tracking-tight",
      {
        "bg-bunch-accent-creme": bg === "creme",
        "bg-bunch-primary-dark": bg === "primary",
        "text-bunch-accent-blue": color === "primary",
        "text-white": color === "white",
        "text-bunch-accent-creme": color === "creme",
        "text-bunch-text-light dark:text-bunch-text-dark": color === "light",
        "border-bunch-primary-darker border": border === "primary",
        "outline-bunch-text-light dark:outline-bunch-text-dark outline-dashed outline-4 -outline-offset-2":
          border === "dotted",
      },
    ]}
  >
    {@render children()}
  </button>
</span>
