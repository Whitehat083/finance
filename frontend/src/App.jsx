import { useMemo, useState } from 'react'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts'

const translations = {
  pt: {
    title: 'Educa Finance',
    subtitle: 'Seu jogo para aprender, praticar e crescer financeiramente.',
    login: 'Login rápido',
    dashboard: 'Dashboard financeiro',
    modules: 'Trilha de aprendizado',
    tools: 'Ferramentas',
  },
  en: {
    title: 'Educa Finance',
    subtitle: 'A game-like space to learn and improve your money habits.',
    login: 'Quick login',
    dashboard: 'Financial dashboard',
    modules: 'Learning path',
    tools: 'Tools',
  },
}

const moduleList = [
  'Conceito de orçamento',
  'Controle de gastos',
  'Poupança vs gastos',
  'Planejamento de metas',
  'Introdução a investimentos simples',
  'Erros comuns a evitar',
]

const categories = [
  { name: 'Alimentação', value: 450 },
  { name: 'Lazer', value: 520 },
  { name: 'Transporte', value: 240 },
  { name: 'Estudos', value: 350 },
]

const lineData = [
  { month: 'Jan', balance: 300 },
  { month: 'Fev', balance: 580 },
  { month: 'Mar', balance: 760 },
  { month: 'Abr', balance: 900 },
]

const colors = ['#2dd4bf', '#f97316', '#a78bfa', '#60a5fa']

export default function App() {
  const [lang, setLang] = useState('pt')
  const [goal, setGoal] = useState(5000)
  const [months, setMonths] = useState(10)

  const t = translations[lang]
  const monthlySaving = useMemo(() => (goal / Math.max(months, 1)).toFixed(2), [goal, months])

  return (
    <main className="container">
      <header className="hero">
        <div>
          <h1>{t.title}</h1>
          <p>{t.subtitle}</p>
        </div>
        <select value={lang} onChange={(e) => setLang(e.target.value)} aria-label="language">
          <option value="pt">Português</option>
          <option value="en">English</option>
        </select>
      </header>

      <section className="card grid">
        <article>
          <h2>{t.login}</h2>
          <p>Cadastro com email/senha + JWT, perfil de renda e objetivos.</p>
          <ul>
            <li>Plano gratuito e premium</li>
            <li>Dados sensíveis protegidos com hash + token</li>
            <li>Fluxo para escolas/empresas (B2B)</li>
          </ul>
        </article>

        <article>
          <h2>{t.dashboard}</h2>
          <div className="kpis">
            <span>Saldo: R$ 2.350</span>
            <span>Pontos: 220</span>
            <span>Meta ativa: Viagem</span>
          </div>
          <div className="chart-row">
            <div className="chart">
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={categories} dataKey="value" cx="50%" cy="50%" outerRadius={80} label>
                    {categories.map((entry, index) => (
                      <Cell key={entry.name} fill={colors[index % colors.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="chart">
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={lineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="balance" stroke="#14b8a6" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </article>
      </section>

      <section className="card">
        <h2>{t.modules}</h2>
        <div className="modules">
          {moduleList.map((m, i) => (
            <div key={m} className="module">
              <strong>Fase {i + 1}</strong>
              <p>{m}</p>
              <small>Quiz + recompensa de 50 pontos</small>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>{t.tools}</h2>
        <div className="tool-grid">
          <label>
            Valor da meta (R$)
            <input type="number" value={goal} onChange={(e) => setGoal(Number(e.target.value))} />
          </label>
          <label>
            Prazo (meses)
            <input type="number" value={months} onChange={(e) => setMonths(Number(e.target.value))} />
          </label>
        </div>
        <p className="result">Você precisa guardar <b>R$ {monthlySaving}/mês</b> para atingir a meta.</p>
      </section>
    </main>
  )
}
