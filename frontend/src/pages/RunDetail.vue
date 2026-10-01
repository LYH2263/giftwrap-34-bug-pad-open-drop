<script setup>
// 面积板只读写入时钉住的 result（pinned projection）。
// 不读 open_projection 里的另一套值：列表 / 详情 / 投影同源，
// 开启防压垫时展示的就是含垫层抬升的 paper_m2，详情不退剥回六面×折边。

import { onMounted, ref } from 'vue'
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

function orderLabel(o) {
  if (o === 'overlap_first') return '先折边再垫'
  if (o === 'pad_first') return '先垫再折边'
  return '—'
}
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>{{ run.box_name }} <span class="meta">#{{ run.id }}</span></h1>
      <p class="lede">以下数值为写入时钉住的结果，不随系统默认垫层百分比或默认叠乘顺序变化。开启防压垫时，面积板即含垫层抬升，与列表行显示的面积一致。</p>
      <ul class="item-list">
        <li>
          <span>最终用纸面积 paper_m2（写入钉住{{ run.pad_enabled ? '，先折边再抬垫' : '' }}）</span>
          <span class="meta"><strong>{{ run.result?.paper_m2 }}</strong> m²</span>
        </li>
        <li>
          <span>列表行面积镜像 list_paper_m2（须与上者一致）</span>
          <span class="meta">{{ run.result?.list_paper_m2 ?? run.open_projection?.list_paper_m2 ?? '—' }} m²</span>
        </li>
        <li>
          <span>防压垫开关 pad_enabled</span>
          <span class="meta">{{ run.pad_enabled ? '开启' : '关闭' }}</span>
        </li>
        <li>
          <span>垫层百分比 pad_pct</span>
          <span class="meta">{{ run.pad_enabled ? `${run.pad_pct}%` : '—' }}</span>
        </li>
        <li>
          <span>叠乘顺序 pad_order</span>
          <span class="meta">{{ run.pad_enabled ? orderLabel(run.pad_order) : '—' }}</span>
        </li>
        <li>
          <span>折边系数 overlap</span>
          <span class="meta">{{ run.overlap }}</span>
        </li>
        <li>
          <span>展开表面积</span>
          <span class="meta">{{ run.result?.box_surface }} m²</span>
        </li>
        <li v-if="run.result?.ribbon">
          <span>丝带（只跟基础三边）</span>
          <span class="meta">{{ run.result.ribbon.ribbon_m }} m</span>
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
