<script setup lang="ts">
import {
  computed, onMounted, onUnmounted, ref, watch,
} from 'vue';

import type { SpriteImage } from '../../story/interpreter';

const props = defineProps<{
  sprite: SpriteImage,
  center: number,
  container: HTMLDivElement,
  framed?: boolean,
}>();

const url = computed(() => `url(${props.sprite.image.src})`);

const idealHeightRatio = 1;
const idealWHRatio = 11 / 16;
const idealCenterTop = 0.70;
const framedAdjustment = 0.6;
const framedTopPadding = 0.10;

// Функции вычисления размеров (без изменений)
function computeImageProperties() {
  const { sprite } = props;
  const { naturalWidth, naturalHeight } = sprite.image;
  const { clientHeight } = props.container;

  const idealHeight = clientHeight * idealHeightRatio;
  const idealScale = idealHeight / naturalHeight;
  const scale = idealScale * (sprite.scale > 0 ? sprite.scale : 1);

  const width = scale * naturalWidth;
  const height = scale * naturalHeight;
  const [centerX, centerY] = sprite.center;

  const centerRatio = idealCenterTop;

  if (!props.framed) {
    const left = -scale * (centerX > 0 ? centerX : naturalWidth / 2);
    const top = clientHeight * centerRatio - scale * (centerY > 0 ? centerY : naturalHeight / 2);
    return [width, height, width, height, left, top, 0, 0, 'none'];
  }

  const boxHeight = idealHeight * framedAdjustment;
  const boxWidth = boxHeight * idealWHRatio;
  const boxLeft = -boxWidth / 2;
  const top = idealHeight * framedTopPadding;
  const boxTop = clientHeight * centerRatio - idealHeight / 2 - top;
  const left = boxWidth / 2 - scale * (centerX > 0 ? centerX : naturalWidth / 2);
  return [
    boxWidth, boxHeight, width, height,
    boxLeft, boxTop, left, top,
    `polygon(${-left}px ${-top}px, ${boxWidth - left}px ${-top}px, \
${boxWidth - left}px ${boxHeight - top}px, ${-left}px ${boxHeight - top}px)`,
  ];
}

const boxWidth = ref(0);
const boxHeight = ref(0);
const width = ref(0);
const height = ref(0);
const boxLeft = ref(0);
const boxTop = ref(0);
const left = ref(0);
const top = ref(0);
const clipPath = ref('');

function updateImageProperties() {
  const properties = computeImageProperties();
  clipPath.value = properties[8] as string;
  [
    boxWidth.value, boxHeight.value, width.value, height.value,
    boxLeft.value, boxTop.value, left.value, top.value,
  ] = properties as number[];
}

updateImageProperties();
onMounted(() => window.addEventListener('resize', updateImageProperties));
onUnmounted(() => window.removeEventListener('resize', updateImageProperties));
watch(() => props.framed, updateImageProperties);

// --- SVG-фильтр для эффекта ряби ---
const rippleEnabled = computed(() => props.sprite.effects?.includes('scan'));
const filterId = `ripple-${Math.random().toString(36).substr(2, 9)}`; // уникальный ID для фильтра
let animationFrame: number | null = null;
const offset = ref(0);

// Функция для анимации смещения градиента
const animateRipple = () => {
  if (!rippleEnabled.value) return;
  offset.value = (offset.value + 2) % 100; // скорость движения полос
  const feImage = document.querySelector(`#${filterId} feImage`);
  if (feImage) {
    // Генерируем градиент с движущимися полосами
    const gradient = `linear-gradient(0deg,
      transparent 0%,
      transparent ${30 + offset.value}%,
      rgba(128,128,128,0.5) ${35 + offset.value}%,
      rgba(128,128,128,0.5) ${40 + offset.value}%,
      transparent ${45 + offset.value}%,
      transparent 100%)`;
    feImage.setAttribute('xlink:href', `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25'%3E%3Crect width='100%25' height='100%25' fill='url(%23g)' /%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='0%25' y2='100%25'%3E${gradient.replace(/#/g, '%23')}%3C/linearGradient%3E%3C/defs%3E%3C/svg%3E`);
  }
  animationFrame = requestAnimationFrame(animateRipple);
};

