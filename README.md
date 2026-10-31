# IACD Knowledge Graph

> **EN:** An interactive knowledge graph of my first semester of the BSc in Artificial Intelligence and Data Science at FCUP (University of Porto). It maps every concept, prerequisite and exercise from my own course materials, ranks concepts by importance (PageRank, dependents, betweenness) and shows the learning roadmap they impose. Built with Python (data pipeline → JSON / SQLite / CSV / RAG chunks) and Cytoscape.js (interface).
>
> **Demo:** open `app/index.html` in Chrome or Edge — no server needed.
>
> *Note: the course materials themselves (slides, exercise sheets, notes) belong to the lecturers and are not included in this repository, so the "open source PDF" links only work locally.*

Mapa vivo do que aprendi no 1.º semestre da Licenciatura em Inteligência Artificial e Ciência de Dados (FCUP), construído **a partir dos meus próprios materiais** (slides, fichas, resumos, cadernos manuscritos e código) — não de conhecimento genérico sobre IA.

Percurso principal: **IACD → UC → Tema → Conceito → Pré-requisitos / Dependentes → Exercícios → PDF e página onde aprendi aquilo.**

---

## Como abrir

**Opção 1 (recomendada):** fazer duplo clique em `Abrir IACD Knowledge Graph.bat`. Arranca um pequeno servidor local (Python) na pasta `1º Semestre` e abre o browser em `http://localhost:8765/IACD%20Knowledge%20Graph/app/`.

**Opção 2:** abrir diretamente `app/index.html` no Chrome/Edge. Funciona sem servidor porque os dados também são gerados em `data/kg.js`. (Os links para os PDFs abrem na página certa — `#page=N`.)

Atalhos: `/` ou `Ctrl+K` pesquisa · `O` overview · `F` filtros · `R` roadmap · `M` mapa · `Esc` limpa a seleção.

## O que a aplicação faz

| Área | Descrição |
|---|---|
| **Mapa** | Vista inicial limpa (IACD + 5 UCs + Horizonte). Clicar numa UC mostra os temas; num tema mostra os conceitos; num conceito ativa o **modo Focus** (verde = de onde vem, laranja = o que depende dele, o resto fica esbatido). Ligações entre conceitos escondidos são agregadas ao nível do tema/UC (nível de detalhe). |
| **Painel lateral** | Importância e dificuldade (com justificação), descrição, fórmula, pré-requisitos, dependentes, relacionados (cada um com natureza Explícita/Inferida e confiança), exercícios e fontes com link direto para a página. |
| **Pesquisa** | Global, sem acentos, com sinónimos (ex.: `matriz` → Matriz, Produto de matrizes, Matriz inversa, Matriz ampliada, Determinante…). Ao escolher: centra, faz zoom e destaca relações. |
| **Filtros** | UC, tipo de nó, dificuldade, importância mínima, tipo de relação; "só importantes", "só com dependências", "relações entre UCs", "inferidas", matéria programada/horizonte, exercícios, ficheiros. |
| **Roadmap** | Progressão conceptual calculada a partir das dependências (camadas = cadeia de pré-requisitos mais longa), em faixas por UC. Não é "Ano 1 → Ano 2": é a ordem real que os materiais impõem. |
| **Bottlenecks** | Conceitos no caminho de muitos outros: "se não dominar isto, o que fica comprometido?" (lista de dependentes + cadeia mais longa). |
| **Estatísticas** | Totais, conceitos por UC, mais conectados, maiores pré-requisitos, pontes entre áreas, densidade de temas, matriz UC×UC, confiança e estado de cada ficheiro. |
| **Minimapa, Overview, Dark mode, exportação PNG** | Canto inferior direito / barra superior. |

## Arquitetura

```
IACD Knowledge Graph/
├── build/
│   ├── knowledge.py      ← base curada (UCs, temas, conceitos, relações, exercícios resolvidos)
│   ├── build.py          ← pipeline (inventário → texto → páginas → exercícios → métricas → layout → export)
│   └── pdf_text.json     ← cache do texto extraído (por página)
├── data/                 ← gerado — NÃO editar à mão
│   ├── kg.json           ← { meta, stats, nodes, edges, bottlenecks, roadmap, files, quality }
│   ├── kg.js             ← o mesmo JSON para abrir a app sem servidor
│   ├── kg.sqlite         ← tabelas nodes, edges, sources, files, bottlenecks
│   ├── csv/nodes.csv · edges.csv · sources.csv
│   ├── rag_chunks.jsonl  ← 1 documento por conceito (para RAG / tutor de IA)
│   └── quality_report.md
├── app/                  ← interface (HTML + CSS + JS; Cytoscape.js incluído em vendor/)
└── Abrir IACD Knowledge Graph.bat
```

A interface só lê `data/`; nenhum conteúdo está escrito no código da app.

## Estrutura dos dados

**Nós** (`type`): `root`, `uc`, `tema`, `conceito`, `formula`, `algoritmo`, `ferramenta`, `exercicio`, `ficheiro`, `aula` (cadernos CAL n / ED n / ALGA n).
Campos principais: `id, label, uc, tema, status (lecionado|programado|horizonte), desc, formula, aliases, difficulty, difficulty_why, importance, importance_why, metrics{pagerank, dependents, betweenness, exercises, cross_uc, pages}, layer, sources[{file, page, note, verified, kind}], pos{map, roadmap}`.

