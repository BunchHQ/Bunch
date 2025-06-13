<script>
import Button from "./ui/button.svelte"
</script>

<div
  class="relative grid max-w-full md:max-w-7xl md:grid-cols-[1fr_0.8fr_1fr] md:grid-rows-1 md:px-4"
>
  <img
    src="/bunch_footer_line.webp"
    alt="Footer line graphic"
    class="absolute left-1/4 w-48 rotate-[58deg] select-none opacity-75 md:left-1/3 md:w-56 md:rotate-0"
  />

  <div class="flex flex-col items-start justify-end gap-4 px-8 md:gap-2">
    <div class="space-y-1">
      <h2 class="text-glow text-4xl font-bold text-white">Discover!</h2>
      <p class="font-bunch text-bunch-text-dark text-lg">
        Whether you're into gaming, music, study groups, or just chill
        convos—there’s a Bunch for you.
      </p>
    </div>
    <span></span>
    <Button class="w-full" innerClass="w-full md:text-2xl text-xl px-4"
      >Browse Public Bunches</Button
    >
    <img
      src="/bunch_mascot_discover.webp"
      alt="Bunch Mascot thumb's up"
      class="h-auto w-32 select-none md:ms-8"
      width="128"
      height="148"
    />
  </div>

  <img
    src="/bunch_mascot_start_jump.webp"
    alt="Bunch Mascot thumb's up"
    class="me-8 h-auto w-40 select-none self-start justify-self-end md:me-0"
    width="160"
    height="186"
  />

  <div class="flex flex-col items-center justify-between gap-16 px-8 pb-16">
    <div class="space-y-1">
      <h2 class="text-glow text-center text-4xl font-bold text-white">
        Start Your Very Own Bunch
      </h2>
      <p class="font-bunch text-bunch-text-dark text-center text-lg">
        Create a space that’s truly yours. Set the vibe, invite your crew.
        You’re in control of how you connect.
      </p>
    </div>
    <Button class="w-full" innerClass="w-full text-2xl px-4 button-glow"
      >Create New Bunch</Button
    >
    <img
      src="/bunch_footer_dot_grid.webp"
      alt="Footer decorative"
      width="900"
      height="225"
      class="h-auto w-full select-none"
    />
  </div>
</div>
