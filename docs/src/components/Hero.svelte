<script>
import { onMount } from "svelte"
import { circOut } from "svelte/easing"
import { blur } from "svelte/transition"
import Button from "./ui/button.svelte"

let mounted = false
onMount(() => {
  mounted = true
})
</script>

<div
  class="px-18 flex w-full max-w-6xl flex-col items-center justify-center gap-8 pt-80"
  id="hero"
>
  <Button
    border="dotted"
    color="light"
    innerClass="text-xl px-4 button-glow"
    class="z-10 md:z-0">What's New!</Button
  >
  <div class="z-[5] space-y-2 md:space-y-0">
    {#if mounted}
      <img
        src="/bunch_title.webp"
        alt="Bunch's title text"
        class="w-[36rem] select-none"
        width="576"
        height="168"
        transition:blur={{ delay: 100, easing: circOut }}
      />
      <h2
        class="text-bunch-primary text-glow text-center text-2xl font-bold md:text-[2.5rem] dark:text-white"
        transition:blur={{ delay: 400, amount: 10, duration: 500 }}
      >
        Hangout HQ for You & Your Fam!
      </h2>
    {/if}
  </div>
</div>
