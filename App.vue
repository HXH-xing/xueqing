<template>
  <div id="app" :class="theme">
    <!-- 登录页面 -->
    <div v-if="!isLogin" class="login-container">
      <div class="login-background">
        <div class="login-blob blob-1"></div>
        <div class="login-blob blob-2"></div>
        <div class="login-blob blob-3"></div>
      </div>
      <div class="login-box">
        <div class="login-header">
          <div class="login-icon">🎓</div>
          <h1>智能学情分析</h1>
          <p>SaaS 管理平台</p>
        </div>
        <div class="login-tabs">
          <button class="login-tab" :class="{ active: loginMode === 'login' }" @click="loginMode = 'login'">登录</button>
          <button class="login-tab" :class="{ active: loginMode === 'register' }" @click="loginMode = 'register'">注册</button>
        </div>
        <div class="login-form">
          <div class="input-group">
            <span class="input-icon">👤</span>
            <input v-model="username" placeholder="请输入用户名" />
          </div>
          <div class="input-group">
            <span class="input-icon">🔒</span>
            <input v-model="password" type="password" placeholder="请输入密码" />
          </div>
          
          <div v-if="loginMode === 'register'" class="role-select-group">
            <label>选择身份：</label>
            <div class="role-options">
              <div class="role-option" :class="{ active: registerRole === 'student' }" @click="registerRole = 'student'">
                <span class="role-icon">👨‍🎓</span>
                <span>学生端</span>
              </div>
              <div class="role-option" :class="{ active: registerRole === 'parent' }" @click="registerRole = 'parent'">
                <span class="role-icon">👨‍👩‍👦</span>
                <span>家长端</span>
              </div>
              <div class="role-option" :class="{ active: registerRole === 'teacher' }" @click="registerRole = 'teacher'">
                <span class="role-icon">👨‍🏫</span>
                <span>教师端</span>
              </div>
            </div>
          </div>
          
          <div class="input-group" v-if="loginMode === 'register'">
            <span class="input-icon">📧</span>
            <input v-model="email" type="email" placeholder="请输入邮箱（可选）" />
          </div>
          <div class="input-group" v-if="loginMode === 'register'">
            <span class="input-icon">🔐</span>
            <input v-model="confirmPassword" type="password" placeholder="请确认密码" />
          </div>
          <button @click="handleLoginOrRegister" class="login-btn">
            <span>{{ loginMode === 'login' ? '登 录' : '注 册' }}</span>
            <span class="btn-arrow">→</span>
          </button>
          <div v-if="loginError" class="error">{{ loginError }}</div>
        </div>
        <div class="login-footer">
          <span v-if="loginMode === 'login'">体验账号：admin / admin123</span>
          <span v-else>注册即表示同意服务条款</span>
        </div>
      </div>
    </div>

    <!-- 主页面 -->
    <div v-else class="main-container">
        <header class="top-nav">
    <div class="nav-left">
      <button class="mobile-menu-btn" @click="mobileNavOpen = !mobileNavOpen" v-if="isMobile">
        <span v-if="!mobileNavOpen">☰</span>
        <span v-else>✕</span>
      </button>
      <div class="logo">
        <span class="logo-icon">📊</span>
        <div class="logo-text-wrap">
          <span class="logo-text">学情分析</span>
          <span class="logo-badge">SaaS</span>
        </div>
      </div>
    </div>
    <div class="nav-center">
      <template v-if="currentRole === 'student'">
        <button v-for="item in studentMenuItems" :key="item.key"
                @click="switchTab(item.key)"
                class="nav-menu-item"
                :class="{ active: activeMenu === item.key }">
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.key === 'alert' && alertCount > 0" class="nav-badge">{{ alertCount }}</span>
        </button>
      </template>
      <template v-if="currentRole === 'parent'">
        <button v-for="item in parentMenuItems" :key="item.key"
                @click="switchTab(item.key)"
                class="nav-menu-item"
                :class="{ active: activeMenu === item.key }">
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </button>
      </template>
      <template v-if="currentRole === 'teacher'">
        <button v-for="item in teacherMenuItems" :key="item.key"
                @click="switchTab(item.key)"
                class="nav-menu-item"
                :class="{ active: activeMenu === item.key }">
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </button>
      </template>
    </div>
    <div class="nav-right">
      <div class="setting-wrap" style="position:relative;">
        <button class="setting-btn" @click="showSettingDrop = !showSettingDrop">⚙️</button>
        <div v-if="showSettingDrop" class="setting-dropdown">
          <div class="setting-dropdown-item">
            <span>深色模式</span>
            <button @click="toggleTheme">{{ theme==='dark-mode'?'关闭':'开启' }}🌓</button>
          </div>
          <div class="setting-dropdown-item">
            <span>账号</span>
            <span>{{ userInfo ? userInfo.full_name : '' }}</span>
          </div>
          <div class="setting-dropdown-item">
            <span>当前身份</span>
            <span class="user-role-badge">{{ getRoleLabel(currentRole) }}</span>
          </div>
          <div class="setting-dropdown-item">
            <span>头像</span>
            <div class="user-avatar-small">{{ userInfo ? userInfo.full_name?.charAt(0) || 'U' : 'U' }}</div>
          </div>
          <div class="setting-dropdown-item">
            <button @click="handleLogout(); showSettingDrop=false" class="logout-btn">🚪 退出登录</button>
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- 移动端折叠导航面板 -->
  <transition name="nav-collapse">
    <nav v-if="isMobile && mobileNavOpen" class="mobile-nav-panel">
      <div class="mobile-nav-list">
        <template v-if="currentRole === 'student'">
          <button v-for="item in studentMenuItems" :key="item.key"
                  @click="switchTab(item.key)"
                  class="mobile-nav-item"
                  :class="{ active: activeMenu === item.key }">
            <span class="mobile-nav-icon">{{ item.icon }}</span>
            <span class="mobile-nav-label">{{ item.label }}</span>
            <span v-if="item.key === 'alert' && alertCount > 0" class="nav-badge">{{ alertCount }}</span>
            <span v-if="activeMenu === item.key" class="mobile-nav-arrow">›</span>
          </button>
        </template>
        <template v-if="currentRole === 'parent'">
          <button v-for="item in parentMenuItems" :key="item.key"
                  @click="switchTab(item.key)"
                  class="mobile-nav-item"
                  :class="{ active: activeMenu === item.key }">
            <span class="mobile-nav-icon">{{ item.icon }}</span>
            <span class="mobile-nav-label">{{ item.label }}</span>
            <span v-if="activeMenu === item.key" class="mobile-nav-arrow">›</span>
          </button>
        </template>
        <template v-if="currentRole === 'teacher'">
          <button v-for="item in teacherMenuItems" :key="item.key"
                  @click="switchTab(item.key)"
                  class="mobile-nav-item"
                  :class="{ active: activeMenu === item.key }">
            <span class="mobile-nav-icon">{{ item.icon }}</span>
            <span class="mobile-nav-label">{{ item.label }}</span>
            <span v-if="activeMenu === item.key" class="mobile-nav-arrow">›</span>
          </button>
        </template>
      </div>
    </nav>
  </transition>

  <div v-if="isMobile && mobileNavOpen" class="mobile-nav-overlay" @click="mobileNavOpen = false"></div>

      <div class="main-layout">
        <div v-if="currentRole === 'student'" class="sidebar-overlay" :class="{ active: !historyCollapsed && isMobile }" @click="historyCollapsed = true"></div>

        <aside v-if="currentRole === 'student'" class="history-sidebar" :class="{ collapsed: historyCollapsed || isMobile }">
          <div class="sidebar-header" @click="toggleHistory">
            <span class="sidebar-icon">{{ historyCollapsed ? '▶' : '▼' }}</span>
            <span class="sidebar-title" v-if="!historyCollapsed">历史搜索</span>
            <span class="sidebar-badge" v-if="!historyCollapsed && searchHistory.length > 0">{{ searchHistory.length }}</span>
          </div>
          <div v-show="!historyCollapsed" class="sidebar-body">
            <div class="history-list">
              <div v-for="(item, index) in searchHistory" :key="index" class="history-item" @click="searchFromHistory(item)">
                <span class="history-icon">🔍</span>
                <span class="history-text">{{ item }}</span>
              </div>
              <div v-if="searchHistory.length === 0" class="history-empty">暂无搜索记录</div>
            </div>
            <div class="sidebar-footer">
              <button class="clear-history-btn" @click="clearHistory" v-if="searchHistory.length > 0">清空记录</button>
              <div class="sidebar-user">
                <div class="user-avatar">{{ userInfo ? userInfo.full_name?.charAt(0) || 'U' : 'U' }}</div>
                <span class="sidebar-user-name">{{ userInfo ? userInfo.full_name : '' }}</span>
              </div>
            </div>
          </div>
        </aside>

        <div class="main-content">
          <div class="content-area">
            <!-- ===== 学生端首页 ===== -->
            <div v-if="activeMenu === 'dashboard' && currentRole === 'student'" class="page-container" @click="showReportMenu = false">
              <div class="page-header dashboard-header">
                <div class="header-greeting">
                  <h2>{{ greeting }}，{{ userInfo ? userInfo.full_name : '同学' }} 👋</h2>
                  <p class="greeting-sub">今日已学习 {{ dashboardStats.weekly_learning_hours || 0 }}h，继续加油！</p>
                </div>
                <div class="header-actions">
                  <button @click.stop="toggleTimer" class="timer-mini-btn" :class="{ running: isTimerRunning }">
                    <span class="timer-mini-icon">{{ isTimerRunning ? '⏸️' : '⏱️' }}</span>
                    <span class="timer-mini-time">{{ formatTimer(studySeconds) }}</span>
                  </button>
                  <button @click.stop="resetTimer" class="timer-reset-btn" title="重置">🔄</button>
                  <button @click="loadAllData" class="btn-refresh">🔄 刷新</button>
                  <div class="report-dropdown">
                    <button @click.stop="showReportMenu = !showReportMenu" class="btn-report">📊 报告</button>
                    <div v-if="showReportMenu" class="report-dropdown-menu" @click.stop>
                      <button @click="exportReport; showReportMenu=false">📥 导出周报</button>
                      <button @click="generateWeeklyReport; showReportMenu=false">📈 生成报告</button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="stats-grid">
                <div class="stat-card clickable stat-card--blue" @click="viewDetail('knowledge')">
                  <div class="stat-icon">📊</div>
                  <div class="stat-info">
                    <span class="stat-label">知识掌握度</span>
                    <span class="stat-value">{{ dashboardStats.knowledge_mastery || 0 }}%</span>
                    <div class="stat-progress-bar"><div class="stat-progress-fill" :style="{ width: (dashboardStats.knowledge_mastery || 0) + '%', background: getMasteryColor(dashboardStats.knowledge_mastery) }"></div></div>
                  </div>
                </div>
                <div class="stat-card clickable stat-card--green" @click="viewDetail('timer')">
                  <div class="stat-icon">⏱️</div>
                  <div class="stat-info">
                    <span class="stat-label">周学习时长</span>
                    <span class="stat-value">{{ dashboardStats.weekly_learning_hours || 0 }}h</span>
                    <div class="stat-trend" :class="(dashboardStats.weekly_growth_rate || 0) > 0 ? 'up' : (dashboardStats.weekly_growth_rate || 0) < 0 ? 'down' : 'neutral'">
                      {{ (dashboardStats.weekly_growth_rate || 0) > 0 ? '📈' : (dashboardStats.weekly_growth_rate || 0) < 0 ? '📉' : '➡️' }} {{ dashboardStats.weekly_growth_rate || 0 }}%
                    </div>
                  </div>
                </div>
                <div class="stat-card clickable stat-card--orange" @click="viewDetail('weak')">
                  <div class="stat-icon">🎯</div>
                  <div class="stat-info">
                    <span class="stat-label">薄弱知识点</span>
                    <span class="stat-value">{{ weakCount }}</span>
                    <div class="stat-trend down">⚠️ 需关注</div>
                  </div>
                </div>
                <div class="stat-card clickable stat-card--red" @click="viewDetail('accuracy')">
                  <div class="stat-icon">📝</div>
                  <div class="stat-info">
                    <span class="stat-label">平均正确率</span>
                    <span class="stat-value">{{ dashboardStats.average_accuracy || 0 }}%</span>
                    <div class="stat-progress-bar"><div class="stat-progress-fill" :style="{ width: (dashboardStats.average_accuracy || 0) + '%', background: getMasteryColor(dashboardStats.average_accuracy) }"></div></div>
                  </div>
                </div>
                <div class="stat-card clickable stat-card--amber" @click="viewDetail('continuous')">
                  <div class="stat-icon">🔥</div>
                  <div class="stat-info">
                    <span class="stat-label">连续学习天数</span>
                    <span class="stat-value">{{ continuousDays }}天</span>
                    <div class="stat-trend up">🔥 保持势头</div>
                  </div>
                </div>
                <div class="stat-card clickable stat-card--purple" @click="viewDetail('task')">
                  <div class="stat-icon">🏆</div>
                  <div class="stat-info">
                    <span class="stat-label">今日完成任务</span>
                    <span class="stat-value">{{ todayCompleted }}</span>
                    <div class="stat-trend up">✅ 已完成</div>
                  </div>
                </div>
              </div>

              <!-- 学习目标 -->
              <div class="goals-section">
                <div class="goals-header">
                  <h3>🎯 本周目标</h3>
                  <button @click="showAddGoal = true" class="btn-add-goal">➕ 添加</button>
                </div>
                <div class="goal-list">
                  <div v-for="goal in goals" :key="goal.id" class="goal-item">
                    <input type="checkbox" v-model="goal.completed" @change="updateGoal(goal)">
                    <span :class="{ completed: goal.completed }">{{ goal.content }}</span>
                    <span class="goal-deadline">📅 {{ goal.deadline }}</span>
                    <button class="goal-delete" @click="deleteGoal(goal.id)">✕</button>
                  </div>
                  <div v-if="goals.length === 0" class="empty-goals">
                    <span>📋</span>
                    <p>还没有设定目标，点击添加开始规划！</p>
                  </div>
                </div>
              </div>

              <!-- 学习路径推荐 -->
              <div class="learning-path-section">
                <div class="path-header">
                  <h3>🤖 智能学习路径推荐</h3>
                  <button @click="generateLearningPath" class="btn-path">🔄 生成路径</button>
                </div>
                <div v-if="learningPath.length > 0" class="path-list">
                  <div v-for="(step, idx) in learningPath" :key="idx" class="path-step">
                    <span class="step-number">{{ idx + 1 }}</span>
                    <div class="step-content">
                      <span class="step-title">{{ step.title }}</span>
                      <span class="step-desc">{{ step.description }}</span>
                    </div>
                    <button class="btn-sm primary" @click="addToPlan(step)">加入计划</button>
                  </div>
                </div>
                <div v-else class="empty-path">
                  <span>🧭</span>
                  <p>点击生成，获取个性化学习路径</p>
                </div>
              </div>

              <div class="reflect-container">
                <div class="reflect-header">
                  <span class="reflect-title">🔄 反思闭环</span>
                  <span class="reflect-badge">{{ alertCount }}</span>
                  <span class="reflect-status-text">🟢 自主感知运行中</span>
                </div>
                <div class="reflect-body">
                  <div class="reflect-grid">
                    <div class="reflect-section">
                      <div class="reflect-section-title">⚠️ 薄弱预警</div>
                      <div v-for="alert in alertList.slice(0, 2)" :key="alert.id" class="reflect-card danger">
                        <div class="reflect-card-title">{{ alert.title }}</div>
                        <div class="reflect-card-desc">{{ alert.description }}</div>
                        <div class="reflect-card-time">{{ alert.time }}</div>
                        <button class="reflect-card-btn danger" @click="handleAlertAction(alert)">立即行动</button>
                      </div>
                      <div v-if="alertList.length === 0" class="reflect-empty">✅ 暂无预警</div>
                    </div>
                    <div class="reflect-section">
                      <div class="reflect-section-title">✅ 掌握反馈</div>
                      <div v-for="(item, index) in masteryFeedback" :key="index" class="reflect-card success">
                        <div class="reflect-card-title">{{ item.title }}</div>
                        <div class="reflect-card-desc">{{ item.description }}</div>
                        <div class="reflect-card-time">{{ item.time }}</div>
                      </div>
                      <div v-if="masteryFeedback.length === 0" class="reflect-empty">暂无反馈</div>
                    </div>
                    <div class="reflect-section">
                      <div class="reflect-section-title">📋 规划建议</div>
                      <div v-for="(item, index) in planSuggestions" :key="index" class="reflect-card primary">
                        <div class="reflect-card-title">{{ item.title }}</div>
                        <div class="reflect-card-desc">{{ item.description }}</div>
                        <div class="reflect-card-meta">
                          <span>{{ item.source }}</span>
                          <button class="reflect-card-btn primary" @click="addToPlan(item)">加入计划</button>
                        </div>
                      </div>
                      <div v-if="planSuggestions.length === 0" class="reflect-empty">暂无建议</div>
                    </div>
                    <div class="reflect-section">
                      <div class="reflect-section-title">🔄 待复盘</div>
                      <div v-for="(item, index) in reviewList" :key="index" class="reflect-card" :class="item.urgencyClass">
                        <div class="reflect-card-title">
                          {{ item.title }}
                          <span class="review-badge" :class="item.urgencyBadge">{{ item.urgencyLabel }}</span>
                        </div>
                        <div class="reflect-card-desc">{{ item.description }}</div>
                        <div class="reflect-card-time">上次复习：{{ item.lastReview }}</div>
                        <div class="reflect-card-actions">
                          <button class="reflect-card-btn warning" @click="startReview(item)">立即复习</button>
                          <button class="reflect-card-btn outline" @click="delayReview(item)">延后</button>
                        </div>
                      </div>
                      <div v-if="reviewList.length === 0" class="reflect-empty">✅ 暂无待复习</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- ===== 家长端首页 ===== -->
            <div v-if="activeMenu === 'dashboard' && currentRole === 'parent'" class="parent-dashboard">
              <div class="page-header">
                <h2>📊 {{ childViewMode ? selectedChild?.name + ' 的学情' : '孩子学情总览' }}</h2>
                <div style="display:flex;gap:10px;">
                  <button v-if="childViewMode" @click="backToParentDashboard" class="btn-refresh">⬅️ 返回</button>
                  <button @click="loadAllData" class="btn-refresh">🔄 刷新</button>
                </div>
              </div>
              <div v-if="currentRole === 'parent'" class="parent-children-section">
                <h3>👨‍👩‍👦 我的孩子</h3>
                <div class="bind-child-area">
                  <div class="bind-child-input">
                    <input v-model="childUsername" placeholder="输入孩子用户名" class="input-sm" />
                    <button @click="bindChild" class="btn-create">绑定</button>
                  </div>
                </div>
                <div v-if="childrenList.length === 0" class="empty-state">
                  <span>📭</span>
                  <p>还没有绑定孩子</p>
                </div>
                <div v-else class="children-grid">
                  <div v-for="child in childrenList" :key="child.id" class="child-card" @click="viewChildDetail(child)">
                    <div class="child-avatar">{{ child.name.charAt(0) }}</div>
                    <div class="child-info">
                      <span class="child-name">{{ child.name }}</span>
                      <span class="child-stats">掌握度：{{ child.mastery }}% | 正确率：{{ child.accuracy }}%</span>
                      <span class="child-weak">薄弱知识点：{{ child.weak_count }}个</span>
                    </div>
                    <span class="child-arrow">→</span>
                  </div>
                </div>
              </div>
              <div v-if="currentRole === 'parent'" class="stats-grid">
                <div class="stat-card">
                  <h3>📈 学习进度</h3>
                  <p>{{ dashboardStats.knowledge_mastery || 0 }}%</p>
                  <span>知识掌握度</span>
                </div>
                <div class="stat-card">
                  <h3>⏱️ 学习时长</h3>
                  <p>{{ dashboardStats.weekly_learning_hours || 0 }}h</p>
                  <span>本周学习</span>
                </div>
                <div class="stat-card">
                  <h3>🎯 薄弱环节</h3>
                  <p>{{ weakCount }}</p>
                  <span>需重点关注</span>
                </div>
                <div class="stat-card">
                  <h3>📝 近期表现</h3>
                  <p>{{ dashboardStats.average_accuracy || 0 }}%</p>
                  <span>平均正确率</span>
                </div>
              </div>
              <div v-if="currentRole === 'parent'" class="parent-alerts">
                <h3>🔔 需要关注的预警</h3>
                <div v-for="alert in alertList.slice(0, 5)" :key="alert.id" class="alert-item" @click="viewAlertDetail(alert)">
                  <span class="alert-icon">⚠️</span>
                  <span>{{ alert.title }}</span>
                  <span class="alert-time">{{ alert.time }}</span>
                </div>
                <div v-if="alertList.length === 0" class="empty-state">🎉 暂无预警，继续保持！</div>
              </div>
            </div>

            <!-- ===== 教师端首页 ===== -->
            <div v-if="activeMenu === 'dashboard' && currentRole === 'teacher'" class="teacher-dashboard">
              <div class="page-header">
                <h2>📚 班级学情总览</h2>
                <button @click="loadAllData" class="btn-refresh">🔄 刷新</button>
              </div>

              <div class="leaderboard-section">
                <h3>🏆 学习排行榜</h3>
                <div class="leaderboard">
                  <div v-for="(user, index) in topLearners" :key="user.id" class="rank-item">
                    <span class="rank-number">{{ index + 1 }}</span>
                    <span class="rank-name">{{ user.name }}</span>
                    <span class="rank-score">{{ user.hours || 0 }}h</span>
                    <div class="rank-bar-bg">
                      <div class="rank-bar" :style="{ width: ((user.hours || 0) / maxHours * 100) + '%' }"></div>
                    </div>
                    <span v-if="index === 0" class="rank-medal">🥇</span>
                    <span v-else-if="index === 1" class="rank-medal">🥈</span>
                    <span v-else-if="index === 2" class="rank-medal">🥉</span>
                  </div>
                </div>
              </div>

              <div class="class-management">
                <div class="class-header">
                  <h3>🏫 我的班级</h3>
                  <button @click="showCreateClass = true" class="btn-create">➕ 创建班级</button>
                </div>
                <div class="class-list-grid">
                  <div v-for="cls in classList" :key="cls.class_id" class="class-card-item">
                    <div class="class-card-info">
                      <h4>{{ cls.name }}</h4>
                      <p>年级：{{ cls.grade }}</p>
                      <p>学生数：{{ cls.student_count }}人</p>
                      <p>平均掌握度：{{ cls.avg_mastery }}%</p>
                      <p>平均正确率：{{ cls.avg_accuracy }}%</p>
                      <p class="class-code-display">🔑 邀请码：<strong>{{ cls.class_code }}</strong></p>
                    </div>
                    <div class="class-card-actions">
                      <button class="btn-sm primary" @click="viewClassDetail(cls.class_id)">查看学生</button>
                      <button class="btn-sm outline" @click="copyClassCode(cls.class_code)">📋 复制邀请码</button>
                    </div>
                  </div>
                  <div v-if="classList.length === 0" class="empty-state">
                    <span>📭</span>
                    <p>还没有班级，点击创建！</p>
                  </div>
                </div>
              </div>

              <div class="stats-grid">
                <div class="stat-card">
                  <h3>👨‍🎓 学生人数</h3>
                  <p>{{ studentList.length }}</p>
                  <span>班级总人数</span>
                </div>
                <div class="stat-card">
                  <h3>📊 平均进度</h3>
                  <p>{{ classAvgMastery }}%</p>
                  <span>班级平均掌握度</span>
                </div>
                <div class="stat-card">
                  <h3>🎯 班级薄弱</h3>
                  <p>{{ classWeakCount }}</p>
                  <span>薄弱知识点</span>
                </div>
                <div class="stat-card">
                  <h3>📝 平均正确率</h3>
                  <p>{{ classAvgAccuracy }}%</p>
                  <span>班级平均正确率</span>
                </div>
              </div>

              <div class="student-list">
                <h3>👨‍🎓 学生列表</h3>
                <div class="student-table">
                  <div class="table-header">
                    <span>姓名</span>
                    <span>掌握度</span>
                    <span>正确率</span>
                    <span>状态</span>
                    <span>操作</span>
                  </div>
                  <div v-for="student in studentList" :key="student.id" class="table-row" @click="viewStudentDetail(student)">
                    <span>{{ student.name }}</span>
                    <span>{{ student.mastery }}%</span>
                    <span>{{ student.accuracy }}%</span>
                    <span><span class="status-badge" :class="student.status">{{ student.status === 'good' ? '✅' : '⚠️' }}</span></span>
                    <span><button class="btn-view" @click.stop="viewStudentDetail(student)">查看</button></span>
                  </div>
                </div>
              </div>
            </div>

            <!-- ===== AI对话（学生端） ===== -->
            <div v-if="activeMenu === 'chat' && currentRole === 'student'" class="chat-wrapper">
              <div class="chat-main">
                <div class="chat-header-bar">
                  <h2>💬 AI 智能对话</h2>
                  <div style="display:flex;gap:8px;">
                    <button @click="showChatHistory = !showChatHistory" class="btn-history" :class="{ active: showChatHistory }">📜 历史记录</button>
                    <button @click="generateQuiz" class="btn-quiz">🎯 智能出题</button>
                    <button @click="clearChat" class="btn-clear">🗑️ 清空</button>
                  </div>
                </div>
                <transition name="history-slide">
                  <div v-if="showChatHistory" class="chat-history-panel">
                    <div class="chat-history-header">
                      <span>🔍 搜索历史（{{ searchHistory.length }}）</span>
                      <button v-if="searchHistory.length > 0" @click="clearHistory" class="chat-history-clear">清空</button>
                    </div>
                    <div class="chat-history-list">
                      <div v-for="(item, index) in searchHistory" :key="index" class="chat-history-item" @click="searchFromHistory(item)">
                        <span class="chat-history-icon">🔍</span>
                        <span class="chat-history-text">{{ item }}</span>
                      </div>
                      <div v-if="searchHistory.length === 0" class="chat-history-empty">暂无搜索记录</div>
                    </div>
                  </div>
                </transition>
                <div class="chat-messages" ref="chatMessages">
                  <div v-for="(msg, index) in chatMessages" :key="index" class="message" :class="msg.type">
                    <div class="message-avatar">{{ msg.type === 'user' ? '👤' : '🤖' }}</div>
                    <div class="message-content">
                      <p>{{ msg.content }}</p>
                      <span class="message-time">{{ msg.time }}</span>
                    </div>
                  </div>
                  <div v-if="chatMessages.length === 0" class="chat-empty">
                    <span class="empty-icon">💬</span>
                    <p>开始学习之旅吧！</p>
                  </div>
                </div>
              </div>
              <div class="chat-input-area" :class="{ collapsed: inputCollapsed }">
                <div class="input-toggle" @click="inputCollapsed = !inputCollapsed">
                  <span>{{ inputCollapsed ? '▲ 展开输入' : '▼ 收起输入' }}</span>
                </div>
                <div v-show="!inputCollapsed">
                  <div class="quick-actions">
                    <button v-for="action in quickActions" :key="action.label"
                            class="quick-btn" :class="action.class"
                            @click="quickAction(action.label)">
                      {{ action.icon }} {{ action.label }}
                    </button>
                  </div>
                  <div class="quiz-settings" v-if="showQuizSettings">
                    <select v-model="quizConfig.difficulty" class="select-sm">
                      <option value="easy">😊 简单</option>
                      <option value="medium">🤔 中等</option>
                      <option value="hard">😤 困难</option>
                    </select>
                    <select v-model="quizConfig.count" class="select-sm">
                      <option v-for="n in [3,5,10]" :key="n" :value="n">{{ n }}题</option>
                    </select>
                    <select v-model="quizConfig.knowledge" class="select-sm">
                      <option v-for="kp in knowledgeList" :key="kp.id" :value="kp.name">{{ kp.name }}</option>
                    </select>
                    <button @click="generateQuizQuestions" class="btn-generate">🎯 生成</button>
                  </div>
                  <div class="input-row">
                    <button @click="triggerFileUpload" class="input-btn">📷</button>
                    <button @click="startVoice" class="input-btn">🎤</button>
                    <input v-model="chatInput" @keydown.enter="sendMessage"
                           placeholder="输入学习内容..." class="chat-input" />
                    <button @click="sendMessage" class="send-btn">发送</button>
                  </div>
                  <input type="file" ref="fileInput" @change="handleFileUpload" accept="image/*" style="display:none" />
                </div>
              </div>
            </div>

            <!-- ===== 学生端我的班级 ===== -->
            <div v-if="activeMenu === 'class' && currentRole === 'student'" class="page-container">
              <div class="page-header">
                <h2>🏫 我的班级</h2>
              </div>

              <!-- 加入班级 -->
              <div class="join-class-section">
                <h3>📥 加入班级</h3>
                <div class="join-class-input">
                  <input v-model="classCode" placeholder="请输入班级邀请码" class="input-sm" />
                  <button @click="joinClass" class="btn-create">加入</button>
                </div>
              </div>

              <!-- 班级信息 -->
              <div v-if="myClass" class="class-info-card">
                <h3>{{ myClass.name }}</h3>
                <p>年级：{{ myClass.grade }}</p>
                <p>班主任：{{ myClass.teacher }}</p>
                <p>班级人数：{{ myClass.student_count }}人</p>
              </div>
              <div v-else class="empty-state">
                <span>📭</span>
                <p>还没有加入班级</p>
                <p style="font-size:12px;color:var(--text-secondary);">请输入邀请码加入班级</p>
              </div>
            </div>

            <!-- ===== 知识图谱 ===== -->
            <div v-if="activeMenu === 'knowledge'" class="page-container">
              <div class="page-header">
                <h2>📚 知识图谱</h2>
                <span class="header-count">共 {{ filteredKnowledge.length }} 个知识点</span>
              </div>
              <div class="header-actions-full">
                <input v-model="knowledgeSearch" placeholder="🔍 搜索知识点..." class="input-sm search-input" />
                <select v-model="knowledgeFilter" class="select-sm">
                  <option value="all">全部</option>
                  <option value="mastered">已掌握</option>
                  <option value="medium">学习中</option>
                  <option value="weak">薄弱</option>
                  <option value="critical">高危薄弱</option>
                </select>
                <input v-model="newKnowledge.name" placeholder="知识点名称" class="input-sm" />
                <select v-model="newKnowledge.subject" class="select-sm">
                  <option value="math">📐 数学</option>
                  <option value="physics">⚛️ 物理</option>
                  <option value="chemistry">🧪 化学</option>
                </select>
                <button @click="createKnowledge" class="btn-create">➕ 创建</button>
              </div>
              <div class="mastery-heatmap-section">
                <h4>🔥 掌握度热力图</h4>
                <div class="heatmap-grid small">
                  <div v-for="kp in filteredAndSearchedKnowledge" :key="kp.id" 
                       class="heatmap-item small" 
                       :style="{ background: getMasteryColor(kp.accuracy) }"
                       @click="openKnowledgeDetail(kp)">
                    <span class="heatmap-label">{{ kp.name }}</span>
                    <span class="heatmap-score">{{ kp.accuracy || 0 }}%</span>
                  </div>
                </div>
              </div>
              <div class="knowledge-grid">
                <div v-for="kp in filteredAndSearchedKnowledge" :key="kp.id" 
                     class="knowledge-card" :class="kp.mastery_level"
                     @dblclick="openKnowledgeDetail(kp)">
                  <div class="knowledge-card-header">
                    <span class="knowledge-name">{{ kp.name }}</span>
                    <span class="knowledge-level">{{ getLevelLabel(kp.mastery_level) }}</span>
                  </div>
                  <div class="knowledge-card-body">
                    <span>正确率：{{ kp.accuracy || 0 }}%</span>
                    <span>练习：{{ kp.total_count || 0 }}次</span>
                  </div>
                  <div class="knowledge-card-actions">
                    <button class="btn-sm success" @click.stop="recordPractice(kp.id, true)">✅ 正确</button>
                    <button class="btn-sm danger" @click.stop="recordPractice(kp.id, false)">❌ 错误</button>
                  </div>
                </div>
                <div v-if="filteredAndSearchedKnowledge.length === 0" class="empty-state">
                  <span>📭</span>
                  <p>暂无匹配的知识点</p>
                </div>
              </div>
            </div>

            <!-- ===== 学习任务（学生端） ===== -->
            <div v-if="activeMenu === 'task' && currentRole === 'student'" class="page-container">
              <div class="page-header">
                <h2>✅ 学习任务</h2>
                <span class="header-count">共 {{ taskList.length }} 个</span>
              </div>
              <div class="header-actions-full">
                <select v-model="taskFilter" class="select-sm">
                  <option value="all">全部</option>
                  <option value="today">今日</option>
                  <option value="week">本周</option>
                  <option value="overdue">逾期</option>
                </select>
                <input v-model="newTask.title" placeholder="任务标题" class="input-sm" />
                <input v-model="newTask.description" placeholder="描述" class="input-sm" />
                <button @click="createTask" class="btn-create">➕ 添加</button>
              </div>
              <div class="task-progress-card">
                <div class="progress-header">
                  <span>📊 任务进度</span>
                  <span>{{ taskProgress.completed_tasks || 0 }}/{{ taskProgress.total_tasks || 0 }}</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: (taskProgress.progress_percentage || 0) + '%' }"></div>
                </div>
                <span class="progress-text">{{ taskProgress.progress_percentage || 0 }}%</span>
              </div>
              <div class="task-list">
                <div v-for="task in filteredTasks" :key="task.id" class="task-card" :class="[task.status, { overdue: isTaskOverdue(task) }]">
                  <div class="task-info">
                    <span class="task-icon">{{ task.icon || '📖' }}</span>
                    <span class="task-title">{{ task.title }}</span>
                    <span class="task-desc">{{ task.description }}</span>
                    <span class="task-status-label">{{ getStatusLabel(task.status) }}</span>
                    <span v-if="isTaskOverdue(task)" class="task-overdue-badge">⚠️ 逾期</span>
                  </div>
                  <div class="task-actions">
                    <button v-if="task.status !== 'done'" class="btn-sm success" @click="completeTask(task.id)">✅</button>
                    <button class="btn-sm danger" @click="deleteTask(task.id)">🗑️</button>
                  </div>
                </div>
                <div v-if="filteredTasks.length === 0" class="empty-state">
                  <span>📋</span>
                  <p>暂无任务</p>
                </div>
              </div>
            </div>

            <!-- ===== 数据预警 ===== -->
            <div v-if="activeMenu === 'alert'" class="page-container">
              <div class="page-header">
                <h2>🔔 数据预警</h2>
                <div style="display:flex;gap:10px;">
                  <span class="alert-auto-check">🤖 自动检测</span>
                  <button @click="runAutoCheck" class="btn-refresh">🔄 检测</button>
                  <button @click="requestNotificationPermission" class="btn-notify">🔔 通知权限</button>
                </div>
              </div>
              <div class="alert-summary-grid">
                <div class="alert-stat-card total">
                  <span class="alert-stat-value">{{ alertList.length }}</span>
                  <span class="alert-stat-label">总预警</span>
                </div>
                <div class="alert-stat-card weak">
                  <span class="alert-stat-value">{{ alertList.filter(a => a.type === 'weak').length }}</span>
                  <span class="alert-stat-label">薄弱</span>
                </div>
                <div class="alert-stat-card decay">
                  <span class="alert-stat-value">{{ alertList.filter(a => a.type === 'decay').length }}</span>
                  <span class="alert-stat-label">衰减</span>
                </div>
              </div>
              <div class="alert-list">
                <div v-for="alert in alertList" :key="alert.id" class="alert-card" :class="alert.type">
                  <div class="alert-icon"><span class="alert-exclamation">❗</span></div>
                  <div class="alert-info">
                    <div class="alert-title">
                      <span class="alert-type-badge" :class="alert.type">{{ alert.type === 'weak' ? '⚠️ 薄弱' : '📉 衰减' }}</span>
                      {{ alert.title }}
                    </div>
                    <div class="alert-desc">{{ alert.description }}</div>
                    <div class="alert-time">{{ alert.time }}</div>
                  </div>
                  <div class="alert-actions">
                    <button class="btn-sm primary" @click="handleAlertAction(alert)">处理</button>
                    <button class="btn-sm outline" @click="dismissAlert(alert.id)">忽略</button>
                  </div>
                </div>
                <div v-if="alertList.length === 0" class="empty-state">
                  <span>🎉</span>
                  <p>暂无预警</p>
                </div>
              </div>
            </div>

            <!-- ===== 作业分析（所有端口） ===== -->
            <div v-if="activeMenu === 'analyze'" class="page-container">
              <div class="page-header">
                <h2>🔍 作业分析</h2>
                <span class="header-count">
                  {{ currentRole === 'student' ? '检测AI完成作业' : currentRole === 'parent' ? '查看孩子作业分析' : '班级作业分析' }}
                </span>
              </div>
              
              <div class="analyze-container">
                <div class="upload-section">
                  <h3>📤 上传作业</h3>
                  <div class="upload-area" @click="triggerHomeworkUpload">
                    <div v-if="!homeworkPreview">
                      <span class="upload-icon">📄</span>
                      <p>点击上传作业图片</p>
                      <span class="upload-hint">支持 JPG、PNG 格式</span>
                    </div>
                    <img v-else :src="homeworkPreview" class="upload-preview" />
                  </div>
                  <input type="file" ref="homeworkFileInput" @change="handleHomeworkUpload" accept="image/*" style="display:none" />
                  <button class="btn-analyze" @click="analyzeHomework" :disabled="!homeworkFile || analyzing">
                    {{ analyzing ? '分析中...' : '🔍 开始分析' }}
                  </button>
                </div>
                
                <div v-if="analyzeResult" class="result-section">
                  <h3>📊 分析结果</h3>
                  <div class="result-card" :class="analyzeResult.is_ai_generated ? 'ai' : 'human'">
                    <div class="result-score">
                      <span class="score-number">{{ analyzeResult.ai_probability }}%</span>
                      <span class="score-label">AI生成概率</span>
                    </div>
                    <div class="result-status">
                      <span class="status-icon">{{ analyzeResult.is_ai_generated ? '⚠️' : '✅' }}</span>
                      <span class="status-text">{{ analyzeResult.recommendation }}</span>
                    </div>
                  </div>
                  <div class="result-details">
                    <h4>📋 分析详情</h4>
                    <table class="detail-table">
                      <tbody>
                        <tr>
                          <td>文本长度</td>
                          <td>{{ analyzeResult.text_length || 0 }} 字</td>
                        </tr>
                        <tr>
                          <td>可信度</td>
                          <td>{{ analyzeResult.confidence || 0 }}%</td>
                        </tr>
                        <tr v-if="analyzeResult.analysis_details">
                          <td>平均句长</td>
                          <td>{{ analyzeResult.analysis_details.avg_sentence_length || 0 }} 字</td>
                        </tr>
                        <tr v-if="analyzeResult.analysis_details">
                          <td>重复率</td>
                          <td>{{ analyzeResult.analysis_details.repetition_rate || 0 }}%</td>
                        </tr>
                        <tr v-if="currentRole === 'student'">
                          <td>知识点状态</td>
                          <td>
                            <span v-if="analyzeResult.is_ai_generated" style="color:#ef4444;">
                            ❌ 已标记为未掌握
                            </span>
                            <span v-else style="color:#22c55e;">
                            ✅ 保持掌握状态
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div v-if="analyzeResult.suggestions && analyzeResult.suggestions.length > 0" class="suggestions">
                    <h4>💡 改进建议</h4>
                    <ul>
                      <li v-for="(s, i) in analyzeResult.suggestions" :key="i">{{ s }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识点详情弹窗 -->
    <div class="modal-overlay" v-if="showKnowledgeModal" @click.self="closeKnowledgeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ selectedKnowledge.name }}</h2>
          <button class="modal-close" @click="closeKnowledgeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">掌握等级</span>
              <span class="detail-value level-tag" :class="selectedKnowledge.mastery_level">
                {{ getLevelLabel(selectedKnowledge.mastery_level) }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">学科</span>
              <span class="detail-value">{{ getSubjectLabel(selectedKnowledge.subject) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">正确率</span>
              <span class="detail-value">{{ selectedKnowledge.accuracy || 0 }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">练习次数</span>
              <span class="detail-value">{{ selectedKnowledge.total_count || 0 }} 次</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">正确次数</span>
              <span class="detail-value">{{ selectedKnowledge.correct_count || 0 }} 次</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">连续正确</span>
              <span class="detail-value">{{ selectedKnowledge.consecutive_high_count || 0 }} 次</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">连续错误</span>
              <span class="detail-value">{{ selectedKnowledge.consecutive_low_count || 0 }} 次</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">预警状态</span>
              <span class="detail-value" :class="{ 'alert-active': selectedKnowledge.is_alert }">
                {{ selectedKnowledge.is_alert ? '⚠️ 已预警' : '✅ 正常' }}
              </span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">最后复习</span>
              <span class="detail-value">{{ formatTime(selectedKnowledge.last_review_date) }}</span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">标签</span>
              <span class="detail-value">
                <span v-for="tag in selectedKnowledge.tags" :key="tag" class="tag-badge">{{ tag }}</span>
                <span v-if="!selectedKnowledge.tags || selectedKnowledge.tags.length === 0">无</span>
              </span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">创建时间</span>
              <span class="detail-value">{{ formatTime(selectedKnowledge.created_at) }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal secondary" @click="closeKnowledgeModal">关闭</button>
          <button class="btn-modal primary" @click="openPracticePage(selectedKnowledge)">📝 去练习</button>
        </div>
      </div>
    </div>

    <!-- ===== 学生详情弹窗（教师端） ===== -->
    <div class="modal-overlay" v-if="showStudentDetail" @click.self="closeStudentDetail">
      <div class="modal-content">
        <div class="modal-header">
          <h2>👨‍🎓 {{ selectedStudent.name }}</h2>
          <button class="modal-close" @click="closeStudentDetail">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">掌握度</span>
              <span class="detail-value">{{ selectedStudent.mastery }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">正确率</span>
              <span class="detail-value">{{ selectedStudent.accuracy }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">薄弱知识点</span>
              <span class="detail-value">{{ selectedStudent.weakCount || 0 }} 个</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">学习状态</span>
              <span class="detail-value">{{ selectedStudent.status === 'good' ? '✅ 良好' : '⚠️ 需关注' }}</span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">学习建议</span>
              <span class="detail-value" style="font-size:14px;color:#6b7280;">
                {{ selectedStudent.mastery < 60 ? '需要重点辅导，建议增加练习量' : '继续保持，可以适当挑战难题' }}
              </span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal secondary" @click="closeStudentDetail">关闭</button>
          <button class="btn-modal primary" @click="generateStudentReport(selectedStudent)">📄 生成报告</button>
        </div>
      </div>
    </div>

    <!-- 练习弹窗 -->
    <div class="modal-overlay" v-if="showPracticeModal" @click.self="closePracticeModal">
      <div class="modal-content practice-modal">
        <div class="modal-header">
          <h2>📝 {{ practiceKnowledge.name }} - 练习</h2>
          <button class="modal-close" @click="closePracticeModal">✕</button>
        </div>
        <div class="modal-body practice-body">
          <div class="practice-section">
            <h3>📖 知识点讲解</h3>
            <div class="knowledge-explanation">
              <p>{{ practiceExplanation }}</p>
            </div>
          </div>
          <div class="practice-section">
            <h3>📝 练习题</h3>
            <div class="question-area">
              <p class="question-text">{{ currentQuestion }}</p>
              <div class="question-options" v-if="questionOptions.length > 0">
                <div v-for="(opt, idx) in questionOptions" :key="idx" 
                     class="option-item" 
                     :class="{ selected: selectedOption === idx, correct: showResult && idx === correctAnswerIndex, wrong: showResult && selectedOption === idx && idx !== correctAnswerIndex }"
                     @click="selectOption(idx)">
                  <span class="option-label">{{ String.fromCharCode(65 + idx) }}.</span>
                  <span class="option-text">{{ opt }}</span>
                </div>
              </div>
              <div v-else class="question-input-area">
                <textarea v-model="userAnswer" placeholder="请输入你的答案..." class="answer-textarea"></textarea>
              </div>
            </div>
            <div class="question-actions">
              <button class="btn-practice primary" @click="submitAnswer" :disabled="submitting">
                {{ submitting ? '提交中...' : '✅ 提交答案' }}
              </button>
              <button class="btn-practice secondary" @click="nextQuestion">➡️ 下一题</button>
              <button class="btn-practice secondary" @click="resetPractice">🔄 重新练习</button>
            </div>
            <div v-if="showResult" class="result-area" :class="{ correct: isAnswerCorrect, wrong: !isAnswerCorrect }">
              <span class="result-icon">{{ isAnswerCorrect ? '✅' : '❌' }}</span>
              <span class="result-text">{{ isAnswerCorrect ? '回答正确！🎉' : '回答错误，继续加油！💪' }}</span>
              <span class="result-detail" v-if="!isAnswerCorrect">正确答案：{{ correctAnswer }}</span>
            </div>
          </div>
          <div class="practice-section">
            <h3>📷 拍照上传练习结果</h3>
            <p class="upload-hint">拍照上传你的练习答案，系统将自动识别并判断</p>
            <div class="upload-area" @click="triggerPracticeUpload">
              <span v-if="!practiceUploadPreview">📸 点击上传图片</span>
              <img v-else :src="practiceUploadPreview" class="upload-preview" />
            </div>
            <input type="file" ref="practiceFileInput" @change="handlePracticeUpload" accept="image/*" style="display:none" />
            <button class="btn-practice primary" @click="analyzePracticeImage" :disabled="!practiceUploadPreview || analyzing">
              {{ analyzing ? '识别中...' : '🔍 识别并判断' }}
            </button>
            <div v-if="ocrResult" class="ocr-result">
              <h4>识别结果</h4>
              <p>{{ ocrResult }}</p>
              <div v-if="ocrJudged" class="ocr-judge" :class="{ correct: ocrIsCorrect, wrong: !ocrIsCorrect }">
                <span>{{ ocrIsCorrect ? '✅ 判断正确！' : '❌ 判断错误！' }}</span>
                <span class="ocr-detail">系统判定：{{ ocrIsCorrect ? '正确' : '错误' }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal secondary" @click="closePracticeModal">关闭练习</button>
          <button class="btn-modal primary" @click="savePracticeResult">💾 保存练习记录</button>
        </div>
      </div>
    </div>

    <!-- 报告弹窗 -->
    <div class="modal-overlay" v-if="showReportModal" @click.self="showReportModal = false">
      <div class="modal-content report-modal">
        <div class="modal-header">
          <h2>📊 学情报告</h2>
          <button class="modal-close" @click="showReportModal = false">✕</button>
        </div>
        <div class="modal-body report-body">
          <div class="report-summary">
            <h3>📈 学习概览</h3>
            <div class="report-stats">
              <div class="report-stat">
                <span class="report-label">学习总时长</span>
                <span class="report-value">{{ reportData.total_hours || 0 }}h</span>
              </div>
              <div class="report-stat">
                <span class="report-label">平均正确率</span>
                <span class="report-value">{{ reportData.avg_accuracy || 0 }}%</span>
              </div>
              <div class="report-stat">
                <span class="report-label">掌握知识点</span>
                <span class="report-value">{{ reportData.mastered_count || 0 }}</span>
              </div>
              <div class="report-stat">
                <span class="report-label">待提升</span>
                <span class="report-value">{{ reportData.weak_count || 0 }}</span>
              </div>
            </div>
          </div>
          <div class="report-strengths">
            <h3>💪 优势领域</h3>
            <ul>
              <li v-for="item in reportData.strengths" :key="item">{{ item }}</li>
              <li v-if="!reportData.strengths || reportData.strengths.length === 0">暂无数据</li>
            </ul>
          </div>
          <div class="report-weaknesses">
            <h3>🎯 待提升领域</h3>
            <ul>
              <li v-for="item in reportData.weaknesses" :key="item">{{ item }}</li>
              <li v-if="!reportData.weaknesses || reportData.weaknesses.length === 0">🎉 没有薄弱领域</li>
            </ul>
          </div>
          <div class="report-recommendations">
            <h3>💡 学习建议</h3>
            <ul>
              <li v-for="item in reportData.recommendations" :key="item">{{ item }}</li>
              <li v-if="!reportData.recommendations || reportData.recommendations.length === 0">继续保持！</li>
            </ul>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal secondary" @click="showReportModal = false">关闭</button>
          <button class="btn-modal primary" @click="exportReportPDF">📥 导出PDF</button>
        </div>
      </div>
    </div>

    <!-- 添加目标弹窗 -->
    <div class="modal-overlay" v-if="showAddGoal" @click.self="showAddGoal = false">
      <div class="modal-content small-modal">
        <div class="modal-header">
          <h2>🎯 添加目标</h2>
          <button class="modal-close" @click="showAddGoal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>目标内容</label>
            <input v-model="newGoalContent" placeholder="输入目标..." class="input-sm full-width" />
          </div>
          <div class="form-group">
            <label>截止日期</label>
            <input v-model="newGoalDeadline" type="date" class="input-sm full-width" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal secondary" @click="showAddGoal = false">取消</button>
          <button class="btn-modal primary" @click="addGoal">添加</button>
        </div>
      </div>
    </div>

    <div class="toast-container">
      <div v-for="(toast, index) in toasts" :key="index" class="toast-item" :class="getToastType(toast.message)">{{ toast.message }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

// 生产部署(前后端同源)时留空走相对路径;本地开发在 .env 里配 VITE_API_BASE
const API_BASE = import.meta.env.VITE_API_BASE || ''

export default {
  data() {
    return {
      // 登录
      isLogin: false,
      username: '',
      password: '',
      loginError: '',
      loginMode: 'login',
      registerRole: 'student',
      email: '',
      confirmPassword: '',
      token: null,
      userInfo: null,
      currentRole: 'student',
      // 家长端
      childrenList: [], 
      childUsername: '',     
      selectedChild: null,   
      showChildDetail: false,
      childViewMode: false,
      
      // 主题
      theme: 'light-mode',
      
      // 导航
      activeMenu: 'dashboard',
      historyCollapsed: false,
      inputCollapsed: false,
      isMobile: false,
      mobileNavOpen: false,
      showChatHistory: false,
      showReportMenu: false,
      showSettingDrop: false,

      
      // 数据
      dashboardStats: {},
      knowledgeList: [],
      knowledgeSearch: '',
      knowledgeFilter: 'all',
      newKnowledge: { name: '', subject: 'math' },
      currentSubject: 'math',
      taskList: [],
      taskFilter: 'all',
      newTask: { title: '', description: '' },
      taskProgress: {},
      alertList: [],
      chatMessages: [],
      chatInput: '',

      // ===== 班级相关 =====
      classCode: '',
      classList: [],
      currentClass: null,
      showClassDetail: false,
      showCreateClass: false,
      newClassName: '',
      newClassGrade: '',
      myClass: null,
      
      // UI状态
      toasts: [],
      weekDays: ['一', '二', '三', '四', '五', '六', '日'],
      searchHistory: JSON.parse(localStorage.getItem('searchHistory') || '[]'),
      alertIdCounter: 0,
      continuousDays: 7,
      todayCompleted: 3,
      
      // 弹窗
      showKnowledgeModal: false,
      selectedKnowledge: {},
      showStudentDetail: false,
      selectedStudent: {},
      showPracticeModal: false,
      practiceKnowledge: {},
      practiceExplanation: '',
      currentQuestion: '',
      questionOptions: [],
      userAnswer: '',
      selectedOption: null,
      correctAnswer: '',
      correctAnswerIndex: -1,
      showResult: false,
      isAnswerCorrect: false,
      submitting: false,
      questionIndex: 0,
      practiceQuestions: [],
      practiceUploadPreview: null,
      practiceUploadFile: null,
      ocrResult: null,
      ocrIsCorrect: false,
      ocrJudged: false,
      analyzing: false,
      
      // 作业分析
      homeworkFile: null,
      homeworkPreview: null,
      analyzeResult: null,
      
      // ===== 新增功能数据 =====
      studySeconds: 0,
      isTimerRunning: false,
      timerInterval: null,
      studyRecords: JSON.parse(localStorage.getItem('studyRecords') || '[]'),
      goals: JSON.parse(localStorage.getItem('goals') || '[]'),
      showAddGoal: false,
      newGoalContent: '',
      newGoalDeadline: '',
      goalIdCounter: 0,
      learningPath: [],
      showQuizSettings: false,
      quizConfig: {
        difficulty: 'medium',
        count: 5,
        knowledge: ''
      },
      quizQuestions: [],
      showReportModal: false,
      reportData: {},
      
      // 反思
      masteryFeedback: [],
      planSuggestions: [],
      reviewList: [],
      
      // 菜单
      studentMenuItems: [
        { key: 'dashboard', icon: '🏠', label: '首页' },
        { key: 'chat', icon: '💬', label: 'AI对话' },
        { key: 'knowledge', icon: '📚', label: '知识图谱' },
        { key: 'task', icon: '✅', label: '学习任务' },
        { key: 'alert', icon: '🔔', label: '数据预警' },
        { key: 'class', icon: '🏫', label: '我的班级' }
      ], 
      parentMenuItems: [
        { key: 'dashboard', icon: '📊', label: '学情总览' },
        { key: 'analyze', icon: '🔍', label: '作业分析' },
        { key: 'alert', icon: '🔔', label: '预警提醒' }
      ],
      teacherMenuItems: [
        { key: 'dashboard', icon: '📊', label: '班级总览' },
        { key: 'knowledge', icon: '📚', label: '教学图谱' },
        { key: 'analyze', icon: '🔍', label: '作业分析' },
        { key: 'alert', icon: '🔔', label: '班级预警' }
      ],
      quickActions: [
        { icon: '📖', label: '错题复盘', class: 'memory' },
        { icon: '📅', label: '今日规划', class: 'plan' },
        { icon: '💡', label: '智能出题', class: 'action' },
        { icon: '🗺️', label: '思维导图', class: 'perceive' },
        { icon: '📄', label: '周总结', class: 'reflect' }
      ],
      
      // 模拟学生数据（教师端）
      studentList: [
        { id: 1, name: '小李', mastery: 78, accuracy: 86, status: 'good', weakCount: 3, hours: 8.5 },
        { id: 2, name: '小王', mastery: 65, accuracy: 72, status: 'warning', weakCount: 6, hours: 5.2 },
        { id: 3, name: '小张', mastery: 82, accuracy: 90, status: 'good', weakCount: 2, hours: 10.1 },
        { id: 4, name: '小刘', mastery: 55, accuracy: 58, status: 'warning', weakCount: 8, hours: 3.8 },
        { id: 5, name: '小陈', mastery: 75, accuracy: 82, status: 'good', weakCount: 4, hours: 7.3 }
      ]
    }
  },
  computed: {
    greeting() {
      const h = new Date().getHours()
      if (h < 6) return '夜深了'
      if (h < 12) return '早上好'
      if (h < 14) return '中午好'
      if (h < 18) return '下午好'
      return '晚上好'
    },
    filteredKnowledge() {
      return this.knowledgeList.filter(kp => kp.subject === this.currentSubject)
    },
    filteredAndSearchedKnowledge() {
      let result = this.filteredKnowledge
      if (this.knowledgeSearch) {
        const s = this.knowledgeSearch.toLowerCase()
        result = result.filter(kp => kp.name.toLowerCase().includes(s))
      }
      if (this.knowledgeFilter !== 'all') {
        result = result.filter(kp => kp.mastery_level === this.knowledgeFilter)
      }
      return result
    },
    filteredTasks() {
      const now = new Date()
      let result = this.taskList
      if (this.taskFilter === 'today') {
        const today = now.toDateString()
        result = result.filter(t => new Date(t.created_at).toDateString() === today)
      } else if (this.taskFilter === 'week') {
        const ws = new Date(now)
        ws.setDate(now.getDate() - now.getDay())
        result = result.filter(t => new Date(t.created_at) >= ws)
      } else if (this.taskFilter === 'overdue') {
        result = result.filter(t => this.isTaskOverdue(t) && t.status !== 'done')
      }
      return result
    },
    weeklyData() {
      return this.dashboardStats.weekly_data?.hours || [0.5, 0.8, 1.2, 0.9, 1.5, 2.1, 1.8]
    },
    alertCount() { return this.alertList.length },
    weakCount() {
      if (this.dashboardStats.weak_knowledge_count !== undefined) return this.dashboardStats.weak_knowledge_count
      return this.knowledgeList.filter(k => ['weak', 'critical'].includes(k.mastery_level)).length
    },
    masteryStats() {
      const s = { mastered: 0, medium: 0, weak: 0, critical: 0 }
      this.knowledgeList.forEach(k => { if (s[k.mastery_level] !== undefined) s[k.mastery_level]++ })
      return s
    },
    classAvgMastery() {
      if (!this.studentList.length) return 0
      return Math.round(this.studentList.reduce((sum, s) => sum + s.mastery, 0) / this.studentList.length)
    },
    classAvgAccuracy() {
      if (!this.studentList.length) return 0
      return Math.round(this.studentList.reduce((sum, s) => sum + s.accuracy, 0) / this.studentList.length)
    },
    classWeakCount() {
      return this.studentList.reduce((sum, s) => sum + (s.weakCount || 0), 0)
    },
    maxHours() {
      return Math.max(...this.studentList.map(u => u.hours || 0), 1)
    },
    topLearners() {
      return [...this.studentList].sort((a, b) => (b.hours || 0) - (a.hours || 0))
    },
    needReview() {
      return this.knowledgeList.filter(kp => {
        const days = (Date.now() - new Date(kp.last_review_date).getTime()) / (1000 * 60 * 60 * 24)
        return days >= 3 && kp.total_count > 0
      })
    }
  },
  methods: {
    // ===== 工具方法 =====
    getLevelLabel(l) {
      const map = { mastered: '已掌握', medium: '学习中', weak: '薄弱', critical: '高危薄弱' }
      return map[l] || l
    },
    getStatusLabel(s) {
      const map = { pending: '⏳ 待办', doing: '🔄 进行中', done: '✅ 已完成' }
      return map[s] || s
    },
    getRoleLabel(role) {
      const map = { student: '学生端', parent: '家长端', teacher: '教师端' }
      return map[role] || role
    },
    getSubjectLabel(subject) {
      const map = { math: '📐 数学', physics: '⚛️ 物理', chemistry: '🧪 化学' }
      return map[subject] || subject
    },
    formatTime(t) {
      if (!t) return ''
      return new Date(t).toLocaleString('zh-CN', { hour12: false })
    },
    isTaskOverdue(t) {
      if (t.status === 'done' || !t.due_date) return false
      return new Date(t.due_date) < new Date()
    },
    switchTab(key) {
      this.activeMenu = key
      this.mobileNavOpen = false
      if (key === 'alert') this.runAutoCheck()
    },
    toggleHistory() {
      this.historyCollapsed = !this.historyCollapsed
    },
    handleResize() {
      this.isMobile = window.innerWidth < 768
      if (!this.isMobile) this.mobileNavOpen = false
    },
    toggleTheme() {
      this.theme = this.theme === 'light-mode' ? 'dark-mode' : 'light-mode'
      localStorage.setItem('theme', this.theme)
    },
    
    // ===== 数据加载（核心修复） =====
    async loadAllData() {
      try {
        await Promise.all([
          this.loadDashboard(),
          this.loadKnowledge(),
          this.loadTasks()
        ])
      } catch (e) {
        console.error('加载数据失败:', e)
      }
      // 如果是家长端，加载孩子列表
        if (this.currentRole === 'parent') {
          await this.loadChildren()
        }
  
      // 如果是教师端，加载班级列表
      if (this.currentRole === 'teacher') {
        await this.loadClassList()
       }
      
      // ✅ 如果知识点为空，生成模拟数据（解决教师端空白问题）
      if (this.knowledgeList.length === 0) {
        this.generateMockData()
      }
      
      this.runAutoCheck()
      this.buildReflectData()
    },
    
    generateMockData() {
      const now = new Date().toISOString()
      
      this.knowledgeList = [
        { id: 1, name: '函数与导数', subject: 'math', mastery_level: 'medium', accuracy: 65, total_count: 12, correct_count: 8, consecutive_low_count: 1, consecutive_high_count: 3, last_review_date: now, is_alert: false, tags: ['高中数学'], created_at: now },
        { id: 2, name: '三角函数', subject: 'math', mastery_level: 'medium', accuracy: 70, total_count: 10, correct_count: 7, consecutive_low_count: 0, consecutive_high_count: 4, last_review_date: now, is_alert: false, tags: ['高中数学'], created_at: now },
        { id: 3, name: '数列', subject: 'math', mastery_level: 'mastered', accuracy: 88, total_count: 15, correct_count: 13, consecutive_low_count: 0, consecutive_high_count: 6, last_review_date: now, is_alert: false, tags: ['高中数学'], created_at: now },
        { id: 4, name: '立体几何', subject: 'math', mastery_level: 'weak', accuracy: 45, total_count: 8, correct_count: 4, consecutive_low_count: 3, consecutive_high_count: 0, last_review_date: now, is_alert: true, tags: ['高中数学'], created_at: now }
      ]
      
      this.dashboardStats = this.dashboardStats && Object.keys(this.dashboardStats).length > 0
        ? this.dashboardStats
        : {
            knowledge_mastery: 67,
            weekly_learning_hours: 8.5,
            average_accuracy: 72,
            weekly_data: { hours: [1.5, 2.0, 1.8, 2.5, 1.2, 0.5, 3.0] }
          }
      
      this.taskList = [
        { id: 1, title: '复习函数与导数', description: '完成5道导数练习题', status: 'doing', priority: 2, icon: '📖', created_at: now, due_date: new Date(Date.now() + 2*24*60*60*1000).toISOString() }
      ]
      
      this.taskProgress = {
        total_tasks: 3,
        completed_tasks: 1,
        progress_percentage: 33,
        pending_tasks: 1,
        doing_tasks: 1
      }
      
      this.showToast('📚 已为您生成示例数据！')
    },
    
    async loadDashboard() {
      try {
        const res = await axios.get(`${API_BASE}/api/dashboard/stats/${this.userInfo.id}`, {
          headers: { 'Authorization': 'Bearer ' + this.token }
        })
        if (res.data.code === 200) this.dashboardStats = res.data.data
      } catch (e) {
        console.error('加载看板失败:', e)
      }
    },
    
    async loadKnowledge() {
      try {
        const res = await axios.get(`${API_BASE}/api/knowledge/user/${this.userInfo.id}`, {
          headers: { 'Authorization': 'Bearer ' + this.token }
        })
        if (res.data.code === 200) this.knowledgeList = res.data.data || []
      } catch (e) {
        this.knowledgeList = []
        this.generateMockData()
      }
    },
    
    async loadTasks() {
      try {
        const taskRes = await axios.get(`${API_BASE}/api/task/user/${this.userInfo.id}`, {
          headers: { 'Authorization': 'Bearer ' + this.token }
        })
        if (taskRes.data.code === 200) this.taskList = taskRes.data.data || []
      } catch (e) {
        this.taskList = []
      }
      
      try {
        const progressRes = await axios.get(`${API_BASE}/api/task/progress/${this.userInfo.id}`, {
          headers: { 'Authorization': 'Bearer ' + this.token }
        })
        if (progressRes.data.code === 200) this.taskProgress = progressRes.data.data || {}
      } catch (e) {
        this.taskProgress = { total_tasks: 0, completed_tasks: 0, progress_percentage: 0 }
      }
    },
    
    // ===== 知识点操作 =====
    async createKnowledge() {
      if (!this.newKnowledge.name) {
        this.showToast('请输入知识点名称')
        return
      }
      try {
        const res = await axios.post(`${API_BASE}/api/knowledge/`, {
          name: this.newKnowledge.name,
          subject: this.currentSubject,
          user_id: this.userInfo.id,  // ✅ 动态获取用户ID
          tags: ["自定义"]
        }, { headers: { 'Authorization': 'Bearer ' + this.token } })
        if (res.data.code === 200) {
          this.showToast('✅ 创建成功！')
          this.newKnowledge.name = ''
          await this.loadKnowledge()
          this.runAutoCheck()
        }
      } catch (e) {
        this.showToast('创建失败：' + e.message)
      }
    },
    
    async recordPractice(kpId, isCorrect) {
      try {
        await axios.post(`${API_BASE}/api/knowledge/${kpId}/record-practice?is_correct=${isCorrect}`, {},
          { headers: { 'Authorization': 'Bearer ' + this.token } })
        await this.loadKnowledge()
        this.runAutoCheck()
        this.buildReflectData()
        this.loadDashboard()
      } catch (e) {
        console.error('记录失败:', e)
      }
    },
    
    // ===== 任务操作 =====
    async createTask() {
      if (!this.newTask.title) {
        this.showToast('请输入任务标题')
        return
      }
      try {
        await axios.post(`${API_BASE}/api/task/`, {
          title: this.newTask.title,
          description: this.newTask.description || '',
          user_id: this.userInfo.id,  // ✅ 动态获取用户ID
          priority: 1,
          due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
        }, { headers: { 'Authorization': 'Bearer ' + this.token } })
        this.showToast('✅ 任务添加成功！')
        this.newTask.title = ''
        this.newTask.description = ''
        this.loadTasks()
      } catch (e) {
        this.showToast('添加失败：' + e.message)
      }
    },
    
    async completeTask(id) {
      try {
        await axios.post(`${API_BASE}/api/task/${id}/complete`, {},
          { headers: { 'Authorization': 'Bearer ' + this.token } })
        this.showToast('🎉 任务已完成！')
        this.loadTasks()
      } catch (e) {
        this.showToast('完成失败：' + e.message)
      }
    },
    
    async deleteTask(id) {
      if (!confirm('确定删除？')) return
      try {
        await axios.delete(`${API_BASE}/api/task/${id}`,
          { headers: { 'Authorization': 'Bearer ' + this.token } })
        this.showToast('🗑️ 已删除')
        this.loadTasks()
      } catch (e) {
        this.showToast('删除失败：' + e.message)
      }
    },
    
    async autoCreateTask(title, desc) {
      try {
        await axios.post(`${API_BASE}/api/task/`, {
          title: title,
          description: desc || '',
          user_id: this.userInfo.id,  // ✅ 动态获取用户ID
          priority: 1,
          due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
        }, { headers: { 'Authorization': 'Bearer ' + this.token } })
      } catch (e) {
        console.error('自动创建任务失败:', e)
      }
    },
    
    // ===== 登录/注册 =====
    async handleLogin() {
      if (!this.username || !this.password) {
        this.loginError = '请填写用户名和密码'
        return
      }
      try {
        const res = await axios.post(`${API_BASE}/api/auth/login`, {
          username: this.username,
          password: this.password
        })
        if (res.data.code === 200) {
          this.token = res.data.data.access_token
          this.userInfo = res.data.data.user

        const originalRole = this.userInfo.original_role
        if (originalRole && ['student', 'parent', 'teacher'].includes(originalRole)) {
          this.currentRole = originalRole
        } else {
           // 兼容旧账号
          let role = this.userInfo.role || 'student'
          if (role === 'admin') {
            role = this.userInfo.username === 'admin' ? 'student' : 'teacher'
          }
          this.currentRole = role
        }
      
        this.isLogin = true
        localStorage.setItem('token', this.token)
        localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
        localStorage.setItem('userRole', this.currentRole)
        await this.loadAllData()
        this.showToast(`登录成功！欢迎${this.userInfo.full_name || this.userInfo.username}`)
      } else {
        this.loginError = res.data.message || '登录失败'
      }
    } catch (e) {
      console.error('登录错误:', e)
      this.loginError = '登录失败：' + (e.response?.data?.message || e.message)
    }
  },

    
    handleLoginOrRegister() {
      if (this.loginMode === 'login') {
        this.handleLogin()
      } else {
        this.handleRegister()
      }
    },
    
    async handleRegister() {
      if (!this.username || !this.password) {
        this.loginError = '请填写用户名和密码'
        return
      }
      if (this.password !== this.confirmPassword) {
        this.loginError = '两次密码不一致'
        return
      }
      if (this.password.length < 6) {
        this.loginError = '密码至少6位'
        return
      }
      try {
        const res = await axios.post(`${API_BASE}/api/auth/register`, {
          username: this.username,
          password: this.password,
          role: this.registerRole
        })
        if (res.data.code === 200) {
          this.token = res.data.data.access_token
          this.userInfo = res.data.data.user
          this.currentRole = this.registerRole
          this.isLogin = true
          localStorage.setItem('token', this.token)
          localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
          localStorage.setItem('userRole', this.registerRole)
          this.showToast(`🎉 注册成功！`)
          await this.loadAllData()
        } else {
          this.loginError = res.data.message
        }
      } catch (e) {
        this.loginError = '注册失败：' + e.message
      }
    },
    
    handleLogout() {
      this.isLogin = false
      this.token = null
      this.userInfo = null
      this.chatMessages = []
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('userRole')
      this.showToast('已退出')
    },
    
    // ===== AI对话 =====
    async sendMessage() {
      if (!this.chatInput.trim()) return
      const msg = { type: 'user', content: this.chatInput, time: new Date().toLocaleTimeString() }
      this.chatMessages.push(msg)
      const input = this.chatInput
      this.chatInput = ''
      this.scrollToBottom()
      this.addSearchHistory(input)
      try {
        const res = await axios.post(`${API_BASE}/api/ai/chat/message`, {
          session_id: 'web_session',
          content: input,
          message_type: 'system'
        }, { headers: { 'Authorization': 'Bearer ' + this.token } })
        let reply = res.data.data?.content || '收到消息：' + input
        this.chatMessages.push({ type: 'system', content: reply, time: new Date().toLocaleTimeString() })
        await this.loadTasks()
      } catch (e) {
        this.chatMessages.push({ type: 'system', content: '❌ 请求失败：' + e.message, time: new Date().toLocaleTimeString() })
      }
      this.scrollToBottom()
    },
    
    quickAction(action) {
      this.chatInput = `帮我做一下${action}`
      this.sendMessage()
    },
    
    clearChat() {
      this.chatMessages = []
      this.showToast('已清空')
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const c = this.$refs.chatMessages
        if (c) c.scrollTop = c.scrollHeight
      })
    },
    
    triggerFileUpload() { this.$refs.fileInput.click() },
    
    async handleFileUpload(e) {
      const file = e.target.files[0]
      if (!file) return
      this.chatMessages.push({ type: 'user', content: '📷 上传：' + file.name, time: new Date().toLocaleTimeString() })
      try {
        const fd = new FormData()
        fd.append('file', file)
        const res = await axios.post(`${API_BASE}/api/tools/ocr/recognize`, fd,
          { headers: { 'Authorization': 'Bearer ' + this.token } })
        if (res.data.code === 200) {
          this.chatMessages.push({ type: 'system', content: '📝 OCR结果：\n' + res.data.data.recognized_text,
            time: new Date().toLocaleTimeString() })
          this.showToast('✅ 识别完成！')
        }
      } catch (err) {
        this.chatMessages.push({ type: 'system', content: '❌ OCR失败：' + err.message, time: new Date().toLocaleTimeString() })
      }
      e.target.value = ''
    },
    
    startVoice() {
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        this.showToast('请使用Chrome浏览器')
        return
      }
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition
      const rec = new SR()
      rec.lang = 'zh-CN'
      rec.continuous = false
      this.isRecording = true
      rec.onresult = (e) => {
        this.chatInput = e.results[0][0].transcript
        this.isRecording = false
        this.sendMessage()
      }
      rec.onerror = () => { this.isRecording = false }
      rec.onend = () => { this.isRecording = false }
      rec.start()
    },
    
    searchFromHistory(item) {
      this.activeMenu = 'chat'
      this.showChatHistory = false
      this.chatInput = `帮我讲解一下 ${item}`
      this.sendMessage()
    },
    
    addSearchHistory(keyword) {
      if (!keyword || !keyword.trim()) return
      const k = keyword.trim()
      const idx = this.searchHistory.indexOf(k)
      if (idx > -1) this.searchHistory.splice(idx, 1)
      this.searchHistory.unshift(k)
      if (this.searchHistory.length > 10) this.searchHistory = this.searchHistory.slice(0, 10)
      localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory))
    },
    
    clearHistory() {
      if (confirm('清空所有搜索历史？')) {
        this.searchHistory = []
        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory))
        this.showToast('已清空')
      }
    },
    
    // ===== 预警 =====
    runAutoCheck() {
      const alerts = []
      const now = new Date().toLocaleString('zh-CN', { hour12: false })
      for (const kp of this.knowledgeList) {
        if (kp.accuracy < 50 && kp.total_count >= 3) {
          alerts.push({
            id: ++this.alertIdCounter,
            type: 'weak',
            title: kp.name,
            description: `正确率 ${kp.accuracy}%，建议重点复习`,
            time: now,
            knowledgePointId: kp.id
          })
        }
        if (kp.consecutive_low_count >= 3) {
          alerts.push({
            id: ++this.alertIdCounter,
            type: 'weak',
            title: kp.name,
            description: `连续 ${kp.consecutive_low_count} 次错误！`,
            time: now,
            knowledgePointId: kp.id
          })
        }
        const days = (Date.now() - new Date(kp.last_review_date).getTime()) / (1000 * 60 * 60 * 24)
        if (days >= 5 && kp.total_count > 0) {
          alerts.push({
            id: ++this.alertIdCounter,
            type: 'decay',
            title: kp.name,
            description: `已 ${Math.floor(days)} 天未复习`,
            time: now,
            knowledgePointId: kp.id
          })
        }
      }
      const seen = new Set()
      this.alertList = alerts.filter(a => {
        const key = a.knowledgePointId + '_' + a.type
        if (seen.has(key)) return false
        seen.add(key)
        return true
      })
    },
    
    handleAlertAction(alert) {
      this.showToast(`🔔 处理预警：${alert.title}`)
      this.activeMenu = 'knowledge'
    },
    
    dismissAlert(id) {
      this.alertList = this.alertList.filter(a => a.id !== id)
      this.showToast('已忽略')
    },
    
    viewAlertDetail(alert) {
      const kp = this.knowledgeList.find(k => k.id === alert.knowledgePointId)
      if (kp) {
        this.activeMenu = 'knowledge'
        this.$nextTick(() => {
          this.selectedKnowledge = kp
          this.showKnowledgeModal = true
        })
        this.showToast(`📚 查看知识点：${kp.name}`)
      } else {
        this.showToast(`🔍 查看预警详情：${alert.title}`)
      }
    },
    
    // ===== 反思闭环 =====
    buildReflectData() {
      this.masteryFeedback = this.knowledgeList
        .filter(k => k.mastery_level === 'mastered' && k.total_count >= 5)
        .slice(0, 3)
        .map(k => ({
          title: k.name,
          description: `正确率 ${k.accuracy}%，已掌握`,
          time: new Date().toLocaleString('zh-CN', { hour12: false })
        }))
      
      if (!this.masteryFeedback.length) {
        this.masteryFeedback = [{ title: '继续练习', description: '坚持练习，越来越好', time: '今日' }]
      }
      
      const weak = this.knowledgeList.filter(k => ['weak', 'critical'].includes(k.mastery_level))
      this.planSuggestions = weak.length
        ? weak.slice(0, 3).map(k => ({
            icon: '📌',
            title: k.name,
            description: `正确率 ${k.accuracy}%，建议复习`,
            source: '系统建议 · 自动生成'
          }))
        : [{ icon: '📌', title: '继续学习', description: '没有薄弱知识点', source: '系统建议' }]
      
      this.reviewList = this.knowledgeList
  .filter(k => {
    // 已掌握且7天以上未复习
    if (k.mastery_level === 'mastered') {
      const days = (Date.now() - new Date(k.last_review_date).getTime()) / (1000 * 60 * 60 * 24)
      return days >= 7 && k.total_count > 0
    }
    // 非已掌握且练习过的（需要复习）
    return k.total_count > 0
  })
  .slice(0, 5)
  .map(k => {
    const days = (Date.now() - new Date(k.last_review_date).getTime()) / (1000 * 60 * 60 * 24)
    let urgencyClass = 'warning'
    let urgencyBadge = 'normal'
    let urgencyLabel = '🟢 可以复习'
    
    if (days >= 14) {
      urgencyClass = 'danger'
      urgencyBadge = 'critical'
      urgencyLabel = '🔴 急需复习'
    } else if (days >= 7) {
      urgencyClass = 'warning'
      urgencyBadge = 'warning'
      urgencyLabel = '🟡 建议复习'
    } else if (days >= 3) {
      urgencyClass = 'primary'
      urgencyBadge = 'normal'
      urgencyLabel = '🟢 可以复习'
    } else {
      urgencyClass = 'success'
      urgencyBadge = 'good'
      urgencyLabel = '✅ 掌握良好'
    }
    
    return {
      title: k.name,
      description: `正确率 ${k.accuracy}%，${k.mastery_level === 'mastered' ? '已掌握' : '学习中'}`,
      lastReview: new Date(k.last_review_date).toLocaleDateString('zh-CN'),
      urgencyClass: urgencyClass,
      urgencyBadge: urgencyBadge,
      urgencyLabel: urgencyLabel
    }
  })

if (!this.reviewList.length) {
  this.reviewList = [{ 
    title: '暂无待复习', 
    description: '掌握得不错！继续保持！',
    urgencyClass: 'success',
    urgencyBadge: 'good',
    urgencyLabel: '✅ 良好',
    lastReview: '—'
  }]
}
    },
    
    addToPlan(item) {
      this.showToast('✅ 已加入计划：' + item.title)
      this.autoCreateTask(`📌 ${item.title}`, item.description)
      this.loadTasks()
    },
    
    startReview(item) {
      this.showToast('📚 开始复习：' + (item.title || item.name))
    },
    
    delayReview(item) {
      this.showToast('⏰ 已延后：' + item.title)
    },
    
    // ===== 作业分析 =====
    triggerHomeworkUpload() {
      this.$refs.homeworkFileInput.click()
    },
    
    handleHomeworkUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      this.homeworkFile = file
      const reader = new FileReader()
      reader.onload = (e) => {
        this.homeworkPreview = e.target.result
      }
      reader.readAsDataURL(file)
      this.analyzeResult = null
      this.showToast('📷 作业已上传，点击"开始分析"')
    },
    
    async analyzeHomework() {
      if (!this.homeworkFile) {
        this.showToast('请先上传作业')
        return
      }
      this.analyzing = true
      try {
        const formData = new FormData()
        formData.append('file', this.homeworkFile)
        const res = await axios.post(`${API_BASE}/api/tools/analyze/homework`, formData, {
          headers: { 'Authorization': 'Bearer ' + this.token }
        })
        if (res.data.code === 200) {
          this.analyzeResult = res.data.data
          if (this.currentRole === 'student' && this.analyzeResult.is_ai_generated) {
            const kpName = this.extractKnowledgePoint(this.analyzeResult)
            if (kpName) {
              await this.markKnowledgeUnmastered(kpName)
              this.showToast(`⚠️ 检测到AI生成作业，已标记"${kpName}"为未掌握`)
            }
          }
          this.showToast('✅ 分析完成！')
        }
      } catch (error) {
        this.showToast('❌ 分析失败：' + error.message)
        this.analyzeResult = {
          ai_probability: 75,
          confidence: 80,
          is_ai_generated: true,
          recommendation: '⚠️ 该作业疑似由AI生成，建议核实',
          text_length: 280,
          analysis_details: {
            avg_sentence_length: 42.5,
            repetition_rate: 8.2
          },
          suggestions: ['📝 建议增加个人思考和具体例子', '💡 尝试加入"我认为"等个人化表达']
        }
        if (this.currentRole === 'student') {
          await this.markKnowledgeUnmastered('函数与导数')
          this.showToast('⚠️ 检测到AI生成作业，已标记知识点为未掌握（演示模式）')
        }
      }
      this.analyzing = false
    },
    
    extractKnowledgePoint(result) {
      const keywords = ['函数', '导数', '三角', '数列', '极限', '积分', '微分']
      for (const kw of keywords) {
        if (this.knowledgeList.some(k => k.name.includes(kw))) {
          return kw
        }
      }
      return this.knowledgeList.length > 0 ? this.knowledgeList[0].name : null
    },
    
    async markKnowledgeUnmastered(kpName) {
      try {
        const kp = this.knowledgeList.find(k => k.name.includes(kpName))
        if (kp) {
          await this.recordPractice(kp.id, false)
          this.showToast(`📚 已标记 "${kp.name}" 为未掌握，请重新学习`)
        }
      } catch (e) {
        console.error('标记失败:', e)
      }
    },
    
    // ===== 知识点弹窗 =====
    openKnowledgeDetail(kp) {
      this.selectedKnowledge = kp
      this.showKnowledgeModal = true
    },
    
    closeKnowledgeModal() {
      this.showKnowledgeModal = false
      this.selectedKnowledge = {}
    },
    
    // ===== 练习 =====
    openPracticePage(kp) {
      this.closeKnowledgeModal()
      this.practiceKnowledge = kp
      this.practiceExplanation = this.generateExplanation(kp)
      this.practiceQuestions = this.generateQuestions(kp, 3)
      this.questionIndex = 0
      this.loadQuestion()
      this.resetPracticeState()
      this.showPracticeModal = true
    },
    
    closePracticeModal() {
      this.showPracticeModal = false
      this.resetPracticeState()
    },
    
    resetPracticeState() {
      this.showResult = false
      this.isAnswerCorrect = false
      this.selectedOption = null
      this.userAnswer = ''
      this.submitting = false
      this.ocrResult = null
      this.ocrJudged = false
      this.ocrIsCorrect = false
      this.practiceUploadPreview = null
      this.practiceUploadFile = null
    },
    
    resetPractice() {
      this.resetPracticeState()
      this.practiceQuestions = this.generateQuestions(this.practiceKnowledge, 3)
      this.questionIndex = 0
      this.loadQuestion()
      this.showToast('🔄 已重置练习')
    },
    
    loadQuestion() {
      if (this.questionIndex < this.practiceQuestions.length) {
        const q = this.practiceQuestions[this.questionIndex]
        this.currentQuestion = q.question
        this.questionOptions = q.options || []
        this.correctAnswer = q.answer
        this.correctAnswerIndex = q.options ? q.options.indexOf(q.answer) : -1
        this.selectedOption = null
        this.userAnswer = ''
        this.showResult = false
        this.isAnswerCorrect = false
      } else {
        this.showToast('🎉 所有题目已完成！')
        this.questionIndex = 0
        this.loadQuestion()
      }
    },
    
    nextQuestion() {
      if (!this.showResult) {
        this.showToast('请先提交答案')
        return
      }
      this.questionIndex++
      this.loadQuestion()
    },
    
    selectOption(idx) {
      if (this.showResult) return
      this.selectedOption = idx
    },
    
    submitAnswer() {
      if (this.submitting) return
      let answer = ''
      if (this.questionOptions.length > 0) {
        if (this.selectedOption === null) {
          this.showToast('请选择一个答案')
          return
        }
        answer = this.questionOptions[this.selectedOption]
      } else {
        if (!this.userAnswer.trim()) {
          this.showToast('请输入你的答案')
          return
        }
        answer = this.userAnswer.trim()
      }
      this.submitting = true
      this.isAnswerCorrect = answer === this.correctAnswer
      this.showResult = true
      this.submitting = false
      const kpId = this.practiceKnowledge.id
      this.recordPractice(kpId, this.isAnswerCorrect)
      if (this.isAnswerCorrect) {
        this.showToast('🎉 回答正确！')
      } else {
        this.showToast('❌ 回答错误，正确答案是：' + this.correctAnswer)
      }
    },
    
    generateExplanation(kp) {
      const explanations = {
        '导数': '导数是函数在某一点的变化率，几何意义是切线的斜率。\n\n基本公式：\n• (xⁿ)\' = nxⁿ⁻¹\n• (sin x)\' = cos x\n• (cos x)\' = -sin x\n• (e^x)\' = e^x',
        '函数': '函数是描述变量之间关系的数学工具。\n\n常见函数类型：\n• 一次函数：y = kx + b\n• 二次函数：y = ax² + bx + c\n• 指数函数：y = a^x\n• 对数函数：y = logₐx',
        '三角函数': '三角函数是研究三角形和圆的重要工具。\n\n基本公式：\n• sin²θ + cos²θ = 1\n• sin(α±β) = sinαcosβ ± cosαsinβ\n• cos(α±β) = cosαcosβ ∓ sinαsinβ',
        '数列': '数列是按一定顺序排列的一列数。\n\n常见数列：\n• 等差数列：aₙ = a₁ + (n-1)d\n• 等比数列：aₙ = a₁·qⁿ⁻¹\n• 求和公式：Sₙ = n(a₁+aₙ)/2'
      }
      for (const [key, value] of Object.entries(explanations)) {
        if (kp.name.includes(key)) return value
      }
      return `${kp.name}是数学中的重要概念，建议通过练习加深理解。\n\n💡 提示：多做练习，掌握核心公式和定理。`
    },
    
    generateQuestions(kp, count = 3) {
      const questions = []
      const name = kp.name
      for (let i = 0; i < count; i++) {
        if (i === 0) {
          questions.push({ question: `请简要说明${name}的定义。`, options: [], answer: `${name}的基本定义描述` })
        } else if (i === 1) {
          questions.push({ question: `请写出${name}的一个核心公式。`, options: [], answer: `${name}的相关公式` })
        } else {
          questions.push({ question: `${name}在解题中有什么作用？`, options: [], answer: `${name}在解题中的应用` })
        }
      }
      return questions
    },
    
    triggerPracticeUpload() {
      this.$refs.practiceFileInput.click()
    },
    
    handlePracticeUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      this.practiceUploadFile = file
      const reader = new FileReader()
      reader.onload = (e) => {
        this.practiceUploadPreview = e.target.result
      }
      reader.readAsDataURL(file)
      this.ocrResult = null
      this.ocrJudged = false
      this.showToast('📷 图片已上传，点击"识别并判断"')
    },
    
    async analyzePracticeImage() {
      if (!this.practiceUploadFile) {
        this.showToast('请先上传图片')
        return
      }
      this.analyzing = true
      try {
        const formData = new FormData()
        formData.append('file', this.practiceUploadFile)
        const res = await axios.post(`${API_BASE}/api/tools/ocr/recognize`, formData, {
          headers: { 'Authorization': 'Bearer ' + this.token }
        })
        if (res.data.code === 200) {
          this.ocrResult = res.data.data.recognized_text
          const keywords = ['正确', '对', 'right', 'correct', 'yes']
          const isCorrect = keywords.some(kw => this.ocrResult.toLowerCase().includes(kw))
          this.ocrIsCorrect = isCorrect
          this.ocrJudged = true
          const kpId = this.practiceKnowledge.id
          await this.recordPractice(kpId, isCorrect)
          this.showToast(isCorrect ? '✅ 判断正确！' : '❌ 判断错误！')
        }
      } catch (error) {
        this.showToast('❌ 识别失败：' + error.message)
      }
      this.analyzing = false
    },
    
    savePracticeResult() {
      this.showToast('💾 练习记录已保存')
      this.closePracticeModal()
      this.loadKnowledge()
      this.loadDashboard()
      this.runAutoCheck()
    },
    
    // ===== 学生详情（教师端） =====
    viewStudentDetail(student) {
      this.selectedStudent = student
      this.showStudentDetail = true
    },
    
    closeStudentDetail() {
      this.showStudentDetail = false
      this.selectedStudent = {}
    },
    
    generateStudentReport(student) {
      this.showToast(`📄 正在生成 ${student.name} 的学习报告...`)
    },
    
    // ===== 新增功能 =====
    // 学习计时器
    toggleTimer() {
      if (this.isTimerRunning) {
        clearInterval(this.timerInterval)
        this.timerInterval = null
        this.saveStudyRecord()
      } else {
        this.timerInterval = setInterval(() => {
          this.studySeconds++
        }, 1000)
      }
      this.isTimerRunning = !this.isTimerRunning
    },
    
    resetTimer() {
      if (this.isTimerRunning) {
        clearInterval(this.timerInterval)
        this.timerInterval = null
        this.isTimerRunning = false
      }
      this.studySeconds = 0
    },
    
    formatTimer(seconds) {
      const h = Math.floor(seconds / 3600)
      const m = Math.floor((seconds % 3600) / 60)
      const s = seconds % 60
      return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
    },
    
    saveStudyRecord() {
      if (this.studySeconds > 60) {
        const record = {
          date: new Date().toISOString(),
          seconds: this.studySeconds,
          hours: Math.round(this.studySeconds / 3600 * 10) / 10
        }
        this.studyRecords.push(record)
        localStorage.setItem('studyRecords', JSON.stringify(this.studyRecords))
        this.showToast(`📚 学习了 ${this.formatTimer(this.studySeconds)}，继续加油！`)
      }
      this.studySeconds = 0
    },
    
    // 学习目标
    addGoal() {
      if (!this.newGoalContent.trim()) {
        this.showToast('请输入目标内容')
        return
      }
      this.goals.push({
        id: ++this.goalIdCounter,
        content: this.newGoalContent,
        deadline: this.newGoalDeadline || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        completed: false,
        created_at: new Date().toISOString()
      })
      localStorage.setItem('goals', JSON.stringify(this.goals))
      this.newGoalContent = ''
      this.newGoalDeadline = ''
      this.showAddGoal = false
      this.showToast('✅ 目标添加成功！')
    },
    
    updateGoal(goal) {
      localStorage.setItem('goals', JSON.stringify(this.goals))
      if (goal.completed) {
        this.showToast('🎉 恭喜完成目标！')
      }
    },
    
    deleteGoal(id) {
      this.goals = this.goals.filter(g => g.id !== id)
      localStorage.setItem('goals', JSON.stringify(this.goals))
    },
    
    // 掌握度热力图
    getMasteryColor(accuracy) {
      if (!accuracy) return '#e5e7eb'
      if (accuracy >= 80) return '#22c55e'
      if (accuracy >= 60) return '#f59e0b'
      if (accuracy >= 40) return '#f97316'
      return '#ef4444'
    },
    
    // 趋势指示
    getTrendClass(value) {
      if (value >= 70) return 'up'
      if (value >= 50) return 'neutral'
      return 'down'
    },

    getMasteryColor(value) {
      const v = value || 0
      if (v >= 80) return '#22c55e'
      if (v >= 60) return '#f59e0b'
      if (v >= 40) return '#f97316'
      return '#ef4444'
    },
    
    getTrendIcon(value) {
      if (value >= 70) return '📈'
      if (value >= 50) return '➡️'
      return '📉'
    },
    
    // 艾宾浩斯遗忘曲线
    getReviewSchedule(kp) {
      const days = (Date.now() - new Date(kp.last_review_date).getTime()) / (1000 * 60 * 60 * 24)
      if (days >= 14) return { urgency: 'critical', label: '🔴 急需复习' }
      if (days >= 7) return { urgency: 'warning', label: '🟡 建议复习' }
      if (days >= 3) return { urgency: 'normal', label: '🟢 可以复习' }
      return { urgency: 'good', label: '✅ 掌握良好' }
    },
    
    // 学习路径推荐
    generateLearningPath() {
      const weakPoints = this.knowledgeList.filter(k => k.mastery_level === 'weak' || k.mastery_level === 'critical')
      if (weakPoints.length === 0) {
        this.showToast('🎉 没有薄弱知识点，继续保持！')
        this.learningPath = [
          { title: '巩固优势', description: '继续练习已掌握的知识点，挑战更高难度' },
          { title: '拓展学习', description: '尝试学习新的知识点，扩展知识面' }
        ]
        return
      }
      this.showToast('🧠 正在生成学习路径...')
      this.learningPath = weakPoints.slice(0, 5).map((kp, idx) => ({
        title: `${idx + 1}. ${kp.name} 专项突破`,
        description: `正确率 ${kp.accuracy}%，建议每天练习 3-5 道相关题目`
      }))
      this.learningPath.push({
        title: '综合复习',
        description: '将薄弱知识点串联，进行综合练习'
      })
      this.showToast('✅ 学习路径生成完成！')
    },
    
    // 智能出题
    generateQuiz() {
      this.showQuizSettings = !this.showQuizSettings
      if (this.showQuizSettings && this.knowledgeList.length > 0) {
        this.quizConfig.knowledge = this.knowledgeList[0].name
      }
    },
    
    generateQuizQuestions() {
      if (!this.quizConfig.knowledge) {
        this.showToast('请选择知识点')
        return
      }
      this.showToast('🎯 正在生成题目...')
      const questions = [
        { content: `${this.quizConfig.knowledge}的核心概念是什么？`, options: ['A. 概念A', 'B. 概念B', 'C. 概念C', 'D. 概念D'], answer: 'A' },
        { content: `${this.quizConfig.knowledge}在实际中的应用？`, options: ['A. 应用A', 'B. 应用B', 'C. 应用C', 'D. 应用D'], answer: 'B' }
      ]
      this.quizQuestions = questions
      this.showToast(`📝 已生成 ${questions.length} 道题目`)
      this.showQuizSettings = false
    },
    
    // 报告生成
    generateWeeklyReport() {
      this.showToast('📊 正在生成报告...')
      const weakPoints = this.knowledgeList.filter(k => k.mastery_level === 'weak' || k.mastery_level === 'critical')
      const masteredPoints = this.knowledgeList.filter(k => k.mastery_level === 'mastered')
      this.reportData = {
        total_hours: this.dashboardStats.weekly_learning_hours || 0,
        avg_accuracy: this.dashboardStats.average_accuracy || 0,
        mastered_count: masteredPoints.length,
        weak_count: weakPoints.length,
        strengths: masteredPoints.slice(0, 3).map(k => k.name) || ['暂无数据'],
        weaknesses: weakPoints.slice(0, 3).map(k => k.name) || [],
        recommendations: weakPoints.length > 0 
          ? weakPoints.map(k => `📌 重点复习 ${k.name}，正确率 ${k.accuracy}%`)
          : ['🎉 没有薄弱知识点，继续拓展学习']
      }
      this.showReportModal = true
      this.showToast('✅ 报告生成完成！')
    },
    
    exportReportPDF() {
      this.showToast('📥 正在导出PDF...')
      setTimeout(() => {
        this.showToast('✅ 报告已导出！')
      }, 1500)
    },
    
    // 通知权限
    requestNotificationPermission() {
      if ('Notification' in window) {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            this.showToast('✅ 通知权限已开启！')
            new Notification('📚 智能学情分析', {
              body: '通知已开启，我们会提醒您学习！',
              icon: '/favicon.ico'
            })
          } else {
            this.showToast('⚠️ 通知权限被拒绝')
          }
        })
      } else {
        this.showToast('⚠️ 浏览器不支持通知')
      }
    },
    
    // 查看详情跳转
    viewDetail(type) {
      if (type === 'knowledge') this.activeMenu = 'knowledge'
      else if (type === 'timer') this.showToast('⏱️ 继续学习，保持专注！')
      else if (type === 'weak') this.activeMenu = 'alert'
      else if (type === 'accuracy') this.showToast('📝 多做练习，提升正确率！')
      else if (type === 'continuous') this.showToast('🔥 保持学习习惯，继续加油！')
      else if (type === 'task') this.activeMenu = 'task'
    },
    
    checkStudyReminder() {
      setInterval(() => {
        const lastStudy = localStorage.getItem('lastStudyTime')
        if (lastStudy && (Date.now() - new Date(lastStudy).getTime()) > 2 * 60 * 60 * 1000) {
          if (Notification.permission === 'granted') {
            new Notification('📚 该学习啦！', {
              body: '您已经2小时没有学习了，坚持每天进步一点点！',
              icon: '/favicon.ico'
            })
          }
        }
      }, 30 * 60 * 1000)
    },
    
    // ===== 通用 =====
    exportReport() {
      this.showToast('📥 学情周报已生成，开始下载')
    },
    
    showToast(msg) {
      this.toasts.push({ message: msg })
      setTimeout(() => this.toasts.shift(), 3000)
    },

    getToastType(msg) {
      if (!msg) return 'toast-info'
      if (msg.startsWith('✅') || msg.startsWith('🎉') || msg.startsWith('🔥')) return 'toast-success'
      if (msg.startsWith('⚠️') || msg.startsWith('❗')) return 'toast-warning'
      if (msg.startsWith('❌') || msg.startsWith('🗑️')) return 'toast-error'
      if (msg.startsWith('📥') || msg.startsWith('🔄') || msg.startsWith('📊')) return 'toast-info'
      return 'toast-info'
    },

    // 加载孩子列表
  async loadChildren() {
    try {
      const res = await axios.get(`${API_BASE}/api/parent/children`, {
        headers: { 'Authorization': 'Bearer ' + this.token }
      })
      if (res.data.code === 200) {
        this.childrenList = res.data.data || []
      }
    } catch (e) {
      console.error('加载孩子列表失败:', e)
    }
  },

  // 绑定孩子
  async bindChild() {
    if (!this.childUsername) {
      this.showToast('请输入孩子用户名')
      return
    }
    try {
      const res = await axios.post(`${API_BASE}/api/parent/bind-child?child_code=${this.childUsername}`, {}, {
        headers: { 'Authorization': 'Bearer ' + this.token }
      })
      if (res.data.code === 200) {
        this.showToast('✅ 绑定成功！')
        this.childUsername = ''
        await this.loadChildren()
      } else {
        this.showToast('❌ ' + res.data.message)
      }
    } catch (e) {
      this.showToast('❌ 绑定失败：' + e.message)
    }
  },
  // 查看孩子详情
  viewChildDetail(child) {
    this.selectedChild = child
    this.childViewMode = true
    this.showChildDetail = true
  
  // 切换到孩子的学情数据
    this.loadChildDashboard(child.id)
    this.loadChildKnowledge(child.id)
    this.loadChildTasks(child.id)
  
    this.showToast(`📊 正在查看 ${child.name} 的学情`)
  },

