# frontend

## Vue

Components:

- [Vue](https://vuejs.org/)
- [Pinia](https://pinia.vuejs.org/)
- [Mitt](https://github.com/developit/mitt)
- [Bootstrap](https://getbootstrap.com/)
- [Popper](https://popper.js.org/)
- [Swiper](https://swiperjs.com/vue)
- [vue-i18n](https://vue-i18n.intlify.dev/guide/)
- [Video.js](https://videojs.com/):
  - Streaming [mpeg-dash (dash)](https://www.mpeg.org/standards/MPEG-DASH/)
    or [http live streaming (hls)](https://datatracker.ietf.org/doc/html/rfc8216) is already included,
  see [videojs-http-streaming](https://github.com/videojs/http-streaming)
  and [videojs-7 blog post](https://videojs.com/blog/video-js-7-is-here/)
  and [videojs-8 vhs-3 blog post](https://videojs.com/blog/videojs-8-and-vhs-3/)
- [marked](https://marked.js.org/):
  - Convert LLM response markdown into html elements
- [dompurify](https://github.com/cure53/DOMPurify):
  - Prevent XSS injection for generated LLM responses
- [prismjs](https://prismjs.com):
  - Syntax highlighting for code snippets included in LLM responses
- [katex](https://github.com/KaTeX/KaTeX):
  - Latex for TeX math rendering of TeX included in LLM responses
- [vuedraggable](https://github.com/SortableJS/Vue.Draggable):
  - Drag and drop, version 4.1.0 required
- [SortableJS](https://github.com/SortableJS/Sortable):
  - Dependency of vuedraggable
- [d3js](https://d3js.org/):
  - Visualization
- [d3-cloud](https://github.com/jasondavies/d3-cloud)
  - Keywords visualization as word cloud

Testing:

- [Vitest](https://vitest.dev/)
  - [Instructions](https://vuejs.org/guide/scaling-up/testing.html#unit-testing)

- [Cypress](https://www.cypress.io/)
  - [Instructions](https://vuejs.org/guide/scaling-up/testing.html#e2e-testing)

Formatting:

- [Prettier](https://prettier.io/)
  - [Editor Integration](https://prettier.io/docs/en/editors.html)

### Initial Setup

```bash
npm init vite@latest vue --template vue-ts
```

Output with used settings:

```bash
> npx
> create-vite vue vue-ts

✔ Select a framework: › Vue
✔ Select a variant: › Customize with create-vue ↗
Need to install the following packages:
create-vue@3.12.2
Ok to proceed? (y) y


> npx
> create-vue vue


Vue.js - The Progressive JavaScript Framework

✔ Add TypeScript? … No / Yes
✔ Add JSX Support? … No / Yes
✔ Add Vue Router for Single Page Application development? … No / Yes
✔ Add Pinia for state management? … No / Yes
✔ Add Vitest for Unit Testing? … No / Yes
✔ Add an End-to-End Testing Solution? › Cypress
✔ Add ESLint for code quality? › Yes
✔ Add Prettier for code formatting? … No / Yes

cd vue
npm install
npm install axios
npm install mitt
npm install bootstrap
npm install @popperjs/core
npm install swiper
npm install vue-i18n
npm install --save-dev video.js
npm install --save-dev @types/video.js
npm install --save videojs-contrib-quality-levels
npm install --save videojs-hotkeys
npm install --save-dev --save-exact prettier
npm install marked
npm install dompurify
npm install prismjs
npm install katex
npm install d3
npm install d3-cloud
npm install vuedraggable@4.1.0
npm install sortablejs@1.15.6
npm install pdfjs-dist
npm run lint
npm run dev
```

### Installation for Testing

```bash
npm install vue@latest @vue/cli@latest esbuild@latest

cd vue
npm install
npm run lint
npm run dev
```
