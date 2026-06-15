A seguir está uma revisão conservadora das inconsistências internas entre o JSON, a análise MD e a árvore/KG conforme os dados fornecidos. Eu **não proponho novos parentes** nem novas hipóteses externas; apenas aponto divergências e sugiro correções mínimas para não corromper informações já consolidadas.

---

# Revisão de inconsistências — Família Gramilo Sodré

## Síntese geral

Há três tipos principais de problema:

1. **Conflitos estruturais no JSON**
   - IDs duplicados;
   - pessoas diferentes usando o mesmo ID;
   - vários registros com `ID=?`;
   - filhos repetidos ou listas de filhos incompatíveis com contagens declaradas.

2. **Conflitos entre JSON e MD**
   - Tomaz Gramilo Sodré aparece como hipotético no JSON, mas como confirmado em parte do MD;
   - a relação Tomaz × Teodora é tratada como confirmada em um trecho, mas como gap crítico em outro;
   - número de irmãos/filhos de Marcelo, José, Otávia, Elisa e Isabel diverge.

3. **Conflitos cronológicos/genealógicos**
   - filhos atribuídos diretamente a Jerônimo Sodré Pereira, do século XVII, com eventos do século XIX;
   - Esmeraldo Vaz Sodré com filhos distribuídos entre ~1870 e ~1930, o que pode indicar homônimos ou datas erradas;
   - Alice dos Santos aparece como filha de Maria Aleluia, mas a nota diz que seria irmã dela.

---

# Inconsistências CRÍTICAS

## 1. IDs duplicados `b8` e `b9` para pessoas diferentes

### Divergência

No JSON aparecem inicialmente:

- `ID=b8 | NOME=Geraldo Bispo`
- `ID=b9 | NOME=Givanildo Bispo`

Depois aparecem novamente:

- `ID=b8 | NOME=Nilda Sodré Bispo de Souza`
- `ID=b9 | NOME=Antônio Carlos Bispo`

Todos aparecem como filhos de:

- Eustázio Eusébio Bispo
- Otávia Rosa Sodré Bispo

### Classificação

**CRÍTICA**

IDs duplicados podem sobrescrever pessoas diferentes em árvore, KG ou banco de dados.

### Correção conservadora

Não fundir as pessoas. Manter todos os nomes, mas atribuir IDs únicos, por exemplo:

- `b8a` = Geraldo Bispo
- `b9a` = Givanildo Bispo
- `b8b` = Nilda Sodré Bispo de Souza
- `b9b` = Antônio Carlos Bispo

Ou, melhor ainda, renumerar todos os filhos de Otávia em uma sequência única após reconciliação.

Até a revisão, marcar a lista de filhos de Otávia como:

> “lista de filhos pendente de reconciliação; há IDs duplicados no JSON”.

---

## 2. Conflito grave na quantidade de filhos de Otávia Rosa Sodré Bispo

### Divergência

No JSON:

- `f8 | Otávia Rosa Sodré Bispo | NOTAS=10 filhos`

A primeira lista de filhos contém exatamente 10:

1. Eustázio Bispo Filho  
2. Creuza Bispo  
3. Tereza Bispo  
4. Cláudio Bispo  
5. Rita Bispo  
6. Rogério Bispo  
7. Lúcia Bispo  
8. Geraldo Bispo  
9. Givanildo Bispo  
10. Nádia Bispo  

Mas depois o JSON acrescenta outros filhos atribuídos ao mesmo casal:

- Nilda Sodré Bispo de Souza
- Antônio Carlos Bispo
- Geni Bispo
- Zenito Bispo
- Sinval Bispo
- Maria Helena Sodré Bispo
- Maiza Rosa Bispo Gouveia
- Zélia Bispo
- Juvenil Sodré Bispo
- Valdeck Bispo

Isso elevaria o total para cerca de 20 nomes, incompatível com a nota “10 filhos”.

### Classificação

**CRÍTICA**

Afeta diretamente a estrutura familiar de uma geração inteira.

### Correção conservadora

Não excluir ninguém automaticamente.

Alterar a nota de Otávia de:

> “10 filhos”

para:

> “número de filhos inconsistente nas fontes internas: uma lista indica 10 filhos; outra lista expandida traz nomes adicionais. Requer reconciliação.”