// 返回家长总览
  backToParentDashboard() {
    this.childViewMode = false
    this.selectedChild = null
    this.showChildDetail = false
  // 重新加载家长自己的数据
    this.loadAllData()
  },

// 加载孩子看板数据
  async loadChildDashboard(childId) {
    try {
      const res = await axios.get(`${API_BASE}/api/dashboard/stats/${childId}`, {
        headers: { 'Authorization': 'Bearer ' + this.token }
      })
      if (res.data.code === 200) {
        this.dashboardStats = res.data.data
      }
    } catch (e) {
      console.error('加载孩子看板失败:', e)
    }
  },

// 加载孩子知识点
  async loadChildKnowledge(childId) {
    try {
      const res = await axios.get(`${API_BASE}/api/knowledge/user/${childId}`, {
        headers: { 'Authorization': 'Bearer ' + this.token }
      })
      if (res.data.code === 200) {
        this.knowledgeList = res.data.data || []
      }
    } catch (e) {
      this.knowledgeList = []
    }
  },

// 加载孩子任务
  async loadChildTasks(childId) {
    try {
      const res = await axios.get(`${API_BASE}/api/task/user/${childId}`, {
        headers: { 'Authorization': 'Bearer ' + this.token }
      })
      if (res.data.code === 200) {
        this.taskList = res.data.data || []
      }
    } catch (e) {
      this.taskList = []
    }
  },

    // ===== 班级相关方法 =====

