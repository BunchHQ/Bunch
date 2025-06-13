<script>
import { circOut } from "svelte/easing"
import { blur } from "svelte/transition"
import Button from "./ui/button.svelte"
</script>

<div
  class="px-18 flex w-full max-w-6xl flex-col items-center justify-center gap-8 pt-80"
  id="hero"
>
  <Button border="dotted" color="light" class="text-xl">What's New!</Button>
  <div class="z-[5]">
    <img
      src="/bunch_title.webp"
      alt="Bunch's title text"
      class="w-[36rem]"
      width="576"
      height="168"
      transition:blur={{ delay: 100, easing: circOut }}
    />
    <h2
      class="text-bunch-primary text-[2.5rem] font-bold dark:text-white"
      transition:blur={{ delay: 400, amount: 10, duration: 500 }}
    >
      Hangout HQ for You & Your Fam!
    </h2>
  </div>
</div>
