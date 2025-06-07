<script>
import { circOut } from "svelte/easing"
import { fly } from "svelte/transition"
import Button from "./ui/button.svelte"

const links = [
  { title: "Discover!", url: "#hero" },
  { title: "FAQ", url: "/faq" },
  { title: "Newsletter", url: "/news" },
  { title: "About Us!", url: "/about" },
]
</script>

<nav class="fixed top-8 z-10 w-full" transition:fly={{y: -100, delay: 200, opacity: 0, easing: circOut}}>
  <div class="m-auto flex w-max flex-row items-stretch justify-stretch gap-4">
    <div class="bg-bunch-primary-dark rounded-xl p-[0.25rem] shadow-2xl">
      <div
        class="bg-bunch-primary border-bunch-primary-darker rounded-[calc(theme(borderRadius.xl)-4px)] border-2"
      >
        {#each links as link}
          <Button bg="none" border="none" color="white" class="text-lg">{link.title}</Button>
        {/each}
      </div>
    </div>
    <Button bg="creme" color="primary" class="text-2xl shadow-xl">Open Bunch</Button>
  </div>
</nav>
