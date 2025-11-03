<template>
  <div class="loading-bar" />
</template>

<style scoped>
.loading-bar {
  background: var(--bar-color, var(--hans-dark-blue));
  position: absolute;
  left: 0;
  top: 0;
  z-index: 1;
  width: 100%;
  height: var(--bar-height, 0.25em);
  animation: line-across 1.5s infinite;
}

@keyframes line-across {
  0% {
    transform: translateX(-50%) scaleX(0%);
  }
  50% {
    transform: translateX(0%) scaleX(100%);
  }
  100% {
    transform: translateX(50%) scaleX(0%);
  }
}
</style>