// 加载班级列表
async loadClassList() {
  try {
    const res = await axios.get(`${API_BASE}/api/teacher/class-overview`, {
      headers: { 'Authorization': 'Bearer ' + this.token }
    })
    if (res.data.code === 200) {
      this.classList = res.data.data
    }
  } catch (e) {
    console.error('加载班级列表失败:', e)
  }
},

// 创建班级
async createClass() {
  if (!this.newClassName || !this.newClassGrade) {
    this.showToast('请填写班级名称和年级')
    return
  }
  try {
    const res = await axios.post(`${API_BASE}/api/teacher/create-class`, {
      name: this.newClassName,
      grade: this.newClassGrade
    }, { headers: { 'Authorization': 'Bearer ' + this.token } })
    if (res.data.code === 200) {
      this.showToast('✅ 班级创建成功！')
      this.showCreateClass = false
      this.newClassName = ''
      this.newClassGrade = ''
      this.loadClassList()
    }
  } catch (e) {
    this.showToast('❌ 创建失败：' + e.message)
  }
},

// 查看班级详情
async viewClassDetail(classId) {
  try {
    const res = await axios.get(`${API_BASE}/api/teacher/class-students/${classId}`, {
      headers: { 'Authorization': 'Bearer ' + this.token }
    })
    if (res.data.code === 200) {
      this.currentClass = res.data.data
      this.showClassDetail = true
    }
  } catch (e) {
    this.showToast('❌ 加载失败：' + e.message)
  }
},

