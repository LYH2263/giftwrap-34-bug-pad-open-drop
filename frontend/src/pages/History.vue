<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const err = ref('')

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function padTag(r) {
  if (!r.pad_enabled) return '防压垫关'
  return `垫 ${r.pad_pct ?? r.result?.pad_pct}%`
}
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="lede">算纸页「写入用纸档」后的落库结果。百分比、面积与叠乘顺序均钉住写入时口径，列表与详情同值，不随后续默认值重抬。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/history/${r.id}`">
          {{ r.box_name }} <span class="meta">#{{ r.id }}</span>
        </router-link>
        <span class="meta">
          {{ r.result?.paper_m2 ?? '—' }} m² · {{ padTag(r) }}
        </span>
      </li>
    </ul>
  </div>
</template>
