<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'

const s = ref({})
const padDefault = ref('')
const err = ref('')
const msg = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    s.value = await getJSON('/api/settings')
    padDefault.value = s.value.pad_pct_default ?? ''
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function savePadDefault() {
  err.value = ''
  msg.value = ''
  const v = Number(padDefault.value)
  if (!Number.isFinite(v) || v < 0) {
    err.value = '垫层百分比须为非负数'
    return
  }
  busy.value = true
  try {
    s.value = await postJSON('/api/settings', { pad_pct_default: v })
    padDefault.value = s.value.pad_pct_default
    msg.value = '已更新。已落库的用纸档仍钉住各自写入时的百分比与面积，不会重抬。'
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>设置</h1>
    <p class="lede">全局参数。折边系数只读展示；默认垫层百分比可改，仅影响之后新算，不回改已写入用纸档。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-if="msg" class="stat-line" style="color: var(--ok); font-weight: 600">{{ msg }}</p>
    <ul class="item-list">
      <li>
        <span>折边系数 overlap</span>
        <span class="meta">{{ s.overlap }}</span>
      </li>
    </ul>
    <div class="row" style="margin-top: 1.25rem">
      <label class="pct-field">
        默认垫层百分比
        <input v-model="padDefault" type="number" min="0" step="0.5" />
        <span class="meta">%</span>
      </label>
      <button :disabled="busy" @click="savePadDefault">保存默认值</button>
    </div>
    <p class="stat-line">叠乘口径（引擎固定）：先折边再垫 —— 用纸面积 = 展开表面积 × 折边系数 × (1 + 垫层%/100)。</p>
  </div>
</template>