// 复制邀请码
copyClassCode(code) {
  navigator.clipboard.writeText(code)
  this.showToast('📋 邀请码已复制！')
},

// 学生加入班级
async joinClass() {
  if (!this.className) {
    this.showToast('请输入班级邀请码')
    return
  }
  try {
    const res = await axios.post(`${API_BASE}/api/student/join-class`, {
      class_code: this.className
    }, { headers: { 'Authorization': 'Bearer ' + this.token } })
    if (res.data.code === 200) {
      this.showToast('✅ 加入班级成功！')
      this.className = ''
    } else {
      this.showToast('❌ ' + res.data.message)
    }
  } catch (e) {
    this.showToast('❌ 加入失败：' + e.message)
  }
},
    
    loadGoals() {
      const goals = localStorage.getItem('goals')
      if (goals) {
        try {
          this.goals = JSON.parse(goals)
          if (this.goals.length > 0) {
            this.goalIdCounter = Math.max(...this.goals.map(g => g.id), 0)
          }
        } catch (e) {
          this.goals = []
        }
      }
    },
    
    loadStudyRecords() {
      const records = localStorage.getItem('studyRecords')
      if (records) {
        try {
          this.studyRecords = JSON.parse(records)
        } catch (e) {
          this.studyRecords = []
        }
      }
    }
  },
  
  mounted() {
    this.handleResize()
    window.addEventListener('resize', this.handleResize)
    
    // 恢复主题
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) this.theme = savedTheme
    
    // 恢复登录状态
    const token = localStorage.getItem('token')
    const userInfo = localStorage.getItem('userInfo')
    const userRole = localStorage.getItem('userRole')
    if (token && userInfo) {
      this.token = token
      this.userInfo = JSON.parse(userInfo)
      this.currentRole = userRole || 'student'
      if (this.userInfo && this.userInfo.original_role) {
        this.currentRole = this.userInfo.original_role
      } else {
        this.currentRole = userRole || 'student'
      }
      this.isLogin = true
      this.loadAllData()
    }
    
    // 加载本地数据
    this.loadGoals()
    this.loadStudyRecords()
    this.checkStudyReminder()
  },
  
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.timerInterval) {
      clearInterval(this.timerInterval)
      this.saveStudyRecord()
    }
  }
}
</script>

