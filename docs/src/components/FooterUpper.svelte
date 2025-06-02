<script>
import Button from "./ui/button.svelte"
</script>

<div class="relative grid max-w-7xl grid-cols-[1fr_0.8fr_1fr] grid-rows-1 px-4">
  <img
    src="/bunch_footer_line.png"
    alt="Footer line graphic"
    class="absolute left-1/3 w-48"
  />

  <div class="flex flex-col items-start justify-end gap-2 px-8">
    <h2 class="text-4xl font-bold">Discover!</h2>
    <p class="font-bunch">
      Whether you're into gaming, music, study groups, or just chill
      convos—there’s a Bunch for you.
    </p>
    <span></span>
    <Button class="w-full">Browse Public Bunches</Button>
    <img
      src="/bunch_mascot_discover.png"
      alt="Bunch Mascot thumb's up"
      class="ms-8 h-auto w-32"
    />
  </div>

  <img
    src="/bunch_mascot_start_jump.png"
    alt="Bunch Mascot thumb's up"
    class="h-auto w-40 self-start justify-self-end"
  />

  <div class="flex flex-col items-center justify-between gap-16 px-8 pb-16">
    <div class="space-y-4">
      <h2 class="text-center text-4xl font-bold">Start Your Very Own Bunch</h2>
      <p class="font-bunch text-center">
        Create a space that’s truly yours. Set the vibe, invite your crew.
        You’re in control of how you connect.
      </p>
    </div>
    <Button class="w-full">Create New Bunch</Button>
    <img
      src="/bunch_footer_dot_grid.png"
      alt="Footer decorative"
      width="900"
      class="h-auto w-full"
    />
  </div>
</div>