**Relações**: `source, target, type, nature (explicita|inferida), confidence (alta|media|baixa), evidence (ficheiro#página), justification`.

Tipos: `contains` (e o inverso `part_of`), `prerequisite_of`, `requires` (exercício → conceito secundário), `related_to`, `used_in`, `applied_in`, `appears_in`, `explained_in`, `tested_by`, `followed_by`.
`followed_by` é **só ordem temporal** (aulas, folhas, temas no índice) e nunca entra no cálculo de dependências.

## Confiança — regra absoluta

* **Explícita**: a relação está escrita nos materiais (ex.: Resumo de ALGA p. 4 "Gauss-Jordan… usado mais à frente para as inversas").
* **Inferida**: deduzida do conteúdo (ex.: a definição ε–N de Cálculo usa quantificadores encadeados de Estruturas Discretas). Aparece **sempre** marcada como "Inferida" (linha tracejada e etiqueta no painel) — nunca como se fosse ensinada.
* Conceitos de **Horizonte** vêm só do índice do livro Stewart e de menções nos slides de IC (IA, Big Data, redes neuronais); todas as ligações para lá são inferidas.
* **IP** não tem enunciados na pasta — os conceitos de programação foram inferidos do código `ex1.py … ex44.py`.

## Como os ficheiros foram analisados

1. Inventário de todos os ficheiros de `1º Semestre` (exceto esta pasta).
2. PDFs com texto → `pdftotext` página a página (ou `pypdf`). O livro Stewart (1404 p.) só teve o índice lido.
3. PDFs digitalizados sem texto (cadernos `CAL 1–12`, `ED 1–6`, `ALGA 1–5`) → **lidos visualmente** página a página; as fontes desses conceitos apontam para a página do caderno. `ED 4.pdf` está em branco.
4. Código Python lido integralmente.
5. Cada conceito tem fontes **verificadas** (lidas manualmente) e fontes **localizadas automaticamente** por palavras-chave (marcadas como tal no painel).
6. Exercícios das fichas extraídos por numeração e classificados por palavras-chave; os que estão resolvidos nos cadernos ficam ligados à resolução.

## Importância e dificuldade

* **Importância (1–5)** combina: PageRank no grafo de dependências invertido (30%), nº de dependentes diretos+indiretos (30%), exercícios (15%), frequência nas páginas (12%) e intermediação/“ponte” (13%). Não é só frequência: um conceito que aparece pouco mas é pré-requisito de muitos fica alto. A justificação textual é gerada para cada conceito.
* **Dificuldade (1–5)** foi atribuída na curadoria com justificação a partir do material (ex.: "Primeira definição com quantificadores encadeados…"). Para exercícios é uma estimativa (marcada como INFERIDA).

## Atualizar com novos materiais

1. Coloca os novos ficheiros nas pastas das UCs (ou cria a pasta de uma UC nova).
2. Em `build/knowledge.py`:
   * nova UC → `UCS`; novo tema → `TEMAS`;
   * novo conceito → `C("id", "Nome", "uc", "tema", "descrição", kw=[regex…], src=[(ficheiro, página, nota)], diff=(n, "porquê"))`;
   * nova relação → `R(origem, tipo, destino, E|I, "alta|media|baixa", "ficheiro#página", "justificação")`;
   * exercícios resolvidos → `SOLVED`; regras para classificar fichas → `SHEET_RULES`.
3. Reconstruir a graph:
   ```
   cd "IACD Knowledge Graph"
   python build/build.py
   ```
   (Só biblioteca padrão; para texto de PDFs novos precisa de `pdftotext` (Poppler) ou `pip install pypdf`.)
4. Ver `data/quality_report.md`: duplicados, sinónimos partilhados, relações contraditórias e ciclos (resolvidos automaticamente), conceitos sem fonte, relações sem justificação, ficheiros não analisados e links partidos.

## Exportar / reutilizar

Menu ⤓ na barra superior, ou diretamente em `data/`:
* **JSON / SQLite / CSV** — dashboards, análise da progressão, sistema de revisão.
* **`rag_chunks.jsonl`** — um documento por conceito com UC, tema, fórmula, pré-requisitos (com natureza/confiança), dependentes e fontes: pronto para RAG, um tutor de IA ou um gerador de exercícios.

Exemplo SQLite:
```sql
SELECT n.label, e.nature, e.confidence, e.evidence
FROM edges e JOIN nodes n ON n.id = e.source
WHERE e.type = 'prerequisite_of' AND e.target = 'limite_eps_n';
```

## Limitações conhecidas

* A transcrição dos cadernos manuscritos foi feita por leitura visual; algumas páginas de continuação (ex.: CAL 1 p.7) só estão referenciadas ao nível do ficheiro.
* A classificação automática dos exercícios das fichas por palavras-chave pode errar no conceito secundário — as ligações estão marcadas como "Inferida · média".
* Os temas de ED ainda não lecionados (Teoria de Números, Relações, Contagem, Grafos) aparecem como **programados** e os respetivos exercícios estão agrupados em blocos.
