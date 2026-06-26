<template>
  <div class="login-container">
    <div class="login-bg"></div>
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <div class="logo-icon">
            <span class="logo-leaf"></span>
          </div>
          <h1 class="logo-title">智慧农业管理平台</h1>
        </div>
        <p class="login-subtitle">Smart Agriculture Management Platform</p>
      </div>

      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span>演示账号: admin / Admin@123456</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: 'admin',
  password: 'Admin@123456',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await authStore.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (err) {
    ElMessage.error(err.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(0, 212, 255, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 50%, rgba(0, 230, 118, 0.06) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 0%, rgba(0, 212, 255, 0.04) 0%, transparent 50%);
}

.login-card {
  width: 420px;
  padding: 48px 40px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  position: relative;
  z-index: 1;
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.3), 0 0 80px rgba(0, 212, 255, 0.05);
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 230, 118, 0.2));
  border: 1px solid var(--accent-dim);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-leaf {
  width: 18px;
  height: 18px;
  background: var(--success);
  border-radius: 50% 0 50% 50%;
  transform: rotate(-45deg);
  box-shadow: 0 0 8px var(--success);
}

.logo-title {
  font-size: 22px;
  font-weight: bold;
  background: linear-gradient(90deg, var(--accent), var(--success));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 3px;
}

.login-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 2px;
}

.login-form :deep(.el-input__wrapper) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  box-shadow: none;
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: var(--accent-dim);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent);
  box-shadow: 0 0 6px var(--accent-dim);
}

.login-form :deep(.el-input__inner) {
  color: var(--text-primary);
}

.login-form :deep(.el-input__inner::placeholder) {
  color: var(--text-muted);
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  letter-spacing: 4px;
  background: linear-gradient(90deg, #00a8cc, #00d4ff);
  border: none;
  margin-top: 8px;
}

.login-btn:hover {
  background: linear-gradient(90deg, #00d4ff, #00e6ff);
}

.login-footer {
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
}
</style>