Até confirmação, evitar afirmações fechadas como “10 filhos” ou “20 filhos”.

Para os filhos adicionais posteriores, se não houver fonte clara separada, rebaixar temporariamente de `confirmada` para:

> `CONF=provável` ou `CONF=a confirmar`

especialmente onde há duplicação de IDs.

---

## 3. Conflito na quantidade de filhos de José Gramilo Sodré “Zeca”

### Divergência

No JSON:

- `f7 | José Gramilo Sodré ("Zeca") | NOTAS=11 filhos`

A lista `z1` a `z11` traz 11 filhos:

1. Josenilda Sudré Bispo  
2. Joselita Sudré Santos  
3. José Carlos Sudré  
4. Jorge Luiz Sudré  
5. Jailson Sudré  
6. João Sudré  
7. Jacyara Sudré  
8. Jânio Sudré  
9. Juscileide Sudré  
10. Manoelito Gramilo Sodré  
11. Joselito Gramilo Sodré  

Mas depois aparecem também como filhos de José/Zeca:

- `ID=6 | José Gramilo Sodré Filho`
- `a107 | Cleide`
- `a108 | Ione Rosa Sudré`
- `a109 | Maria Rita`

Isso eleva a lista para 15 nomes, salvo se houver duplicidades não identificadas.

### Classificação

**CRÍTICA**

A contagem de filhos e a estrutura do ramo de José ficam contraditórias.

### Correção conservadora

Não remover os nomes adicionais.

Alterar a nota de José/Zeca de:

> “11 filhos”

para:

> “lista de filhos inconsistente: há uma relação inicial de 11 filhos e registros adicionais atribuídos ao mesmo pai. Requer reconciliação.”

Manter todos os nomes como candidatos ao núcleo familiar, mas marcar os adicionais como:

> `CONF=provável` ou `CONF=a confirmar`

até verificar se algum é duplicado ou se a contagem “11 filhos” estava desatualizada.

---

## 4. Tomaz Gramilo Sodré: confirmado em parte do MD, hipotético no JSON e gap crítico em outro trecho

### Divergência

No JSON:

- `ID=1 | Tomaz Gramilo Sodré | CONF=hipotética`
- Notas: “Possível avô ou bisavô de Francisco.”

No MD, seção “O que temos confirmado”:

- “Tomaz Gramilo Sodré × Teodora Julia da Cruz — casaram ~1891, Amargosa/BA”
- “Tomaz como pai de Marguida, casado com Antônia de Gramilo, em registro paroquial 1825”

Mas na seção de gaps:

- `G1 | Ascendentes de Tomaz Gramilo Sodré | NÃO ENCONTRADO`
- `G2 | Tomaz × Teodora | ZERO resultados FS`
- mapa: “Tomaz Gramilo Sodré (~1860-1890) — PAI DE MARCELO?”

Além disso, há conflito entre:

- Tomaz × Teodora Julia da Cruz, casamento ~1891;
- Tomaz casado com Antônia de Gramilo em registro de 1825.

É improvável que seja a mesma pessoa, salvo erro de data, homônimo ou interpretação incorreta.

### Classificação

**CRÍTICA**

Esse conflito pode direcionar a pesquisa para uma linha ancestral errada.

### Correção conservadora

Separar em duas entidades ou, no mínimo, não tratá-las como a mesma pessoa:

1. **Tomaz Gramilo Sodré × Teodora Julia da Cruz**
   - manter como ancestral hipotético/provável;
   - não marcar como confirmado enquanto o casamento ~1891 não for localizado.

2. **Tomaz associado a Antônia de Gramilo e Marguida, registro paroquial de 1825**
   - criar como possível homônimo ou candidato ancestral;
   - não conectar automaticamente a Marcelo.

Correção no MD:

Substituir:

> “Tomaz Gramilo Sodré × Teodora Julia da Cruz — confirmado”

por:

> “Tomaz Gramilo Sodré × Teodora Julia da Cruz — hipótese familiar forte, ainda sem confirmação documental localizada.”

E registrar separadamente:

> “Tomaz × Antônia de Gramilo, pais de Marguida, registro paroquial 1825 — possível homônimo ou ancestral colateral; não deve ser fundido automaticamente com Tomaz × Teodora.”

