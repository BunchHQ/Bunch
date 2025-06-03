<script lang="ts">
import FooterLower from "./components/FooterLower.svelte"
import FooterUpper from "./components/FooterUpper.svelte"
import Hero from "./components/Hero.svelte"
import Navbar from "./components/Navbar.svelte"
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
  class="dark:bg-bunch-secondary-dark h-max min-h-svh w-full overflow-x-hidden overflow-y-clip"
>
  <Navbar />

  <div class="relative m-auto max-w-6xl">
    <img
      src="/squirly-arrow.svg"
      alt="Arrow pointing to Bunch"
      width="200"
      class="absolute left-10 top-6 w-52"
    />
    <img
      src="/bunch_mascot_hero.webp"
      alt="Bunch's Mascot"
      class="absolute right-4 top-16 w-96"
    />
  </div>

  <div
    class="dark:bg-bunch-secondary m-auto flex h-full w-full flex-col items-center"
  >
    <Hero />
  </div>

  <!-- wavy divider -->
  <svg
    width="100%"
    height="100%"
    viewBox="0 0 1440 390"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <filter id="shadow">
        <feDropShadow dx="0" dy="-16" stdDeviation="6" flood-opacity="0.2" />
      </filter>
    </defs>
    <path
      d="M 0,400 L 0,150 C 44.26930573744046,188.67702082028507 88.53861147488092,227.35404164057016 125,220 C 161.46138852511908,212.64595835942984 190.1148598379168,159.26085425800449 223,156 C 255.8851401620832,152.73914574199551 293.00194917345175,199.60254132741179 343,206 C 392.99805082654825,212.39745867258821 455.8773434682762,178.32898043234832 500,147 C 544.1226565317238,115.67101956765168 569.4886769534438,87.08153694319498 602,102 C 634.5113230465562,116.91846305680502 674.1679487179488,175.34487179487178 716,175 C 757.8320512820512,174.65512820512822 801.8395281747612,115.53897587731787 846,114 C 890.1604718252388,112.46102412268213 934.473938583006,168.4992246958568 976,183 C 1017.526061416994,197.5007753041432 1056.264717493215,170.46412533925488 1097,168 C 1137.735282506785,165.53587466074512 1180.4671914441344,187.64427394712368 1213,202 C 1245.5328085558656,216.35572605287632 1267.8665167302474,222.95877887225035 1304,213 C 1340.1334832697526,203.04122112774965 1390.0667416348763,176.5206105638748 1440,150 L 1440,400 L 0,400 Z"
      stroke="none"
      stroke-width="0"
      fill="currentColor"
      class="fill-bunch-secondary dark:fill-bunch-secondary"
      fill-opacity="1"
      transform="rotate(-180 720 200)"
      filter="url(#shadow)"
    >
    </path>
  </svg>

  <!-- app demo section -->
  <div
    class="dark:bg-bunch-secondary-dark m-auto flex h-full max-w-6xl flex-col items-center"
  >
    <img
      src="/bunch_window.webp"
      alt="Bunch App's Main Window"
      width="900"
      height="530"
      class="h-auto w-full"
    />

    <p class="font-bunch w-3/4 text-center text-2xl text-white">
      Your all-in-one space to chat, and stay connected with your crew—no matter
      where they are!
    </p>
  </div>

  <!-- wavy divider -->
  <svg
    width="100%"
    height="100%"
    viewBox="0 0 1440 390"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <filter id="shadow">
        <feDropShadow dx="0" dy="-16" stdDeviation="6" flood-opacity="0.2" />
      </filter>
    </defs>
    <path
      d="M 0,400 L 0,150 C 44.26930573744046,188.67702082028507 88.53861147488092,227.35404164057016 125,220 C 161.46138852511908,212.64595835942984 190.1148598379168,159.26085425800449 223,156 C 255.8851401620832,152.73914574199551 293.00194917345175,199.60254132741179 343,206 C 392.99805082654825,212.39745867258821 455.8773434682762,178.32898043234832 500,147 C 544.1226565317238,115.67101956765168 569.4886769534438,87.08153694319498 602,102 C 634.5113230465562,116.91846305680502 674.1679487179488,175.34487179487178 716,175 C 757.8320512820512,174.65512820512822 801.8395281747612,115.53897587731787 846,114 C 890.1604718252388,112.46102412268213 934.473938583006,168.4992246958568 976,183 C 1017.526061416994,197.5007753041432 1056.264717493215,170.46412533925488 1097,168 C 1137.735282506785,165.53587466074512 1180.4671914441344,187.64427394712368 1213,202 C 1245.5328085558656,216.35572605287632 1267.8665167302474,222.95877887225035 1304,213 C 1340.1334832697526,203.04122112774965 1390.0667416348763,176.5206105638748 1440,150 L 1440,400 L 0,400 Z"
      stroke="none"
      stroke-width="0"
      fill="currentColor"
      class="fill-bunch-secondary dark:fill-bunch-secondary"
      fill-opacity="1"
      filter="url(#shadow)"
    >
    </path>
  </svg>

  <!-- Footer -->
  <div
    class="dark:bg-bunch-secondary m-auto flex h-full w-full flex-col items-center"
  >
    <FooterUpper />
  </div>

  <div class="dark:bg-bunch-secondary-dark m-auto h-full w-full">
    <FooterLower />
  </div>

  <div class="bg-bunch-accent-cream h-full w-full">
    <svg
      width="100%"
      height="100%"
      id="svg"
      viewBox="0 0 1430 390"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M 0,400 L 0,0 C 34.632480022500104,95.78518534315188 69.26496004500021,191.57037068630376 109,202 C 148.7350399549998,212.42962931369624 193.5726398424992,137.50370259793687 231,129 C 268.4273601575008,120.49629740206313 298.4444805850029,178.4148189219488 331,187 C 363.5555194149971,195.5851810780512 398.6494378174894,154.83702171426796 441,154 C 483.3505621825106,153.16297828573204 532.9577681450396,192.23709422097934 569,192 C 605.0422318549604,191.76290577902066 627.5194896023522,152.2146014018146 663,124 C 698.4805103976478,95.78539859818541 746.9642734455515,78.90450017176228 786,91 C 825.0357265544485,103.09549982823772 854.6234166154424,144.16739791113628 882,144 C 909.3765833845576,143.83260208886372 934.5420600926794,102.42590818369257 978,100 C 1021.4579399073206,97.57409181630743 1083.20834301384,134.12896935409344 1123,166 C 1162.79165698616,197.87103064590656 1180.6245678519606,225.05821439993372 1210,220 C 1239.3754321480394,214.94178560006628 1280.2933855783183,177.6381730461717 1322,151 C 1363.7066144216817,124.36182695382831 1406.2018898347662,108.38909341537952 1426,85 C 1445.7981101652338,61.61090658462048 1442.899055082617,30.80545329231024 1440,0 L 1440,400 L 0,400 Z"
        stroke="none"
        stroke-width="0"
        fill="currentColor"
        fill-opacity="1"
        class="dark:fill-bunch-secondary-dark"
        transform="rotate(-180 720 200)"
      >
      </path>
    </svg>
    <div
      class="m-auto flex max-w-7xl flex-col items-center justify-center pt-16"
    >
      <img
        src="/bunch_title.webp"
        alt="Bunch's title text"
        class="w-[36rem] translate-y-7"
      />
      <img
        src="/bunch_mascot_footer_peek.webp"
        alt="Bunch's Mascot Peeking"
        class="z-[5] w-80"
      />
    </div>
  </div>
</main>
