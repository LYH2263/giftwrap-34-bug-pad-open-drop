<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const boxes = ref([])
const bid = ref(1)
const out = ref(null)
const err = ref('')
const busy = ref(false)
const padEnabled = ref(false)
// 留空时由后端取系统默认垫层百分比
const padPct = ref('')

onMounted(async () => {
  try {
    boxes.value = (await getJSON('/api/boxes')).items.filter((b) => b.data_quality === 'clean')
    if (boxes.value.length) bid.value = boxes.value[0].id
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function padParams() {
  const pct = padPct.value === '' ? null : Number(padPct.value)
  return { pad_enabled: padEnabled.value, pad_pct: pct }
}

async function go(save) {
  err.value = ''
  out.value = null
  busy.value = true
  try {
    const pad = padParams()
    out.value = save
      ? await postJSON('/api/estimate', { box_id: bid.value, save: true, ...pad })
      : await getJSON(
          `/api/estimate?box_id=${bid.value}&pad_enabled=${pad.pad_enabled}` +
            (pad.pad_pct === null ? '' : `&pad_pct=${pad.pad_pct}`),
        )
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">先试算看面积与展开，确认后再写入用纸档。防压垫按「先折边再垫」口径叠乘。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
    </div>
    <div class="row pad-row">
      <label class="switch">
        <input v-model="padEnabled" type="checkbox" />
        <span>开启防压垫</span>
      </label>
      <label v-if="padEnabled" class="pct-field">
        垫层百分比
        <input v-model="padPct" type="number" min="0" step="0.5" placeholder="系统默认 %" />
        <span class="meta">%</span>
      </label>
      <span v-if="padEnabled" class="meta">顺序：先折边 → 再抬垫；丝带仍只跟基础三边</span>
    </div>
    <div class="row">
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
      <p class="stat-line">
        折边系数 × {{ out.overlap }}
        <template v-if="out.pad_enabled">
          ｜防压垫 {{ out.pad_pct }}%（{{ out.pad_order === 'overlap_first' ? '先折边再垫' : out.pad_order }}）
        </template>
        <template v-else>｜防压垫关闭</template>
      </p>
      <p class="stat-line" v-if="out.ribbon">
        {{ out.ribbon.wrap_style === 'band' ? '单绕丝带' : '十字丝带' }}约
        {{ out.ribbon.ribbon_m ?? out.ribbon }} m（只跟基础三边）
      </p>
      <p v-if="out.run_id" class="stat-line">
        已写入用纸档 #{{ out.run_id }}，
        <router-link :to="`/history/${out.run_id}`">查看钉住的详情</router-link>
      </p>
      <BoxUnfold
        :l="out.box.length"
        :w="out.box.width"
        :h="out.box.height"
        :paper-m2="out.paper_m2"
      />
    </div>
  </div>
</template>
