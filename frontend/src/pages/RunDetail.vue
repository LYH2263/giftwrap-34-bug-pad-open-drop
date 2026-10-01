<script setup>
// 详情面积板：与列表同一钉住口径，优先读 open_projection（垫开关/百分比/垫序/面积均为写入值）

import { computed, onMounted, ref } from 'vue'
import { getJSON } from '../api'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

// 钉住视图：投影、落库列、result_json 三方同值，任一处缺失都有兜底
const pinned = computed(() => {
  const r = run.value
  if (!r) return null
  const proj = r.open_projection || {}
  const res = r.result || {}
  return {
    paper_m2: proj.paper_m2 ?? res.paper_m2,
    pad_enabled: proj.pad_enabled ?? r.pad_enabled,
    pad_pct: proj.pad_pct ?? r.pad_pct ?? res.pad_pct,
    pad_order: proj.pad_order ?? r.pad_order ?? res.pad_order,
    overlap: r.overlap ?? res.overlap,
    box_surface: res.box_surface,
    ribbon: res.ribbon,
  }
})

function orderLabel(o) {
  if (o === 'overlap_first') return '先折边再垫'
  if (o === 'pad_first') return '先垫再折边'
  return '—'
}
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run && pinned">
      <h1>{{ run.box_name }} <span class="meta">#{{ run.id }}</span></h1>
      <p class="lede">以下数值为写入时钉住的结果，与列表行同口径，不随系统默认垫层百分比或默认叠乘顺序变化。</p>
      <ul class="item-list">
        <li>
          <span>最终用纸面积 paper_m2</span>
          <span class="meta"><strong>{{ pinned.paper_m2 }}</strong> m²</span>
        </li>
        <li>
          <span>防压垫开关 pad_enabled</span>
          <span class="meta">{{ pinned.pad_enabled ? '开启' : '关闭' }}</span>
        </li>
        <li>
          <span>垫层百分比 pad_pct</span>
          <span class="meta">{{ pinned.pad_enabled ? `${pinned.pad_pct}%` : '—' }}</span>
        </li>
        <li>
          <span>叠乘顺序 pad_order</span>
          <span class="meta">{{ pinned.pad_enabled ? orderLabel(pinned.pad_order) : '—' }}</span>
        </li>
        <li>
          <span>折边系数 overlap</span>
          <span class="meta">{{ pinned.overlap }}</span>
        </li>
        <li>
          <span>展开表面积</span>
          <span class="meta">{{ pinned.box_surface }} m²</span>
        </li>
        <li v-if="pinned.ribbon">
          <span>丝带（只跟基础三边）</span>
          <span class="meta">{{ pinned.ribbon.ribbon_m }} m</span>
        </li>
        <li>
          <span>写入时间</span>
          <span class="meta">{{ run.created_at }}</span>
        </li>
      </ul>
      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
        <router-link class="btn" to="/bench">去算纸台同参复算</router-link>
      </div>
    </template>
  </div>
</template>