// Включаем/выключаем анимацию при изменении эффекта
watch(rippleEnabled, (enabled) => {
  if (enabled) {
    animateRipple();
  } else if (animationFrame) {
    cancelAnimationFrame(animationFrame);
    animationFrame = null;
  }
});

onUnmounted(() => {
  if (animationFrame) cancelAnimationFrame(animationFrame);
});
</script>

<template>
  <div class="sprite" :class="sprite.effects ?? []"
    :style="{ left: `${center}px` }"
  >
    <!-- SVG-фильтр для эффекта ряби -->
    <svg style="position: absolute; width: 0; height: 0;" v-if="rippleEnabled">
      <defs>
        <filter :id="filterId" x="-20%" y="-20%" width="140%" height="140%">
          <feImage id="displacement-map" result="displacementMap" />
          <feDisplacementMap
            in="SourceGraphic"
            in2="displacementMap"
            scale="30"
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>
      </defs>
    </svg>

    <div class="sprite-frame"
      :style="{
        left: `${boxLeft}px`,
        top: `${boxTop}px`,
        width: `${boxWidth}px`,
        height: `${boxHeight}px`,
      }"
    >
      <img
        :src="sprite.image.classList.contains('failed') ? '' : sprite.image.src"
        :style="{
          left: `${left}px`,
          top: `${top}px`,
          width: `${width}px`,
          height: `${height}px`,
          clipPath: clipPath as string,
          filter: rippleEnabled ? `url(#${filterId})` : 'none',
        }"
      />
      <div class="frame-foreground" v-if="framed"></div>
      <div class="frame-background" v-if="framed"></div>
    </div>
  </div>
</template>

<style>
/* ... все предыдущие стили остаются без изменений ... */

/* Удаляем старые стили для .scan-bar, если они есть */
.sprite.scan .scan-bar {
  display: none; /* или просто удалить из шаблона */
}
</style><script setup lang="ts">
import {
  computed, onMounted, onUnmounted, ref, watch,
} from 'vue';

import type { SpriteImage } from '../../story/interpreter';

const props = defineProps<{
  sprite: SpriteImage,
  center: number,
  container: HTMLDivElement,
  framed?: boolean,
}>();

const url = computed(() => `url(${props.sprite.image.src})`);

const idealHeightRatio = 1;
const idealWHRatio = 11 / 16;
const idealCenterTop = 0.70;
const framedAdjustment = 0.6;
const framedTopPadding = 0.10;

// Функции вычисления размеров (без изменений)
function computeImageProperties() {
  const { sprite } = props;
  const { naturalWidth, naturalHeight } = sprite.image;
  const { clientHeight } = props.container;

  const idealHeight = clientHeight * idealHeightRatio;
  const idealScale = idealHeight / naturalHeight;
  const scale = idealScale * (sprite.scale > 0 ? sprite.scale : 1);

  const width = scale * naturalWidth;
  const height = scale * naturalHeight;
  const [centerX, centerY] = sprite.center;

  const centerRatio = idealCenterTop;

  if (!props.framed) {
    const left = -scale * (centerX > 0 ? centerX : naturalWidth / 2);
    const top = clientHeight * centerRatio - scale * (centerY > 0 ? centerY : naturalHeight / 2);
    return [width, height, width, height, left, top, 0, 0, 'none'];
  }

  const boxHeight = idealHeight * framedAdjustment;
  const boxWidth = boxHeight * idealWHRatio;
  const boxLeft = -boxWidth / 2;
  const top = idealHeight * framedTopPadding;
  const boxTop = clientHeight * centerRatio - idealHeight / 2 - top;
  const left = boxWidth / 2 - scale * (centerX > 0 ? centerX : naturalWidth / 2);
  return [
    boxWidth, boxHeight, width, height,
    boxLeft, boxTop, left, top,
    `polygon(${-left}px ${-top}px, ${boxWidth - left}px ${-top}px, \
${boxWidth - left}px ${boxHeight - top}px, ${-left}px ${boxHeight - top}px)`,
  ];
}