---

## 5. Alice dos Santos: filha de Maria Aleluia, mas nota diz que é irmã de Maria Aleluia

### Divergência

No JSON:

- `Alice dos Santos`
- `PAIS=['Gervásio Eusébio dos Santos', 'Maria Aleluia dos Santos']`

Mas a nota diz:

> “Irmã de Maria Aleluia dos Santos”

Se Alice é filha de Gervásio e Maria Aleluia, ela seria irmã de Atanagilda Odete dos Santos, não irmã da própria Maria Aleluia.

### Classificação

**CRÍTICA**

É erro de geração e pode deslocar Alice uma geração para cima.

### Correção conservadora

Se os pais informados estiverem corretos, corrigir a nota para:

> “Irmã de Atanagilda Odete dos Santos.”

Se houver dúvida sobre os pais, então manter Alice como:

> “parente dos Santos; relação exata a confirmar.”

Mas não deixar simultaneamente:

- filha de Maria Aleluia;
- irmã de Maria Aleluia.

---

## 6. Pessoas atribuídas diretamente a Jerônimo Sodré Pereira, do século XVII, com eventos do século XIX

### Divergência

No JSON:

- `h1 | Jerônimo Sodré Pereira | NASC=séc. XVII | FALEC=séc. XVIII ou ~1661-1700`

Mas vários registros aparecem como filhos dele:

- `a116 | Edgard Sodré | PAIS=['Jerônimo Sodré Pereira', 'Francisca de Aragão']`
- `a117 | Eduardo Sodré | PAIS=['Jerônimo Sodré Pereira']`
- `a118 | Elisa Sodré Pereira | PAIS=['Jerônimo Sodré Pereira'] | NOTAS=bat. 1881, Salvador`
- `a119 | Henrique Sodré`
- `a122 | José Lino Coutinho Sodré Pereira`

O caso mais evidente é `Elisa Sodré Pereira`, com batismo em 1881, impossível como filha direta de Jerônimo do século XVII.

### Classificação

**CRÍTICA**

Cria uma conexão impossível entre séculos diferentes.

### Correção conservadora

Não ligar esses indivíduos diretamente ao `h1` Jerônimo Sodré Pereira colonial.

Alterar os pais desses registros para algo como:

> `PAIS=['Jerônimo Sodré Pereira [homônimo não identificado]']`

ou remover temporariamente o vínculo direto com `h1`, mantendo nota:

> “Possível homônimo; não conectar ao tronco colonial sem documentação intermediária.”

Também corrigir a geração:

- filhos reais de `h1` não poderiam estar em `GER=5` se `h1` é geração 0;
- portanto, `GER=5` nesses registros indica que provavelmente pertencem a outra linha ou outro Jerônimo.

---

## 7. Esmeraldo Vaz Sodré: cronologia de filhos possivelmente impossível

### Divergência

No JSON:

- `fs1 | Esmeraldo Vaz Sodré | NASC=~1850 (?)`
- filhos atribuídos:
  - `fs3 | Luiz Vaz Sodré | NASC=~1870`
  - `fs2 | Olímpio Sodré | NASC=18/11/1913`
  - `fs4 | Maria do Carmo Sodré | NASC=~1930`

Se Esmeraldo nasceu por volta de 1850, teria:

- cerca de 20 anos em 1870;
- cerca de 63 anos em 1913;
- cerca de 80 anos em 1930.

A paternidade aos 63 é possível, embora tardia; aos 80 é muito improvável. Além disso, a maternidade de Florinda de Andrade em intervalo tão extenso também é suspeita.

### Classificação

**CRÍTICA / MODERADA**

Crítica se todos forem tratados como filhos do mesmo casal; moderada se as datas forem apenas aproximadas ou mal interpretadas.

### Correção conservadora

Não excluir Maria do Carmo nem Luiz Vaz Sodré.

Mas alterar a confiança da relação parental ou da data de Maria do Carmo:

> `NASC=~1930 (?) — data ou filiação a confirmar`

Nota sugerida:

> “Atribuição a Esmeraldo Vaz Sodré e Florinda de Andrade requer verificação: intervalo cronológico dos filhos é muito amplo.”

