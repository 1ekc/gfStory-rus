<script setup lang="ts">
import type { SelectLine } from '@brocatel/mdc';
import {
  nextTick, onMounted, ref, watch,
} from 'vue';

import AnimatedText from './AnimatedText.vue';
import SpriteImageView from '../media/SpriteImage.vue';
import type { SpriteImage } from '../../story/interpreter';

// eslint-disable-next-line import/no-unresolved
import circleSvg from '../../assets/circle.svg?raw';
// eslint-disable-next-line import/no-unresolved
import gfSystemSvg from '../../assets/G.F.system.svg?raw';
// eslint-disable-next-line import/no-unresolved
import boxLayerSvg from '../../assets/box-layer.svg?raw';

const boxLayerSvgUrl = `url("${
  URL.createObjectURL(new Blob([boxLayerSvg], {
    type: 'image/svg+xml',
  }))
}")`;

const props = defineProps<{
  backgroundUrl: string,
  backgroundStyle: 'contain' | 'cover' | string,
  classes: string[],
  narratorHtml: string,
  sprites: SpriteImage[],
  options: SelectLine['select'],
  remote: Set<string>,
  textHtml: string,
  textHeight?: string,
  popCharAnimationInterval?: number,

  loading?: boolean,

  history?: [string, string][];

  // Пропсы для навигации
  hasPrevStory?: boolean,
  hasNextStory?: boolean,
}>();

const emit = defineEmits<{
  (event: 'click'): void,
  (event: 'choose', option: number): void,
  (event: 'animation-finished'): void,
  // События навигации
  (event: 'prev-story'): void,
  (event: 'next-story'): void,
}>();

const textBox = ref<HTMLDivElement>();
const textAnimating = ref(false);

watch(() => textAnimating.value, (animating) => {
  if (!animating) {
    emit('animation-finished');
  }
});

let clickX = 0;
let clickY = 0;
function setDownPosition(event: MouseEvent) {
  clickX = event.clientX;
  clickY = event.clientY;
}
function next() {
  if (textAnimating.value) {
    textAnimating.value = false;
  } else {
    emit('click');
  }
}
function emitClick(event: MouseEvent) {
  if ((event.target as HTMLElement).nodeName === 'BUTTON') {
    return;
  }
  const dx = clickX - event.clientX;
  const dy = clickY - event.clientY;
  const distance = dx * dx + dy * dy;
  if (distance < 9) {
    next();
  }
}

const backgroundSpace = ref<HTMLDivElement>();
function computeCenter(i: number) {
  const div = backgroundSpace.value!;
  const unit = div.clientWidth / (props.sprites.length + 1);
  return (i + 1) * unit;
}

onMounted(() => {
  document.addEventListener('keypress', (e) => {
    if (props.options.length > 0) {
      return;
    }
    if (document.activeElement?.tagName === 'BODY') {
      if (e.key === 'Enter' || e.key === ' ') {
        next();
      }
    }
  });
});

watch(() => props.history, (history) => {
  if (history) {
    nextTick(() => {
      if (textBox.value) {
        textBox.value.scrollTop = textBox.value.scrollHeight;
      }
    });
  }
});
</script>

