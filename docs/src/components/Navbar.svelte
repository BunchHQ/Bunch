<script>
import Button from "./ui/button.svelte"

const links = [
  { title: "Discover!", url: "#hero" },
  { title: "FAQ", url: "/faq" },
  { title: "Newsletter", url: "/news" },
  { title: "About Us!", url: "/about" },
]
</script>

<nav class="fixed top-8 z-10 w-full">
  <div class="m-auto flex w-max flex-row items-stretch justify-stretch gap-4">
    <div class="bg-bunch-primary-dark rounded-xl p-2">
      <div
        class="bg-bunch-primary border-bunch-primary-darker rounded-[calc(theme(borderRadius.xl)-6px)] border-2"
      >
        {#each links as link}
          <Button bg="none" border="none" color="white" class="text-lg">{link.title}</Button>
        {/each}
      </div>
    </div>
    <Button bg="creme" color="primary" class="text-2xl">Open Bunch</Button>
  </div>
</nav>