const boxWidth = ref(0);
const boxHeight = ref(0);
const width = ref(0);
const height = ref(0);
const boxLeft = ref(0);
const boxTop = ref(0);
const left = ref(0);
const top = ref(0);
const clipPath = ref('');

function updateImageProperties() {
  const properties = computeImageProperties();
  clipPath.value = properties[8] as string;
  [
    boxWidth.value, boxHeight.value, width.value, height.value,
    boxLeft.value, boxTop.value, left.value, top.value,
  ] = properties as number[];
}

updateImageProperties();
onMounted(() => window.addEventListener('resize', updateImageProperties));
onUnmounted(() => window.removeEventListener('resize', updateImageProperties));
watch(() => props.framed, updateImageProperties);

// --- SVG-фильтр для эффекта ряби ---
const rippleEnabled = computed(() => props.sprite.effects?.includes('scan'));
const filterId = `ripple-${Math.random().toString(36).substr(2, 9)}`; // уникальный ID для фильтра
let animationFrame: number | null = null;
const offset = ref(0);

// Функция для анимации смещения градиента
const animateRipple = () => {
  if (!rippleEnabled.value) return;
  offset.value = (offset.value + 2) % 100; // скорость движения полос
  const feImage = document.querySelector(`#${filterId} feImage`);
  if (feImage) {
    // Генерируем градиент с движущимися полосами
    const gradient = `linear-gradient(0deg,
      transparent 0%,
      transparent ${30 + offset.value}%,
      rgba(128,128,128,0.5) ${35 + offset.value}%,
      rgba(128,128,128,0.5) ${40 + offset.value}%,
      transparent ${45 + offset.value}%,
      transparent 100%)`;
    feImage.setAttribute('xlink:href', `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25'%3E%3Crect width='100%25' height='100%25' fill='url(%23g)' /%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='0%25' y2='100%25'%3E${gradient.replace(/#/g, '%23')}%3C/linearGradient%3E%3C/defs%3E%3C/svg%3E`);
  }
  animationFrame = requestAnimationFrame(animateRipple);
};

// Включаем/выключаем анимацию при изменении эффекта
watch(rippleEnabled, (enabled) => {
  if (enabled) {
    animateRipple();
  } else if (animationFrame) {
    cancelAnimationFrame(animationFrame);
    animationFrame = null;
  }
});

onUnmounted(() => {
  if (animationFrame) cancelAnimationFrame(animationFrame);
});
</script>

<template>
  <div class="sprite" :class="sprite.effects ?? []"
    :style="{ left: `${center}px` }"
  >
    <!-- SVG-фильтр для эффекта ряби -->
    <svg style="position: absolute; width: 0; height: 0;" v-if="rippleEnabled">
      <defs>
        <filter :id="filterId" x="-20%" y="-20%" width="140%" height="140%">
          <feImage id="displacement-map" result="displacementMap" />
          <feDisplacementMap
            in="SourceGraphic"
            in2="displacementMap"
            scale="30"
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>
      </defs>
    </svg>

    <div class="sprite-frame"
      :style="{
        left: `${boxLeft}px`,
        top: `${boxTop}px`,
        width: `${boxWidth}px`,
        height: `${boxHeight}px`,
      }"
    >
      <img
        :src="sprite.image.classList.contains('failed') ? '' : sprite.image.src"
        :style="{
          left: `${left}px`,
          top: `${top}px`,
          width: `${width}px`,
          height: `${height}px`,
          clipPath: clipPath as string,
          filter: rippleEnabled ? `url(#${filterId})` : 'none',
        }"
      />
      <div class="frame-foreground" v-if="framed"></div>
      <div class="frame-background" v-if="framed"></div>
    </div>
  </div>
</template>

<style>
/* ... все предыдущие стили остаются без изменений ... */

/* Удаляем старые стили для .scan-bar, если они есть */
.sprite.scan .scan-bar {
  display: none; /* или просто удалить из шаблона */
}
</style>