<template>
  <div class="story-background" :class="classes">
    <!-- Верхняя панель кнопок (для десктопа и мобильных) -->
    <div class="button-slot" v-show="!history">
      <!-- Слот для кнопок из родительского компонента (Меню, Текст, История, Авто) -->
      <slot></slot>

      <!-- Кнопки навигации для десктопа (скрываются на мобильных через CSS) -->
      <button
        v-if="hasPrevStory"
        @click.stop="$emit('prev-story')"
        class="nav-btn desktop-nav"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" fill="currentColor"/>
        </svg>
        <span>назад</span>
      </button>
      <button
        v-if="hasNextStory"
        @click.stop="$emit('next-story')"
        class="nav-btn desktop-nav"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" fill="currentColor"/>
        </svg>
        <span>далее</span>
      </button>
    </div>

    <!-- Мобильная навигация (только на мобильных) -->
    <div class="mobile-nav" v-if="!history && (hasPrevStory || hasNextStory)">
      <button
        v-if="hasPrevStory"
        @click.stop="$emit('prev-story')"
        @touchstart.prevent
        class="mobile-nav-btn prev"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" fill="currentColor"/>
        </svg>
        <span>назад</span>
      </button>

      <button
        v-if="hasNextStory"
        @click.stop="$emit('next-story')"
        @touchstart.prevent
        class="mobile-nav-btn next"
      >
        <span>далее</span>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" fill="currentColor"/>
        </svg>
      </button>
    </div>

    <!-- Основной контент -->
    <div class="background-image">
      <img v-show="backgroundUrl.endsWith('/') ? '' : backgroundUrl"
        :src="backgroundUrl"
        :style="(backgroundStyle == 'contain' || backgroundStyle == 'cover')
          ? { objectFit: backgroundStyle }
          : backgroundStyle
        "
      />
    </div>
    <div ref="backgroundSpace" class="story"
      @click="emitClick"
      @mousedown="setDownPosition"
    >
      <transition-group name="sprite" tag="div" class="sprites">
        <sprite-image-view
          v-for="sprite, i in sprites"
          :sprite="sprite"
          :center="computeCenter(i)"
          :container="backgroundSpace!"
          :framed="remote.has(sprite.id)"
          :key="sprite.id"
        >
        </sprite-image-view>
      </transition-group>
      <div class="options" v-show="options.length > 0 && !history">
        <button v-html="option.option.text" v-for="option in options" :key="option.option.text"
          @click="emit('choose', option.key)"
        >
        </button>
      </div>
      <div class="dialog">
        <div class="narrator-box">
          <div class="narrator" v-html="history ? '' : narratorHtml"></div>
          <div class="narrator-corner"></div>
        </div>
        <div ref="textBox" class="text" :style="{ height: textHeight }">
          <animated-text v-show="!history" :html="textHtml" :duration-ms="popCharAnimationInterval"
            v-model:animating="textAnimating">
          </animated-text>
          <div v-if="history">
            <table class="history-lines">
              <tr v-for="line, i in history!" :key="i">
                <td v-html="line[0]"></td>
                <td v-html="line[1]"></td>
              </tr>
            </table>
          </div>
        </div>
        <div class="corner">
          <span class="loaded-circle" v-html="circleSvg" v-show="!textAnimating" />
          <span v-html="gfSystemSvg" />
        </div>
      </div>
    </div>
    <div v-if="loading" class="loading-spinner" v-html="circleSvg" />
  </div>
</template>

<style>
@import url('https://fonts.font.im/css2?family=Noto+Sans+SC&display=swap');

/* ========== ОСНОВНЫЕ СТИЛИ ========== */
.story-background .button-slot {
  position: absolute;
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-content: center;
  z-index: 3;
  margin: 0.5em 1.2em 0.5em 1.2em;
}