<style>
/* ===== 完整样式 ===== */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; padding-bottom: env(safe-area-inset-bottom); }

/* ===== 主题 ===== */
.light-mode {
  --bg-primary: #f0f2f5;
  --bg-card: #ffffff;
  --text-primary: #1a2332;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
  --shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.dark-mode {
  --bg-primary: #0f0f1a;
  --bg-card: #16213e;
  --text-primary: #ffffff;
  --text-secondary: #a0aec0;
  --border-color: #2d3748;
  --shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.dark-mode .stat-card,
.dark-mode .dashboard-chart,
.dark-mode .dashboard-quick,
.dark-mode .reflect-container,
.dark-mode .task-progress-card,
.dark-mode .task-card,
.dark-mode .knowledge-card,
.dark-mode .alert-card,
.dark-mode .alert-stat-card,
.dark-mode .upload-section,
.dark-mode .result-section,
.dark-mode .chat-main,
.dark-mode .chat-input-area,
.dark-mode .study-timer-card,
.dark-mode .goals-section,
.dark-mode .mastery-heatmap-section,
.dark-mode .learning-path-section,
.dark-mode .forgetting-curve-section,
.dark-mode .parent-alerts,
.dark-mode .student-list,
.dark-mode .leaderboard-section {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
}

.dark-mode .stat-label,
.dark-mode .header-count,
.dark-mode .reflect-section-title,
.dark-mode .reflect-card-desc,
.dark-mode .task-desc,
.dark-mode .knowledge-card-body,
.dark-mode .alert-desc,
.dark-mode .history-empty,
.dark-mode .sidebar-title {
  color: var(--text-secondary) !important;
}

.dark-mode .page-header h2,
.dark-mode .dashboard-chart h3,
.dark-mode .dashboard-quick h3,
.dark-mode .reflect-title,
.dark-mode .task-title,
.dark-mode .knowledge-name,
.dark-mode .alert-title,
.dark-mode .goals-header h3,
.dark-mode .mastery-heatmap-section h3,
.dark-mode .learning-path-section .path-header h3,
.dark-mode .forgetting-curve-section h3 {
  color: var(--text-primary) !important;
}

.dark-mode .stat-value {
  color: var(--text-primary) !important;
}

.dark-mode .detail-table td,
.dark-mode .detail-table td:first-child {
  color: var(--text-primary) !important;
}

.dark-mode .input-sm,
.dark-mode .select-sm,
.dark-mode .chat-input {
  background: var(--bg-primary) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-color) !important;
}

.dark-mode .modal-content,
.dark-mode .modal-header,
.dark-mode .modal-footer {
  background: var(--bg-card) !important;
}

.dark-mode .modal-header h2 {
  color: var(--text-primary) !important;
}

.dark-mode .modal-close {
  color: var(--text-secondary) !important;
}

.dark-mode .modal-close:hover {
  background: var(--bg-primary) !important;
}

.dark-mode .btn-modal.secondary {
  background: var(--bg-primary) !important;
  color: var(--text-secondary) !important;
}

.dark-mode .detail-label {
  color: var(--text-secondary) !important;
}

.dark-mode .detail-value {
  color: var(--text-primary) !important;
}

.dark-mode .tag-badge {
  background: var(--bg-primary) !important;
  color: var(--text-secondary) !important;
}

.dark-mode .toast-item {
  background: #1a2332 !important;
  color: #fff !important;
}

.dark-mode .history-sidebar {
  background: #0f0f1a !important;
}

/* ===== 登录页面 ===== */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.login-blob {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
  animation: float 8s ease-in-out infinite;
}

.login-blob.blob-1 {
  width: 500px;
  height: 500px;
  background: #667eea;
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.login-blob.blob-2 {
  width: 400px;
  height: 400px;
  background: #764ba2;
  bottom: -50px;
  left: -50px;
  animation-delay: 2s;
}

.login-blob.blob-3 {
  width: 300px;
  height: 300px;
  background: #f093fb;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

.login-box {
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 24px;
  padding: 48px 40px;
  width: 420px;
  position: relative;
  z-index: 1;
  box-shadow: 0 25px 80px rgba(0,0,0,0.4);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header .login-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.5px;
}

.login-header p {
  font-size: 14px;
  color: rgba(255,255,255,0.6);
  margin-top: 4px;
  letter-spacing: 2px;
}

.login-tabs {
  display: flex;
  justify-content: center;
  gap: 0;
  margin-bottom: 24px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.1);
}

.login-tab {
  flex: 1;
  padding: 10px 0;
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.5);
  border: none;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s;
}

.login-tab.active {
  background: rgba(102,126,234,0.3);
  color: #fff;
}

.login-tab:hover {
  background: rgba(255,255,255,0.1);
}

.login-form .input-group {
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 0 16px;
  margin-bottom: 16px;
  transition: all 0.3s;
}

.login-form .input-group:focus-within {
  border-color: #667eea;
  background: rgba(255,255,255,0.1);
  box-shadow: 0 0 0 4px rgba(102,126,234,0.15);
}

.login-form .input-icon {
  font-size: 18px;
  color: rgba(255,255,255,0.4);
  margin-right: 12px;
}

.login-form input {
  flex: 1;
  padding: 16px 0;
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  font-size: 15px;
}

.login-form input::placeholder {
  color: rgba(255,255,255,0.3);
}

.role-select-group {
  margin-bottom: 12px;
}

.role-select-group label {
  font-size: 14px;
  color: rgba(255,255,255,0.7);
  display: block;
  margin-bottom: 8px;
}

.role-options {
  display: flex;
  gap: 8px;
}

.role-option {
  flex: 1;
  padding: 10px 8px;
  background: rgba(255,255,255,0.06);
  border: 2px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  color: rgba(255,255,255,0.5);
}

.role-option:hover {
  border-color: rgba(255,255,255,0.3);
}

.role-option.active {
  border-color: #667eea;
  background: rgba(102,126,234,0.2);
  color: #fff;
}

.role-option .role-icon {
  font-size: 24px;
  display: block;
  margin-bottom: 4px;
}

.role-option span:last-child {
  font-size: 12px;
}

.login-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  margin-top: 8px;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(102,126,234,0.4);
}

