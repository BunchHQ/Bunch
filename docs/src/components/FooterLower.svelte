<script lang="ts">
import Instagram from "../assets/icons/instagram.svelte"
import Twitter from "../assets/icons/twitter.svelte"
</script>

<div class="m-auto flex w-full max-w-6xl flex-col gap-2 px-16 py-16">
  <div class="flex flex-row items-center gap-2">
    <img
      src="/apple-touch-icon.png"
      alt="Bunch Logo"
      class="h-auto w-16"
      width="64"
      height="64"
    />
    <h3 class="text-bunch-text-dark font-sans text-2xl font-extrabold">
      Bunch
    </h3>
  </div>
  <p class="text-bunch-text-muted max-w-xs text-sm">
    Your all-in-one space to chat, and stay connected with your crew—no matter
    where they are
  </p>
  <div class="mt-4 flex flex-row gap-2">
    <span class="text-yellow-300">
      <Twitter width="1.5em" height="1.5em" />
    </span>
    <span class="text-yellow-300">
      <Instagram width="1.5em" height="1.5em" />
    </span>
  </div>
</div>

<hr class="text-bunch-text-muted/20" />
<p class="text-bunch-text-muted py-4 text-center text-xs">
  &copy; 2025 Bunch. All rights reserved.
</p>
