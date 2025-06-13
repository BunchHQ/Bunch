<script lang="ts">
import type { Snippet } from "svelte"
import type { ClassValue } from "svelte/elements"

interface ButtonProps {
  border?: "primary" | "dotted" | "none"
  bg?: "creme" | "primary" | "none"
  color?: "primary" | "white" | "creme" | "light"
  children: Snippet
  innerClass?: ClassValue
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
    "text-nowrap rounded-xl",
    {
      "border-bunch-primary-dark border-4": border === "primary",
    },
    "w-min",
    props.class,
  ]}
>
  <button
    class={[
      "font-bunch h-full cursor-pointer rounded-[calc(theme(borderRadius.xl)-4px)] px-2 py-1 pb-2 font-medium tracking-tight transition-colors duration-75 md:px-6",
      {
        "bg-bunch-accent-cream hover:bg-bunch-accent-blue hover:text-bunch-accent-cream active:bg-bunch-primary-darker":
          bg === "creme",
        "bg-bunch-primary-dark dark:hover:bg-bunch-primary-darker hover:bg-bunch-primary dark:active:bg-bunch-secondary active:bg-bunch-primary-darker":
          bg === "primary",
        "hover:bg-bunch-primary-dark active:bg-bunch-primary-dark ring-bunch-primary-darker mx-1 my-1 rounded-lg ring-0 active:ring-2":
          bg === "none",
        "text-bunch-accent-blue": color === "primary",
        "text-white": color === "white",
        "text-bunch-accent-cream": color === "creme",
        "text-bunch-text-dark": color === "light",
        "border-bunch-primary-darker border": border === "primary",
        "outline-bunch-text-light dark:outline-bunch-text-dark outline-5 outline-dashed -outline-offset-2":
          border === "dotted",
      },
      props.innerClass,
    ]}
  >
    {@render children()}
  </button>
</span>
