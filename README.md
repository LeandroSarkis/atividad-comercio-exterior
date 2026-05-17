# App Comex – Cálculo de Preço de Exportação

Projeto acadêmico desenvolvido para a disciplina **Comércio Exterior**  
CESUPA – Engenharia da Computação | Maio 2026

---

## 📋 Funcionalidades

- Cadastro básico da mercadoria (nome, NCM, preço interno, câmbio)
- Configuração de tributos **CBS** e **IBS** (alíquotas configuráveis)
- Inserção de créditos tributários recuperáveis (desoneração)
- Inserção de custos logísticos (embalagem, frete, desembaraço, seguro, outros)
- Seleção do **Incoterm** com descrição automática
- Cálculo automático de **FOB** e **CIF/CPT** em BRL e USD
- Lucro estimado e margem percentual
- Resumo completo da exportação

---

## 🚀 Como rodar

### Opção 1 – Script rápido (Windows)
Dê duplo-clique em `rodar_app.bat`.

### Opção 2 – Manual (Windows / Linux / macOS)

```bash
# 1. Instalar dependências
pip install flet

# 2. Executar
python main.py
```

### Opção 3 – Gerar executável standalone

```bash
# Linux/macOS
chmod +x build.sh
./build.sh

# Windows – via pip
pip install flet pyinstaller
flet pack main.py --name AppComex
# Executável gerado em: dist/AppComex (ou dist/AppComex.exe)
```

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
| **Flet**  | Interface gráfica multiplataforma |

---

## 👥 Equipe

Enzo Kikuchi · Jorge Vasconcelos · Leandro Sarkis · Lucas Salviano  
Professor: André Reis
