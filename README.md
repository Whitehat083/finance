# Sistema de Educação Financeira (14–30 anos)

Plataforma web com backend Flask + frontend React para ensinar finanças de forma gamificada.

## Arquitetura

- **Frontend:** React + Vite + Recharts (dashboard, módulos, simuladores, UI responsiva).
- **Backend:** Flask + SQLAlchemy + JWT (autenticação, regras de negócio, APIs REST).
- **Banco:** SQLite local (fácil dev); em produção usar PostgreSQL.

## Funcionalidades implementadas

- Cadastro e login com JWT.
- Perfil com idade, renda e tipo de perfil.
- Dashboard com saldo, despesas por categoria, feedback automático e dicas.
- Registro de transações e metas.
- Simulador de metas (quanto poupar por mês).
- Trilha de módulos com bloqueio sequencial.
- Gamificação com pontos por conclusão de módulo.
- Endpoint de monetização (free/premium/B2B).
- Interface bilingue (PT/EN) e mobile-first.

## Segurança de dados sensíveis

- Senhas armazenadas com hash (`werkzeug.security.generate_password_hash`).
- Tokens JWT assinados no backend.
- Segredos em variáveis de ambiente (`JWT_SECRET` recomendado em produção).
- Em produção: HTTPS obrigatório, rotação de segredo JWT, criptografia em repouso no banco, backups com controle de acesso.

## Métricas de sucesso sugeridas

1. % de conclusão de módulos por coorte.
2. Redução média de despesas discricionárias (ex.: lazer) por usuário ativo.
3. Taxa de criação e cumprimento de metas.
4. Retenção de assinantes Premium (D30/D90).

## Regras de negócio

- Módulos só podem ser concluídos em sequência.
- Alerta para gastos altos em lazer (>20% da renda no período).
- Usuários autenticados só acessam endpoints financeiros.

## Como rodar (passo a passo)

### Pré-requisitos

- Python **3.10+**
- Node.js **18+**
- npm **9+**

### 1) Subir o backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Backend ficará em: `http://localhost:5000`

Opcional (segredo JWT em ambiente):

```bash
export JWT_SECRET="troque-este-segredo-em-producao"
```

### 2) Subir o frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend ficará em: `http://localhost:5173`

### 3) Fluxo rápido para testar

1. Acesse o frontend em `http://localhost:5173`.
2. Faça cadastro/login (o backend já expõe endpoints JWT).
3. Cadastre transações e metas para popular o dashboard.
4. Teste o simulador de metas e a trilha de módulos.

## Testes automatizados

```bash
cd backend && pytest
cd frontend && npm test
```

## Observação sobre este ambiente

Se `pip install` ou `npm install` falhar com erro de rede/proxy (ex.: `403 Forbidden`), rode o projeto em uma rede com acesso ao PyPI/npm ou configure o proxy corporativo localmente.