Também considerar possibilidade de homônimo:

> “Pode haver mais de um Esmeraldo Vaz Sodré ou erro na data estimada de nascimento.”

---

# Inconsistências MODERADAS

## 8. Marcelo e Rita: “6 irmãos de Francisco” no MD versus 6 filhos conhecidos no JSON

### Divergência

No JSON:

- Marcelo e Rita são pais de:
  1. Francisco
  2. Arlindo
  3. José/Zeca
  4. Otávia
  5. Elisa
  6. Isabel

Ou seja, são 6 filhos conhecidos do casal, incluindo Francisco.

No MD aparece:

> “6 irmãos de Francisco: Arlindo, José, Otávia, Elisa, Isabel + 1 não identificado”

Isso implicaria 7 filhos de Marcelo e Rita:

- Francisco;
- 6 irmãos.

### Classificação

**MODERADA**

Afeta contagem familiar, mas não altera nomes conhecidos.

### Correção conservadora

Substituir no MD:

> “6 irmãos de Francisco”

por:

> “5 irmãos conhecidos de Francisco: Arlindo, José/Zeca, Otávia, Elisa e Isabel.”

Se houver tradição oral sobre mais um filho não identificado, escrever:

> “possível 6º irmão de Francisco / 7º filho de Marcelo e Rita — a confirmar.”

---

## 9. Elisa Gramilo Sodré: nota diz 3 filhos, mas há 4º filho listado

### Divergência

No JSON:

- `f9 | Elisa Gramilo Sodré | NOTAS=3 filhos: Zeilde, Valdeci, Elizete.`

Mas há quatro filhos listados:

- `e1 | Zeilde`
- `e2 | Valdeci`
- `e3 | Elizete`
- `a124 | Sísio | NOTAS=4º filho de Elisa`

### Classificação

**MODERADA**

A estrutura está quase completa; a nota está desatualizada.

### Correção conservadora

Atualizar a nota de Elisa para:

> “4 filhos conhecidos: Zeilde, Valdeci, Elizete e Sísio.”

Também acrescentar `Alfredo` como cônjuge de Elisa apenas se já estiver aceito pela própria árvore, pois ele aparece nos campos `PAIS` dos filhos:

- `PAIS=['Elisa Gramilo Sodré', 'Alfredo']`

Correção mínima:

> `CONJ=Alfredo (?)`

ou

> “companheiro/cônjuge indicado nos registros dos filhos; dados completos a confirmar.”

---

## 10. Isabel Gramilo Sodré: nota lista 8 filhos, mas enumera apenas 6; depois aparecem 8 nomes

### Divergência

No JSON:

- `f10 | Isabel Gramilo Sodré | NOTAS=8 filhos: Etelvina "Tezinha", Valdivino, Carlos, Francisco, Dutinha, Edvaldo`

A nota diz 8 filhos, mas lista apenas 6.

Depois aparecem:

- Etelvina “Tezinha”
- Carlos
- Francisco
- Dutinha
- Edvaldo
- Lelinha
- Maria
- Valdivino

Isso fecha 8 nomes.

### Classificação

**MODERADA**

A contagem pode estar correta; a nota inicial está incompleta.

### Correção conservadora

Atualizar a nota de Isabel para:

> “8 filhos conhecidos: Etelvina ‘Tezinha’, Valdivino, Carlos, Francisco, Dutinha, Edvaldo, Lelinha e Maria.”

Também padronizar a mãe de Valdivino:

Atualmente:

- `PAIS=['Isabel Sodré', 'Maximiliano']`

Deve ser:

- `PAIS=['Isabel Gramilo Sodré', 'Maximiliano']`

---

## 11. Arlindo Gramilo Sodré: listas de filhos possivelmente sobrepostas

### Divergência

Primeira lista de filhos de Arlindo e Noemia:

- `f4a | Ana Lúcia Sodré`
- `f4b | Arlindo Sodré Filho`
- `f4c | Sandro Sodré`

Depois aparece outra lista:

- `a92 | Arlenô Gramilo Sodré | 1º filho`
- `a93 | Marcelo Gramilo Sodré Neto | 2º filho`
- `a94 | Antonio Cesar Silva Sodré | 4º filho`
- `a95 | Luciane Silva Sodré | 5ª filha`
- `a96 | Cristiane Silva Sodré | 6ª filha`
- `a97 | Rita de Cássia Silva Sodré Figueredo | 7ª filha`
- `a98 | Manoel Ailton Silva Sodré | 8º filho`

Há lacuna do “3º filho” nessa segunda enumeração. É possível que um dos primeiros três — Ana Lúcia, Arlindo Filho ou Sandro — corresponda ao 3º filho, mas isso não está explicitado.

### Classificação

**MODERADA**

Pode haver duplicação, omissão ou lista parcial.

### Correção conservadora

Não fundir nomes.

Inserir nota em Arlindo:

> “Lista de filhos possui duas camadas de informação; ordem de nascimento e possíveis duplicidades pendentes de reconciliação.”

Não afirmar total definitivo de filhos até reconciliar as duas listas.

---

## 12. Gervásio Eusébio dos Santos versus Gervásio Barbosa dos Santos

### Divergência

No JSON:

- `gm1 | Gervásio Eusébio dos Santos`

No MD, próximos passos:

- `p_293583909851 (Gervásio Barbosa dos Santos) → pais`

Pode ser uma pessoa diferente ou variante de nome, mas não há evidência interna suficiente para identificá-los como a mesma pessoa.

### Classificação

**MODERADA**

Pode causar fusão indevida de pessoas.

### Correção conservadora

Não tratar `Gervásio Barbosa dos Santos` como equivalente a `Gervásio Eusébio dos Santos`.

Registrar como:

> “Gervásio Barbosa dos Santos — candidato/homônimo a verificar; não fundir com Gervásio Eusébio dos Santos sem documento.”

---

## 13. Pais de Atanagilda: JSON marca como provável; MD trata como confirmado por memória oral

### Divergência

No JSON:

- `gm1 | Gervásio Eusébio dos Santos | CONF=provável`
- `gm2 | Maria Aleluia dos Santos | CONF=provável`

Mas no MD:

- “Gervásio Eusébio dos Santos × Maria Aleluia dos Santos — avós maternos”
- aparece com marca de confirmação por memória oral.

### Classificação

**MODERADA**

É uma diferença de grau de confiança.

### Correção conservadora

Padronizar a confiança como:

> `CONF=confirmada por memória oral; documental pendente`

ou, se o esquema aceitar apenas uma palavra:

> `CONF=provável`

com nota:

> “Relação confirmada pela memória familiar; falta confirmação documental.”

Evitar misturar “confirmada documentalmente” com “confirmada por tradição oral”.

---

## 14. Ramo Vaz Sodré: “mesmo ramo” no JSON pode ser forte demais frente ao MD

### Divergência

No JSON, alguns registros dizem:

- `Horácio Vaz Sodré | Sobrenome Vaz Sodré = mesmo ramo`
- `José Virgílio Vaz Sodré | Vaz Sodré = mesmo ramo de Horácio e Luiz`

No MD, porém, a conexão entre Vaz Sodré e Gramilo Sodré é descrita como:

- “conexão provável”
- “hipótese forte”
- “possível elo”

### Classificação

**MODERADA**

A expressão “mesmo ramo” pode ser interpretada como conexão já comprovada com os Gramilo Sodré, quando o MD ainda a trata como hipótese.

### Correção conservadora

Reformular notas do JSON:

De:

> “mesmo ramo”

Para:

> “mesmo agrupamento Vaz Sodré de Amargosa; conexão com Gramilo Sodré ainda hipotética.”

Assim se preserva a ligação interna dos Vaz Sodré sem afirmar elo direto com Marcelo/Tomaz.

---

## 15. Francisco Ludgero Vaz Sodré corretamente marcado como distinto, mas o nome Francisco pode gerar fusão indevida

### Divergência

O JSON informa corretamente:

- `fs13 | Francisco Ludgero Vaz Sodré`
- Nota: “Pessoa DISTINTA de Francisco Gramilo Sodré.”

Não há contradição, mas existe risco de fusão por nomes parecidos:

- Francisco Ludgero Vaz Sodré
- Francisco Gramilo Sodré
- Francisco Gramilo Sodré Filho
- Francisco, filho de Isabel e Maximiliano