.story-background .button-slot button {
  color: white;
  background-color: #0000;
  border: 1px solid #fff8;
  border-radius: 3px;
  width: 60px;
  height: 45px;
  position: relative;
  filter: drop-shadow(1px 1px 1px #fff8);
  cursor: pointer;
}

.story-background .button-slot button.toggled {
  color: orange;
  border: 1px solid orange;
  box-shadow: 0 0 5px orange;
}

.story-background .button-slot button:not(:first-child) {
  margin-left: 1em;
}

.story-background .button-slot button:hover {
  box-shadow: 0 0 3px white;
}

.story-background .button-slot button:active {
  box-shadow: 0 0 3px white inset;
}

.story-background .button-slot button > svg {
  position: absolute;
  left: 0;
  top: 0;
  width: 30px;
  height: 30px;
}

.story-background .button-slot button > span {
  position: absolute;
  right: 0;
  bottom: 0;
  padding-right: 3px;
  font-size: 0.8em;
}

.story-background .background-image,
.story-background > .background-image > img {
  position: absolute;
  z-index: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.story-background > .background-image > img[src=""] {
  opacity: 0;
}

.story-background, .story {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  filter: drop-shadow(1px 1px 3px black);
  z-index: 2;
}

.sprites {
  --box-border-image-source: v-bind(boxLayerSvgUrl);
}

.story .options {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: absolute;
  width: 100%;
  height: calc(100% - 10em);
  z-index: 3;
  filter: drop-shadow(1px 1px 2px #000);
}

.story .options button {
  position: relative;
  display: block;
  margin: 5px;
  padding: 0.8em;
  line-height: 1em;
  width: 75%;
  max-width: 42em;
  background-color: #0006;
  color: white;
  border: 1px solid #fdb300c0;
  cursor: pointer;
}

.story .options button::before {
  position: absolute;
  content: "";
  text-align: left;
  width: 5px;
  height: 5px;
  left: 5px;
  top: 5px;
  background-color: #fdb300c0;
}

.story .options button:hover {
  background-color: #000a;
}

.story .options button:active {
  background-color: #000f;
}

.dialog {
  position: absolute;
  bottom: 0;
  min-width: 300px;
  min-height: 6em;
  margin: auto;
  margin-bottom: 2em;
  width: calc(100% - 2em);
  max-width: 42em;
  left: 0;
  right: 0;
  z-index: 10;

  border: 1.5px solid #ccca;
  box-shadow: inset 0 0 1px black;
  background-image: radial-gradient(#ccc8 0, #000a 0.6px);
  background-size: 4px 4px;
  clip-path: polygon(0 0, 0 100%, 100% 100%, 100% 18px, 258px 18px, 240px 0);

  font-family: 'Noto Sans SC', sans-serif;
  color: white;
}

.dialog .corner {
  position: absolute;
  right: 0;
  bottom: 0;
  padding: 0 7px 0 0;
}

@media (max-height: 20rem) {
  .dialog {
    font-size: 0.8em;
  }
}

.dialog .text {
  font-size: 1.1em;
  margin: 0.5em 1.2em 1.2em 1.2em;
  word-wrap: break-word;
  overflow-y: auto;
  height: 5em;
  transition: height 0.2s;
}

.dialog .text p {
  margin: 0;
}

.dialog .text table.history-lines > tr > td:first-child {
  padding-right: 1em;
  vertical-align: top;
}

.loaded-circle svg {
  display: block;
  margin-left: auto;
  margin-right: 6px;
  width: 12px;
  height: 12px;
}

.narrator-box {
  height: 24px;
}

.narrator-box .narrator {
  display: inline-block;
  height: 24px;
  vertical-align: top;
}

.narrator-box .narrator span {
  font-size: 1.2em;
  margin-left: 1em;
}

.narrator-box .narrator-corner {
  display: inline-block;
  position: absolute;
  top: 0;
  right: 0;
  height: 24px;
  width: calc(100% - 238px);
  background: linear-gradient(0.25turn, #ccca 0, #ccca 18px, #fdb300c0 19px);
  clip-path: polygon(0 0, 25px 25px, 100% 25px, 100% 0);
  box-shadow: 0 0 2px black;
}

@keyframes loading-spin {
  from { transform: rotate(0); }
  50% { transform: rotate(180deg); }
  to { transform: rotate(360deg); }
}

.story-background .loading-spinner {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 4em;
  height: 4em;
  z-index: 10;
  margin: 1em
}

.story-background .loading-spinner svg {
  width: 100%;
  height: 100%;
  animation: loading-spin 4s linear infinite;
}

/* Эффекты */
.night.story-background .background-image {
  background-color: #00f8;
}

.night.story-background .background-image > img {
  mix-blend-mode: multiply;
}

.story-background .background-image {
  transition: 0.5s opacity;
}

.blank.story-background .background-image {
  opacity: 0;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fade-in.story-background .background-image,
.fade-in.story-background .sprites {
  animation: fade-in 1s linear 0s 1;
}

/* ========== МОБИЛЬНАЯ АДАПТАЦИЯ ========== */
@media (max-width: 768px) {
  /* Скрываем десктопные кнопки навигации */
  .desktop-nav {
    display: none !important;
  }

  /* Адаптируем верхние кнопки для мобильных */
  .story-background .button-slot {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    margin: 0;
    padding: 8px 10px;
    background: rgba(0, 0, 0, 0.9);
    backdrop-filter: blur(10px);
    z-index: 1000;
    flex-wrap: wrap;
    justify-content: flex-start;
    border-bottom: 1px solid rgba(255, 215, 0, 0.3);
  }

  .story-background .button-slot button {
    width: 50px;
    height: 40px;
    margin: 0 4px !important;
    background: rgba(30, 30, 30, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .story-background .button-slot button > svg {
    width: 24px;
    height: 24px;
  }

  .story-background .button-slot button > span {
    font-size: 0.7em;
    padding-right: 2px;
  }

  /* Специально для кнопки Авто и её ползунка */
  .auto-speed {
    margin-left: 5px;
    height: 40px;
    width: 70px;
  }

  /* Добавляем отступ для контента, чтобы не перекрывать кнопками */
  .story {
    padding-top: 60px !important;
    padding-bottom: 80px !important;
  }

  /* Мобильная навигация внизу */
  .mobile-nav {
    position: fixed;
    bottom: 15px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    padding: 0 15px;
    z-index: 1000;
    pointer-events: none;
  }

  .mobile-nav-btn {
    pointer-events: auto;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: rgba(30, 30, 30, 0.9);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 215, 0, 0.5);
    border-radius: 30px;
    color: white;
    font-size: 16px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    min-width: 110px;
    justify-content: center;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
  }

  .mobile-nav-btn:active {
    transform: scale(0.95);
    background: rgba(50, 50, 50, 0.9);
    border-color: gold;
  }

  .mobile-nav-btn.prev {
    margin-right: auto;
  }

  .mobile-nav-btn.next {
    margin-left: auto;
  }

  .mobile-nav-btn svg {
    width: 22px;
    height: 22px;
    fill: gold;
  }

  /* Исправление для модального окна */
  .n-drawer {
    z-index: 10000 !important;
    background-color: #1a1a1a !important;
  }

  .n-drawer-mask {
    z-index: 9999 !important;
    background-color: rgba(0, 0, 0, 0.7) !important;
  }

  .n-drawer-content {
    z-index: 10001 !important;
    background-color: #1a1a1a !important;
  }

  .n-drawer-body {
    height: 100% !important;
    overflow-y: auto !important;
    -webkit-overflow-scrolling: touch;
  }
}

/* Для очень маленьких экранов */
@media (max-width: 480px) {
  .story-background .button-slot button {
    width: 45px;
    height: 36px;
  }

  .story-background .button-slot button > svg {
    width: 20px;
    height: 20px;
  }

  .story {
    padding-top: 55px !important;
    padding-bottom: 70px !important;
  }

  .mobile-nav-btn {
    padding: 10px 16px;
    min-width: 95px;
    font-size: 14px;
  }

  .mobile-nav-btn svg {
    width: 18px;
    height: 18px;
  }
}

/* Альбомная ориентация на мобильных */
@media (max-width: 768px) and (orientation: landscape) {
  .dialog {
    max-width: 70%;
    margin-bottom: 60px;
  }

  .story {
    padding-bottom: 60px;
  }

  .mobile-nav {
    bottom: 10px;
  }

  .mobile-nav-btn {
    padding: 8px 14px;
    min-width: 90px;
    font-size: 13px;
  }
}

/* Десктоп: скрываем мобильную навигацию */
@media (min-width: 769px) {
  .mobile-nav {
    display: none;
  }
}
</style>