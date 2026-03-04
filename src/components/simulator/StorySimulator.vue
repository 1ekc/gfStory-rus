<script setup lang="ts">
import { micromark } from 'micromark';
import { directive, directiveHtml } from 'micromark-extension-directive';
import {
  NConfigProvider,
  NDrawer, NDrawerContent,
  NModal, NModalProvider,
  darkTheme, ruRU,
  type MenuInst,
} from 'naive-ui';
import {
  computed, onMounted, ref, watch,
} from 'vue';

import StoryList from './StoryList.vue';
import StoryTeller from '../viewer/StoryTeller.vue';
import { compileMarkdown } from '../../story/compiler';
import {
  STORY_PATH_PREFIX,
} from '../../types/assets';

const chunk = ref('');
const html = ref('');
const loading = ref(false);
const storyList = ref<{value: string, label: string}[]>([]);
const currentStoryIndex = ref(0);

async function switchStory(path: string) {
  loading.value = true;
  try {
    const markdown = await fetch(path).then((res) => res.text());
    chunk.value = await compileMarkdown(markdown);
    html.value = micromark(markdown, {
      allowDangerousHtml: true,
      extensions: [directive()],
      htmlExtensions: [directiveHtml({
        '*': function (d) {
          this.tag('<span');
          this.tag(` class="${d.name} directive"`);
          this.tag('>');
          this.raw(d.label ?? '');
          this.tag('</span>');
          return true;
        },
      })],
    });
    loading.value = false;
  } catch (e) {
    loading.value = false;
    console.error('Error loading story:', e);
  }
}

const showMenu = ref(false);
const value = ref('');
const menu = ref<MenuInst>();

// Обновление текущего индекса при смене сцены
function updateCurrentIndex(file: string) {
  const index = storyList.value.findIndex(s => s.value === file);
  if (index !== -1) {
    currentStoryIndex.value = index;
  }
}

// Переход к следующей сцене в списке
function nextStory() {
  if (currentStoryIndex.value < storyList.value.length - 1) {
    const nextIndex = currentStoryIndex.value + 1;
    value.value = storyList.value[nextIndex].value;
  }
}

// Переход к предыдущей сцене в списке
function prevStory() {
  if (currentStoryIndex.value > 0) {
    const prevIndex = currentStoryIndex.value - 1;
    value.value = storyList.value[prevIndex].value;
  }
}

function onStoryEnded() {
  // Автоматически переходим к следующей сцене
  nextStory();
}

function saveProgress(storyId: string) {
  localStorage.setItem('storyProgress', storyId);
}

watch(() => value.value, (file) => {
  updateCurrentIndex(file); // обновляем индекс
  menu.value?.showOption(file);
  const url = new URL(window.location.toString());
  if (url.searchParams.get('story') !== file) {
    url.searchParams.set('story', file);
    window.history.pushState({}, '', url);
  }
  showMenu.value = false;
  switchStory(`${STORY_PATH_PREFIX}${file}`);
  saveProgress(file);
});

function updateFromLocation() {
  const search = new URLSearchParams(window.location.search);
  const story = search.get('story');
  if (story && story !== '') {
    value.value = story;
  }
}

async function loadStoryList() {
  try {
    const response = await fetch('/stories.json');
    const data = await response.json();
    // Преобразуем данные в плоский список, если это дерево
    storyList.value = flattenStoryData(data);

    // Восстановление прогресса
    const savedProgress = localStorage.getItem('storyProgress');
    if (savedProgress && storyList.value.some(s => s.value === savedProgress)) {
      value.value = savedProgress;
    } else if (storyList.value.length > 0) {
      value.value = storyList.value[0].value;
    }
  } catch (e) {
    console.error('Error loading story list:', e);
  }
}

// Рекурсивно преобразует дерево глав в плоский список сцен
function flattenStoryData(data: any): {value: string, label: string}[] {
  const result: {value: string, label: string}[] = [];

  function traverse(items: any[]) {
    if (!Array.isArray(items)) return;

    for (const item of items) {
      // Если есть поле files — это сцена
      if (item.files && Array.isArray(item.files)) {
        for (const file of item.files) {
          if (typeof file === 'string') {
            result.push({
              value: file,
              label: item.name || file
            });
          } else if (Array.isArray(file) && file.length >= 2) {
            result.push({
              value: file[0],
              label: file[1] || item.name
            });
          }
        }
      }
      // Если есть children — рекурсивно обходим
      if (item.children && Array.isArray(item.children)) {
        traverse(item.children);
      }
      // Для корневых разделов (main, event, etc.) — обходим их содержимое
      if (typeof item === 'object' && !item.files && !item.children) {
        traverse(Object.values(item));
      }
    }
  }

  traverse([data]);
  return result;
}

const width = ref(window.innerWidth);
onMounted(() => {
  loadStoryList();
  updateFromLocation();
  window.addEventListener('popstate', () => {
    updateFromLocation();
  });
  window.addEventListener('resize', () => {
    width.value = window.innerWidth;
  });
});

const showText = ref(false);

// Вычисляем наличие предыдущей/следующей сцены
const hasPrevStory = computed(() =>
  storyList.value.length > 0 && currentStoryIndex.value > 0
);
const hasNextStory = computed(() =>
  storyList.value.length > 0 && currentStoryIndex.value < storyList.value.length - 1
);
</script>

<template>
  <n-config-provider :theme="darkTheme" :locale="ruRU">
    <n-modal-provider>
      <n-drawer
        v-model:show="showMenu" :width="Math.min(width * 0.8, 400)"
        placement="left" display-directive="show"
      >
        <n-drawer-content title="Выбор глав" :native-scrollbar="false">
          <story-list v-model:value="value" :options="storyList" set-title-when-selected />
          <slot name="footer" id="footer">
            <p>
              Это реворк оригинального сайта с сюжетом
              <a href="https://gfstory-en.pages.dev/" target="_blank">GFL</a>
              на английском.
            </p>
            <p>
              Код симулятора сюжета можно найти на
              <a href="https://github.com/gudzpoz/gfStory" target="_blank">GitHub</a>.
            </p>
          </slot>
        </n-drawer-content>
      </n-drawer>
      <story-teller
        menu-button text-button
        @menu="showMenu = true" @text="showText = true" @ended="onStoryEnded"
        :chunk="chunk"
        :loading="loading"
        :has-prev-story="hasPrevStory"
        :has-next-story="hasNextStory"
        @prev-story="prevStory"
        @next-story="nextStory"
      />
      <n-modal
        v-model:show="showText" preset="card" size="huge"
        style="max-width: 90vw; max-height: 90vh; overflow-y: auto"
      >
        <div class="plain-text" v-html="html"></div>
      </n-modal>
    </n-modal-provider>
  </n-config-provider>
</template>

<style>
/* ... существующие стили ... */
</style>