### Classificação

**MODERADA**

É risco de identidade, não erro atual.

### Correção conservadora

Manter nota de distinção e reforçar:

> “Não fundir com Francisco Gramilo Sodré de Ibitupã/Aiquara nem com Francisco Gramilo Sodré Filho.”

---

# Inconsistências LEVES ou de sincronização

## 16. Contagem de membros: 121 no cabeçalho versus 84 no MD

### Divergência

Cabeçalho:

> “JSON (121 membros)”

MD:

> “Memória oral — 84 pessoas no JSON”

Arquivos de referência:

> `membros_encontrados.json — 84 pessoas`

### Classificação

**LEVE / MODERADA**

É metadado inconsistente. Pode confundir controle de versão.

### Correção conservadora

Atualizar o MD para:

> “84 pessoas na versão inicial da memória oral; 121 membros na consolidação atual.”

Ou, se a versão atual realmente tem 121:

> `membros_encontrados.json — 121 pessoas na versão consolidada de 2026-06-15.`

---

## 17. Knowledge Graph: 514 fatos versus “10 relações”

### Divergência

Cabeçalho:

> “KG (514 fatos)”

MD:

> “Knowledge Graph — 10 relações”

Seção KG:

> “Entidades com mais relações:”  
> mas não há relações listadas.

### Classificação

**LEVE / MODERADA**

Parece inconsistência de metadados ou relatório incompleto.

### Correção conservadora

Distinguir:

> “KG completo: 514 fatos; subconjunto genealógico principal: 10 relações.”

Ou atualizar o MD se “10 relações” estiver obsoleto.

Também registrar:

> “Relações do KG não foram incluídas no material enviado; auditoria KG↔JSON não pôde ser feita integralmente.”

---

## 18. Vários registros com `ID=?`

### Divergência

Há várias pessoas com `ID=?`, por exemplo:

- Valdivino
- Alice dos Santos
- Marcos Freire de Andrade
- Florença Reis Andrade
- Magno Reis Andrade
- Iêda Reis Andrade
- Magnaldo Reis Andrade

### Classificação

**LEVE / MODERADA**

Não é erro genealógico em si, mas prejudica integridade da árvore e KG.

### Correção conservadora

Atribuir IDs únicos temporários sem alterar relações, por exemplo:

- `tmp_valdivino_01`
- `tmp_alice_santos_01`
- `tmp_marcos_andrade_01`

Depois substituir por IDs definitivos.

---

## 19. Cônjuge de Veralúcia: campo `CONJ` contém nota descritiva

### Divergência

No JSON:

- `c2 | CONJ=Magnaldo Reis Andrade (1ª esposa dele)`

O campo de cônjuge mistura nome e observação.

### Classificação

**LEVE**

Formatação.

### Correção conservadora

Separar:

- `CONJ=Magnaldo Reis Andrade`
- `NOTAS=n. 30/09/1955; 1ª esposa de Magnaldo Reis Andrade`

---

## 20. José/Zeca: referências de pai com e sem apelido

### Divergência

Alguns filhos usam:

- `PAIS=['José Gramilo Sodré']`

Outros usam:

- `PAIS=['José Gramilo Sodré ("Zeca")']`

### Classificação

**LEVE**

Nomenclatura; pode causar duplicação automática.

### Correção conservadora

Padronizar internamente por ID:

- `PAIS=[f7]`

Nome exibido:

> José Gramilo Sodré, “Zeca”.

---

## 21. Isabel aparece como “Isabel Gramilo Sodré” e “Isabel Sodré”

### Divergência

No registro de Valdivino:

- `PAIS=['Isabel Sodré', 'Maximiliano']`

Mas a pessoa principal é:

- `f10 | Isabel Gramilo Sodré`

### Classificação

**LEVE**

Variação de nome.

### Correção conservadora

Padronizar como:

> Isabel Gramilo Sodré

Mantendo “Isabel Sodré” como forma abreviada/variante.

---

## 22. Jerônimo Sodré Pereira: data de falecimento incompatível com século informado

### Divergência

No JSON:

- `FALEC=Bahia, séc. XVIII (~1661-1700)`

