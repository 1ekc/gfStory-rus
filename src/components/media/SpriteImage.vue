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

// --- Эффект ряби (scan) через canvas ---
const rippleEnabled = computed(() => props.sprite.effects?.includes('scan'));

const imgRef = ref<HTMLImageElement | null>(null);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const frameForegroundRef = ref<HTMLDivElement | null>(null);
const frameBackgroundRef = ref<HTMLDivElement | null>(null);

let animationFrame: number | null = null;
let originalData: Uint8ClampedArray | null = null;
let imageLoaded = false;

const stopAnimation = () => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
    animationFrame = null;
  }
  originalData = null; // сброс для возможного перезапуска
};

const startAnimation = () => {
  if (!rippleEnabled.value || !canvasRef.value || !imgRef.value || !props.sprite.image) return;

  const canvas = canvasRef.value;
  const ctx = canvas.getContext('2d', { alpha: true, willReadFrequently: true });
  if (!ctx) return;

  // Устанавливаем правильные физические размеры canvas
  const imgElement = imgRef.value;
  const w = imgElement.clientWidth;
  const h = imgElement.clientHeight;
  canvas.width = w;
  canvas.height = h;

  // Рисуем изображение и сохраняем исходные пиксели
  ctx.drawImage(props.sprite.image, 0, 0, w, h);
  const imageData = ctx.getImageData(0, 0, w, h);
  originalData = imageData.data;

  // Параметры анимации (как в последнем рабочем тесте)
  const barHeight = 5;
  const maxShift = 10;
  const speed = 2.5;
  const phases = [0, -h/3, -2*h/3];

  let offset = 0;

  const animate = () => {
    offset = (offset + speed) % h;

    const newImageData = ctx.createImageData(w, h);
    const newData = newImageData.data;
    newData.set(originalData!);

    for (let i = 0; i < 3; i++) {
      let centerY = (phases[i] + offset + h) % h;
      let y0 = centerY - barHeight / 2;

      for (let j = -1; j <= 1; j++) {
        let yStart = y0 + j * h;
        let yEnd = yStart + barHeight;
        let yMin = Math.max(0, Math.floor(yStart));
        let yMax = Math.min(h, Math.ceil(yEnd));

        for (let y = yMin; y < yMax; y++) {
          let dist = Math.abs(y - centerY);
          let intensity = 1 - dist / (barHeight / 2);
          if (intensity < 0) intensity = 0;
          let shift = Math.round(intensity * maxShift);

          for (let x = 0; x < w; x++) {
            let srcX = x - shift;
            if (srcX < 0) srcX = 0;
            if (srcX >= w) srcX = w - 1;
            let srcIdx = (y * w + srcX) * 4;
            let dstIdx = (y * w + x) * 4;
            newData[dstIdx] = originalData![srcIdx];
            newData[dstIdx + 1] = originalData![srcIdx + 1];
            newData[dstIdx + 2] = originalData![srcIdx + 2];
            newData[dstIdx + 3] = originalData![srcIdx + 3];
          }
        }
      }
    }

    ctx.putImageData(newImageData, 0, 0);

    // Рисуем визуальные полосы поверх
    ctx.fillStyle = '#0ff3';
    ctx.shadowColor = '#0ff3';
    ctx.shadowBlur = 8;
    for (let i = 0; i < 3; i++) {
      let centerY = (phases[i] + offset + h) % h;
      let y0 = centerY - barHeight / 2;
      for (let j = -1; j <= 1; j++) {
        let y = y0 + j * h;
        if (y > -barHeight && y < h) {
          ctx.fillRect(0, y, w, barHeight);
        }
      }
    }

    animationFrame = requestAnimationFrame(animate);
  };

  animate();
};

// Наблюдаем за включением эффекта
watch(rippleEnabled, (enabled) => {
  if (enabled) {
    // Поднимаем z-index рамки
    if (frameForegroundRef.value) frameForegroundRef.value.style.zIndex = '10';
    if (frameBackgroundRef.value) frameBackgroundRef.value.style.zIndex = '9';

    // Скрываем оригинальное изображение
    if (imgRef.value) imgRef.value.style.opacity = '0';

    // Даём время на обновление DOM, затем запускаем анимацию
    nextTick(() => {
      startAnimation();
    });
  } else {
    // Возвращаем оригинал
    if (imgRef.value) imgRef.value.style.opacity = '1';
    stopAnimation();
  }
}, { immediate: true }); // immediate, чтобы обработать случай, когда эффект уже включён при монтировании

// При уничтожении компонента останавливаем анимацию
onUnmounted(() => {
  stopAnimation();
  window.removeEventListener('resize', updateImageProperties);
});
</script>

<template>
  <div class="sprite" :class="sprite.effects ?? []"
    :style="{ left: `${center}px` }"
  >
    <div class="sprite-frame"
      :style="{
        left: `${boxLeft}px`,
        top: `${boxTop}px`,
        width: `${boxWidth}px`,
        height: `${boxHeight}px`,
      }"
    >
      <!-- Оригинальное изображение -->
      <img ref="imgRef"
        :src="sprite.image.classList.contains('failed') ? '' : sprite.image.src"
        :style="{
          left: `${left}px`,
          top: `${top}px`,
          width: `${width}px`,
          height: `${height}px`,
          clipPath: clipPath as string,
        }"
      />

      <!-- Canvas для эффекта (виден только при наличии scan) -->
      <canvas v-if="rippleEnabled" ref="canvasRef" class="distortion-canvas"
        :style="{
          left: `${left}px`,
          top: `${top}px`,
          width: `${width}px`,
          height: `${height}px`,
          clipPath: clipPath as string,
          position: 'absolute',
          pointerEvents: 'none',
          zIndex: '5',
        }"
      ></canvas>

      <div ref="frameForeground" class="frame-foreground" v-if="framed"></div>
      <div ref="frameBackground" class="frame-background" v-if="framed"></div>
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

/* Стили для canvas эффекта */
.distortion-canvas {
  will-change: transform;
}
</style>