.login-btn .btn-arrow {
  transition: transform 0.3s;
}

.login-btn:hover .btn-arrow {
  transform: translateX(4px);
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  color: rgba(255,255,255,0.3);
  font-size: 13px;
}

.error {
  color: #ff6b6b;
  margin-top: 12px;
  text-align: center;
  font-size: 14px;
}

/* ===== 主布局 ===== */
.main-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-primary);
}

/* ===== 顶部导航 ===== */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 24px;
  background: #1a2332;
  flex-shrink: 0;
  min-height: 56px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  width: auto;
}

.logo-badge {
  font-size: 9px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  padding: 2px 8px;
  border-radius: 20px;
}

.logo-text-wrap {
  display: flex;
  flex-direction: column;
  gap:4px;
}

.theme-toggle {
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 16px;
  cursor: pointer;
  color: #fff;
  transition: all 0.2s;
}

.theme-toggle:hover {
  background: rgba(255,255,255,0.2);
}

.nav-center {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.nav-menu-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: rgba(255,255,255,0.5);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.nav-menu-item:hover {
  color: #fff;
  background: rgba(255,255,255,0.06);
}

.nav-menu-item.active {
  color: #fff;
  background: rgba(102,126,234,0.2);
}

.nav-badge {
  position: absolute;
  top: 0;
  right: 2px;
  background: #ef4444;
  color: #fff;
  font-size: 9px;
  padding: 1px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  font-size: 13px;
  color: rgba(255,255,255,0.7);
}

.user-role-badge {
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 12px;
  background: rgba(102,126,234,0.3);
  color: #667eea;
  border: 1px solid rgba(102,126,234,0.2);
}

.user-avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 13px;
}

.logout-btn-small {
  padding: 4px 10px;
  border: none;
  border-radius: 6px;
  background: rgba(239,68,68,0.15);
  color: #ef4444;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn-small:hover {
  background: rgba(239,68,68,0.3);
}

.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  color: #fff;
  font-size: 22px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 8px;
  transition: background 0.2s;
}

.mobile-menu-btn:active {
  background: rgba(255,255,255,0.1);
}

/* ===== 移动端折叠导航面板 ===== */
.mobile-nav-panel {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #1a2332;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  max-height: 70vh;
  overflow-y: auto;
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;
}

.mobile-nav-list {
  display: flex;
  flex-direction: column;
  padding: 60px 12px 16px;
  gap: 4px;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: rgba(255,255,255,0.75);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.mobile-nav-item:active {
  background: rgba(255,255,255,0.08);
  transform: scale(0.98);
}

.mobile-nav-item.active {
  background: linear-gradient(135deg, rgba(102,126,234,0.25), rgba(118,75,162,0.2));
  color: #fff;
  font-weight: 600;
}

.mobile-nav-icon {
  font-size: 20px;
  width: 28px;
  text-align: center;
}

.mobile-nav-label {
  flex: 1;
}

.mobile-nav-arrow {
  font-size: 20px;
  color: rgba(255,255,255,0.3);
}

.mobile-nav-item.active .mobile-nav-arrow {
  color: #667eea;
}

.mobile-nav-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 999;
}

/* 折叠动画 */
.nav-collapse-enter-active,
.nav-collapse-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.nav-collapse-enter-from,
.nav-collapse-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* ===== 主内容 ===== */
.main-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  overflow: hidden;
}

.content-area {
  flex: 1;
  padding: 20px 28px;
  overflow-y: auto;
}

/* ===== 侧边栏 ===== */
.history-sidebar {
  width: 220px;
  background: #1a2332;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.3s;
  overflow: hidden;
}

.history-sidebar.collapsed {
  width: 48px;
}

.history-sidebar.collapsed .sidebar-title {
  display: none;
}

.history-sidebar.collapsed .sidebar-badge {
  display: none;
}

.history-sidebar.collapsed .sidebar-body {
  display: none;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  cursor: pointer;
  color: rgba(255,255,255,0.5);
  transition: all 0.3s;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}

.sidebar-header:hover {
  color: #fff;
  background: rgba(255,255,255,0.04);
}

.sidebar-icon {
  font-size: 12px;
}

.sidebar-title {
  font-size: 13px;
  font-weight: 500;
  flex: 1;
}

.sidebar-badge {
  font-size: 10px;
  background: #667eea;
  color: #fff;
  padding: 1px 8px;
  border-radius: 12px;
}

.sidebar-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 12px;
  overflow: hidden;
}

.history-list {
  flex: 1;
  overflow-y: auto;
}

.history-list::-webkit-scrollbar {
  width: 3px;
}

.history-list::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.15);
  border-radius: 2px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: rgba(255,255,255,0.4);
  font-size: 13px;
}

.history-item:hover {
  background: rgba(255,255,255,0.06);
  color: #fff;
}

.history-item .history-icon {
  font-size: 12px;
  opacity: 0.4;
}

.history-item .history-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-empty {
  font-size: 12px;
  color: rgba(255,255,255,0.2);
  text-align: center;
  padding: 16px 0;
}

.sidebar-footer {
  border-top: 1px solid rgba(255,255,255,0.06);
  padding-top: 12px;
  margin-top: auto;
}

.clear-history-btn {
  width: 100%;
  padding: 6px;
  border: none;
  border-radius: 6px;
  background: rgba(239,68,68,0.12);
  color: rgba(239,68,68,0.6);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
}

