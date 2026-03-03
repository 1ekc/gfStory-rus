<script setup lang="ts">
import {
  computed, onMounted, onUnmounted, ref, watch, nextTick,
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

// --- Эффект ряби через canvas и feImage ---
const rippleEnabled = computed(() => props.sprite.effects?.includes('scan'));
const filterId = `ripple-${Math.random().toString(36).substr(2, 9)}`;
let animationFrame: number | null = null;
const canvasRef = ref<HTMLCanvasElement | null>(null);
const feImageRef = ref<SVGFEImageElement | null>(null);

// Рисование трёх полос на canvas
const drawRipple = (ctx: CanvasRenderingContext2D, width: number, height: number, offset: number) => {
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = 'black';
  ctx.fillRect(0, 0, width, height);

  const barHeight = 40;
  const gap = (height - 3 * barHeight) / 2; // распределяем равномерно

  ctx.fillStyle = 'gray';
  // Первая полоса
  let y = (gap + offset) % height;
  ctx.fillRect(0, y, width, barHeight);
  // Вторая полоса
  y = (y + barHeight + gap) % height;
  ctx.fillRect(0, y, width, barHeight);
  // Третья полоса
  y = (y + barHeight + gap) % height;
  ctx.fillRect(0, y, width, barHeight);
};

let offset = 0;
const animateRipple = () => {
  if (!rippleEnabled.value || !canvasRef.value || !feImageRef.value) return;

  const canvas = canvasRef.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // Задаём размер canvas (можно изменить для другой плотности)
  canvas.width = 100;
  canvas.height = 300;

  drawRipple(ctx, canvas.width, canvas.height, offset);
  offset = (offset + 2) % canvas.height; // скорость движения

  const dataUrl = canvas.toDataURL();
  feImageRef.value.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', dataUrl);

  animationFrame = requestAnimationFrame(animateRipple);
};

watch(rippleEnabled, (enabled) => {
  if (enabled) {
    nextTick(() => {
      offset = 0;
      animateRipple();
    });
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
    <!-- Скрытый canvas для генерации карты смещения -->
    <canvas ref="canvasRef" style="display: none;"></canvas>

    <!-- SVG-фильтр для эффекта ряби -->
    <svg style="position: absolute; width: 0; height: 0;" v-if="rippleEnabled">
      <defs>
        <filter :id="filterId" x="-20%" y="-20%" width="140%" height="140%">
          <feImage ref="feImageRef" result="displacementMap" />
          <feDisplacementMap
            in="SourceGraphic"
            in2="displacementMap"
            :scale="50"
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
.sprite.sprite-enter-from, .sprite.sprite-leave-to {
  opacity: 0;
  transform: translateX(calc(-50% - 20px));
}
.sprite {
  transition: all 0.2s ease;
  transform: translateX(-50%);
  overflow: visible;
  position: absolute;
  user-select: none;
}
.sprite .sprite-frame {
  position: absolute;
}
.sprite .sprite-frame img {
  position: absolute;
}
.sprite .sprite-frame .frame-background {
  position: relative;
  z-index: -1;
  border-image-source: var(--box-border-image-source);
  border-image-repeat: stretch;
  border-image-slice: fill 37.5% 37.5% 60% 60%;
  border-style: solid;
  border-width: 37.5px 37.5px 60px 60px;
  left: -18.15px;
  top: -5.75px;
  width: calc(100% - 73.85px);
  height: calc(100% - 68.35px);
}
.sprite .sprite-frame .frame-foreground::before {
  display: block;
  content: "";
  position: absolute;
  z-index: 2;
  left: 1px;
  top: 1px;
  width: 16px;
  height: 16px;
  background-color: #fdb300;
}
.sprite .sprite-frame .frame-foreground {
  display: block;
  content: "";
  position: absolute;
  z-index: 1;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(#ccc7 0, #0ff3 0.6px);
  background-size: 3px 3px;
  overflow: hidden;
}

.sprite.stealth {
  opacity: 0.5;
  filter: drop-shadow(0 0 5px cyan) blur(2px);
}

@supports (mask-type: luminance) {
  .sprite.stealth {
    filter: blur(1px) drop-shadow(0 0 2px cyan);
    opacity: 0.6;
  }
  .sprite.stealth .sprite-frame {
    mask-image: v-bind(url);
    mask-size: cover;
    mask-mode: luminance;
    background-color: #47f;
  }
  .sprite.stealth .sprite-frame img {
    mix-blend-mode: luminosity;
    mask-image: v-bind(url);
    mask-size: cover;
    mask-mode: luminance;
    filter: grayscale(1) brightness(0.5) contrast(5);
  }
}

.sprite img[src=""] {
  opacity: 0;
}
</style>