O intervalo `1661-1700` pertence majoritariamente ao século XVII, não ao século XVIII.

### Classificação

**LEVE / MODERADA**

Erro cronológico de anotação.

### Correção conservadora

Substituir por:

> `FALEC=Bahia, fim do séc. XVII ou início do séc. XVIII; data incerta`

Ou simplesmente:

> `FALEC=Bahia, data incerta`

Não usar simultaneamente “séc. XVIII” e “~1661-1700”.

---

# Correções conservadoras prioritárias

## Prioridade 1 — proteger integridade da árvore

1. Corrigir IDs duplicados `b8` e `b9`.
2. Substituir todos os `ID=?` por IDs temporários únicos.
3. Não conectar registros do século XIX diretamente ao Jerônimo Sodré Pereira colonial.
4. Separar o Tomaz de 1825 do Tomaz × Teodora ~1891, salvo prova de que são a mesma pessoa.

## Prioridade 2 — reconciliar núcleos familiares

5. Revisar filhos de Otávia: há conflito entre “10 filhos” e lista expandida.
6. Revisar filhos de José/Zeca: há conflito entre “11 filhos” e 15 nomes possíveis.
7. Revisar filhos de Arlindo: há duas listas possivelmente sobrepostas.
8. Atualizar Elisa para 4 filhos, incluindo Sísio.
9. Atualizar Isabel para 8 filhos completos, incluindo Lelinha e Maria.

## Prioridade 3 — padronização de confiança

10. Diferenciar:
   - confirmado por documento;
   - confirmado por memória oral;
   - provável;
   - hipotético.

Especialmente nos casos:

- Gervásio Eusébio dos Santos;
- Maria Aleluia dos Santos;
- Tomaz Gramilo Sodré;
- Teodora Julia da Cruz;
- conexão Vaz Sodré ↔ Gramilo Sodré.

---

# Recomendações de redação conservadora

Para evitar perda de informação consolidada, eu usaria estas fórmulas:

## Para Tomaz

> “Tomaz Gramilo Sodré é ancestral candidato da linha de Marcelo Gramilo Sodré. A ligação com Teodora Julia da Cruz e a posição exata como pai ou avô de Marcelo permanecem hipotéticas até confirmação documental. O Tomaz associado a Antônia de Gramilo em 1825 deve ser tratado como possível homônimo ou ancestral distinto.”

## Para o ramo Vaz Sodré

> “O ramo Vaz Sodré de Amargosa é documentalmente relevante e geograficamente compatível, mas a conexão direta com o ramo Gramilo Sodré ainda não está comprovada.”

## Para Otávia

> “A lista de filhos de Otávia Rosa Sodré Bispo apresenta conflito interno: uma tradição/lista indica 10 filhos, enquanto a consolidação contém nomes adicionais. A contagem final deve permanecer aberta.”

## Para José/Zeca

> “José Gramilo Sodré, ‘Zeca’, possui uma lista inicial de 11 filhos, mas há registros adicionais atribuídos a ele. A relação deve ser reconciliada antes de fixar a contagem definitiva.”

## Para Alice dos Santos

> “Alice dos Santos aparece como filha de Gervásio Eusébio dos Santos e Maria Aleluia dos Santos; portanto, se essa filiação estiver correta, ela é irmã de Atanagilda Odete dos Santos, não de Maria Aleluia.”

---

# Conclusão

As informações mais sólidas continuam sendo:

- Marcelo Gramilo Sodré × Rita Rosa Sodré como pais de Francisco e seus irmãos;
- Francisco Gramilo Sodré × Atanagilda Odete dos Santos;
- os 12 filhos de Francisco e Atanagilda;
- a existência documental do ramo Vaz Sodré de Amargosa;
- a distinção entre Francisco Gramilo Sodré e Francisco Ludgero Vaz Sodré.

Os pontos que exigem maior cautela são:

1. Tomaz Gramilo Sodré e sua identidade real;
2. a ligação Tomaz ↔ Marcelo;
3. a conexão Vaz Sodré ↔ Gramilo Sodré;
4. a lista de filhos de Otávia;
5. a lista de filhos de José/Zeca;
6. os registros atribuídos indevidamente ao Jerônimo Sodré Pereira colonial.