.clear-history-btn:hover {
  background: rgba(239,68,68,0.25);
  color: #ef4444;
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 6px;
  background: rgba(255,255,255,0.04);
}

.sidebar-user .user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 12px;
  flex-shrink: 0;
}

.sidebar-user-name {
  font-size: 12px;
  color: rgba(255,255,255,0.6);
}

/* ===== 遮罩 ===== */
.sidebar-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 998;
}

.sidebar-overlay.active {
  display: block;
}

/* ===== 页面通用 ===== */
.page-container {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.dashboard-header {
  align-items: flex-end;
}

.header-greeting h2 {
  font-size: 20px;
  color: var(--text-primary);
  margin: 0;
}

.greeting-sub {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  position: relative;
}

.report-dropdown {
  position: relative;
}

.report-dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  padding: 4px;
  min-width: 130px;
  z-index: 100;
}

.report-dropdown-menu button {
  display: block;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 13px;
  text-align: left;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.report-dropdown-menu button:hover {
  background: var(--bg-primary);
}

/* 迷你计时器按钮 */
.timer-mini-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-variant-numeric: tabular-nums;
}

.timer-mini-btn:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.timer-mini-btn.running {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  border-color: transparent;
  animation: timer-pulse 2s ease-in-out infinite;
}

.timer-mini-btn.running:hover {
  filter: brightness(1.08);
}

.timer-mini-icon {
  font-size: 14px;
}

.timer-mini-time {
  letter-spacing: 0.5px;
}

.timer-reset-btn {
  padding: 7px 8px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  line-height: 1;
}

.timer-reset-btn:hover {
  background: #fee2e2;
  color: #ef4444;
  border-color: #fca5a5;
}

@keyframes timer-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
}

.page-header h2 {
  font-size: 20px;
  color: var(--text-primary);
}

.header-count {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 400;
}

.header-actions-full {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: center;
}

/* ===== 学习计时器 ===== */
.study-timer-card {
  background: var(--bg-card);
  padding: 16px 24px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.timer-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timer-icon {
  font-size: 28px;
}

.timer-text {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Monaco', monospace;
}

.timer-controls {
  display: flex;
  gap: 8px;
}

.timer-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}

.timer-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102,126,234,0.3);
}

