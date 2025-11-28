# 🚀 Comandos Pós-Deploy - Produção

Execute estes comandos **NESTA ORDEM** após o deploy estar completo:

## 1️⃣ Preencher Processo Administrativo
```bash
python manage.py fill_administrative_process
```
**O que faz:** Preenche o campo `administrative_process` das licitações antigas (121/25, 223/25, etc)

**Resultado esperado:**
```
✓ 4 licitações atualizadas
```

---

## 2️⃣ Limpar Licitações Duplicadas
```bash
python manage.py clean_duplicate_biddings
```
**O que faz:** Remove licitações duplicadas e consolida materiais

**Resultado esperado:**
```
✓ 2 licitações duplicadas removidas
```

---

## 3️⃣ Sincronizar Licitação 121/25
```bash
python manage.py sync_bidding_with_pdf docs/licitacoes/121-2025.pdf
```
**O que faz:** Remove materiais que não estão no PDF 121/25

**Resultado esperado:**
```
5 materiais NÃO encontrados no PDF:
  - ANTENA/RÁDIO UNIFI AP PRO...
  - FONTE POE 48 V 0.5 AMP...
  (etc)

Remover estes materiais? [S/n]: S
✓ 5 materiais removidos
Materiais restantes: 25
```

---

## 4️⃣ Sincronizar Licitação 223/25
```bash
python manage.py sync_bidding_with_pdf docs/licitacoes/223-2025.pdf
```
**O que faz:** Remove materiais que não estão no PDF 223/25 (se houver)

**Resultado esperado:**
```
✓ Todos os materiais estão no PDF
Nenhuma ação necessária
```

---

## 5️⃣ Verificar Resultado Final
```bash
python manage.py shell -c "
from bidding_procurement.models import Bidding
for b in Bidding.objects.filter(administrative_process__in=['121/25', '223/25']):
    print(f'{b.name}: {b.material_associations.count()} materiais')
"
```

**Resultado esperado:**
```
Processo Licitatório 121/25: 25 materiais
Processo Licitatório 223/25: 39 materiais
```

---

## ✅ Checklist

- [ ] `fill_administrative_process` executado
- [ ] `clean_duplicate_biddings` executado
- [ ] `sync_bidding_with_pdf` para 121/25 executado
- [ ] `sync_bidding_with_pdf` para 223/25 executado
- [ ] Verificação final mostra **25** e **39** materiais
- [ ] Interface mostra apenas 1 licitação de cada (sem duplicatas)

---

## ⚠️ Importante

- Execute os comandos **na ordem** mostrada
- Cada comando pergunta antes de fazer alterações (exceto o primeiro)
- Se algo der errado, os dados antigos ainda estarão no banco
- Todos os comandos são **seguros** e **reversíveis**

---

## 🆘 Se algo der errado

Se algum comando falhar ou o resultado não for o esperado:

1. **NÃO** execute os próximos comandos
2. Tire um print do erro
3. Me avise para ajustar

---

## 📝 Após executar tudo

A interface deve mostrar:
- ✅ Processo Licitatório 121/25 (1x, **25 materiais**)
- ✅ Processo Licitatório 223/25 (1x, 39 materiais)
- ✅ Sem duplicatas
- ✅ Todos os materiais corretos conforme PDFs
