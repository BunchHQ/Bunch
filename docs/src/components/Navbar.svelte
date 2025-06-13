<script>
import { onMount } from "svelte"
import { circOut } from "svelte/easing"
import { fly } from "svelte/transition"
import Button from "./ui/button.svelte"

const links = [
  { title: "Discover!", url: "#hero" },
  { title: "FAQ", url: "/faq" },
  { title: "Newsletter", url: "/news" },
  { title: "About Us!", url: "/about" },
]

let mounted = false
onMount(() => {
  mounted = true
})
</script>

<!-- workaround for transitions not playing in build -->
{#if mounted}
  <nav
    class="absolute top-8 z-10 w-full md:fixed"
    transition:fly={{ y: -100, opacity: 0, easing: circOut }}
  >
    <div
      class="m-auto flex w-max flex-col items-center justify-stretch gap-2 md:flex-row md:items-stretch md:gap-4"
    >
      <div
        class="bg-bunch-primary-dark justify-self-end rounded-xl p-[0.25rem] shadow-2xl"
      >
        <div
          class="bg-bunch-primary border-bunch-primary-darker border-1 rounded-[calc(theme(borderRadius.xl)-4px)] md:border-2"
        >
          {#each links as link}
            <Button
              bg="none"
              border="none"
              color="white"
              innerClass="md:text-lg">{link.title}</Button
            >
          {/each}
        </div>
      </div>
      <Button
        bg="creme"
        color="primary"
        class="justify-self-center shadow-xl md:justify-self-start"
        innerClass="md:text-2xl text-xl px-4">Open Bunch</Button
      >
    </div>
  </nav>
{/if}