.timer-btn.running {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.timer-btn.reset {
  background: #e5e7eb;
  color: #6b7280;
}

.timer-btn.reset:hover {
  background: #d1d5db;
  box-shadow: none;
}

.timer-tips {
  font-size: 14px;
  color: var(--text-secondary);
  flex: 1;
  text-align: right;
}

/* ===== 学习目标 ===== */
.goals-section {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

.goals-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.goals-header h3 {
  font-size: 15px;
  color: var(--text-primary);
}

.btn-add-goal {
  padding: 4px 16px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-goal:hover {
  transform: scale(1.05);
}

.goal-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.goal-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.goal-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.goal-item span {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
}

.goal-item .completed {
  text-decoration: line-through;
  color: var(--text-secondary);
}

.goal-deadline {
  font-size: 12px;
  color: var(--text-secondary);
}

.goal-delete {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 14px;
  padding: 0 4px;
}

.goal-delete:hover {
  color: #dc2626;
}

.empty-goals {
  text-align: center;
  padding: 16px;
  color: var(--text-secondary);
}

.empty-goals span {
  font-size: 32px;
  display: block;
  margin-bottom: 4px;
}

/* ===== 掌握度热力图 ===== */
.mastery-heatmap-section {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

.mastery-heatmap-section h3 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
}

.heatmap-grid.small {
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
}

.heatmap-item {
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
  color: #fff;
  font-weight: 500;
}

.heatmap-item:hover {
  transform: scale(1.05);
}

.heatmap-item.small {
  padding: 4px 8px;
  font-size: 12px;
}

.heatmap-label {
  flex: 1;
}

.heatmap-score {
  background: rgba(0,0,0,0.15);
  padding: 0 6px;
  border-radius: 4px;
  font-size: 12px;
}

/* ===== 学习路径 ===== */
.learning-path-section {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

.path-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.path-header h3 {
  font-size: 15px;
  color: var(--text-primary);
}

.btn-path {
  padding: 4px 16px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-path:hover {
  transform: scale(1.05);
}

.path-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.path-step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 600;
  color: var(--text-primary);
  display: block;
}

.step-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.empty-path {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
}

.empty-path span {
  font-size: 32px;
  display: block;
  margin-bottom: 4px;
}

/* ===== 艾宾浩斯遗忘曲线 ===== */
.forgetting-curve-section {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

.forgetting-curve-section h3 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.review-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.review-item span:first-child {
  flex: 1;
  color: var(--text-primary);
  font-weight: 500;
}

.review-badge {
  font-size: 10px;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.review-badge.critical {
  background: #fee2e2;
  color: #dc2626;
}

.review-badge.warning {
  background: #fef3c7;
  color: #d97706;
}

.review-badge.normal {
  background: #dbeafe;
  color: #2563eb;
}

.review-badge.good {
  background: #dcfce7;
  color: #16a34a;
}

.empty-review {
  text-align: center;
  padding: 12px;
  color: var(--text-secondary);
}

/* ===== 统计卡片 ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  transition: all 0.2s;
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.stat-card--blue   { border-left: 4px solid #667eea; }
.stat-card--green  { border-left: 4px solid #2ecc71; }
.stat-card--orange { border-left: 4px solid #f39c12; }
.stat-card--red    { border-left: 4px solid #e74c3c; }
.stat-card--amber  { border-left: 4px solid #f59e0b; }
.stat-card--purple { border-left: 4px solid #8b5cf6; }

.stat-icon {
  font-size: 28px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-trend {
  font-size: 11px;
  font-weight: 500;
  margin-top: 2px;
}

.stat-progress-bar {
  width: 100%;
  height: 6px;
  background: var(--bg-primary);
  border-radius: 3px;
  margin-top: 6px;
  overflow: hidden;
}

.stat-progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.stat-trend.up {
  color: #22c55e;
}

.stat-trend.down {
  color: #ef4444;
}

.stat-trend.neutral {
  color: #f59e0b;
}

/* ===== 双栏 ===== */
.dashboard-two-col {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.dashboard-chart {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
}

.dashboard-chart h3 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.trend-chart {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  height: 120px;
  padding: 0 4px;
}

.trend-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.trend-bar-wrapper {
  flex: 1;
  display: flex;
  align-items: flex-end;
  width: 100%;
}

.trend-bar {
  width: 100%;
  background: linear-gradient(180deg, #667eea, #764ba2);
  border-radius: 6px 6px 0 0;
  min-height: 8px;
  position: relative;
  transition: height 0.5s ease;
}

.trend-bar .trend-value {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: var(--text-secondary);
}

.trend-label {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 4px;
}

.dashboard-quick {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
}

.dashboard-quick h3 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.pie-chart {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pie-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-primary);
}

.pie-color {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  display: inline-block;
}

.pie-color.mastered {
  background: #22c55e;
}

.pie-color.medium {
  background: #f59e0b;
}

.pie-color.weak {
  background: #f97316;
}

.pie-color.critical {
  background: #ef4444;
}

.pie-total {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
  padding-top: 6px;
  border-top: 1px solid var(--border-color);
}

/* ===== 反思闭环 ===== */
.reflect-container {
  background: var(--bg-card);
  border-radius: 14px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

.reflect-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  background: linear-gradient(135deg, #1a2332, #2c3e50);
  color: #fff;
}

.reflect-title {
  font-size: 15px;
  font-weight: 600;
  flex: 1;
}

.reflect-badge {
  background: #ef4444;
  color: #fff;
  font-size: 11px;
  padding: 1px 10px;
  border-radius: 20px;
}

.reflect-status-text {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
}

.reflect-body {
  padding: 14px 16px;
}

.reflect-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.reflect-section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.reflect-card {
  padding: 8px 12px;
  margin-bottom: 6px;
  border-radius: 8px;
  border-left: 3px solid #d1d5db;
}

.reflect-card.danger {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.reflect-card.success {
  background: #ecfdf5;
  border-left-color: #22c55e;
}

.reflect-card.primary {
  background: #eef2ff;
  border-left-color: #6366f1;
}

.reflect-card.warning {
  background: #fffbeb;
  border-left-color: #f59e0b;
}

.reflect-card-title {
  font-size: 13px;
  font-weight: 600;
}

.reflect-card.danger .reflect-card-title {
  color: #dc2626;
}

.reflect-card.success .reflect-card-title {
  color: #16a34a;
}

.reflect-card.primary .reflect-card-title {
  color: #4f46e5;
}

.reflect-card.warning .reflect-card-title {
  color: #d97706;
}

.reflect-card-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 2px 0;
}

.reflect-card-time {
  font-size: 10px;
  color: #9ca3af;
}

.reflect-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
  font-size: 11px;
  color: #9ca3af;
}

.reflect-card-actions {
  display: flex;
  gap: 6px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.reflect-card-btn {
  padding: 3px 10px;
  border: none;
  border-radius: 6px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.reflect-card-btn.danger {
  background: #ef4444;
  color: #fff;
}

.reflect-card-btn.danger:hover {
  background: #dc2626;
}

.reflect-card-btn.primary {
  background: #4f46e5;
  color: #fff;
}

.reflect-card-btn.primary:hover {
  background: #4338ca;
}

.reflect-card-btn.warning {
  background: #f59e0b;
  color: #fff;
}

.reflect-card-btn.warning:hover {
  background: #d97706;
}

.reflect-card-btn.outline {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.reflect-card-btn.outline:hover {
  background: var(--bg-primary);
}

.reflect-empty {
  text-align: center;
  color: var(--text-secondary);
  font-size: 12px;
  padding: 4px 0;
}

/* ===== AI对话 ===== */
.chat-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 0;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border-radius: 14px 14px 0 0;
  box-shadow: var(--shadow);
  overflow: hidden;
  min-height: 0;
}

.chat-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.chat-header-bar h2 {
  font-size: 18px;
  color: var(--text-primary);
}

.btn-quiz {
  padding: 6px 16px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-quiz:hover {
  transform: scale(1.05);
}

.btn-clear {
  padding: 6px 16px;
  border: none;
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear:hover {
  background: #fee2e2;
  color: #ef4444;
}

.btn-history {
  padding: 6px 14px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-history:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.btn-history.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border-color: transparent;
}

/* 聊天历史记录面板 */
.chat-history-panel {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  max-height: 220px;
  overflow-y: auto;
}

.chat-history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px 6px;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
  position: sticky;
  top: 0;
  background: var(--bg-card);
}

.chat-history-clear {
  padding: 2px 10px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #ef4444;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.chat-history-clear:hover {
  background: rgba(239, 68, 68, 0.1);
}

.chat-history-list {
  padding: 4px 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.chat-history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.chat-history-item:hover {
  background: var(--bg-primary);
}

.chat-history-item:active {
  transform: scale(0.98);
}

.chat-history-icon {
  font-size: 14px;
  opacity: 0.5;
}

.chat-history-text {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-history-empty {
  padding: 16px;
  text-align: center;
  font-size: 13px;
  color: var(--text-secondary);
  opacity: 0.6;
}

/* 历史面板滑入动画 */
.history-slide-enter-active,
.history-slide-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.history-slide-enter-from,
.history-slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.history-slide-enter-to,
.history-slide-leave-from {
  max-height: 220px;
  opacity: 1;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  min-height: 200px;
  max-height: 100%;
}

.chat-messages::-webkit-scrollbar {
  width: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  background: var(--bg-primary);
}

.message.user .message-avatar {
  background: #667eea;
}

.message-content {
  max-width: 75%;
  padding: 10px 16px;
  border-radius: 12px;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.message.user .message-content {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}

.message-content p {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.message-content .message-time {
  font-size: 11px;
  color: #999;
  display: block;
  margin-top: 4px;
  text-align: right;
}

.message.user .message-content .message-time {
  color: rgba(255,255,255,0.6);
}

.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  padding: 20px;
}

.chat-empty .empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.chat-empty p {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* ===== 输入区域 ===== */
.chat-input-area {
  flex-shrink: 0;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  border-radius: 0 0 14px 14px;
  padding: 6px 16px 10px 16px;
  transition: all 0.3s ease;
}

.chat-input-area.collapsed {
  padding: 2px 16px 4px 16px;
}

.chat-input-area.collapsed .quick-actions,
.chat-input-area.collapsed .input-row,
.chat-input-area.collapsed .quiz-settings {
  display: none;
}

.input-toggle {
  text-align: center;
  padding: 2px 0 4px 0;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 12px;
  user-select: none;
}

.input-toggle:hover {
  color: #667eea;
}

.quick-actions {
  display: flex;
  gap: 4px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 2px 10px;
  border: none;
  border-radius: 14px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  transform: translateY(-1px);
}

.quick-btn.memory {
  background: #fffbeb;
  color: #f59e0b;
}

.quick-btn.plan {
  background: #eef2ff;
  color: #2563eb;
}

.quick-btn.action {
  background: #f3e8ff;
  color: #9333ea;
}

.quick-btn.perceive {
  background: #ecfdf5;
  color: #059669;
}

.quick-btn.reflect {
  background: #fef2f2;
  color: #dc2626;
}

.quiz-settings {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
  padding: 8px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.quiz-settings .select-sm {
  padding: 4px 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 12px;
  background: var(--bg-card);
  color: var(--text-primary);
}

.btn-generate {
  padding: 4px 14px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-generate:hover {
  transform: scale(1.05);
}

.input-row {
  display: flex;
  gap: 6px;
  align-items: center;
}

.input-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: var(--bg-primary);
  cursor: pointer;
  font-size: 15px;
  transition: all 0.2s;
}

.input-btn:hover {
  background: var(--border-color);
}

.chat-input {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  background: var(--bg-card);
  color: var(--text-primary);
}

.chat-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
}

.send-btn {
  padding: 6px 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(102,126,234,0.3);
}

/* ===== 知识图谱 ===== */
.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 12px;
}

.knowledge-card {
  position: relative;
  background: var(--bg-card);
  padding: 14px 16px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  border-left: 4px solid #d1d5db;
  transition: all 0.2s;
  cursor: pointer;
}

.knowledge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.knowledge-card::after {
  content: '双击查看详情';
  position: absolute;
  bottom: 6px;
  right: 10px;
  font-size: 10px;
  color: #b0b0b0;
  opacity: 0;
  transition: opacity 0.3s;
}

.knowledge-card:hover::after {
  opacity: 1;
}

.knowledge-card.mastered {
  border-left-color: #22c55e;
}

.knowledge-card.medium {
  border-left-color: #f59e0b;
}

.knowledge-card.weak {
  border-left-color: #f97316;
}

.knowledge-card.critical {
  border-left-color: #ef4444;
}

.knowledge-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.knowledge-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.knowledge-level {
  font-size: 10px;
  padding: 2px 10px;
  border-radius: 20px;
  font-weight: 500;
}

.knowledge-card.mastered .knowledge-level {
  background: #dcfce7;
  color: #16a34a;
}

.knowledge-card.medium .knowledge-level {
  background: #fef3c7;
  color: #d97706;
}

.knowledge-card.weak .knowledge-level {
  background: #ffedd5;
  color: #ea580c;
}

.knowledge-card.critical .knowledge-level {
  background: #fee2e2;
  color: #dc2626;
}

.knowledge-card-body {
  display: flex;
  gap: 14px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.knowledge-card-actions {
  display: flex;
  gap: 6px;
}

/* ===== 家长端 ===== */
.parent-dashboard .stats-grid {
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 16px;
}

.parent-dashboard .stat-card {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: var(--shadow);
}

.parent-dashboard .stat-card h3 {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.parent-dashboard .stat-card p {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.parent-dashboard .stat-card span {
  font-size: 12px;
  color: var(--text-secondary);
}

.parent-alerts {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: var(--shadow);
}

.parent-alerts h3 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.parent-alerts .alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.2s;
}

.parent-alerts .alert-item:hover {
  background: var(--bg-primary);
}

.parent-alerts .alert-item:last-child {
  border-bottom: none;
}

.parent-alerts .alert-item .alert-icon {
  font-size: 18px;
}

.parent-alerts .alert-item .alert-time {
  font-size: 12px;
  color: var(--text-secondary);
  margin-left: auto;
}

/* ===== 教师端 ===== */
.teacher-dashboard .stats-grid {
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 16px;
}

.teacher-dashboard .stat-card {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: var(--shadow);
}

.teacher-dashboard .stat-card h3 {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.teacher-dashboard .stat-card p {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.teacher-dashboard .stat-card span {
  font-size: 12px;
  color: var(--text-secondary);
}

.student-list {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: var(--shadow);
}

.student-list h3 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.student-table {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-x: auto;
}

.table-header, .table-row {
  display: grid;
  grid-template-columns: 100px 80px 80px 70px 70px;
  padding: 8px 12px;
  align-items: center;
  gap: 8px;
}

.table-header {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 13px;
  border-bottom: 2px solid var(--border-color);
}

.table-row {
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s;
  font-size: 14px;
  color: var(--text-primary);
}

.table-row:hover {
  background: var(--bg-primary);
}

.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.status-badge.good {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.warning {
  background: #fee2e2;
  color: #dc2626;
}

.btn-view {
  padding: 2px 12px;
  border: none;
  border-radius: 4px;
  background: #667eea;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
}

.btn-view:hover {
  background: #5a6fd6;
}

/* ===== 排行榜 ===== */
.leaderboard-section {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

.leaderboard-section h3 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.leaderboard {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  background: var(--bg-primary);
  border-radius: 6px;
}

.rank-number {
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 24px;
}

.rank-name {
  flex: 1;
  font-weight: 500;
  color: var(--text-primary);
}

.rank-score {
  font-weight: 600;
  color: var(--text-secondary);
}

.rank-bar-bg {
  flex: 1;
  height: 6px;
  background: var(--border-color);
  border-radius: 10px;
  overflow: hidden;
}

.rank-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 10px;
  transition: width 0.6s ease;
}

.rank-medal {
  font-size: 18px;
}

/* ===== 作业分析 ===== */
.analyze-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.upload-section {
  background: var(--bg-card);
  padding: 24px;
  border-radius: 14px;
  box-shadow: var(--shadow);
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #667eea;
}

.upload-area .upload-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.upload-area .upload-hint {
  font-size: 12px;
  color: var(--text-secondary);
}

.upload-preview {
  max-width: 100%;
  max-height: 200px;
}

.btn-analyze {
  width: 100%;
  padding: 12px;
  margin-top: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

.btn-analyze:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102,126,234,0.3);
}

.btn-analyze:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result-section {
  background: var(--bg-card);
  padding: 24px;
  border-radius: 14px;
  box-shadow: var(--shadow);
}

.result-card {
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}

.result-card.human {
  background: #dcfce7;
  border: 1px solid #22c55e;
}

.result-card.ai {
  background: #fee2e2;
  border: 1px solid #ef4444;
}

.result-score .score-number {
  font-size: 48px;
  font-weight: 700;
  color: var(--text-primary);
}

.result-score .score-label {
  font-size: 14px;
  color: var(--text-secondary);
  display: block;
}

.result-status {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.result-status .status-icon {
  font-size: 24px;
}

.result-status .status-text {
  font-size: 16px;
  font-weight: 500;
}

.detail-table {
  width: 100%;
  margin: 12px 0;
  border-collapse: collapse;
}

.detail-table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.detail-table td:first-child {
  color: var(--text-secondary);
}

.suggestions ul {
  list-style: none;
  padding: 0;
}

.suggestions li {
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  margin-bottom: 4px;
  color: var(--text-primary);
}

/* ===== 弹窗 ===== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: var(--bg-card);
  border-radius: 16px;
  max-width: 520px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  animation: slideUp 0.3s ease;
}

.modal-content.small-modal {
  max-width: 420px;
}

.modal-content.report-modal {
  max-width: 640px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.modal-header h2 {
  font-size: 20px;
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: transparent;
  font-size: 18px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  max-height: 60vh;
}

.modal-footer {
  padding: 14px 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  background: var(--bg-secondary);
}

.btn-modal {
  padding: 8px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-modal.primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}

.btn-modal.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102,126,234,0.3);
}

.btn-modal.secondary {
  background: var(--bg-primary);
  color: var(--text-secondary);
}

.btn-modal.secondary:hover {
  background: var(--border-color);
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.detail-value .level-tag {
  display: inline-block;
  padding: 2px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.detail-value .level-tag.mastered {
  background: #dcfce7;
  color: #16a34a;
}

.detail-value .level-tag.medium {
  background: #fef3c7;
  color: #d97706;
}

.detail-value .level-tag.weak {
  background: #ffedd5;
  color: #ea580c;
}

.detail-value .level-tag.critical {
  background: #fee2e2;
  color: #dc2626;
}

.detail-value .alert-active {
  color: #dc2626;
  font-weight: 600;
}

.tag-badge {
  display: inline-block;
  padding: 2px 10px;
  background: var(--bg-primary);
  border-radius: 12px;
  font-size: 12px;
  color: var(--text-secondary);
  margin: 2px 4px 2px 0;
}

/* ===== 报告弹窗 ===== */
.report-body {
  max-height: 70vh !important;
}

.report-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin: 12px 0 16px 0;
}

.report-stat {
  background: var(--bg-primary);
  padding: 12px;
  border-radius: 8px;
  text-align: center;
}

.report-stat .report-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
}

.report-stat .report-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.report-strengths, .report-weaknesses, .report-recommendations {
  margin-bottom: 12px;
}

.report-strengths h3, .report-weaknesses h3, .report-recommendations h3 {
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.report-strengths ul, .report-weaknesses ul, .report-recommendations ul {
  list-style: none;
  padding: 0;
}

.report-strengths li, .report-weaknesses li, .report-recommendations li {
  padding: 4px 8px;
  font-size: 14px;
  color: var(--text-primary);
}

/* ===== 练习弹窗 ===== */
.practice-modal {
  max-width: 700px !important;
  width: 95% !important;
}

.practice-body {
  max-height: 70vh !important;
  padding: 16px 20px !important;
}

.practice-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.practice-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.practice-section h3 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.knowledge-explanation {
  background: var(--bg-primary);
  padding: 14px 18px;
  border-radius: 10px;
  border-left: 4px solid #667eea;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
  color: var(--text-primary);
}

.question-area {
  background: var(--bg-card);
  padding: 14px 18px;
  border-radius: 10px;
  border: 2px solid var(--border-color);
  min-height: 120px;
}

.question-text {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.question-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-primary);
}

.option-item:hover {
  border-color: #667eea;
}

.option-item.selected {
  border-color: #667eea;
  background: #eef2ff;
}

.option-item.correct {
  border-color: #22c55e;
  background: #dcfce7;
}

.option-item.wrong {
  border-color: #ef4444;
  background: #fee2e2;
}

.option-label {
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 28px;
}

.option-text {
  flex: 1;
}

.answer-textarea {
  width: 100%;
  min-height: 80px;
  padding: 10px 14px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  outline: none;
  background: var(--bg-card);
  color: var(--text-primary);
}

.answer-textarea:focus {
  border-color: #667eea;
}

.question-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.btn-practice {
  padding: 8px 20px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-practice.primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}

.btn-practice.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102,126,234,0.3);
}

.btn-practice.secondary {
  background: var(--bg-primary);
  color: var(--text-secondary);
}

.btn-practice.secondary:hover {
  background: var(--border-color);
}

.result-area {
  margin-top: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.result-area.correct {
  background: #dcfce7;
  border: 1px solid #22c55e;
}

.result-area.wrong {
  background: #fee2e2;
  border: 1px solid #ef4444;
}

.result-icon {
  font-size: 20px;
}

.result-text {
  font-weight: 500;
  color: var(--text-primary);
}

.result-detail {
  font-size: 13px;
  color: var(--text-secondary);
}

.ocr-result {
  margin-top: 12px;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.ocr-result h4 {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.ocr-result p {
  font-size: 14px;
  color: var(--text-primary);
}

.ocr-judge {
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.ocr-judge.correct {
  background: #dcfce7;
  color: #16a34a;
}

.ocr-judge.wrong {
  background: #fee2e2;
  color: #dc2626;
}

.ocr-detail {
  font-size: 13px;
}

/* ===== 学习任务 ===== */
.task-progress-card {
  background: var(--bg-card);
  padding: 14px 18px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  margin-bottom: 14px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.progress-bar {
  height: 6px;
  background: var(--border-color);
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 10px;
  transition: width 0.6s ease;
}

.progress-text {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
  display: block;
  text-align: right;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-card);
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  border-left: 4px solid #d1d5db;
  transition: all 0.2s;
}

.task-card:hover {
  transform: translateX(4px);
}

.task-card.pending {
  border-left-color: #f59e0b;
}

.task-card.doing {
  border-left-color: #6366f1;
}

.task-card.done {
  border-left-color: #22c55e;
  opacity: 0.7;
}

.task-card.overdue {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.task-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  flex: 1;
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.task-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.task-status-label {
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 20px;
  background: var(--bg-primary);
  color: var(--text-secondary);
}

.task-card.pending .task-status-label {
  background: #fef3c7;
  color: #d97706;
}

.task-card.doing .task-status-label {
  background: #eef2ff;
  color: #4f46e5;
}

.task-card.done .task-status-label {
  background: #dcfce7;
  color: #16a34a;
}

.task-overdue-badge {
  font-size: 10px;
  color: #ef4444;
  font-weight: 600;
}

.task-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

/* ===== 数据预警 ===== */
.alert-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.alert-stat-card {
  background: var(--bg-card);
  padding: 14px 18px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  text-align: center;
}

.alert-stat-card .alert-stat-value {
  font-size: 24px;
  font-weight: 700;
  display: block;
  color: var(--text-primary);
}

.alert-stat-card .alert-stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.alert-stat-card.total .alert-stat-value {
  color: #6366f1;
}

.alert-stat-card.weak .alert-stat-value {
  color: #ef4444;
}

.alert-stat-card.decay .alert-stat-value {
  color: #f59e0b;
}

.alert-auto-check {
  font-size: 13px;
  color: #059669;
  background: #ecfdf5;
  padding: 4px 12px;
  border-radius: 20px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-notify {
  padding: 4px 14px;
  border: none;
  border-radius: 6px;
  background: #8b5cf6;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-notify:hover {
  transform: scale(1.05);
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alert-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-card);
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  border-left: 4px solid #d1d5db;
  transition: all 0.2s;
}

.alert-card.weak {
  border-left-color: #ef4444;
}

.alert-card.decay {
  border-left-color: #f59e0b;
}

.alert-card .alert-icon {
  font-size: 24px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.alert-card .alert-exclamation {
  color: #ef4444;
  animation: pulse-alert 1.5s infinite;
}

@keyframes pulse-alert {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
}

.alert-card .alert-info {
  flex: 1;
}

.alert-card .alert-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.alert-type-badge {
  font-size: 10px;
  padding: 2px 10px;
  border-radius: 20px;
  font-weight: 500;
}

.alert-type-badge.weak {
  background: #fee2e2;
  color: #dc2626;
}

.alert-type-badge.decay {
  background: #fef3c7;
  color: #d97706;
}

.alert-card .alert-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.alert-card .alert-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.alert-card .alert-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

/* ===== 通用组件 ===== */
.btn-sm {
  padding: 4px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sm.success {
  background: #22c55e;
  color: #fff;
}

.btn-sm.success:hover {
  background: #16a34a;
}

.btn-sm.danger {
  background: #ef4444;
  color: #fff;
}

.btn-sm.danger:hover {
  background: #dc2626;
}

.btn-sm.primary {
  background: #6366f1;
  color: #fff;
}

.btn-sm.primary:hover {
  background: #4f46e5;
}

.btn-sm.outline {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-sm.outline:hover {
  background: var(--bg-primary);
}

.input-sm {
  padding: 8px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  transition: all 0.2s;
  min-width: 140px;
  background: var(--bg-card);
  color: var(--text-primary);
}

.input-sm:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
}

.select-sm {
  padding: 8px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  background: var(--bg-card);
  color: var(--text-primary);
}

.btn-create {
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-create:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102,126,234,0.3);
}

.btn-refresh {
  padding: 8px 18px;
  border: none;
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: var(--border-color);
}

.btn-export {
  padding: 8px 18px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-export:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(46,204,113,0.3);
}

.btn-report {
  padding: 8px 18px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-report:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139,92,246,0.3);
}

.search-input {
  min-width: 160px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.empty-state span {
  font-size: 40px;
  display: block;
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 15px;
}

.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
}

.toast-item {
  padding: 12px 24px;
  background: #1a2332;
  color: #fff;
  border-radius: 10px;
  margin-bottom: 8px;
  font-size: 14px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  animation: slideIn 0.3s ease;
  border-left: 4px solid #667eea;
}

.toast-item.toast-success { border-left-color: #22c55e; }
.toast-item.toast-warning { border-left-color: #f59e0b; }
.toast-item.toast-error   { border-left-color: #ef4444; }
.toast-item.toast-info    { border-left-color: #667eea; }

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

/* ===== 响应式 ===== */
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(3, 1fr); }
  .dashboard-two-col { grid-template-columns: 1fr; }
  .reflect-grid { grid-template-columns: repeat(2, 1fr); }
  .analyze-container { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .mobile-menu-btn { display: block; }
  .top-nav { padding: 8px 12px; flex-wrap: nowrap; }
  .nav-left .logo-text { font-size: 14px; }
  .nav-left .logo-badge { font-size: 7px; padding: 1px 6px; }
  .nav-center { display: none; }
  .user-name { display: none; }
  .history-sidebar {
    position: fixed !important;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 999;
    width: 280px !important;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    border-radius: 0 !important;
  }
  .history-sidebar:not(.collapsed) { transform: translateX(0); }
  .history-sidebar.collapsed { width: 280px !important; transform: translateX(-100%); }
  .sidebar-overlay.active { display: block; }
  .main-content { padding: 0; }
  .content-area { padding: 12px 12px; }
  .stats-grid { grid-template-columns: 1fr !important; gap: 10px; }
  .stat-card { padding: 12px 14px; }
  .stat-card .stat-icon { font-size: 22px; }
  .stat-card .stat-value { font-size: 18px; }
  .stat-card .stat-label { font-size: 11px; }
  .stat-trend { font-size: 10px; }
  .dashboard-two-col { grid-template-columns: 1fr !important; gap: 12px; }
  .dashboard-chart { padding: 14px 16px; }
  .trend-chart { height: 100px; gap: 8px; }
  .trend-bar .trend-value { font-size: 10px; top: -14px; }
  .trend-label { font-size: 10px; }
  .study-timer-card { padding: 12px 16px; gap: 12px; }
  .timer-text { font-size: 24px; }
  .timer-btn { padding: 6px 14px; font-size: 12px; }
  .reflect-grid { grid-template-columns: 1fr 1fr !important; gap: 10px; }
  .reflect-header { flex-wrap: wrap; padding: 10px 14px; }
  .reflect-title { font-size: 13px; }
  .reflect-card { padding: 8px 10px; }
  .reflect-card-title { font-size: 12px; }
  .chat-header-bar { padding: 10px 14px; flex-wrap: wrap; }
  .chat-header-bar h2 { font-size: 15px; }
  .chat-messages { padding: 12px 14px; flex: 1; max-height: none; }
  .message-content { max-width: 90%; padding: 8px 12px; font-size: 13px; }
  .chat-input-area { padding: 4px 12px; }
  .quick-btn { font-size: 10px; padding: 2px 8px; }
  .input-btn { width: 28px; height: 28px; font-size: 13px; }
  .chat-input { font-size: 13px; padding: 6px 10px; }
  .send-btn { padding: 6px 12px; font-size: 13px; }
  .knowledge-grid { grid-template-columns: 1fr 1fr !important; gap: 10px; }
  .knowledge-card { padding: 12px 14px; }
  .knowledge-name { font-size: 13px; }
  .heatmap-grid { grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); }
  .header-actions-full { flex-wrap: wrap; }
  .header-actions-full .input-sm { min-width: 100%; }
  .header-actions-full .select-sm { width: 100%; }
  .task-card { flex-wrap: wrap; padding: 10px 14px; }
  .task-info { width: 100%; }
  .task-actions { width: 100%; justify-content: flex-end; }
  .alert-summary-grid { grid-template-columns: 1fr !important; gap: 8px; }
  .alert-card { flex-wrap: wrap; padding: 10px 14px; }
  .alert-card .alert-actions { width: 100%; justify-content: flex-end; }
  .modal-content { max-width: 95%; }
  .detail-grid { grid-template-columns: 1fr; }
  .modal-header h2 { font-size: 17px; }
  .practice-modal { max-width: 98% !important; }
  .practice-body { padding: 12px 14px !important; max-height: 60vh !important; }
  .question-text { font-size: 14px; }
  .option-item { padding: 8px 12px; font-size: 13px; }
  .btn-practice { padding: 6px 14px; font-size: 12px; }
  .upload-area { height: 120px; }
  .parent-dashboard .stats-grid { grid-template-columns: 1fr 1fr; }
  .teacher-dashboard .stats-grid { grid-template-columns: 1fr 1fr; }
  .table-header, .table-row { grid-template-columns: 70px 60px 60px 50px 60px; font-size: 12px; }
  .toast-container { top: 10px; right: 10px; }
  .toast-item { font-size: 13px; padding: 8px 16px; }
  .page-header h2 { font-size: 17px; }
  .header-count { font-size: 12px; }
  .report-stats { grid-template-columns: 1fr 1fr; }
  .leaderboard-section .rank-item { font-size: 13px; }
  .rank-bar-bg { display: none; }
  .goals-section { padding: 12px 14px; }
  .goal-item { flex-wrap: wrap; padding: 6px 10px; }
  .goal-deadline { font-size: 10px; }
  .learning-path-section { padding: 12px 14px; }
  .path-step { flex-wrap: wrap; padding: 8px 12px; }
  .step-number { width: 24px; height: 24px; font-size: 11px; }
  .forgetting-curve-section .review-item { flex-wrap: wrap; font-size: 12px; }
}

@media (max-width: 420px) {
  .stats-grid { grid-template-columns: 1fr 1fr !important; gap: 8px; }
  .reflect-grid { grid-template-columns: 1fr !important; }
  .knowledge-grid { grid-template-columns: 1fr !important; }
  .login-box { width: 95%; padding: 32px 20px; }
  .practice-modal { max-width: 98% !important; }
  .modal-content { max-width: 98%; padding: 0; }
  .parent-dashboard .stats-grid { grid-template-columns: 1fr 1fr; }
  .teacher-dashboard .stats-grid { grid-template-columns: 1fr 1fr; }
  .table-header, .table-row { grid-template-columns: 80px 65px 65px 55px 60px; font-size: 11px; gap: 4px; min-width: 340px; }
  .role-options { flex-direction: column; }
  .study-timer-card { flex-direction: column; align-items: stretch; gap: 8px; }
  .timer-controls { justify-content: center; }
  .timer-tips { text-align: center; }
  .heatmap-grid { grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); }
  .heatmap-item.small { font-size: 10px; padding: 3px 6px; }
  .report-stats { grid-template-columns: 1fr 1fr; }
  .report-stat .report-value { font-size: 18px; }
}
  .join-class-section {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

.join-class-section h3 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.join-class-input {
  display: flex;
  gap: 10px;
}

.join-class-input .input-sm {
  flex: 1;
}

.class-management {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.class-header h3 {
  font-size: 15px;
  color: var(--text-primary);
}

.class-list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
}

.class-card-item {
  background: var(--bg-primary);
  padding: 14px 16px;
  border-radius: 10px;
  border-left: 4px solid #667eea;
}

.class-card-item .class-card-info h4 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.class-card-item .class-card-info p {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 2px 0;
}

.class-card-actions {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}

/* 创建班级弹窗 */
.create-class-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.create-class-form .form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.create-class-form .form-group label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.create-class-form .form-group input {
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: var(--bg-card);
  color: var(--text-primary);
  outline: none;
}

.create-class-form .form-group input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
}

/* 班级详情弹窗 */
.class-detail-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.class-detail-student {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.class-detail-student .student-name {
  font-weight: 500;
  color: var(--text-primary);
}

.class-detail-student .student-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}

.class-detail-student .student-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}
/* ===== 家长端孩子列表 ===== */
.parent-children-section {
  background: var(--bg-card);
  padding: 16px 20px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

.parent-children-section h3 {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.children-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
}

.child-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.child-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.child-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  flex-shrink: 0;
}

.child-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.child-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.child-stats {
  font-size: 12px;
  color: var(--text-secondary);
}

.child-weak {
  font-size: 12px;
  color: #ef4444;
}

.child-arrow {
  font-size: 18px;
  color: var(--text-secondary);
}
.class-code-display {
  margin-top: 4px;
  font-size: 13px;
  color: var(--text-secondary);
}

.class-code-display strong {
  color: #667eea;
  font-size: 15px;
  letter-spacing: 2px;
}
/* ===== 复习紧急程度标签 ===== */
.review-badge {
  font-size: 10px;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 500;
  margin-left: 8px;
}
.review-badge.critical { background: #fee2e2; color: #dc2626; }
.review-badge.warning { background: #fef3c7; color: #d97706; }
.review-badge.normal { background: #dbeafe; color: #2563eb; }
.review-badge.good { background: #dcfce7; color: #16a34a; }

.reflect-card-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin: 2px 0 4px 0;
}
.bind-child-area {
  margin-bottom: 12px;
}
.bind-child-input {
  display: flex;
  gap: 10px;
}
.bind-child-input .input-sm {
  flex: 1;
}
.setting-wrap {
  position: relative;
}
.setting-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255,255,255,0.12);
  color: #fff;
  border: none;
  font-size: 16px;
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.setting-btn:hover {
  background: rgba(255,255,255,0.22);
}
.setting-dropdown {
  position: absolute;
  top: 44px;
  right: 0;
  min-width: 180px;
  background: #1a2332;
  border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.35);
  z-index: 9999;
  overflow: hidden;
}
.setting-dropdown-item {
  padding: 11px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  color: #ffffff;
  font-size: 14px;
}
.setting-dropdown-item:hover {
  background: rgba(255,255,255,0.08);
}
.setting-dropdown-item button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 13px;
}
.setting-dropdown-item .logout-btn {
  color: #ff6b6b;
}

</style>