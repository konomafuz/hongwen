<template>
  <div class="page-container">
    <div class="pricing-header">
      <h2>选择适合你的会员方案</h2>
      <p>解锁更多创作能力，让AI助你写出爆款小说</p>
    </div>
    <div class="pricing-grid">
      <el-card v-for="plan in plans" :key="plan.name" :class="['pricing-card', { featured: plan.featured }]">
        <div class="plan-name">{{ plan.label }}</div>
        <div class="plan-price">
          <span class="price">{{ plan.price }}</span>
          <span class="unit">{{ plan.unit }}</span>
        </div>
        <div class="plan-desc">{{ plan.desc }}</div>
        <el-divider />
        <ul class="plan-features">
          <li v-for="f in plan.features" :key="f">{{ f }}</li>
        </ul>
        <el-button :type="plan.featured ? 'primary' : 'default'" style="width: 100%; margin-top: 16px">
          {{ plan.cta }}
        </el-button>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
const plans = [
  {
    name: 'free', label: '免费版', price: '¥0', unit: '/永久', desc: '适合体验创作',
    features: ['1个项目', '2万字限制', '每日2章生成', '基础创作工作流'], cta: '当前使用', featured: false,
  },
  {
    name: 'vip', label: '普通会员', price: '¥29', unit: '/月', desc: '适合全职作者',
    features: ['无限项目', '无限字数', '每日50章生成', 'Word导出'], cta: '升级', featured: true,
  },
  {
    name: 'premium', label: '高级会员', price: '¥99', unit: '/月', desc: '适合专业作者',
    features: ['全部普通会员功能', '文风选择器', '知识库可视化', 'AI对话助手', '进度仪表盘', 'RAG语感检索', '热点分析', 'AI续写/润色/封面'],
    cta: '升级', featured: false,
  },
]
</script>

<style scoped>
.pricing-header { text-align: center; margin-bottom: 40px; }
.pricing-header h2 { font-size: 28px; margin-bottom: 8px; }
.pricing-header p { color: var(--text-secondary); }
.pricing-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; max-width: 960px; margin: 0 auto; }
.pricing-card { text-align: center; }
.pricing-card.featured { border: 2px solid var(--primary-color); transform: scale(1.05); }
.plan-name { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
.plan-price { margin-bottom: 8px; }
.price { font-size: 36px; font-weight: bold; color: var(--primary-color); }
.unit { color: var(--text-secondary); font-size: 14px; }
.plan-desc { color: var(--text-secondary); font-size: 13px; margin-bottom: 16px; }
.plan-features { list-style: none; padding: 0; text-align: left; }
.plan-features li { padding: 6px 0; color: var(--text-regular); }
.plan-features li::before { content: '✓ '; color: var(--success-color); font-weight: bold; }
</style>