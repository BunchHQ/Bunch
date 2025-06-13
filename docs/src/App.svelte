<script lang="ts">
import { onMount } from "svelte"
import { circOut } from "svelte/easing"
import { blur } from "svelte/transition"
import BottomDivider from "./components/BottomDivider.svelte"
import FooterLower from "./components/FooterLower.svelte"
import FooterUpper from "./components/FooterUpper.svelte"
import Hero from "./components/Hero.svelte"
import Navbar from "./components/Navbar.svelte"
import WavyDivider from "./components/WavyDivider.svelte"

let mounted = false
onMount(() => {
  mounted = true
})
</script>

<svelte:head>
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
  <link
    rel="apple-touch-icon"
    sizes="180x180"
    href="/apple-touch-icon-light.png"
    media="(prefers-color-scheme: light)"
  />
  <link
    rel="apple-touch-icon"
    sizes="180x180"
    href="/apple-touch-icon-dark.png"
    media="(prefers-color-scheme: dark)"
  />

  <link
    rel="icon"
    type="image/png"
    sizes="32x32"
    href="/favicon-32x32-dark.png"
    media="(prefers-color-scheme: dark)"
  />
  <link
    rel="icon"
    type="image/png"
    sizes="32x32"
    href="/favicon-32x32-light.png"
    media="(prefers-color-scheme: light)"
  />

  <link
    rel="icon"
    type="image/png"
    sizes="16x16"
    href="/favicon-16x16-dark.png"
    media="(prefers-color-scheme: dark)"
  />
  <link
    rel="icon"
    type="image/png"
    sizes="16x16"
    href="/favicon-16x16-light.png"
    media="(prefers-color-scheme: light)"
  />

  <!-- Default favicon (for browsers that don't support media queries in link tags (aka firefox)) -->
  <link rel="icon" href="/favicon.ico" type="image/x-icon" />
  <link
    rel="icon"
    type="image/x-icon"
    href="/favicon-light.ico"
    media="(prefers-color-scheme: light)"
  />
  <link
    rel="icon"
    type="image/x-icon"
    href="/favicon-dark.ico"
    media="(prefers-color-scheme: dark)"
  />

  <link rel="manifest" href="/site.webmanifest" />

  <title>Bunch!</title>
</svelte:head>

<main
  class="bg-bunch-accent-blue dark:bg-bunch-secondary-dark h-max min-h-svh w-full overflow-x-hidden overflow-y-clip"
>
  <Navbar />

  <div class="relative m-auto max-w-6xl">
    {#if mounted}
      <img
        src="/squirly-arrow.svg"
        alt="Arrow pointing to Bunch"
        width="200"
        class="absolute -left-12 top-12 w-52 rotate-[24deg] select-none invert md:left-10 md:rotate-0 dark:invert-0"
        transition:blur={{ delay: 600, easing: circOut }}
      />
      <img
        src="/bunch_mascot_hero.webp"
        alt="Bunch's Mascot"
        class="absolute right-0 top-32 w-48 select-none md:right-4 md:top-16 md:w-96"
        width="384"
        height="485"
        transition:blur={{ delay: 300, easing: circOut }}
      />
    {/if}
  </div>

  <div
    class="bg-bunch-accent-cream dark:from-bunch-secondary-dark dark:to-bunch-secondary m-auto flex h-full w-full flex-col items-center bg-gradient-to-b dark:bg-gradient-to-b dark:to-50%"
  >
    <Hero />
  </div>

  <!-- wavy divider -->
  <WavyDivider colorClass="fill-bunch-accent-cream dark:fill-bunch-secondary" />

  <!-- app demo section -->
  <div class="m-auto flex h-full max-w-6xl flex-col items-center">
    <img
      src="/bunch_window.webp"
      alt="Bunch App's Main Window"
      width="900"
      height="530"
      class="h-auto w-full"
    />

    <p
      class="font-bunch text-glow w-3/4 text-center text-xl text-white md:text-2xl"
    >
      Your all-in-one space to chat, and stay connected with your crew—no matter
      where they are!
    </p>
  </div>

  <!-- wavy divider -->
  <WavyDivider
    colorClass="fill-bunch-primary-darker dark:fill-bunch-secondary"
    orientation="up"
  />

  <!-- Footer -->
  <div
    class="bg-bunch-primary-darker dark:bg-bunch-secondary m-auto flex h-full w-full flex-col items-center"
  >
    <FooterUpper />
  </div>

  <div
    class="bg-bunch-secondary dark:bg-bunch-secondary-dark m-auto h-full w-full"
  >
    <FooterLower />
  </div>

  <div class="bg-bunch-accent-cream h-full w-full">
    <BottomDivider />
    <div
      class="m-auto flex w-full max-w-7xl flex-col items-center justify-center pt-16"
    >
      <img
        src="/bunch_title.webp"
        alt="Bunch's title text"
        class="w-72 translate-y-7 select-none md:w-[36rem]"
        width="576"
        height="168"
      />
      <img
        src="/bunch_mascot_footer_peek.webp"
        alt="Bunch's Mascot Peeking"
        class="z-[5] w-64 select-none md:w-80"
        width="320"
        height="320"
      />
    </div>
  </div>
</main>
