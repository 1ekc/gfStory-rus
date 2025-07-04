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
  onMounted, ref, watch,
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

function onStoryEnded() {
  const currentIndex = storyList.value.findIndex(s => s.value === value.value);
  if (currentIndex >= 0 && currentIndex < storyList.value.length - 1) {
    const nextStory = storyList.value[currentIndex + 1];
    value.value = nextStory.value;
  }
}

function saveProgress(storyId: string) {
  localStorage.setItem('storyProgress', storyId);
}

watch(() => value.value, (file) => {
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
    storyList.value = await response.json();

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
#app,
.story-background {
  height: 100vh;
}

.story-heading {
  font-weight: bold;
  margin-right: 1em;
}

.n-drawer a {
  color: #63e2b7;
}

.plain-text {
  max-width: 90vw;
}

.plain-text .directive.audio::before {
  content: "BGM：";
}
.plain-text .directive.background::before {
  content: "Background: ";
}
.plain-text .directive.se::before {
  content: "SFX: ";
}
.plain-text .directive.audio::before,
.plain-text .directive.background::before,
.plain-text .directive.se::before {
  font-style: italic;
}

.plain-text .directive.classes,
.plain-text .directive.color,
.plain-text .directive.remote,
.plain-text .directive.sprites,
.plain-text pre code.language-lua {
  display: none;
}
.plain-text > p {
  margin-left: 2em;
}
.plain-text .directive.narrator:not(:empty) {
  font-size: 1.1em;
  font-weight: bold;
  margin-left: -2em;
  border-left: 2px solid orange;
  padding-left: 0.5em;
}

.plain-text > ul::before {
  content: "Settings：";
  font-weight: bold;
  font-style: italic;
  margin-left: -2em;
}

.plain-text p > code {
  font-size: 0.8em;
}
.plain-text p > code:last-child::before {
  content: "Jump to branch：";
  font-weight: bold;
  font-style: italic;
}
.plain-text p > code:first-child:not(:last-child)::before {
  content: "Branches：";
  font-weight: bold;
  font-style: italic;
  margin-left: -2em;
}
.plain-text p > code:first-child::after {
  display: block;
  content: "";
}
</style>