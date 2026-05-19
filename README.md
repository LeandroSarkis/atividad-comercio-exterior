# App Comex – Cálculo de Preço de Exportação

Projeto acadêmico desenvolvido para a disciplina **Comércio Exterior** CESUPA – Engenharia da Computação | Maio 2026

---

## 📋 Funcionalidades

- Interface em formato *Stepper* (passo a passo) fluida e intuitiva.
- Cadastro básico da mercadoria (nome, NCM, preço interno, câmbio).
- Configuração de tributos **CBS** e **IBS** (alíquotas configuráveis pós-reforma).
- Inserção de créditos tributários recuperáveis (desoneração da exportação).
- Inserção de custos logísticos internos (embalagem, frete, desembaraço, seguro, outros).
- Seleção dinâmica de **Incoterm** com atualização de regras de frete/seguro em tempo real.
- Sistema de validação de dados blindado contra caracteres inválidos (suporta `1.500,00` ou `1500.00`).
- Cálculo automático de **FOB** e **CIF/CPT** em BRL e USD.
- Exibição de lucro estimado e margem percentual com cards de destaque visual.

---

## 🚀 Como rodar o projeto

### Opção 1 – Executar o Código Fonte (Desenvolvimento)

Certifique-se de ter o Python 3 instalado na sua máquina.

```bash
# 1. Instalar a versão recomendada do Flet
pip install flet  # no Mac/Linux use: python3 -m pip install flet

# 2. Executar o aplicativo
python main.py    # no Mac/Linux use: python3 main.py
```

### Opção 2 – Gerar executável standalone (.exe ou .app)

Para distribuir o aplicativo como um programa nativo sem precisar do Python instalado:

```bash
# 1. Instalar as ferramentas de empacotamento
pip install pyinstaller flet

# 2. Gerar o executável nativo
flet pack main.py --name "AppComex"
```
O resultado será gerado dentro da pasta dist/ na raiz do projeto.

---

## 🧮 Lógica de cálculo

```
FOB (R$) = Preço Mercado Interno − Crédito Recuperável + Custos Internos

CIF/CPT (R$) = FOB + Frete Internacional + Seguro Internacional
               (conforme Incoterm escolhido)

FOB (USD) = FOB (R$) ÷ Taxa de Câmbio

Lucro Estimado = FOB (R$) − Preço Mercado Interno
```

CBS e IBS incidem sobre o preço de mercado interno.  
O crédito recuperável (desoneração) é subtraído diretamente, refletindo  
a reforma tributária vigente.

---

## 🛠 Tecnologias

| Biblioteca | Uso |
|-----------|-----|
|**Python Nativo** | Lógica de cálculo otimizada e sem dependências pesadas |
| **Flet (v0.85+)**  | Interface gráfica multiplataforma moderna baseada em Flutter |

---

## 👥 Equipe

Enzo Kikuchi · Jorge Vasconcelos · Leandro Sarkis · Lucas Salviano  
Professor: André Reis
