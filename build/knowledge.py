# -*- coding: utf-8 -*-
"""
IACD Knowledge Graph — base de conhecimento curada.

Este ficheiro é a "fonte de verdade" humana da graph. Tudo o que está aqui foi
retirado dos materiais da pasta "1º Semestre" (slides, fichas, resumos,
cadernos manuscritos e código). O script build.py lê este ficheiro, localiza
automaticamente as páginas onde cada conceito aparece (através das palavras-chave
`kw`) e gera JSON / CSV / SQLite.

Convenções
----------
* Caminhos de ficheiros são relativos à pasta "1º Semestre".
* `src` = fontes verificadas manualmente: (ficheiro, página, nota).
  Para os cadernos manuscritos (CAL n, ED n, ALGA n) as páginas foram lidas
  visualmente (são digitalizações sem texto).
* `diff` = (dificuldade 1-5, justificação). A justificação deve citar o material.
* Relações em REL: (origem, tipo, destino, natureza, confiança, fonte, justificação)
    natureza  = "explicita" (indicada nos materiais) | "inferida" (deduzida)
    confiança = "alta" | "media" | "baixa"
* status: "lecionado" (já dado), "programado" (no programa/enunciados mas ainda
  sem matéria dada), "horizonte" (aparece apenas em material de referência,
  ex.: índice do livro Stewart, ou menções nos slides).
"""

ROOT = dict(id="iacd", name="IACD", full="Licenciatura em Inteligência Artificial e Ciência de Dados · FCUP · 1.º ano, 1.º semestre (2026/2027)")

UCS = [
    dict(id="alga", name="Álgebra Linear e Geometria Analítica", short="ALGA", code="M1002",
         folder="Álgebra Linear e Geometria Analítica", hue=212,
         desc="Vetores, retas e planos; sistemas de equações lineares; matrizes; determinantes e aplicações."),
    dict(id="cal", name="Cálculo I", short="Cálculo I", code="",
         folder="Cálculo I", hue=268,
         desc="Sucessões e limites (ε–N), séries e critérios de convergência, funções, continuidade e derivadas (livro: Stewart)."),
    dict(id="ed", name="Estruturas Discretas", short="ED", code="",
         folder="Estruturas Discretas", hue=158,
         desc="Lógica proposicional e de primeira ordem, inferência, conjuntos e indução. Programa inclui ainda teoria de números, relações, contagem e grafos."),
    dict(id="ip", name="Introdução à Programação", short="IP", code="",
         folder="Introdução à Programação", hue=28,
         desc="Programação em Python: I/O, condicionais, ciclos, funções, strings e tuplos (inferido a partir das resoluções ex1–ex44)."),
    dict(id="ic", name="Introdução aos Computadores", short="IC", code="CC1002",
         folder="Introdução aos Computadores", hue=340,
         desc="O computador, história e computabilidade, arquitetura, shell Unix e representação de dados (Prof. Miguel Areias)."),
    dict(id="hz", name="Horizonte", short="Horizonte", code="",
         folder="", hue=45, horizon=True,
         desc="Matéria que aparece apenas em material de referência (índice do livro Stewart, menções nos slides de IC). Ainda não lecionada — todas as ligações para aqui são INFERIDAS."),
]

# (id, uc, nome, descrição, status)
TEMAS = [
    # ALGA
    ("alga_retas", "alga", "Vetores, Retas e Planos", "Produto interno, norma, equações cartesianas e vetoriais de retas e planos em R² e R³.", "lecionado"),
    ("alga_sist", "alga", "Sistemas de Equações Lineares", "Classificação, matriz ampliada, eliminação de Gauss, característica e discussão de sistemas.", "lecionado"),
    ("alga_mat", "alga", "Matrizes", "Matrizes especiais, operações, produto, inversa e matrizes elementares.", "lecionado"),
    ("alga_det", "alga", "Determinantes", "Definição axiomática, propriedades, expansão de Laplace e regra de Sarrus.", "lecionado"),
    ("alga_apl", "alga", "Aplicações dos Determinantes", "Áreas, volumes, colinearidade, regra de Cramer e produto vetorial.", "lecionado"),
    # Cálculo
    ("cal_suc", "cal", "Sucessões e Limites", "Definição ε–N, propriedades dos limites, subsucessões, sucessões monótonas.", "lecionado"),
    ("cal_ser", "cal", "Séries", "Somas parciais, séries geométricas e telescópicas, critérios de convergência.", "lecionado"),
    ("cal_fun", "cal", "Funções, Limites e Continuidade", "Domínios, funções trigonométricas e inversas, limite ε–δ e continuidade.", "lecionado"),
    ("cal_der", "cal", "Derivadas", "Definição, reta tangente, regras de derivação, regra da cadeia, derivada da inversa.", "lecionado"),
    ("cal_apl", "cal", "Aplicações das Derivadas", "Monotonia, extremos, aproximação linear (Taylor 1.ª ordem) e método de Newton.", "lecionado"),
    ("cal_prim", "cal", "Primitivas", "Primitiva de uma função (início da matéria).", "lecionado"),
    # ED
    ("ed_lp", "ed", "Lógica Proposicional", "Conectivas, tabelas de verdade, tautologias e equivalência lógica.", "lecionado"),
    ("ed_fn", "ed", "Formas Normais", "FNN, FND e FNC; decidir satisfazibilidade e validade.", "lecionado"),
    ("ed_lpo", "ed", "Lógica de Primeira Ordem", "Predicados, quantificadores, negação e formalização de frases.", "lecionado"),
    ("ed_inf", "ed", "Regras de Inferência", "Modus ponens, modus tollens e provas formais de validade.", "lecionado"),
    ("ed_conj", "ed", "Teoria de Conjuntos", "Operações, conjunto das partes, produto cartesiano, cardinalidade e provas.", "lecionado"),
    ("ed_ind", "ed", "Indução e Técnicas de Prova", "Indução (simples e forte), recorrências, demonstrações diretas e por contradição.", "lecionado"),
    ("ed_num", "ed", "Teoria de Números", "Divisibilidade, mdc, algoritmo de Euclides e primos (no programa; exercícios 98–131).", "programado"),
    ("ed_rel", "ed", "Relações e Funções", "Relações binárias, equivalência, partições, funções (no programa; exercícios 132–173).", "programado"),
    ("ed_cont", "ed", "Contagem", "Princípios de contagem (no programa; exercícios 174–214).", "programado"),
    ("ed_graf", "ed", "Grafos", "Grafos, graus, caminhos e conexidade (no programa; exercícios 215–240).", "programado"),
    # IP
    ("ip_base", "ip", "Valores, I/O e Expressões", "print/input, tipos, conversões, operadores e formatação (ex1–ex7).", "lecionado"),
    ("ip_cond", "ip", "Condicionais", "if/elif/else e operadores relacionais e lógicos (ex8–ex11, ex18, ex19).", "lecionado"),
    ("ip_ciclos", "ip", "Ciclos", "while, for/range, acumuladores e contadores (ex12–ex17, ex20–ex22).", "lecionado"),
    ("ip_func", "ip", "Funções", "def/return e decomposição de problemas (ex23–ex32).", "lecionado"),
    ("ip_seq", "ip", "Strings e Tuplos", "Indexação, slicing, iteração e tuplos (ex33–ex44).", "lecionado"),
    # IC
    ("ic_comp", "ic", "O Computador", "Hardware, software, CPU, memória e armazenamento.", "lecionado"),
    ("ic_hist", "ic", "História e Computabilidade", "Algoritmos, Babbage/Lovelace, Turing, von Neumann, transístor e lei de Moore.", "lecionado"),
    ("ic_arq", "ic", "Arquitetura do Computador", "Arquitetura de von Neumann, barramentos, load/store e Harvard.", "lecionado"),
    ("ic_shell", "ic", "Shell de Comandos Unix", "Navegação, ficheiros, permissões, processos, glob, pipes e filtros (Folhas 1–2).", "lecionado"),
    ("ic_repr", "ic", "Representação de Dados", "Bases de numeração, inteiros, complemento para 2, vírgula flutuante e texto.", "lecionado"),
    # Horizonte
    ("hz_calc", "hz", "Cálculo (livro Stewart)", "Capítulos do livro de referência ainda não lecionados (apenas índice lido).", "horizonte"),
    ("hz_dados", "hz", "IA e Dados (menções em IC)", "Referências a IA, Big Data e redes neuronais nos slides de IC.", "horizonte"),
]

F = dict(  # atalhos para ficheiros
    ALGA_R="Álgebra Linear e Geometria Analítica/Resumo_ALGA_Cap1-3.pdf",
    ALGA_S1="Álgebra Linear e Geometria Analítica/1-sist_eq_lin_2x1.pdf",
    ALGA_S2="Álgebra Linear e Geometria Analítica/2-matrizes_2x1.pdf",
    ALGA_S3="Álgebra Linear e Geometria Analítica/3-determinantes_2x1.pdf",
    ALGA_E1="Álgebra Linear e Geometria Analítica/1-exerc-sistemas.pdf",
    ALGA_E2="Álgebra Linear e Geometria Analítica/2-exerc-matrizes.pdf",
    CAL_R="Cálculo I/Resumo_Calculo_I.pdf",
    STEW="Cálculo I/Stewart.pdf",
    ED_R="Estruturas Discretas/Resumo_Estruturas_Discretas.pdf",
    ED_L="Estruturas Discretas/logica.pdf",
    ED_C="Estruturas Discretas/conjuntos.pdf",
    ED_I="Estruturas Discretas/inducao.pdf",
    ED_E="Estruturas Discretas/exercicios.pdf",
    IC0="Introdução aos Computadores/00-introducao.pdf",
    IC1="Introdução aos Computadores/01-historia-dos-computadores.pdf",
    IC2="Introdução aos Computadores/02-anatomia-do-computador.pdf",
    IC3="Introdução aos Computadores/03-armazenamento-de-dados.pdf",
    F1="Introdução aos Computadores/f01.pdf",
    F2="Introdução aos Computadores/f02.pdf",
    F3="Introdução aos Computadores/f03.pdf",
    F4="Introdução aos Computadores/f04.pdf",
)


def cad(uc, n):
    return {"cal": f"Cálculo I/CAL {n}.pdf", "ed": f"Estruturas Discretas/ED {n}.pdf",
            "alga": f"Álgebra Linear e Geometria Analítica/ALGA {n}.pdf"}[uc]


CONCEPTS = []


def C(id, name, uc, tema, desc, kw=(), type="conceito", src=(), diff=None, aliases=(), formula=None, status=None):
    CONCEPTS.append(dict(id=id, name=name, uc=uc, tema=tema, desc=desc, kw=list(kw), type=type,
                         src=[dict(file=s[0], page=s[1], note=s[2] if len(s) > 2 else "") for s in src],
                         diff=diff, aliases=list(aliases), formula=formula, status=status))


# =============================================================================
# ÁLGEBRA LINEAR E GEOMETRIA ANALÍTICA
# =============================================================================
C("vetores_rn", "Vetores em Rⁿ", "alga", "alga_retas",
  "Vetores u = (a₁,…,aₙ) de Rⁿ; base para descrever retas, planos e sistemas.",
  kw=[r"vetores?\s+(em|de)\s+R", r"Rn\b", r"\(a1\s*,"], src=[(F["ALGA_R"], 2, "§1 Vetores em Rⁿ"), (F["ALGA_S1"], 1, "1.1 Revisão")],
  diff=(1, "Revisão do secundário (slide 1.1 'Revisão sobre retas e planos')."), aliases=["vetor", "vetores"])
C("produto_interno", "Produto interno", "alga", "alga_retas",
  "Produto escalar usual u·v = a₁b₁ + … + aₙbₙ. Define norma, distância e ortogonalidade.",
  type="formula", formula="u·v = a₁b₁ + a₂b₂ + … + aₙbₙ",
  kw=[r"produto\s+(escalar|interno)", r"u\s*·\s*v"], src=[(F["ALGA_R"], 2, "definição"), (F["ALGA_S1"], 1, "Produto escalar ou interno (usual)")],
  diff=(1, "Fórmula direta; usada em quase todos os métodos-tipo do Resumo §9."), aliases=["produto escalar", "dot product"])
C("norma", "Norma e distância", "alga", "alga_retas",
  "‖u‖ = √(u·u) e d(u,v) = ‖u − v‖.", type="formula", formula="‖u‖ = √(u·u),  d(u,v) = ‖u − v‖",
  kw=[r"\bnorma\b", r"comprimento", r"d\(u,\s*v\)"], src=[(F["ALGA_R"], 2, "")],
  diff=(1, "Definida a partir do produto interno numa linha do Resumo §1."), aliases=["comprimento", "distância"])
C("ortogonalidade", "Ortogonalidade e colinearidade", "alga", "alga_retas",
  "u ⊥ v se u·v = 0; u ∥ v se u = a·v com a ≠ 0. Critério de paralelismo de retas e planos.",
  kw=[r"ortogona", r"colinear", r"paralel", r"perpendicular"], src=[(F["ALGA_R"], 2, "Definição")],
  diff=(2, "Usada para decidir paralelismo de retas/planos (Resumo §1, exercícios 1.1–1.2)."), aliases=["perpendicular", "paralelo"])
C("eq_cartesiana", "Equação cartesiana de reta e plano", "alga", "alga_retas",
  "Reta em R²: ax+by=c; plano em R³: ax+by+cz=d com (a,b,c) vetor normal. Uma reta em R³ é a interseção de dois planos.",
  kw=[r"equa[çc][ãa]o\s+cartesiana", r"cartesianas?", r"vetor\s+normal"], src=[(F["ALGA_R"], 2, "Equações cartesianas e vetoriais"), (F["ALGA_S1"], 2, ""), (cad("alga", 1), 2, "Ex. 1.1, 1.2")],
  diff=(2, "Requer passar entre representações (exercícios 1.1–1.3)."), aliases=["vetor normal", "equação do plano"])
C("eq_vetorial", "Equação vetorial de reta e plano", "alga", "alga_retas",
  "Reta: P + t·v; plano: P + s·u + t·v com u, v não colineares. Converter vetorial ↔ cartesiana eliminando parâmetros.",
  kw=[r"equa[çc][ãa]o\s+vetorial", r"vetor\s+diretor", r"param[ée]tric"], src=[(F["ALGA_R"], 2, ""), (F["ALGA_S1"], 2, "Equação vetorial de uma reta"), (cad("alga", 1), 4, "Ex. 1.3")],
  diff=(2, "Conversões vetorial↔cartesiana aparecem como método-tipo (Resumo §9)."), aliases=["vetor diretor", "equações paramétricas"])
C("eq_linear", "Equação e sistema linear", "alga", "alga_sist",
  "Equação a₁x₁+…+aₙxₙ = b; sistema de m equações em n incógnitas; solução é um n-tuplo que satisfaz todas.",
  kw=[r"equa[çc][ãa]o\s+linear", r"sistemas?\s+de\s+equa", r"sistema\s+linear"], src=[(F["ALGA_R"], 3, "§2"), (F["ALGA_S1"], 4, "1.2 Sistemas de equações lineares")],
  diff=(1, "Definição inicial do capítulo 1."), aliases=["sistema linear", "sistemas lineares"])
C("sist_homogeneo", "Sistema homogéneo", "alga", "alga_sist",
  "Termos independentes nulos; tem sempre a solução nula; ou só a nula ou infinitas. Relaciona-se com a unicidade da solução do sistema completo.",
  kw=[r"homog[ée]ne"], src=[(F["ALGA_R"], 3, "Sistemas homogéneos"), (F["ALGA_S1"], 4, "")],
  diff=(2, "Propriedades estruturais (s+t, λs) com corolários no Resumo §2."), aliases=["homogéneo associado"])
C("classif_sist", "Classificação de sistemas (SPD, SPI, SI)", "alga", "alga_sist",
  "Impossível (0 soluções), possível e determinado (1), possível e indeterminado (∞).",
  kw=[r"\bSPD\b", r"\bSPI\b", r"\bSI\b", r"poss[ií]vel\s+e\s+(in)?determinado", r"imposs[ií]vel"], src=[(F["ALGA_R"], 3, "Classificação"), (cad("alga", 2), 3, "Ex. 1.8")],
  diff=(2, "Classificação aplicada em quase todos os exercícios da folha 1."), aliases=["SPD", "SPI", "SI"])
C("op_elementares", "Operações elementares", "alga", "alga_sist",
  "Lᵢ↔Lⱼ, λLᵢ (λ≠0), Lⱼ+λLᵢ: produzem sistemas equivalentes. Base da eliminação de Gauss, da inversa e dos determinantes.",
  kw=[r"opera[çc][õo]es?\s+elementar", r"sistemas?\s+equivalentes", r"L\s*i\s*↔"], src=[(F["ALGA_R"], 3, ""), (F["ALGA_R"], 4, "Operações elementares sobre linhas"), (F["ALGA_S1"], 5, "")],
  diff=(2, "Mecânicas, mas todo o capítulo 1–3 depende delas."), aliases=["operações sobre linhas", "sistemas equivalentes"])
C("matriz_ampliada", "Matriz ampliada (A | B)", "alga", "alga_sist",
  "Um sistema corresponde à matriz dos coeficientes A, à coluna B e à matriz ampliada (A|B).",
  kw=[r"matriz\s+(ampliada|alargada)", r"\(A\s*\|\s*B\)"], src=[(F["ALGA_R"], 4, "§3"), (F["ALGA_S1"], 6, "1.3 Matrizes e a resolução de sistemas"), (F["ALGA_E1"], 1, "Ex. 1.6–1.7")],
  diff=(1, "Tradução direta sistema → matriz (Ex. 1.6)."), aliases=["matriz alargada", "matriz dos coeficientes"])
C("forma_escada", "Forma em escada e pivô", "alga", "alga_sist",
  "Pivô = primeira entrada não nula; matriz em escada se linhas nulas em baixo e pivôs a deslocar-se para a direita.",
  kw=[r"em\s+escada", r"escalonad", r"piv[ôo]"], src=[(F["ALGA_R"], 4, "Definição"), (F["ALGA_S1"], 7, "")],
  diff=(2, "Reconhecer e produzir a forma em escada é o passo central do método exigido."), aliases=["escalonada", "pivô", "pivôs"])
C("forma_reduzida", "Forma reduzida", "alga", "alga_sist",
  "Em escada, pivôs iguais a 1 e restantes entradas das colunas-pivô nulas. É única.",
  kw=[r"forma\s+reduzida", r"\breduzida\b"], src=[(F["ALGA_R"], 4, ""), (F["ALGA_S1"], 7, "Algoritmo para a forma reduzida")],
  diff=(2, "Extensão da forma em escada; usada mais à frente para as inversas (Resumo §3)."))
C("caracteristica", "Característica car(A)", "alga", "alga_sist",
  "Número de pivôs de uma forma em escada de A. Decide a classificação do sistema.",
  kw=[r"caracter[ií]stica", r"car\s*\("], src=[(F["ALGA_R"], 4, ""), (cad("alga", 2), 3, "Ex. 1.8"), (cad("alga", 3), 2, "Discussão com parâmetros")],
  diff=(3, "Conceito abstrato que liga escalonamento e número de soluções."), aliases=["car(A)", "rank", "posto"])
C("gauss", "Eliminação de Gauss", "alga", "alga_sist",
  "(A|B) → forma em escada → resolver de baixo para cima. É o método exigido na UC.",
  type="algoritmo",
  kw=[r"elimina[çc][ãa]o\s+de\s+Gauss", r"m[ée]todo\s+de\s+Gauss", r"\bGauss\b"], src=[(F["ALGA_R"], 4, "'É o método exigido'"), (F["ALGA_S1"], 8, ""), (cad("alga", 2), 2, "Ex. 1.7"), (cad("alga", 2), 4, "Ex. 1.9")],
  diff=(3, "Algoritmo com muitos passos; a maioria dos exercícios da folha 1 depende dele."), aliases=["escalonamento", "Gauss"])
C("gauss_jordan", "Método de Gauss-Jordan", "alga", "alga_sist",
  "(A|B) → forma reduzida. Usado para calcular inversas com (A | I).",
  type="algoritmo",
  kw=[r"Gauss-Jordan", r"Gauss\s*–\s*Jordan"], src=[(F["ALGA_R"], 4, "'usado mais à frente para as inversas'"), (F["ALGA_S2"], 5, "2.3 Matrizes invertíveis")],
  diff=(3, "Continuação de Gauss até à forma reduzida."), aliases=["Gauss Jordan"])
C("discussao_sist", "Discussão de sistemas", "alga", "alga_sist",
  "SI ⇔ car(A) ≠ car(A|B); SPI ⇔ car(A)=car(A|B) < n; SPD ⇔ car(A)=car(A|B)=n. Sistemas com mais incógnitas que equações nunca são SPD.",
  type="formula", formula="SPD ⇔ car(A) = car(A|B) = n",
  kw=[r"discuss[ãa]o", r"discut", r"car\(A\)\s*=\s*car"], src=[(F["ALGA_R"], 4, "Resultado (discussão de sistemas)"), (F["ALGA_S1"], 9, "Corolário")],
  diff=(3, "Combina característica e classificação."), aliases=["teorema da característica"])
C("sist_parametros", "Sistemas com parâmetros", "alga", "alga_sist",
  "Escalonar sem dividir por expressões que possam ser 0; analisar os valores que anulam pivôs (última linha (0…0 | f(a))).",
  type="algoritmo",
  kw=[r"par[âa]metros?"], src=[(F["ALGA_R"], 10, "Métodos-tipo: discutir um sistema com parâmetros"), (cad("alga", 3), 2, "Exemplo do caderno (a, b)")],
  diff=(4, "Exige casos e cuidado com divisões por zero; marcado como método-tipo de exame."), aliases=["discutir em função de parâmetros"])
C("interpolacao", "Interpolação polinomial", "alga", "alga_sist",
  "Dados n pontos com abcissas distintas existe um único polinómio de grau < n que passa por eles — resolve-se como sistema linear.",
  kw=[r"interpola", r"polin[óo]mio\s+de\s+grau"], src=[(F["ALGA_R"], 4, "Aplicação: interpolação polinomial"), (cad("alga", 2), 5, "Ex. 1.17")],
  diff=(2, "Aplicação direta de sistemas 3×3/4×4."), aliases=["polinómio interpolador"])
C("matriz", "Matriz (definição e tipos)", "alga", "alga_mat",
  "Matriz m×n; especiais: linha/coluna, nula, quadrada, identidade, diagonal, triangular, simétrica.",
  kw=[r"\bmatriz(es)?\b", r"identidade", r"triangular", r"sim[ée]trica"], src=[(F["ALGA_R"], 5, "§4 Matrizes especiais"), (F["ALGA_S2"], 1, "2.1 Matrizes especiais")],
  diff=(1, "Definições."), aliases=["matrizes", "matriz identidade", "matriz triangular", "matriz simétrica"])
C("op_matrizes", "Operações com matrizes", "alga", "alga_mat",
  "Soma (mesmo tipo), multiplicação por escalar e transposta (A + B)ᵗ = Aᵗ + Bᵗ.",
  kw=[r"transposta", r"adi[çc][ãa]o", r"A\s*\+\s*B"], src=[(F["ALGA_R"], 5, "Operações"), (F["ALGA_S2"], 2, "2.2 Operações com matrizes")],
  diff=(1, "Operações entrada-a-entrada."), aliases=["transposta", "soma de matrizes"])
C("produto_matrizes", "Produto de matrizes", "alga", "alga_mat",
  "(AB)ᵢⱼ = Σₖ aᵢₖ bₖⱼ = (linha i de A)·(coluna j de B). Associativo mas não comutativo; (AB)ᵗ = BᵗAᵗ.",
  type="formula", formula="cᵢⱼ = Σₖ aᵢₖ·bₖⱼ",
  kw=[r"produto\s+de\s+matrizes", r"multiplica[çc][ãa]o\s+de\s+matrizes", r"AB\s*[̸≠]=?\s*BA", r"n[ãa]o\s+[ée]\s+comutativo"], src=[(F["ALGA_R"], 5, "Produto; 'Atenção: não é comutativo'"), (F["ALGA_S2"], 3, "Sistemas e multiplicação de matrizes"), (cad("alga", 3), 3, "")],
  diff=(3, "Regra linha×coluna e armadilhas (AB ≠ BA, AB = 0 com A,B ≠ 0) sublinhadas no Resumo."), aliases=["multiplicação de matrizes", "produto matricial", "operações matriciais"])
C("forma_matricial", "Forma matricial AX = B", "alga", "alga_mat",
  "Todo o sistema escreve-se como AX = B (A m×n, X n×1, B m×1).",
  kw=[r"AX\s*=\s*B", r"forma\s+matricial"], src=[(F["ALGA_R"], 5, "Sistemas na forma matricial"), (F["ALGA_S2"], 3, "")],
  diff=(2, "Liga sistemas e produto de matrizes."), aliases=["sistema na forma matricial"])
C("inversa", "Matriz invertível e inversa", "alga", "alga_mat",
  "A é invertível se existe B com AB = I = BA (única, A⁻¹). (AB)⁻¹ = B⁻¹A⁻¹; se A invertível, AX = B tem solução única X = A⁻¹B.",
  kw=[r"invert[ií]ve", r"\binversa\b", r"A\s*[−-]\s*1"], src=[(F["ALGA_R"], 6, "§5 Matrizes invertíveis"), (F["ALGA_S2"], 4, "2.3"), (cad("alga", 5), 2, "Ex. 2.7")],
  diff=(3, "Várias propriedades e cuidados ('só vale se C for invertível')."), aliases=["matriz inversa", "A⁻¹", "invertível"])
C("inversa_2x2", "Inversa 2×2", "alga", "alga_mat",
  "A = [a b; c d] é invertível ⇔ ad − bc ≠ 0, e A⁻¹ = (1/(ad−bc))·[d −b; −c a].",
  type="formula", formula="A⁻¹ = 1/(ad−bc) · [d −b; −c a]",
  kw=[r"ad\s*[−-]\s*bc"], src=[(F["ALGA_R"], 6, "Resultado (inversa 2×2)"), (cad("alga", 5), 2, "Ex. 2.7 a)")],
  diff=(1, "Fórmula fechada."))
C("inversa_gj", "Cálculo da inversa por (A | I)", "alga", "alga_mat",
  "Aplicar Gauss-Jordan a (A | I): se se chega a (I | C), então A⁻¹ = C; caso contrário A não é invertível.",
  type="algoritmo",
  kw=[r"\(A\s*\|\s*I\)", r"\(A\|I\)"], src=[(F["ALGA_R"], 6, "Método (Gauss-Jordan)"), (cad("alga", 4), 2, "Exemplo 3×3"), (cad("alga", 5), 2, "Ex. 2.11, 2.12")],
  diff=(3, "Algoritmo longo com muitas contas (exercícios 2.11–2.12)."), aliases=["inversa por Gauss-Jordan"])
C("mat_elementares", "Matrizes elementares", "alga", "alga_mat",
  "E_α = operação α aplicada à identidade; aplicar α a A equivale a E_α·A. São invertíveis; qualquer matriz é produto de elementares pela sua forma reduzida.",
  kw=[r"matriz(es)?\s+elementar", r"E\s*α", r"Eα"], src=[(F["ALGA_R"], 6, "Matrizes elementares"), (F["ALGA_S2"], 5, "")],
  diff=(4, "Abstração que liga operações elementares, inversas e determinantes."), aliases=["E_alpha"])
C("det_def", "Função determinante", "alga", "alga_det",
  "Função det: Mₙ,ₙ(R) → R com det I = 1, alternada e multilinear nas linhas; existe e é única.",
  kw=[r"fun[çc][ãa]o\s+determinante", r"multilinear", r"alternada", r"\bdeterminantes?\b"], src=[(F["ALGA_R"], 7, "§6 Definição"), (F["ALGA_S3"], 1, "3.1 Definição formal")],
  diff=(4, "Definição axiomática (abstrata)."), aliases=["determinante", "det"])
C("det_prop", "Propriedades dos determinantes", "alga", "alga_det",
  "Troca de linhas muda o sinal; aLᵢ multiplica por a; Lᵢ + aLⱼ não altera; triangular = produto da diagonal. det(AB) = detA·detB, det Aᵗ = det A, det(aA) = aⁿ det A, det A⁻¹ = 1/det A.",
  type="formula", formula="det(AB) = det A · det B",
  kw=[r"det\s*\(AB\)", r"det\s*A\s*t", r"produto\s+da\s+diagonal", r"troca\s+de\s+sinal"], src=[(F["ALGA_R"], 7, "Tabela de efeitos"), (F["ALGA_S3"], 2, "Propriedades das funções determinante")],
  diff=(3, "Várias regras a memorizar; 'Atenção: det(A+B) ≠ detA + detB'."), aliases=["det(AB)"])
C("det_invertivel", "A invertível ⇔ det A ≠ 0", "alga", "alga_det",
  "Critério de invertibilidade via determinante.", type="formula", formula="A invertível ⇔ det A ≠ 0",
  kw=[r"invert[ií]vel\s+se\s+e\s+s[óo]\s+se\s+det", r"invert[ií]vel\s*⇐⇒\s*det", r"det\s*A\s*[̸≠]=?\s*0"], src=[(F["ALGA_R"], 7, "Resultado"), (F["ALGA_S3"], 2, "")],
  diff=(2, "Enunciado curto, muito usado."))
C("laplace", "Expansão de Laplace", "alga", "alga_det",
  "det A = Σⱼ (−1)^{i+j} aᵢⱼ det Aᵢⱼ, com Aᵢⱼ a matriz menor; sinais em xadrez.",
  type="algoritmo", formula="det A = Σⱼ (−1)^{i+j} aᵢⱼ det Aᵢⱼ",
  kw=[r"Laplace", r"menor"], src=[(F["ALGA_R"], 8, "§7"), (F["ALGA_S3"], 3, "3.2 Expansão de Laplace")],
  diff=(3, "Recursiva; estratégia 'linha com mais zeros'."), aliases=["cofatores", "menor"])
C("sarrus", "Regra de Sarrus", "alga", "alga_det",
  "Fórmula para determinantes 3×3.", type="formula",
  kw=[r"Sarrus"], src=[(F["ALGA_R"], 8, ""), (F["ALGA_S3"], 4, "Determinantes 3×3")],
  diff=(1, "Fórmula mecânica."))
C("det_estrategias", "Estratégias de cálculo de determinantes", "alga", "alga_det",
  "Laplace na linha/coluna com mais zeros; Gauss até forma triangular; misto (criar zeros e aplicar Laplace). Pode usar operações sobre colunas, mas nunca em sistemas.",
  type="algoritmo",
  kw=[r"Estrat[ée]gias", r"opera[çc][õo]es\s+elementares\s+sobre\s+colunas", r"colunas"], src=[(F["ALGA_R"], 8, "Estratégias"), (F["ALGA_S3"], 2, "Operações sobre colunas"), (F["ALGA_S3"], 5, "")],
  diff=(3, "Escolher a estratégia certa reduz muito as contas."))
C("areas_volumes", "Áreas, volumes e colinearidade", "alga", "alga_apl",
  "Área de paralelogramo/triângulo e volume de paralelepípedo/tetraedro por determinantes; pontos colineares/coplanares ⇔ determinante nulo; reta/plano por pontos.",
  kw=[r"[áa]rea", r"volume", r"colineares", r"coplanares"], src=[(F["ALGA_R"], 9, "§8"), (F["ALGA_S3"], 6, "3.3 Aplicações")],
  diff=(2, "Aplicações diretas de fórmulas."), aliases=["área", "volume", "coplanares"])
C("cramer", "Regra de Cramer", "alga", "alga_apl",
  "Se det A ≠ 0, a solução única de AX = B é xᵢ = det(Aᵢ)/det A, com Aᵢ = A com a coluna i substituída por B.",
  type="formula", formula="xᵢ = det(A com coluna i ← B) / det A",
  kw=[r"Cramer"], src=[(F["ALGA_R"], 9, "Regra de Cramer"), (F["ALGA_S3"], 6, "")],
  diff=(2, "Fórmula direta, só para sistemas quadrados com det ≠ 0."))
C("produto_vetorial", "Produto vetorial", "alga", "alga_apl",
  "u × v (determinante simbólico com i, j, k): ortogonal a u e v, ‖u×v‖ = área do paralelogramo; dá a direção de uma reta definida por dois planos e a normal a um plano.",
  type="formula", formula="u × v = det[i j k; x₁ y₁ z₁; x₂ y₂ z₂]",
  kw=[r"produto\s+vetorial", r"u\s*×\s*v", r"cross"], src=[(F["ALGA_R"], 9, "Produto vetorial em R³"), (F["ALGA_S3"], 7, ""), (F["ALGA_R"], 10, "Métodos-tipo: plano perpendicular a dois planos")],
  diff=(3, "Combina determinantes com geometria; vários métodos-tipo dependem dele."), aliases=["produto externo", "cross product"])
C("produto_misto", "Produto misto", "alga", "alga_apl",
  "u·(v × w) = det[u; v; w]; |det| = volume do paralelepípedo.", type="formula", formula="u·(v×w) = det[u; v; w]",
  kw=[r"produto\s+misto"], src=[(F["ALGA_R"], 9, "")],
  diff=(2, "Junta produto interno e vetorial."))

# =============================================================================
# CÁLCULO I
# =============================================================================
C("sucessao", "Sucessão", "cal", "cal_suc",
  "Sequência (aₘ)ₘ∈N de números reais; objeto base de limites, séries e do método de Newton.",
  kw=[r"sucess[ãa]o", r"sucess[õo]es"], src=[(F["CAL_R"], 2, "§1"), (cad("cal", 2), 2, "")],
  diff=(1, "Noção intuitiva."), aliases=["sequência", "sucessões"])
C("limite_eps_n", "Definição de limite (ε–N)", "cal", "cal_suc",
  "aₘ → L ⇔ ∀ε>0 ∃N(ε): m > N ⇒ |aₘ − L| < ε. Para provar: partir de |aₘ − L| < ε e resolver em ordem a m.",
  type="formula", formula="∀ε>0 ∃N(ε)>0: m>N ⇒ |aₘ − L| < ε",
  kw=[r"ε\s*[–-]\s*N", r"∀ε\s*>\s*0", r"\|am\s*−\s*L\|", r"converge\s+para"], src=[(F["CAL_R"], 2, "Definição + 'Como provar um limite pela definição'"), (cad("cal", 2), 2, "Definição e exemplos"), (cad("cal", 2), 3, "Exemplo (3m−7,1)/(4m−10,3)")],
  diff=(4, "Primeira definição com quantificadores encadeados; exemplos com cálculo de N(ε) no caderno CAL 2."), aliases=["épsilon", "definição de limite", "convergência"])
C("prop_limites", "Propriedades dos limites", "cal", "cal_suc",
  "Limite da soma, produto e quociente — todas provadas pela definição ε–N.",
  kw=[r"Propriedades\s+dos\s+Limites", r"lim\s*\(xm\s*\+\s*ym\)", r"\bSoma\.", r"Produto\.", r"Quociente\."], src=[(F["CAL_R"], 2, "§2 'Todas se provam pela definição ε–N'"), (F["CAL_R"], 3, "Quociente"), (cad("cal", 3), 2, "Prova da soma"), (cad("cal", 5), 2, "Prova do produto"), (cad("cal", 5), 3, "Prova do quociente")],
  diff=(4, "As provas exigem escolher εx, εy e majorar — feitas em detalhe nos cadernos CAL 3 e CAL 5."), aliases=["álgebra de limites"])
C("desig_triangular", "Desigualdade triangular", "cal", "cal_suc",
  "|a + b| ≤ |a| + |b| — ferramenta central nas provas de limites.", type="formula", formula="|a + b| ≤ |a| + |b|",
  kw=[r"desigualdade\s+triangular", r"\|a\s*\+\s*b\|"], src=[(F["CAL_R"], 2, "Ideia da prova (soma)"), (cad("cal", 3), 2, "")],
  diff=(2, "Enunciado simples; difícil é saber quando usar."))
C("convergente_limitada", "Toda a sucessão convergente é limitada", "cal", "cal_suc",
  "Lema: existe M₀ com |xₘ| ≤ M₀; se L ≠ 0 há ainda um minorante m₀ = |L| − ε a partir de certa ordem.",
  kw=[r"convergente\s+[ée]\s+limitada", r"Lema\."], src=[(F["CAL_R"], 2, "Lema"), (cad("cal", 5), 2, "Lema")],
  diff=(3, "Lema técnico usado na prova do produto e do quociente."))
C("enquadramento", "Teorema do enquadramento", "cal", "cal_suc",
  "Se xₘ ≤ yₘ ≤ zₘ e xₘ, zₘ → L, então yₘ → L.",
  kw=[r"[Ee]nquadramento"], src=[(F["CAL_R"], 3, ""), (cad("cal", 5), 3, "")],
  diff=(2, "Enunciado intuitivo."), aliases=["teorema das sucessões enquadradas", "sandwich"])
C("subsucessoes", "Subsucessões", "cal", "cal_suc",
  "aₘₖ com mₖ estritamente crescente. Se aₘ → L todas as subsucessões → L; duas subsucessões com limites diferentes provam divergência.",
  kw=[r"subsucess"], src=[(F["CAL_R"], 3, "§4"), (cad("cal", 1), 2, "Definição, teorema e exemplo (−1)ᵐ")],
  diff=(3, "Técnica de prova de divergência, reutilizada nas séries."))
C("monotonas", "Sucessões monótonas e limitadas", "cal", "cal_suc",
  "Monótona (crescente, decrescente, constante) e limitada ⇒ convergente. Se aₘ → 0 e bₘ limitada, aₘbₘ → 0.",
  kw=[r"mon[óo]tona", r"limitada"], src=[(F["CAL_R"], 4, "§5"), (cad("cal", 1), 4, "")],
  diff=(2, "Teoremas de aplicação direta."), aliases=["monotonia de sucessões", "sucessão limitada"])
C("lhopital", "Regra de L'Hôpital", "cal", "cal_suc",
  "Levanta indeterminações 0/0 e ∞/∞; com o teorema f(m) = aₘ ⇒ lim aₘ = lim f(x) aplica-se a sucessões.",
  type="ferramenta",
  kw=[r"L.?H[ôo]pital", r"l.Hospital"], src=[(F["CAL_R"], 3, "§3 Ferramentas"), (cad("cal", 1), 3, "Ferramentas")],
  diff=(2, "Ferramenta de cálculo (requer derivadas)."), aliases=["L'Hospital"])
C("lim_continua", "Limite e funções contínuas", "cal", "cal_suc",
  "Se aₘ → L e f é contínua em L, então f(aₘ) → f(L). Também: |aₘ| → 0 ⇔ aₘ → 0.",
  kw=[r"cont[ií]nua\s+em\s+L", r"lim\s*\|am\|"], src=[(F["CAL_R"], 3, ""), (cad("cal", 1), 3, "")],
  diff=(2, "Resultados de aplicação direta."))
C("serie", "Série e somas parciais", "cal", "cal_ser",
  "Σaₘ converge para s se a sucessão das somas parciais Sₘ = a₁+…+aₘ converge para s.",
  kw=[r"\bs[ée]ries?\b", r"soma\s+parcial", r"somas\s+parciais"], src=[(F["CAL_R"], 4, "§6"), (cad("cal", 1), 5, "Séries")],
  diff=(3, "Definição de série via limite de outra sucessão."), aliases=["séries", "somas parciais", "série numérica"])
C("serie_geometrica", "Série geométrica", "cal", "cal_ser",
  "Σ a·x^{m−1} converge para a/(1−x) se |x| < 1 e diverge se |x| ≥ 1 (a ≠ 0). Fórmula via Sₘ = a(1−xᵐ)/(1−x).",
  type="formula", formula="Σ a·xᵐ⁻¹ = a / (1 − x),  |x| < 1",
  kw=[r"geom[ée]trica"], src=[(F["CAL_R"], 4, "§7"), (cad("cal", 1), 6, ""), (cad("cal", 4), 2, "Exercícios 26, 38, 59, 62")],
  diff=(2, "Fórmula fechada; exercícios incluem intervalos de convergência (59)."))
C("serie_telescopica", "Série telescópica", "cal", "cal_ser",
  "Σ(aₘ − aₘ₊₁): Sₘ = a₁ − aₘ₊₁; converge sse lim aₘ existe (finito).",
  kw=[r"telesc[óo]pic"], src=[(F["CAL_R"], 5, "§8"), (cad("cal", 4), 3, "Exercícios 44, 46")],
  diff=(2, "Fácil de estudar uma vez reconhecida."))
C("termo_geral", "Teste do termo geral", "cal", "cal_ser",
  "Se Σaₘ converge então aₘ → 0; logo, se lim aₘ ≠ 0 a série diverge. O recíproco é falso (série harmónica).",
  kw=[r"termo\s+geral", r"lim\s+am\s*=\s*0"], src=[(F["CAL_R"], 5, "Teste do termo geral"), (cad("cal", 4), 3, "Teorema"), (cad("cal", 4), 4, "")],
  diff=(2, "Primeiro teste a aplicar."), aliases=["condição necessária de convergência"])
C("harmonica", "Série harmónica", "cal", "cal_ser",
  "Σ 1/m diverge apesar de 1/m → 0 — contra-exemplo do recíproco do teste do termo geral.",
  kw=[r"harm[óo]nica"], src=[(F["CAL_R"], 5, "OBS"), (cad("cal", 4), 4, "")],
  diff=(2, "Exemplo de referência usado em comparações."))
C("prop_series", "Propriedades das séries", "cal", "cal_ser",
  "Σcaₘ = cA e Σ(aₘ+bₘ) = A+B; retirar/acrescentar um número finito de termos não altera a natureza.",
  kw=[r"Propriedades\s+das\s+S[ée]ries"], src=[(F["CAL_R"], 5, "§9"), (cad("cal", 4), 4, "")],
  diff=(1, "Linearidade."))
C("p_series", "p-séries", "cal", "cal_ser",
  "Σ 1/mᵖ converge se p > 1 e diverge se p ≤ 1 (Stewart 11.3).",
  type="formula", formula="Σ 1/mᵖ converge ⇔ p > 1",
  kw=[r"p-s[ée]rie", r"\bp\s*>\s*1"], src=[(F["CAL_R"], 5, "§10 (Secção 11.3)"), (cad("cal", 4), 4, "Secção 11.3")],
  diff=(1, "Resultado a memorizar; série de referência para comparações."))
C("criterio_comparacao", "Critério da comparação", "cal", "cal_ser",
  "Séries de termos não negativos: se aₘ ≤ bₘ e Σbₘ converge, Σaₘ converge; se aₘ ≥ bₘ e Σbₘ diverge, Σaₘ diverge (Stewart 11.4).",
  kw=[r"Crit[ée]rio\s+da\s+Compara[çc][ãa]o", r"\bCC\b"], src=[(F["CAL_R"], 6, "Secção 11.4"), (cad("cal", 4), 5, "Exercícios 1a, 3, 4, 9")],
  diff=(3, "Exige escolher bem a série de comparação."), aliases=["CC", "comparação"])
C("comparacao_limite", "Critério da comparação no limite", "cal", "cal_ser",
  "Se lim aₘ/bₘ = c > 0 (finito), ambas convergem ou ambas divergem. Dica: ficar com as potências dominantes.",
  kw=[r"Compara[çc][ãa]o\s+no\s+Limite", r"CCNL"], src=[(F["CAL_R"], 6, ""), (cad("cal", 4), 6, "Exercícios 25, 10")],
  diff=(3, "Escolha de bₘ e cálculo do limite."), aliases=["CCNL"])
C("series_alternadas", "Séries alternadas (critério de Leibniz)", "cal", "cal_ser",
  "Σ(−1)^{m−1}bₘ com bₘ ≥ 0: se (bₘ) é decrescente e bₘ → 0, a série converge (CSA).",
  kw=[r"altern"], src=[(cad("cal", 8), 2, "Séries alternadas + exercícios 11.5 (5, 7, 17)"), (cad("cal", 8), 3, "Ex. 35")],
  diff=(3, "Duas condições a verificar (monotonia + limite)."), aliases=["CSA", "Leibniz"])
C("conv_absoluta", "Convergência absoluta e condicional", "cal", "cal_ser",
  "Σaₘ é absolutamente convergente se Σ|aₘ| converge (e então converge); condicionalmente convergente se converge mas não absolutamente. Só séries abs. convergentes podem ser reordenadas.",
  kw=[r"absolutamente", r"condicionalmente"], src=[(cad("cal", 8), 3, "Definições e teorema"), (cad("cal", 8), 4, "Exemplo sen(m)cos(m)/3ᵐ"), (cad("cal", 8), 5, "Reordenação")],
  diff=(3, "Distinção subtil, com o exemplo Σ(−1)ᵐ/m."), aliases=["absolutamente convergente", "condicionalmente convergente"])
C("criterio_razao", "Critério da razão (d'Alembert)", "cal", "cal_ser",
  "lim |aₘ₊₁/aₘ| = L: L < 1 ⇒ abs. convergente; L > 1 ⇒ diverge; L = 1 inconclusivo (Stewart 11.6).",
  kw=[r"raz[ãa]o"], src=[(cad("cal", 8), 4, "Critério da razão + ex. 11.6 (7, 10)")],
  diff=(3, "Bom para fatoriais e exponenciais."), aliases=["d'Alembert", "ratio test"])
C("criterio_raiz", "Critério da raiz (Cauchy)", "cal", "cal_ser",
  "lim ᵐ√|aₘ| = L: L < 1 ⇒ abs. convergente; L > 1 ⇒ diverge; L = 1 inconclusivo.",
  kw=[r"crit[ée]rio\s+da\s+raiz"], src=[(cad("cal", 8), 5, "Critério da raiz + ex. 11.6 (25, 27)")],
  diff=(3, "Bom para potências m-ésimas."), aliases=["Cauchy", "root test"])
C("funcao", "Funções e domínios", "cal", "cal_fun",
  "Domínio de funções racionais, raízes, exp e ln (inversas uma da outra); funções trigonométricas e respetivas inversas (arccos, arcsen, arctg).",
  kw=[r"dom[ií]nio", r"\bD\s*f\b", r"arcos", r"arcsen", r"arctg"], src=[(cad("cal", 8), 6, "Funções")],
  diff=(2, "Revisão, com inversas trigonométricas como novidade."), aliases=["domínio", "trigonométricas inversas", "arctg"])
C("limite_funcao", "Limite de uma função (ε–δ)", "cal", "cal_fun",
  "lim_{x→x₀} f(x) = L ⇔ ∀ε>0 ∃δ>0: 0<|x−x₀|<δ ⇒ |f(x) − L| < ε.",
  type="formula", formula="∀ε>0 ∃δ>0: 0<|x−x₀|<δ ⇒ |f(x)−L| < ε",
  kw=[r"Limite\s+de\s+uma\s+fun[çc][ãa]o", r"δ\s*\(ε\)", r"∃δ"], src=[(F["CAL_R"], 6, "§11"), (cad("cal", 5), 3, "Funções: definição"), (cad("cal", 6), 3, "")],
  diff=(4, "Versão contínua da definição ε–N, com dois quantificadores."), aliases=["épsilon-delta", "limite de função"])
C("continuidade", "Continuidade", "cal", "cal_fun",
  "f contínua em x₀ se lim_{x→x₀} f(x) = f(x₀) (definição ε–δ).",
  kw=[r"cont[ií]nu"], src=[(F["CAL_R"], 6, "Continuidade"), (cad("cal", 6), 3, "Continuidade")],
  diff=(2, "Definida a partir do limite."), aliases=["função contínua"])
C("derivada", "Derivada", "cal", "cal_der",
  "f'(x₀) = lim (f(x) − f(x₀))/(x − x₀) = lim_{h→0} (f(a+h) − f(a))/h — limite da taxa de variação; declive da reta tangente.",
  type="formula", formula="f'(a) = lim_{h→0} (f(a+h) − f(a)) / h",
  kw=[r"[Dd]erivad", r"taxa\s+de\s+varia"], src=[(F["CAL_R"], 7, "§12"), (cad("cal", 6), 3, "Δy/Δx"), (cad("cal", 11), 2, "Definição e exemplo x² − 8x + 9")],
  diff=(3, "Combina limite e geometria; casos de não-derivabilidade (|x| em 0)."), aliases=["derivadas", "f'(x)", "diferenciável"])
C("reta_tangente", "Reta tangente", "cal", "cal_der",
  "Reta que passa em P(a, f(a)) com declive f'(a): y = f(a) + f'(a)(x − a).",
  kw=[r"reta\s+tangente", r"tangente"], src=[(cad("cal", 11), 2, "Definição"), (cad("cal", 11), 4, "Exemplo")],
  diff=(2, "Aplicação direta da derivada."), aliases=["tangente"])
C("regras_derivacao", "Regras de derivação", "cal", "cal_der",
  "(f+g)' = f'+g', (fg)' = f'g + fg', (1/f)' = −f'/f², (f/g)' = (f'g − fg')/g².",
  type="formula", formula="(fg)' = f'g + fg'",
  kw=[r"Regras\s+de\s+deriva", r"\(f\s*g\)", r"f\s*′\s*g"], src=[(F["CAL_R"], 7, "Regras de derivação + ideia da prova (produto)"), (cad("cal", 6), 3, "Soma"), (cad("cal", 11), 3, "Ferramentas")],
  diff=(2, "Regras mecânicas com provas a partir da definição."), aliases=["derivada do produto", "derivada do quociente"])
C("derivadas_elementares", "Derivadas elementares", "cal", "cal_der",
  "Polinómios, sen, cos, tan (= 1 + tan²), eˣ, ln x (= 1/x), bˣ = bˣ ln b; sec, cosec, cotan.",
  kw=[r"Derivadas\s+a\s+saber", r"sec\s*x", r"cos\s*x"], src=[(F["CAL_R"], 7, "Derivadas a saber"), (cad("cal", 6), 2, "Exemplos"), (cad("cal", 11), 4, "Ferramentas")],
  diff=(1, "Tabela a memorizar."), aliases=["tabela de derivadas"])
C("dif_continua", "Diferenciável ⇒ contínua", "cal", "cal_der",
  "Se f é diferenciável em a então é contínua em a; o recíproco é falso (|x| em 0).",
  kw=[r"Diferenciabilidade", r"diferenci[áa]vel"], src=[(cad("cal", 11), 3, "Teorema + nota")],
  diff=(2, "Teorema com contra-exemplo clássico."))
C("regra_cadeia", "Regra da cadeia", "cal", "cal_der",
  "(f∘g)'(x) = f'(g(x))·g'(x) (Stewart 3.4); estende-se a composições de 3 funções.",
  type="formula", formula="(f∘g)'(x) = f'(g(x)) · g'(x)",
  kw=[r"cadeia", r"fun[çc][ãa]o\s+composta"], src=[(cad("cal", 9), 3, "Regra + prova"), (cad("cal", 10), 2, "Derivada da função composta"), (cad("cal", 11), 4, "Secção 3.4 + exercícios")],
  diff=(3, "Composições encaixadas (exercícios 3.4: 30, 35, 61)."), aliases=["derivada da função composta", "chain rule"])
C("derivada_inversa", "Derivada da função inversa", "cal", "cal_der",
  "(g⁻¹)'(y) = 1 / g'(g⁻¹(y)), obtida derivando g⁻¹∘g = id com a regra da cadeia.",
  type="formula", formula="(g⁻¹)'(y) = 1 / g'(g⁻¹(y))",
  kw=[r"inversa"], src=[(cad("cal", 9), 3, "Função inversa de g(x)"), (cad("cal", 9), 4, "'MILAGRE'"), (cad("cal", 10), 2, "")],
  diff=(4, "Derivação via regra da cadeia; notação confusa (g⁻¹ ≠ 1/g)."))
C("ordem_superior", "Derivadas de ordem superior", "cal", "cal_der",
  "f'', f''' , f⁽ⁿ⁾ — notação.", kw=[r"f\s*\(n\)", r"segunda\s+derivada"], src=[(cad("cal", 11), 3, "Notação")],
  diff=(1, "Notação."), aliases=["segunda derivada"])
C("monotonia_derivada", "Monotonia e sinal da derivada", "cal", "cal_apl",
  "f' > 0 ⇒ f crescente numa vizinhança; f' < 0 ⇒ decrescente; f' ≥ 0 em [a,b] ⇒ crescente em [a,b].",
  kw=[r"crescente", r"decrescente"], src=[(cad("cal", 7), 2, ""), (cad("cal", 11), 6, "Teorema")],
  diff=(2, "Aplicação direta."))
C("extremos", "Extremos locais e absolutos", "cal", "cal_apl",
  "Máx/mín local e absoluto; Fermat: extremo local com f' definida ⇒ f'(c) = 0 (recíproco falso, x³); Weierstrass: contínua em [a,b] atinge máx e mín absolutos; candidatos: zeros de f', pontos sem f', extremos do intervalo; teste da 2.ª derivada.",
  kw=[r"m[áa]ximo", r"m[ií]nimo", r"Fermat", r"Weierstrass", r"extremo"], src=[(cad("cal", 7), 2, "x₀ máx/mín ⇒ f'(x₀) = 0"), (cad("cal", 11), 5, "Capítulo 4: definições, Weierstrass"), (cad("cal", 11), 6, "Fermat; onde procurar; 2.ª derivada")],
  diff=(3, "Vários teoremas e casos a verificar."), aliases=["máximos e mínimos", "Fermat", "Weierstrass"])
C("taylor1", "Aproximação linear (Taylor de 1.ª ordem)", "cal", "cal_apl",
  "f(x) ≈ y(x) = f(x₀) + f'(x₀)(x − x₀); |f(x) − y(x)| < ε|x − x₀| perto de x₀ ('dentro do cone').",
  type="formula", formula="f(x) ≈ f(x₀) + f'(x₀)(x − x₀)",
  kw=[r"Taylor", r"aproxima[çc][ãa]o\s+linear"], src=[(cad("cal", 7), 3, "Conclusão: Taylor 1.ª ordem"), (cad("cal", 9), 2, "Teorema + prova")],
  diff=(3, "A prova usa a definição ε–δ da derivada."), aliases=["polinómio de Taylor", "linearização", "Taylor"])
C("newton", "Método de Newton", "cal", "cal_apl",
  "xₘ₊₁ = xₘ − f(xₘ)/f'(xₘ): aproxima zeros de f usando a reta tangente; gera uma sucessão; falha se f'(xₘ) = 0 ou pode divergir (∛x). Stewart 4.8.",
  type="algoritmo", formula="xₘ₊₁ = xₘ − f(xₘ) / f'(xₘ)",
  kw=[r"Newton"], src=[(cad("cal", 9), 2, "Derivação a partir de Taylor"), (cad("cal", 9), 3, "'→ Sucessão'"), (cad("cal", 10), 2, "Gráficos: quando funciona/não funciona"), (cad("cal", 11), 6, "Passos do método"), (cad("cal", 12), 2, "Secção 4.8: ex. 3, 4, 6, 7, 8"), (cad("cal", 12), 3, "Ex. 11, 15, 33")],
  diff=(3, "Algoritmo iterativo; exige análise de convergência (ex. 4.8.33)."), aliases=["Newton-Raphson"])
C("bolzano", "Teorema de Bolzano-Cauchy", "cal", "cal_apl",
  "Usado para garantir a existência de uma raiz num intervalo antes de aplicar Newton (ex. 4.8.15).",
  kw=[r"Bolzano"], src=[(cad("cal", 12), 3, "Ex. 15: 'Pelo corolário do Teorema de Bolzano-Cauchy'")],
  diff=(2, "Aparece apenas como ferramenta num exercício."), aliases=["valor intermédio"])
C("primitiva", "Primitiva", "cal", "cal_prim",
  "F é primitiva de f se F' = f; P(c·xⁿ) = c·xⁿ⁺¹/(n+1); primitiva de polinómios termo a termo (+C).",
  kw=[r"[Pp]rimitiva"], src=[(cad("cal", 10), 2, "Definição"), (cad("cal", 10), 3, "Polinómios")],
  diff=(2, "Inverso da derivação."), aliases=["antiderivada", "primitivas"])

# =============================================================================
# ESTRUTURAS DISCRETAS
# =============================================================================
C("proposicao", "Proposições e cálculo proposicional", "ed", "ed_lp",
  "Variáveis proposicionais p, q, r tomam v/f (1/0, ⊤/⊥); o CP dá significado às conectivas booleanas.",
  kw=[r"C[áa]lculo\s+Proposicional", r"vari[áa]veis\s+proposicionais", r"proposi[çc]"], src=[(F["ED_R"], 3, "§2"), (F["ED_L"], 8, "Cálculo Proposicional (CP)")],
  diff=(1, "Introdução."), aliases=["cálculo proposicional", "variável proposicional"])
C("conectivas", "Conectivas lógicas", "ed", "ed_lp",
  "¬, ∧, ∨, ⊕, →, ↔ e respetivas tabelas de verdade.",
  kw=[r"[Cc]onectivas?", r"[Cc]onjun[çc][ãa]o", r"[Dd]isjun[çc][ãa]o", r"[Nn]ega[çc][ãa]o"], src=[(F["ED_R"], 3, "Definição"), (F["ED_L"], 9, "Conectivas lógicas"), (F["ED_L"], 10, "")],
  diff=(1, "Tabelas a memorizar."), aliases=["e", "ou", "não", "ou exclusivo", "xor"])
C("implicacao", "Implicação e contrapositiva", "ed", "ed_lp",
  "P → Q só é falsa com P=v, Q=f; P → Q ⇔ ¬P ∨ Q ⇔ ¬Q → ¬P. Recíproca e inversa não são equivalentes. Condição suficiente/necessária.",
  type="formula", formula="P → Q ⇔ ¬P ∨ Q ⇔ ¬Q → ¬P",
  kw=[r"[Ii]mplica[çc][ãa]o", r"contrapositiva", r"P\s*→\s*Q"], src=[(F["ED_R"], 3, "A implicação P → Q"), (F["ED_L"], 14, ""), (F["ED_L"], 15, "Formas de ler P → Q")],
  diff=(3, "Fonte clássica de erros (recíproca vs contrapositiva)."), aliases=["contrapositiva", "condicional", "se então"])
C("tabela_verdade", "Tabelas de verdade", "ed", "ed_lp",
  "Avaliar uma fórmula para todas as atribuições de valores lógicos.",
  type="algoritmo", kw=[r"tabelas?\s+de\s+verdade"], src=[(F["ED_R"], 4, ""), (F["ED_R"], 12, "Exercícios resolvidos 2, 13"), (cad("ed", 1), 2, "Ex. 2d"), (cad("ed", 1), 5, "Ex. 13")],
  diff=(1, "Mecânico."), aliases=["tabela de verdade"])
C("tautologia", "Tautologia, contradição e satisfazibilidade", "ed", "ed_lp",
  "Tautologia: verdadeira para todas as atribuições; contradição: falsa para todas; satisfazível: verdadeira para pelo menos uma.",
  kw=[r"[Tt]autologia", r"[Cc]ontradi[çc][ãa]o", r"satisfaz[ií]ve"], src=[(F["ED_R"], 3, "Definição"), (F["ED_L"], 18, "Tautologias e Contradições"), (cad("ed", 1), 5, "Ex. 13")],
  diff=(2, "Conceitos centrais para formas normais e inferência."), aliases=["satisfazível", "contradição", "válida"])
C("equivalencia_logica", "Equivalência lógica", "ed", "ed_lp",
  "P₁ ⇔ P₂ se têm sempre o mesmo valor, i.e. P₁ ↔ P₂ é tautologia. Prova por tabela ou álgebra; refutação por uma atribuição.",
  kw=[r"[Ee]quival[êe]ncia\s+l[óo]gica", r"logicamente\s+equivalentes", r"semanticamente\s+equivalentes"], src=[(F["ED_R"], 4, "Definição"), (F["ED_L"], 20, ""), (cad("ed", 1), 3, "Ex. 6"), (cad("ed", 1), 4, "Ex. 7, 9, 14")],
  diff=(2, "Exige escolher entre tabela e álgebra booleana."), aliases=["logicamente equivalentes"])
C("leis_equivalencia", "Leis de equivalência (álgebra booleana)", "ed", "ed_lp",
  "Identidade, absorvente, idempotência, dupla negação, comutatividade, associatividade, distributividade, complementar, absorção, implicação, dupla implicação, ou exclusivo.",
  kw=[r"Leis\s+de\s+equival", r"[Dd]istributividade", r"[Aa]bsor[çc][ãa]o", r"[Ii]dempot"], src=[(F["ED_R"], 4, "Leis de equivalência"), (F["ED_L"], 21, ""), (F["ED_E"], 9, "Leis da álgebra booleana")],
  diff=(2, "Tabela extensa a dominar."), aliases=["álgebra booleana", "distributividade", "absorção"])
C("de_morgan", "Leis de De Morgan", "ed", "ed_lp",
  "¬(P ∧ Q) ⇔ ¬P ∨ ¬Q e ¬(P ∨ Q) ⇔ ¬P ∧ ¬Q — também para conjuntos (complemento da união/interseção).",
  type="formula", formula="¬(P ∧ Q) ⇔ ¬P ∨ ¬Q",
  kw=[r"De\s*Morgan", r"DeMorgan"], src=[(F["ED_R"], 4, ""), (F["ED_L"], 22, "Leis de DeMorgan"), (F["ED_C"], 18, "Conjuntos: Leis de De Morgan"), (cad("ed", 2), 4, "Ex. 16")],
  diff=(2, "Usadas em formas normais, inferência e conjuntos."), aliases=["De Morgan"])
C("literal", "Literal", "ed", "ed_fn",
  "Uma variável p ou a sua negação ¬p.", kw=[r"[Ll]iteral"], src=[(F["ED_R"], 5, ""), (F["ED_L"], 25, "")],
  diff=(1, "Definição."))
C("fnn", "Forma normal negativa (FNN)", "ed", "ed_fn",
  "¬ só ocorre em literais; obtém-se com De Morgan e dupla negação.",
  kw=[r"normal\s+negativa", r"\bFNN\b"], src=[(F["ED_R"], 5, ""), (F["ED_L"], 25, "Forma normal negativa")],
  diff=(2, "Passo intermédio para FND/FNC."))
C("fnd", "Forma normal disjuntiva (FND)", "ed", "ed_fn",
  "Disjunção de conjunções de literais; pela tabela: linhas com φ = v. Satisfazível sse alguma conjunção o é.",
  kw=[r"normal\s+disjuntiva", r"\bFND\b", r"\bDNF\b"], src=[(F["ED_R"], 5, ""), (F["ED_L"], 27, ""), (F["ED_L"], 30, ""), (cad("ed", 2), 2, "Ex. 11, 12")],
  diff=(3, "Conversão algébrica longa."), aliases=["DNF"])
C("fnc", "Forma normal conjuntiva (FNC)", "ed", "ed_fn",
  "Conjunção de disjunções de literais; pela tabela: linhas com φ = f, sinais trocados. Tautologia sse todas as disjunções o são.",
  kw=[r"normal\s+conjuntiva", r"\bFNC\b", r"\bCNF\b"], src=[(F["ED_R"], 5, ""), (F["ED_L"], 33, ""), (F["ED_L"], 35, "Exercícios"), (cad("ed", 2), 2, "Ex. 11, 12")],
  diff=(3, "Dual da FND; fácil trocar sinais."), aliases=["CNF"])
C("alg_fn", "Algoritmo de conversão para forma normal", "ed", "ed_fn",
  "1) eliminar → e ↔; 2) passar a FNN; 3) distribuir ∧ sobre ∨ (FND) ou ∨ sobre ∧ (FNC).",
  type="algoritmo",
  kw=[r"Prova\s+\(algoritmo\)", r"Eliminar\s+→", r"eliminar\s+as\s+conectivas"], src=[(F["ED_R"], 5, "Prova (algoritmo)"), (F["ED_L"], 28, "Método para encontrar uma fórmula equivalente em DNF")],
  diff=(3, "Vários passos encadeados."))
C("decisao_fn", "Decidir satisfazibilidade/validade com formas normais", "ed", "ed_fn",
  "Conjunção de literais satisfazível sse não contém l e ¬l; disjunção é tautologia sse contém l e ¬l.",
  kw=[r"Decidir\s+com\s+as\s+formas", r"[Ss]atisfazibilidade\s+de\s+f[óo]rmulas"], src=[(F["ED_R"], 5, "Decidir com as formas normais"), (F["ED_L"], 31, ""), (F["ED_L"], 34, "")],
  diff=(2, "Lemas simples depois de obter a forma normal."))
C("predicados", "Predicados e universo", "ed", "ed_lpo",
  "A LPO acrescenta variáveis num universo, funções e predicados; o valor depende do universo (∀x x ≥ 0 é v em N e f em Z).",
  kw=[r"[Pp]redicado", r"[Uu]niverso", r"Primeira\s+Ordem", r"\bLPO\b"], src=[(F["ED_R"], 6, "§4"), (F["ED_L"], 37, ""), (F["ED_L"], 38, "")],
  diff=(2, "Nova sintaxe."), aliases=["LPO", "lógica de primeira ordem", "universo de discurso"])
C("quantificadores", "Quantificadores ∀ e ∃", "ed", "ed_lpo",
  "∀x∈A P(x) é v sse P(x) é v para todo x; ∃x∈A P(x) é v sse é v para pelo menos um x.",
  kw=[r"[Qq]uantificador", r"∀", r"∃"], src=[(F["ED_R"], 6, ""), (F["ED_L"], 39, "Quantificadores"), (F["ED_L"], 40, "Exemplos")],
  diff=(2, "Leitura e avaliação em universos diferentes (ex. 23)."), aliases=["quantificador universal", "quantificador existencial", "para todo", "existe"])
C("negacao_quant", "Negação de quantificadores", "ed", "ed_lpo",
  "¬∀x P(x) ⇔ ∃x ¬P(x); ¬∃x P(x) ⇔ ∀x ¬P(x); com vários quantificadores troca-se cada um, da esquerda para a direita.",
  type="formula", formula="¬∀x P(x) ⇔ ∃x ¬P(x)",
  kw=[r"Nega[çc][ãa]o\s+de\s+(proposi[çc][õo]es\s+com\s+)?quantifica"], src=[(F["ED_R"], 6, ""), (F["ED_L"], 42, ""), (cad("ed", 2), 5, "Ex. 26")],
  diff=(3, "Erros frequentes com vários quantificadores."))
C("ordem_quant", "Ordem dos quantificadores", "ed", "ed_lpo",
  "∀x∀y ⇔ ∀y∀x, mas ∀x∃y P(x,y) não é equivalente a ∃y∀x P(x,y) (em Z, ∀n∃m m>n é v, ∃m∀n m>n é f).",
  kw=[r"A\s+ordem\s+importa", r"comutatividade"], src=[(F["ED_R"], 6, "OBS: A ordem importa!"), (F["ED_L"], 41, "Cuidado com a comutatividade")],
  diff=(3, "Subtil e crítico para definições como ε–N."))
C("formalizacao", "Formalização de frases", "ed", "ed_lpo",
  "'Todo o A é B': ∀x(A(x)→B(x)); 'Algum A é B': ∃x(A(x)∧B(x)); a | b ⇔ ∃k b = ka; Primo(p); Goldbach; infinidade de primos.",
  kw=[r"Formalizar", r"Formule", r"Goldbach", r"Primo\s*\("], src=[(F["ED_R"], 6, "Formalizar frases"), (F["ED_L"], 49, ""), (cad("ed", 2), 5, "Ex. 25, 27")],
  diff=(3, "Tradução linguagem natural → fórmula."), aliases=["formalizar"])
C("regra_inferencia", "Regras de inferência e argumentos válidos", "ed", "ed_inf",
  "Qualquer tautologia A → B dá uma regra A ⇒ B; hipóteses P₁∧…∧Pₙ ⇒ conclusão Q.",
  kw=[r"[Rr]egras?\s+de\s+infer", r"hip[óo]teses", r"premissas"], src=[(F["ED_R"], 7, "§5"), (F["ED_L"], 43, "")],
  diff=(2, "Ideia de argumento formal."), aliases=["inferência", "argumento válido"])
C("modus_ponens", "Modus Ponens", "ed", "ed_inf",
  "De P e P → Q conclui-se Q (tautologia P ∧ (P → Q) → Q).", type="formula", formula="P, P → Q ⊢ Q",
  kw=[r"[Mm]odus\s+[Pp]onens"], src=[(F["ED_R"], 7, ""), (F["ED_L"], 44, ""), (cad("ed", 2), 3, "Ex. 15")],
  diff=(1, "Regra básica."))
C("modus_tollens", "Modus Tollens", "ed", "ed_inf",
  "De P → Q e ¬Q conclui-se ¬P.", type="formula", formula="P → Q, ¬Q ⊢ ¬P",
  kw=[r"[Mm]odus\s+[Tt]ollens"], src=[(F["ED_R"], 7, ""), (F["ED_L"], 47, ""), (cad("ed", 2), 4, "Ex. 16")],
  diff=(2, "Usa a contrapositiva."))
C("outras_regras", "Adição, simplificação, transitividade, casos e dilema", "ed", "ed_inf",
  "Adição (P ⊢ P∨Q), simplificação (P∧Q ⊢ P), conjunção, transitividade, contradição, prova por casos, dilema construtivo.",
  kw=[r"[Aa]di[çc][ãa]o", r"[Ss]implifica[çc][ãa]o", r"[Tt]ransitividade", r"[Dd]ilema"], src=[(F["ED_R"], 7, "Regras"), (F["ED_L"], 45, ""), (F["ED_E"], 10, "Algumas regras de inferência")],
  diff=(2, "Catálogo de regras."), aliases=["transitividade", "prova por casos", "dilema construtivo"])
C("falacias", "Argumentos inválidos (falácias)", "ed", "ed_inf",
  "Afirmar o consequente (P→Q, Q ⊢ P) e negar o antecedente (P→Q, ¬P ⊢ ¬Q) não são válidos (ex. 17).",
  kw=[r"inv[áa]lidos", r"consequente", r"antecedente"], src=[(F["ED_R"], 7, "OBS: Argumentos inválidos")],
  diff=(2, "Reconhecer padrões inválidos."), aliases=["afirmar o consequente", "negar o antecedente"])
C("prova_formal", "Provas formais", "ed", "ed_inf",
  "Assumir hipóteses verdadeiras e aplicar regras e equivalências até à conclusão, indicando cada regra.",
  type="algoritmo", kw=[r"Provas\s+formais", r"indicando\s+em\s+cada\s+passo"], src=[(F["ED_L"], 46, ""), (F["ED_R"], 13, "Inferência 15, 16"), (cad("ed", 2), 3, "Ex. 15, 16")],
  diff=(3, "Encadear regras sem saltos."))
C("conjunto", "Conjuntos (extensão e compreensão)", "ed", "ed_conj",
  "Coleção de objetos distintos; ordem e repetições não importam; S = {x | P(x)}. N = {0,1,2,…}.",
  kw=[r"[Cc]onjuntos?", r"compreens[ãa]o", r"extens[ãa]o"], src=[(F["ED_R"], 8, "§6"), (F["ED_C"], 2, "Teoria de Conjuntos"), (F["ED_C"], 4, "Compreensão")],
  diff=(1, "Definições."), aliases=["conjunto", "compreensão", "extensão"])
C("subconjunto", "Pertença, subconjunto e igualdade", "ed", "ed_conj",
  "A ⊆ B ⇔ ∀x (x ∈ A → x ∈ B); A = B ⇔ A ⊆ B ∧ B ⊆ A; ∅ ⊆ A; ∈ não é o mesmo que ⊆.",
  type="formula", formula="A ⊆ B ⇔ ∀x (x ∈ A → x ∈ B)",
  kw=[r"[Ss]ubconjunto", r"⊆", r"pertence"], src=[(F["ED_R"], 8, "Subconjuntos e igualdade"), (F["ED_C"], 6, ""), (F["ED_C"], 8, "Conjuntos de conjuntos")],
  diff=(2, "Confusão ∈ vs ⊆ sublinhada nos slides."), aliases=["inclusão", "⊆", "conjunto vazio"])
C("partes", "Conjunto das partes", "ed", "ed_conj",
  "P(A) = 2ᴬ = {S | S ⊆ A}, |2ᴬ| = 2^|A|; P(A)∩P(B) = P(A∩B).",
  type="formula", formula="|P(A)| = 2^|A|",
  kw=[r"conjunto\s+das\s+partes", r"P\(A\)", r"2A"], src=[(F["ED_R"], 8, ""), (F["ED_C"], 9, ""), (cad("ed", 5), 2, "Ex. 33–35")],
  diff=(3, "Conjuntos de conjuntos."), aliases=["power set", "2^A"])
C("op_conjuntos", "Operações com conjuntos", "ed", "ed_conj",
  "A∩B, A∪B, A\\B, complementar Ā = U\\A.",
  kw=[r"[Ii]nterse[çc]", r"[Uu]ni[ãa]o", r"[Dd]iferen[çc]a", r"complementar"], src=[(F["ED_R"], 8, "Operações"), (F["ED_C"], 10, ""), (cad("ed", 5), 2, "Ex. 30")],
  diff=(1, "Operações básicas."), aliases=["interseção", "união", "diferença", "complementar"])
C("produto_cartesiano", "Produto cartesiano e n-tuplos", "ed", "ed_conj",
  "A × B = {(a,b) | a∈A, b∈B}; n-tuplo ordenado (a₁,…,aₙ); |A×B| = |A|·|B|.",
  kw=[r"[Pp]roduto\s+cartesiano", r"tuplo", r"par\s+ordenado"], src=[(F["ED_R"], 8, ""), (F["ED_C"], 16, "Produto cartesiano de conjuntos")],
  diff=(1, "Definição."), aliases=["n-tuplo", "par ordenado", "A×B"])
C("cardinalidade", "Cardinalidade", "ed", "ed_conj",
  "|A| = número de elementos distintos; finito/infinito; |A\\B| = |A| − |A∩B|.",
  kw=[r"[Cc]ardinalidade"], src=[(F["ED_R"], 9, ""), (F["ED_C"], 14, "")],
  diff=(1, "Definição."))
C("inclusao_exclusao", "Princípio de inclusão-exclusão", "ed", "ed_conj",
  "|A∪B| = |A| + |B| − |A∩B| (e versão para 3 conjuntos).",
  type="formula", formula="|A∪B| = |A| + |B| − |A∩B|",
  kw=[r"[Ii]nclus[ãa]o\s*[–-]?\s*exclus", r"\|A\s*∪\s*B\|"], src=[(F["ED_R"], 9, "Exemplo das línguas"), (F["ED_C"], 15, "Ex. 4 (100 estudantes)")],
  diff=(2, "Contagem com sobreposições."))
C("algebra_conjuntos", "Álgebra de conjuntos", "ed", "ed_conj",
  "Mesmas leis da lógica com ∩↔∧, ∪↔∨, complemento↔¬, U↔T, ∅↔F (instância de álgebra booleana).",
  kw=[r"[ÁA]lgebra\s+Boolean", r"Propriedades\s+alg[ée]bricas", r"propriedades"], src=[(F["ED_R"], 9, "Propriedades (álgebra booleana)"), (F["ED_C"], 17, ""), (F["ED_E"], 16, "")],
  diff=(2, "Transferência das leis lógicas."), aliases=["álgebra booleana de conjuntos"])
C("provas_conjuntos", "Provas com conjuntos", "ed", "ed_conj",
  "Igualdade: x arbitrário e x∈X ⇔ x∈Y traduzindo para lógica (∩→∧, ∪→∨, \\→∧¬); inclusão: 'seja x∈X…'; falsidade: contra-exemplo pequeno.",
  type="algoritmo", kw=[r"Como\s+fazer\s+provas", r"[Pp]rove", r"contra-exemplo"], src=[(F["ED_R"], 9, "Como fazer provas com conjuntos"), (F["ED_C"], 19, "Provas..."), (F["ED_C"], 22, ""), (cad("ed", 5), 3, "Ex. 36, 47, 53")],
  diff=(3, "Exige rigor na tradução para lógica."))
C("inducao", "Princípio de indução matemática", "ed", "ed_ind",
  "Caso base P(n₀) + passo de indução (assumir P(n), a HI, e provar P(n+1)) ⇒ ∀n ≥ n₀ P(n).",
  type="formula", formula="P(n₀) ∧ ∀n≥n₀ (P(n) → P(n+1)) → ∀n≥n₀ P(n)",
  kw=[r"[Ii]ndu[çc][ãa]o", r"[Cc]aso\s+base", r"hip[óo]tese\s+de\s+indu"], src=[(F["ED_R"], 11, "§7"), (F["ED_I"], 3, ""), (F["ED_I"], 5, "Passos"), (cad("ed", 3), 2, "Exemplos"), (cad("ed", 6), 2, "Ex. 61, 63"), (cad("ed", 6), 3, "Ex. 64, 65")],
  diff=(3, "Estrutura rígida; escrever n+1 em função de n."), aliases=["indução", "caso base", "passo de indução", "HI"])
C("inducao_forte", "Indução forte", "ed", "ed_ind",
  "Assume P(n₀),…,P(n) para provar P(n+1). Ex.: todo o inteiro > 1 é produto de primos; jogo das cartas; n = 3x + 7y para n ≥ 12.",
  kw=[r"[Ii]ndu[çc][ãa]o\s+(Matem[áa]tica\s+)?[Ff]orte"], src=[(F["ED_I"], 10, ""), (F["ED_I"], 11, "Produto de primos"), (F["ED_I"], 12, "Jogo das cartas")],
  diff=(4, "Generaliza a indução; escolher vários casos base."))
C("recorrencia", "Recorrências", "ed", "ed_ind",
  "Definições por recorrência (Torre de Hanói Tₙ, Fibonacci) e adivinhar/provar fórmulas fechadas por indução.",
  kw=[r"[Rr]ecorr[êe]ncia", r"Hanoi", r"Fibonacci"], src=[(F["ED_I"], 15, "Torre de Hanói"), (F["ED_I"], 16, "Fórmula de recorrência"), (F["ED_E"], 19, "Ex. 88")],
  diff=(3, "Ligar definição recursiva e prova por indução."), aliases=["Torre de Hanói", "Fibonacci", "recursivo"])
C("soma_geometrica", "Soma geométrica Σ rⁱ", "ed", "ed_ind",
  "Σᵢ₌₀ⁿ rⁱ = (rⁿ⁺¹ − 1)/(r − 1), r ≠ 1 — provada por indução.",
  type="formula", formula="Σᵢ₌₀ⁿ rⁱ = (rⁿ⁺¹ − 1) / (r − 1)",
  kw=[r"r\s*i\s*=", r"rn\+1\s*−\s*1", r"r\s*−\s*1"], src=[(F["ED_R"], 11, "Exemplo"), (F["ED_I"], 9, "Exercícios"), (cad("ed", 3), 2, "")],
  diff=(2, "Prova por indução curta."), aliases=["soma de progressão geométrica"])
C("prova_direta", "Demonstração direta", "ed", "ed_ind",
  "Cadeia de afirmações derivadas do conhecimento comum até à propriedade (ex.: n par ⇒ n² par).",
  kw=[r"[Dd]emonstra[çc][õo]es\s+directas?"], src=[(F["ED_I"], 19, ""), (F["ED_I"], 20, ""), (F["ED_I"], 21, "")],
  diff=(2, "Técnica base."))
C("prova_contradicao", "Demonstração por contradição", "ed", "ed_ind",
  "Assumir ¬A e derivar uma contradição (ex.: √2 irracional, log₂3 irracional).",
  kw=[r"por\s+contradi[çc][ãa]o", r"irracional"], src=[(F["ED_I"], 22, ""), (F["ED_I"], 23, "√2 irracional"), (F["ED_I"], 25, "log₂ 3")],
  diff=(3, "Requer formular bem a negação."), aliases=["redução ao absurdo", "absurdo"])
# --- ED: temas programados (exercícios existentes, matéria ainda não dada)
C("divisibilidade", "Divisibilidade", "ed", "ed_num",
  "a | b ⇔ ∃k b = ka; propriedades (a|b ∧ b|c ⇒ a|(b+c), …).",
  kw=[r"a\s*\|\s*b", r"divis[ií]ve"], src=[(F["ED_R"], 6, "Formalizar: a | b"), (F["ED_E"], 21, "Acerca de Números, ex. 98")],
  diff=(2, "Definição usada já na formalização (LPO)."), status="programado")
C("mdc_euclides", "mdc e algoritmo de Euclides", "ed", "ed_num",
  "Máximo divisor comum; primos relativos (mdc = 1); algoritmo de Euclides (ex. 107, 111).",
  type="algoritmo", kw=[r"mdc", r"Euclides", r"primos\s+relativos"], src=[(F["ED_E"], 22, "Ex. 107: algoritmo de Euclides"), (F["IC1"], 5, "Algoritmo de Euclides (IC)")],
  diff=(3, "Algoritmo recursivo + propriedades."), aliases=["algoritmo de Euclides", "máximo divisor comum"], status="programado")
C("primos", "Números primos e factorização", "ed", "ed_num",
  "Primo(p) ⇔ p > 1 ∧ ∀d (d|p → d=1 ∨ d=p); todo o inteiro > 1 é produto de primos (indução forte); factorização (ex. 121).",
  kw=[r"\bprimos?\b", r"factoriza", r"fatoriza"], src=[(F["ED_R"], 6, "Primo(p)"), (F["ED_I"], 11, "Produto de primos"), (F["ED_E"], 23, "Ex. 121")],
  diff=(2, "Definição já formalizada em LPO."), aliases=["primo", "factorização em primos"], status="programado")
C("relacoes", "Relações binárias e de equivalência", "ed", "ed_rel",
  "Relações em Z, partições e classes de equivalência (ex. 132–171).",
  kw=[r"rela[çc][ãa]o", r"parti[çc]", r"equival[êe]ncia"], src=[(F["ED_E"], 24, "Relações e funções"), (F["ED_E"], 27, "Partições")],
  diff=(3, "Ainda não lecionado — estimativa."), status="programado")
C("funcoes_discretas", "Funções injetivas e sobrejetivas", "ed", "ed_rel",
  "Exemplos de f: N → Z injetiva/sobrejetiva (ex. 172).",
  kw=[r"injectiva", r"sobrejectiva"], src=[(F["ED_E"], 29, "Ex. 172")],
  diff=(2, "Ainda não lecionado — estimativa."), aliases=["injetiva", "sobrejetiva", "bijetiva"], status="programado")
C("contagem", "Princípios de contagem", "ed", "ed_cont",
  "Contagem de inteiros, funções, respostas; princípio da gaveta (ex. 174–214).",
  kw=[r"Quantos?", r"De\s+quantas\s+maneiras"], src=[(F["ED_E"], 30, "Contagem"), (F["ED_E"], 33, "Ex. 206")],
  diff=(3, "Ainda não lecionado — estimativa."), aliases=["combinatória", "princípio da gaveta"], status="programado")
C("grafos", "Grafos", "ed", "ed_graf",
  "Grafos dirigidos e não dirigidos, graus, caminhos, conexidade e componentes conexas (ex. 215–240).",
  kw=[r"[Gg]rafo", r"v[ée]rtice", r"aresta"], src=[(F["ED_E"], 34, "Grafos"), (F["ED_E"], 36, "")],
  diff=(3, "Ainda não lecionado — estimativa."), aliases=["grafo", "vértices", "arestas"], status="programado")

# =============================================================================
# INTRODUÇÃO À PROGRAMAÇÃO (inferido do código — não há enunciados na pasta)
# =============================================================================
IPF = "Introdução à Programação/ex{}.py"
C("py_io", "Entrada e saída (input / print)", "ip", "ip_base",
  "Ler valores com input() e escrever com print().", type="ferramenta",
  kw=[], src=[(IPF.format(1), None, "print"), (IPF.format(2), None, "input")],
  diff=(1, "Primeiros exercícios (ex1, ex2)."), aliases=["input", "print"])
C("py_tipos", "Tipos e conversões (int, float, str, bool)", "ip", "ip_base",
  "int(input()), float(input()), str(); True/False como resultado de funções.",
  kw=[], src=[(IPF.format(3), None, "float/int"), (IPF.format(27), None, "bool")],
  diff=(1, "Uso direto."), aliases=["int", "float", "str", "bool", "conversão de tipos"])
C("py_operadores", "Operadores aritméticos", "ip", "ip_base",
  "+, −, *, /, ** e funções max/min/round.", type="ferramenta",
  kw=[], src=[(IPF.format(4), None, "R**2 * pi"), (IPF.format(5), None, "")],
  diff=(1, "Aritmética básica."), aliases=["potência", "round"])
C("py_divint", "Divisão inteira e resto (// e %)", "ip", "ip_base",
  "// e % para converter unidades (ex7), testar paridade/divisibilidade (ex12, ex14) e extrair dígitos (ex17).",
  type="ferramenta", kw=[], src=[(IPF.format(7), None, "horas/minutos/segundos"), (IPF.format(12), None, "FizzBuzz"), (IPF.format(17), None, "soma de dígitos")],
  diff=(2, "Usado em muitos exercícios posteriores."), aliases=["módulo", "resto", "divisão inteira", "%", "//"])
C("py_fstrings", "Formatação com f-strings", "ip", "ip_base",
  "f\"…{x}…\" com especificadores ({f_h:02}).", type="ferramenta",
  kw=[], src=[(IPF.format(2), None, ""), (IPF.format(7), None, ":02")],
  diff=(1, "Sintaxe."), aliases=["f-string", "format"])
C("py_if", "Condicionais (if / elif / else)", "ip", "ip_cond",
  "Ramificação com if/elif/else, incluindo condicionais encadeadas (ex9).", kw=[],
  src=[(IPF.format(8), None, ""), (IPF.format(9), None, "máximo de 3"), (IPF.format(10), None, "escalões")],
  diff=(1, "Estrutura básica."), aliases=["if", "elif", "else"])
C("py_bool_ops", "Operadores relacionais e lógicos", "ip", "ip_cond",
  "==, !=, <, >=, and, or em condições (ex10: grade>=20 and grade<50).", kw=[],
  src=[(IPF.format(10), None, "and"), (IPF.format(12), None, "i%3==0 and i%5==0")],
  diff=(1, "Combinação de condições."), aliases=["and", "or", "not"])
C("py_while", "Ciclo while", "ip", "ip_ciclos",
  "Repetição enquanto uma condição é verdadeira (ex12 FizzBuzz, ex29 Collatz).", kw=[],
  src=[(IPF.format(12), None, ""), (IPF.format(29), None, "")],
  diff=(2, "Condição de paragem."), aliases=["while"])
C("py_for", "Ciclo for e range", "ip", "ip_ciclos",
  "for i in range(a, b, passo) e iteração sobre sequências.", kw=[],
  src=[(IPF.format(13), None, ""), (IPF.format(21), None, "range decrescente")],
  diff=(2, "Limites de range."), aliases=["for", "range"])
C("py_acumulador", "Acumuladores e contadores", "ip", "ip_ciclos",
  "Padrão: variável inicializada antes do ciclo e atualizada (soma, contagem, melhor sequência).",
  type="algoritmo", kw=[], src=[(IPF.format(14), None, "pares/ímpares"), (IPF.format(16), None, "maior sequência"), (IPF.format(30), None, "")],
  diff=(2, "Padrão recorrente em ex14–ex30."), aliases=["contador", "acumulador"])
C("py_def", "Funções (def / return)", "ip", "ip_func",
  "Definir funções com parâmetros e devolver resultados (ex23 em diante).", kw=[],
  src=[(IPF.format(23), None, "def sum"), (IPF.format(24), None, "")],
  diff=(2, "Decomposição em funções."), aliases=["def", "return", "função"])
C("py_math", "Módulo math", "ip", "ip_func",
  "import math: math.pi, math.sqrt, math.ceil.", type="ferramenta", kw=[],
  src=[(IPF.format(18), None, "math.pi"), (IPF.format(19), None, "math.sqrt"), (IPF.format(31), None, "math.ceil")],
  diff=(1, "Importar e usar."), aliases=["import math", "sqrt"])
C("py_strings", "Strings: indexação e slicing", "ip", "ip_seq",
  "word[0], word[-1], word[1:-1], len(), iteração por caracteres e construção de strings.", kw=[],
  src=[(IPF.format(33), None, ""), (IPF.format(37), None, ""), (IPF.format(42), None, "")],
  diff=(2, "Índices negativos e limites."), aliases=["slicing", "string", "len"])
C("py_tuplos", "Tuplos", "ip", "ip_seq",
  "Sequências imutáveis; concatenação (t + (x,)), devolver vários valores (a, b).", kw=[],
  src=[(IPF.format(35), None, ""), (IPF.format(36), None, ""), (IPF.format(40), None, "")],
  diff=(2, "Tuplo de 1 elemento (x,)."), aliases=["tuple", "tuplo"])
C("py_digitos", "Algoritmos sobre dígitos", "ip", "ip_ciclos",
  "Extrair dígitos com // 10ⁱ e % 10 ou via str(n) (soma de dígitos, sequências crescentes, 'mountain').",
  type="algoritmo", kw=[], src=[(IPF.format(17), None, ""), (IPF.format(22), None, ""), (IPF.format(30), None, ""), (IPF.format(31), None, "")],
  diff=(3, "ex22 combina estado e casos."))
C("py_divisores", "Divisores, números perfeitos e factorização", "ip", "ip_func",
  "Procurar divisores com % (número perfeito ex20) e factorizar em primos até √n (ex32).",
  type="algoritmo", kw=[], src=[(IPF.format(20), None, "número perfeito"), (IPF.format(32), None, "factorize")],
  diff=(3, "Limite √n e ciclo while interno."), aliases=["factorize", "número perfeito"])
C("py_fatorial", "Fatorial (iterativo)", "ip", "ip_func",
  "factorial(n) com ciclo for e acumulador multiplicativo.", type="algoritmo", kw=[],
  src=[(IPF.format(28), None, "")], diff=(1, "Acumulador."), aliases=["n!", "factorial"])
C("py_collatz", "Sequência de Collatz", "ip", "ip_func",
  "Gerar a sequência n → n/2 ou 3n+1 até 1.", type="algoritmo", kw=[],
  src=[(IPF.format(29), None, "")], diff=(2, "while com regra por casos."))
C("py_pesquisa", "Pesquisa em sequências", "ip", "ip_seq",
  "Pesquisa linear (primeira/última ocorrência, ex40), palíndromos (ex34), subsequência (ex41), contagem (ex39).",
  type="algoritmo", kw=[], src=[(IPF.format(34), None, "palíndromo"), (IPF.format(40), None, "search"), (IPF.format(41), None, "substring")],
  diff=(2, "Índices e saídas antecipadas (return dentro do ciclo)."), aliases=["pesquisa linear", "palíndromo"])
C("py_fibonacci", "Palavras de Fibonacci", "ip", "ip_seq",
  "Construção iterativa (A→AB, B→A, ex43) e tuplo FIB para descobrir a letra na posição n (ex44).",
  type="algoritmo", kw=[], src=[(IPF.format(43), None, "evolve"), (IPF.format(44), None, "whichone")],
  diff=(4, "ex44 usa a estrutura recursiva das palavras."), aliases=["palavras de Fibonacci"])

# =============================================================================
# INTRODUÇÃO AOS COMPUTADORES
# =============================================================================
C("hardware_software", "Hardware e software", "ic", "ic_comp",
  "Hardware = componentes físicas; software = instruções passo-a-passo (programa). Software de sistema (SO, drivers) vs aplicacional.",
  kw=[r"[Hh]ardware", r"[Ss]oftware"], src=[(F["IC0"], 3, "Partes de um Sistema Computacional"), (F["IC0"], 12, "Tipos de Software")],
  diff=(1, "Introdutório."), aliases=["software de sistema", "sistema operativo"])
C("cpu", "CPU (UC + UAL)", "ic", "ic_comp",
  "'Cérebro' do computador: unidade de controlo (gere instruções) e unidade aritmética-lógica (operações aritméticas e lógicas).",
  kw=[r"\bCPU\b", r"Unidade\s+Aritm", r"Unidade\s+de\s+Controlo", r"[Mm]icroprocessador"], src=[(F["IC0"], 8, ""), (F["IC2"], 11, "")],
  diff=(1, "Introdutório."), aliases=["processador", "UAL", "ALU", "microprocessador"])
C("memoria", "Memória (RAM, ROM, volátil)", "ic", "ic_comp",
  "Volátil vs não volátil; RAM guarda programas em execução; ROM guarda o bootstrap.",
  kw=[r"[Mm]em[óo]ria", r"\bRAM\b", r"\bROM\b", r"vol[áa]til"], src=[(F["IC0"], 9, ""), (F["IC0"], 10, ""), (F["IC2"], 15, "Memória principal")],
  diff=(1, "Introdutório."), aliases=["RAM", "ROM", "memória principal"])
C("armazenamento", "Armazenamento permanente (HDD, SSD)", "ic", "ic_comp",
  "Magnético (HDD), ótico (CD/DVD) e estado sólido (SSD, flash NAND); SSD muito mais rápido.",
  kw=[r"\bHDD\b", r"\bSSD\b", r"[Aa]rmazenamento"], src=[(F["IC0"], 11, ""), (F["IC2"], 19, ""), (F["IC2"], 22, "HDD vs SSD")],
  diff=(1, "Introdutório."), aliases=["HDD", "SSD", "disco"])
C("io_devices", "Dispositivos de entrada/saída", "ic", "ic_comp",
  "Input (teclado, rato), output (monitor, impressora) e I/O (ecrã tátil).",
  kw=[r"[Dd]ispositivos\s+de\s+(entrada|sa[ií]da)", r"\bI/O\b"], src=[(F["IC0"], 5, ""), (F["IC0"], 6, ""), (F["IC0"], 7, "")],
  diff=(1, "Introdutório."), aliases=["I/O", "periféricos"])
C("algoritmo", "Algoritmo", "ic", "ic_hist",
  "Sequência de passos para resolver um problema (ex.: mudar um pneu); o estudo de algoritmos começou na Matemática.",
  kw=[r"[Aa]lgoritmo"], src=[(F["IC1"], 2, "Algoritmo"), (F["IC1"], 3, "Mudar um pneu"), (F["IC1"], 4, "História dos Algoritmos")],
  diff=(1, "Conceito fundamental, introdução intuitiva."), aliases=["algoritmos"])
C("euclides_ic", "Algoritmo de Euclides (história)", "ic", "ic_hist",
  "Exemplo histórico de algoritmo matemático apresentado em IC.", type="algoritmo",
  kw=[r"Euclides"], src=[(F["IC1"], 5, "Algoritmo de Euclides")],
  diff=(1, "Apenas apresentado."))
C("maquina_analitica", "Máquina Analítica (Babbage e Lovelace)", "ic", "ic_hist",
  "Primeiro projeto de computador de uso geral (1834–36), programável com cartões perfurados; Ada Lovelace e os números de Bernoulli.",
  kw=[r"M[áa]quina\s+Anal[ií]tica", r"Lovelace", r"Babbage"], src=[(F["IC1"], 9, ""), (F["IC1"], 14, "Números de Bernoulli")],
  diff=(1, "Histórico."), aliases=["Babbage", "Ada Lovelace"])
C("turing", "Máquina de Turing", "ic", "ic_hist",
  "Modelo de computação (fita, cabeça, estados); a máquina universal computa tudo o que é computável; computador 'Turing-complete'.",
  kw=[r"Turing"], src=[(F["IC1"], 19, ""), (F["IC1"], 20, "Máquina universal"), (F["IC1"], 22, "Exemplo de funcionamento"), (F["IC1"], 25, "Turing-complete")],
  diff=(3, "Modelo abstrato de computação."), aliases=["Turing-complete", "máquina universal"])
C("church_turing", "Computabilidade (Gödel, Church-Turing)", "ic", "ic_hist",
  "Teorema da incompletude de Gödel (1930); tese de Church-Turing (1936): modelo geral do que pode ser computado.",
  kw=[r"Church", r"G[öo]del", r"[Cc]omput[áa]ve"], src=[(F["IC1"], 16, "É tudo computável?"), (F["IC1"], 17, "Funções computáveis"), (F["IC1"], 18, "Tese de Church-Turing")],
  diff=(3, "Conceitos teóricos."), aliases=["tese de Church-Turing", "incompletude", "funções computáveis"])
C("transistor", "Transístor e circuito integrado", "ic", "ic_hist",
  "Transístor (1947), circuito integrado (Kilby 1958), fotolitografia; Intel 4004 primeiro microprocessador.",
  kw=[r"[Tt]ransi?[ií]stor", r"[Cc]ircuito\s+[Ii]ntegrado", r"[Ff]otolitografia"], src=[(F["IC1"], 41, ""), (F["IC1"], 44, ""), (F["IC1"], 48, "Intel 4004")],
  diff=(1, "Histórico."), aliases=["circuito integrado", "chip"])
C("moore", "Lei de Moore", "ic", "ic_hist",
  "Nº de transístores num circuito integrado duplica a cada ~18 meses (também na capacidade de armazenamento).",
  kw=[r"Moore"], src=[(F["IC1"], 59, ""), (F["IC1"], 60, "")],
  diff=(1, "Histórico."))
C("multicore", "Multicore e unidades especializadas (GPU, IA)", "ic", "ic_hist",
  "Desempenho via mais núcleos; chips com GPU, núcleos genéricos e unidades de IA (redes neuronais).",
  kw=[r"[Mm]ulticore", r"Diferenciadas", r"\bGPU\b"], src=[(F["IC1"], 63, ""), (F["IC1"], 64, "16 Inteligência Artificial (redes neuronais)"), (F["IC2"], 16, "GPU")],
  diff=(1, "Introdutório."), aliases=["GPU", "multi-core"])
C("von_neumann", "Arquitetura de von Neumann", "ic", "ic_arq",
  "'Stored-program computer': microprocessador, memória com dados e programas, I/O e barramentos. Implementada por todos os computadores atuais.",
  kw=[r"von\s+Neumann", r"stored-program"], src=[(F["IC1"], 37, "Proposta em 1945 (EDVAC)"), (F["IC2"], 3, ""), (F["IC2"], 4, "Componentes")],
  diff=(2, "Modelo central da UC."), aliases=["stored-program", "programa armazenado"])
C("barramentos", "Motherboard e barramentos", "ic", "ic_arq",
  "Barramentos de dados e instruções na placa principal; CPU-memória (NorthBridge) e I/O (SouthBridge).",
  kw=[r"[Bb]arramento", r"[Mm]otherboard", r"NorthBridge", r"SouthBridge"], src=[(F["IC2"], 8, ""), (F["F3"], 1, "Ex. 1 (f), (g)")],
  diff=(2, "Componentes concretos."), aliases=["motherboard", "chipset", "northbridge"])
C("load_store", "Arquitetura load/store", "ic", "ic_arq",
  "load registo, endereço / store registo, endereço: protocolo entre processador e memória; dados são lidos para registos.",
  kw=[r"load", r"store", r"[Rr]egisto"], src=[(F["IC2"], 10, ""), (F["IC3"], 13, "Dados usados nas instruções"), (F["IC3"], 14, "")],
  diff=(2, "Modelo de execução."), aliases=["registos", "load", "store"])
C("harvard", "Arquitetura de Harvard", "ic", "ic_arq",
  "Variante de von Neumann com barramentos diferentes para instruções e dados (melhor desempenho).",
  kw=[r"Harvard"], src=[(F["IC2"], 10, "")], diff=(2, "Variante."))
C("segmentos", "Segmentos de instruções e de dados", "ic", "ic_arq",
  "Programas em memória têm segmentos de instruções e de dados; o processador interpreta os bits pelo contexto (espaço de endereçamento).",
  kw=[r"segmentos?\s+de\s+(instru|dados)", r"[Ee]spa[çc]o\s+de\s+endere"], src=[(F["IC3"], 9, ""), (F["IC3"], 10, ""), (F["IC3"], 11, "Execução de instruções")],
  diff=(3, "Abstração sobre como o CPU executa."), aliases=["espaço de endereçamento", "processo"])
C("sh_navegacao", "Shell: navegação e diretórios", "ic", "ic_shell",
  "pwd, cd, cd ~, mkdir, tree, history — sistema de ficheiros em árvore.", type="ferramenta",
  kw=[r"\bpwd\b", r"\bmkdir\b", r"\bcd\b"], src=[(F["F1"], 1, "Ex. 1–3")],
  diff=(1, "Comandos básicos."), aliases=["pwd", "cd", "mkdir", "bash", "terminal"])
C("sh_ficheiros", "Shell: gestão de ficheiros", "ic", "ic_shell",
  "cat, cp (-a), mv, rm, diff, file, head/tail/less, tar (compactar/restaurar).", type="ferramenta",
  kw=[r"\bcp\b", r"\brm\b", r"\btar\b", r"\bcat\b", r"\bdiff\b"], src=[(F["F1"], 1, "Ex. 4–5"), (F["F1"], 2, "Ex. 6–10"), (F["F1"], 3, "Ex. 13 tar")],
  diff=(1, "Comandos básicos."), aliases=["cp", "mv", "rm", "tar", "cat"])
C("sh_permissoes", "Permissões (chmod)", "ic", "ic_shell",
  "ls -l e chmod para utilizador, grupo e outros (leitura, escrita, execução).", type="ferramenta",
  kw=[r"chmod", r"permiss"], src=[(F["F1"], 2, "Ex. 11")], diff=(2, "Notação de permissões."), aliases=["chmod"])
C("sh_processos", "Processos e jobs", "ic", "ic_shell",
  "Executar em background (&), ps, jobs, kill %1.", type="ferramenta",
  kw=[r"\bps\b", r"\bjobs\b", r"\bkill\b"], src=[(F["F2"], 1, "Ex. 1"), (F["F2"], 3, "Ex. 9")],
  diff=(2, "Conceito de processo."), aliases=["ps", "kill", "background"])
C("sh_glob", "Padrões glob (wildcards)", "ic", "ic_shell",
  "*, ?, [...] para selecionar ficheiros por nome/extensão.", type="ferramenta",
  kw=[r"glob", r"[Ww]ildcards"], src=[(F["F2"], 1, "Ex. 2")], diff=(2, "Sintaxe própria."), aliases=["wildcards", "glob"])
C("sh_pipes", "Redirecionamento e pipes", "ic", "ic_shell",
  "> e < para ficheiros; | liga a saída de um comando à entrada de outro.", type="ferramenta",
  kw=[r"redirecion", r"sa[ií]da\s+padr", r"entrada\s+padr"], src=[(F["F2"], 1, "Ex. 3"), (F["F2"], 2, "")],
  diff=(2, "Composição de comandos."), aliases=["pipe", "redirecionamento", "stdin", "stdout"])
C("sh_filtros", "Filtros de texto (grep, sort, cut, sed, find)", "ic", "ic_shell",
  "Processar ficheiros de texto (users.txt): grep, sort, cut/campos ':', sed, find, wc.", type="ferramenta",
  kw=[r"\bgrep\b", r"\bsort\b", r"\bsed\b", r"\bfind\b"], src=[(F["F2"], 2, "Ex. 4–6"), (F["F2"], 3, "Ex. 7–10")],
  diff=(3, "Combinar vários comandos numa linha."), aliases=["grep", "sort", "sed", "find"])
C("regex", "Expressões regulares", "ic", "ic_shell",
  "Padrões como ^[a-zA-Z]+[0-9]+$ testados com grep.", type="ferramenta",
  kw=[r"express[ãa]o\s+regular"], src=[(F["F2"], 3, "Ex. 11")], diff=(3, "Sintaxe densa."), aliases=["regex"])
C("bit_byte", "Bit, byte e unidades", "ic", "ic_repr",
  "Bit = dígito binário (número, booleano, voltagem); byte = 8 bits; KB = 2¹⁰ bytes, MB = 2²⁰, GB = 2³⁰. Toda a informação é sequência de bits.",
  kw=[r"\b[Bb]its?\b", r"[Bb]ytes?"], src=[(F["IC3"], 2, "Os bits e o seu significado"), (F["IC3"], 3, ""), (F["IC3"], 4, "Unidades de medida")],
  diff=(1, "Base de toda a representação."), aliases=["bit", "byte", "kilobyte"])
C("base_binaria", "Base binária e notação posicional", "ic", "ic_repr",
  "Representar números em potências de 2 (vs potências de 10); conversões binário ↔ decimal.",
  kw=[r"[Bb]in[áa]ri", r"base\s+2", r"pot[êe]ncias\s+de\s+2"], src=[(F["IC3"], 16, "Base binária"), (F["IC3"], 17, ""), (F["IC3"], 21, "100101 → decimal"), (F["F4"], 1, "Ex. 1")],
  diff=(2, "Conversões manuais."), aliases=["binário", "base 2"])
C("octal_hex", "Octal e hexadecimal", "ic", "ic_repr",
  "Compactam o binário: 1 símbolo octal = 3 bits; 1 símbolo hexadecimal = 4 bits.",
  kw=[r"[Oo]ctal", r"[Hh]exadecimal"], src=[(F["IC3"], 18, ""), (F["IC3"], 22, "Conversões"), (F["F4"], 1, "Ex. 1–2")],
  diff=(2, "Agrupar bits."), aliases=["hexadecimal", "octal", "base 16", "base 8"])
C("conversao_bases", "Conversão decimal → binário", "ic", "ic_repr",
  "Determinar a representação binária de um inteiro positivo (divisões sucessivas / tabela de potências de 2).",
  type="algoritmo", kw=[r"[Dd]eterminar\s+a\s+representa", r"converter", r"converta"], src=[(F["IC3"], 23, ""), (F["IC3"], 24, "Exemplo: 13"), (F["F4"], 1, "Ex. 1")],
  diff=(2, "Procedimento repetitivo."))
C("inteiros_sem_sinal", "Inteiros sem sinal", "ic", "ic_repr",
  "Com n bits representam-se 0 … 2ⁿ − 1.", type="formula", formula="0 ≤ x ≤ 2ⁿ − 1",
  kw=[r"sem\s+sinal"], src=[(F["IC3"], 19, ""), (F["IC3"], 20, "Maior número: 2ⁿ − 1"), (F["F4"], 1, "Ex. 3")],
  diff=(2, "Fórmula de limites."), aliases=["unsigned"])
C("inteiros_com_sinal", "Inteiros com sinal (bit de sinal)", "ic", "ic_repr",
  "O bit mais significativo indica o sinal (0 positivo, 1 negativo).",
  kw=[r"com\s+sinal", r"bit\s+de\s+sinal", r"bit\s+mais\s+significativo"], src=[(F["IC3"], 25, ""), (F["IC3"], 35, "")],
  diff=(2, "Ponte para o complemento para 2."), aliases=["signed"])
C("complemento2", "Complemento para 2", "ic", "ic_repr",
  "−x representa-se como 2ⁿ − x; alternativa: inverter os bits e somar 1. Gama: −2ⁿ⁻¹ … 2ⁿ⁻¹ − 1.",
  type="formula", formula="−x ≡ 2ⁿ − x  (= inverter bits + 1)",
  kw=[r"[Cc]omplemento\s+para\s+(2|dois)"], src=[(F["IC3"], 26, ""), (F["IC3"], 27, "Limites"), (F["IC3"], 29, "Algoritmo para −6"), (F["IC3"], 30, "Inverter e somar 1"), (F["IC3"], 33, "Conversões")],
  diff=(3, "Várias formas equivalentes e casos-limite."), aliases=["complemento de dois", "two's complement"])
C("extensao_sinal", "Extensão do sinal", "ic", "ic_repr",
  "Para passar de n para m > n bits, replicar o bit de sinal à esquerda.",
  kw=[r"[Ee]xtens[ãa]o\s+do\s+sinal"], src=[(F["IC3"], 31, ""), (F["IC3"], 32, "Exemplo −6")],
  diff=(2, "Regra simples."), aliases=["sign extension"])
C("adicao_binaria", "Adição binária", "ic", "ic_repr",
  "Soma bit a bit com transporte; em complemento para 2 soma diretamente positivos e negativos.",
  type="algoritmo", kw=[r"[Aa]di[çc][ãa]o\s+bin[áa]ria", r"[Aa]di[çc][ãa]o\s+de\s+(um|v[áa]rios)\s+bits?"], src=[(F["IC3"], 16, "Adição de um/vários bits"), (F["IC3"], 36, "Adição binária em complemento para 2"), (F["F4"], 2, "Ex. 6–7")],
  diff=(2, "Procedimento manual."))
C("overflow", "Overflow", "ic", "ic_repr",
  "Resultado não representável com os bits disponíveis; em complemento para 2 só ocorre somando números do mesmo sinal (positivo+positivo dá negativo ou vice-versa).",
  kw=[r"[Oo]verflow"], src=[(F["IC3"], 37, ""), (F["IC3"], 38, "Como detetar"), (F["IC3"], 40, "Nota sobre overflow"), (F["F4"], 2, "Ex. 6–7")],
  diff=(3, "Regra de deteção com sinais."))
C("notacao_cientifica", "Notação científica e normalização (base 2)", "ic", "ic_repr",
  "Um único dígito não nulo à esquerda do ponto: 0.0001011111 = 1.011111 × 2⁻⁴.",
  kw=[r"[Nn]ota[çc][ãa]o\s+cient", r"[Nn]ormaliza"], src=[(F["IC3"], 43, "Base 10"), (F["IC3"], 44, "Base 2")],
  diff=(2, "Analogia com base 10."), aliases=["normalização"])
C("virgula_flutuante", "Vírgula flutuante (sinal, expoente, mantissa)", "ic", "ic_repr",
  "Número = (−1)ˢ × 1.m × 2ᵉ; frações binárias como 101.101.",
  type="formula", formula="(−1)ˢ × 1.m × 2ᵉ",
  kw=[r"v[ií]rgula\s+flutuante", r"[Mm]antissa", r"[Ee]xpoente"], src=[(F["IC3"], 41, "101.101"), (F["IC3"], 42, ""), (F["IC3"], 45, "")],
  diff=(3, "Vários campos a combinar."), aliases=["floating point", "mantissa"])
C("ieee754", "Norma IEEE 754", "ic", "ic_repr",
  "Precisão simples (32 bits: 1+8+23, bias 127) e dupla (64 bits, bias 1023); expoentes 00…0 e 11…1 reservados (infinito, não normalizados).",
  type="formula", formula="expoente guardado = e + 127 (simples)",
  kw=[r"IEEE\s*754", r"bias", r"precis[ãa]o\s+(simples|dupla)"], src=[(F["IC3"], 46, ""), (F["IC3"], 49, "Bias"), (F["IC3"], 51, "Exemplo −0,6875"), (F["IC3"], 52, "Exemplo −9,6875"), (F["IC3"], 53, "Casos especiais")],
  diff=(4, "Codificação bit-a-bit com bias e normalização."), aliases=["IEEE", "precisão simples", "precisão dupla", "bias"])
C("adicao_vf", "Adição em vírgula flutuante", "ic", "ic_repr",
  "1) alinhar expoentes; 2) somar; 3) normalizar; 4) arredondar a mantissa; 5) repetir se necessário.",
  type="algoritmo", kw=[r"[Aa]di[çc][ãa]o\s+em\s+v[ií]rgula"], src=[(F["IC3"], 54, "Algoritmo"), (F["IC3"], 55, "Exemplo 12,6875 + 5,125")],
  diff=(3, "Algoritmo com arredondamento."))
C("texto_ascii", "Representação de texto: ASCII e Unicode (UTF-8)", "ic", "ic_repr",
  "Cada carácter tem uma sequência de bits: ASCII (7 bits, 128), Latin-1 (8 bits), Unicode: UTF-8 (1–4 bytes, compatível com ASCII), UTF-16, UTF-32.",
  kw=[r"ASCII", r"Unicode", r"UTF-?8", r"[Rr]epresenta[çc][ãa]o\s+de\s+texto"], src=[(F["IC3"], 56, ""), (F["IC3"], 57, "Tabela ASCII"), (F["IC3"], 58, "UTF-8")],
  diff=(2, "Tabelas e compatibilidade."), aliases=["ASCII", "Unicode", "UTF-8", "caracteres"])
C("interpretacao_contexto", "Interpretação dos bits pelo contexto", "ic", "ic_repr",
  "A mesma sequência de 32 bits pode ser inteiro com sinal, float ou instrução; é o tipo de instrução (add, addu, add.s, add.d) que decide.",
  kw=[r"add\.s", r"addu", r"depende\s+do\s+seu\s+contexto", r"dependendo\s+do\s+contexto"], src=[(F["IC3"], 5, ""), (F["IC3"], 6, "Sequência de 32 bits"), (F["IC3"], 15, "add / addu / add.s / add.d")],
  diff=(3, "Ideia abstrata mas fundamental."), aliases=["tipos de dados", "assembly"])

# =============================================================================
# HORIZONTE (apenas índice do Stewart / menções nos slides)
# =============================================================================
C("hz_serie_taylor", "Séries de potências e de Taylor", "hz", "hz_calc",
  "Stewart 11.8–11.11: séries de potências, séries de Taylor e Maclaurin, aplicações dos polinómios de Taylor. (Apenas o índice foi lido.)",
  kw=[r"Power\s+Series", r"Taylor\s+and\s+Maclaurin"], src=[(F["STEW"], None, "Índice: 11.8 Power Series (p. 746), 11.10 Taylor and Maclaurin Series (p. 759)")],
  diff=(4, "Estimativa — não lecionado."), status="horizonte", aliases=["série de Taylor", "Maclaurin"])
C("hz_integral", "Integral definido e Teorema Fundamental do Cálculo", "hz", "hz_calc",
  "Stewart cap. 5: áreas, integral definido, Teorema Fundamental do Cálculo, integrais indefinidos.",
  kw=[r"Definite\s+Integral", r"Fundamental\s+Theorem"], src=[(F["STEW"], None, "Índice: 5.2 The Definite Integral (p. 378), 5.3 The Fundamental Theorem of Calculus (p. 392)")],
  diff=(3, "Estimativa — não lecionado."), status="horizonte", aliases=["integral", "integrais", "TFC"])
C("hz_derivadas_parciais", "Funções de várias variáveis e derivadas parciais", "hz", "hz_calc",
  "Stewart cap. 14: funções de várias variáveis, limites, derivadas parciais, planos tangentes e regra da cadeia.",
  kw=[r"Partial\s+Derivatives", r"Several\s+Variables"], src=[(F["STEW"], None, "Índice: 14.1 (p. 888), 14.3 Partial Derivatives (p. 911), 14.4 Tangent Planes and Linear Approximations (p. 927)")],
  diff=(4, "Estimativa — não lecionado."), status="horizonte", aliases=["derivada parcial"])
C("hz_gradiente", "Derivada direcional e vetor gradiente", "hz", "hz_calc",
  "Stewart 14.6: Directional Derivatives and the Gradient Vector.",
  kw=[r"Gradient\s+Vector", r"Directional\s+Derivatives"], src=[(F["STEW"], None, "Índice: 14.6 (p. 946)")],
  diff=(4, "Estimativa — não lecionado."), status="horizonte", aliases=["gradiente", "nabla"])
C("hz_otimizacao", "Otimização em várias variáveis e multiplicadores de Lagrange", "hz", "hz_calc",
  "Stewart 14.7 Maximum and Minimum Values; 14.8 Lagrange Multipliers (e 4.7 Optimization Problems em 1 variável).",
  kw=[r"Lagrange\s+Multipliers", r"Optimization\s+Problems"], src=[(F["STEW"], None, "Índice: 4.7 Optimization Problems (p. 330), 14.7 (p. 959), 14.8 Lagrange Multipliers (p. 971)")],
  diff=(4, "Estimativa — não lecionado."), status="horizonte", aliases=["Lagrange", "otimização"])
C("hz_vetores_stewart", "Vetores e geometria do espaço (Stewart cap. 12)", "hz", "hz_calc",
  "12.2 Vectors, 12.3 The Dot Product, 12.4 The Cross Product, 12.5 Equations of Lines and Planes — sobrepõe-se a ALGA.",
  kw=[r"The\s+Dot\s+Product", r"The\s+Cross\s+Product"], src=[(F["STEW"], None, "Índice: 12.3 Dot Product (p. 807), 12.4 Cross Product (p. 814), 12.5 Lines and Planes (p. 823)")],
  diff=(2, "Já coberto em ALGA."), status="horizonte", aliases=["vetores no espaço"])
C("hz_edo", "Equações diferenciais (método de Euler)", "hz", "hz_calc",
  "Stewart cap. 9: modelação com equações diferenciais, campos de direções e método de Euler.",
  kw=[r"Differential\s+Equations", r"Euler.s\s+Method"], src=[(F["STEW"], None, "Índice: 9.1 (p. 586), 9.2 Direction Fields and Euler's Method (p. 591)")],
  diff=(4, "Estimativa — não lecionado."), status="horizonte", aliases=["EDO", "Euler"])
C("hz_ia", "Inteligência Artificial: Data Mining e Deep Learning", "hz", "hz_dados",
  "'Técnicas de IA, como Data Mining e Deep Learning, extraem conhecimento a partir de grandes volumes de dados.'",
  kw=[r"Intelig[êe]ncia\s+Artificial", r"Deep\s+Learning", r"Data\s+Mining"], src=[(F["IC0"], 27, "Inteligência Artificial (IA)")],
  diff=(4, "Estimativa — não lecionado."), status="horizonte", aliases=["IA", "deep learning", "data mining", "machine learning"])
C("hz_bigdata", "Big Data e Internet of Things", "hz", "hz_dados",
  "'Os computadores estão em todo o lado e produzem enormes quantidades de dados.'",
  kw=[r"Big\s+Data"], src=[(F["IC0"], 26, "")], diff=(2, "Menção."), status="horizonte", aliases=["IoT", "dados"])
C("hz_redes_neuronais", "Redes neuronais (hardware de IA)", "hz", "hz_dados",
  "Chips modernos incluem unidades dedicadas a IA (redes neuronais).",
  kw=[r"redes\s+neuronais"], src=[(F["IC1"], 64, "8 GPU, 4+4 cores + 16 Inteligência Artificial (redes neuronais)")],
  diff=(4, "Estimativa — não lecionado."), status="horizonte", aliases=["neural networks"])

# =============================================================================
# RELAÇÕES CONCEITO ↔ CONCEITO
# (origem, tipo, destino, natureza, confiança, fonte, justificação)
# prerequisite_of: origem é pré-requisito de destino
# =============================================================================
REL = []


def R(a, t, b, nat, conf, fonte, just):
    REL.append(dict(source=a, type=t, target=b, nature=nat, confidence=conf, evidence=fonte, justification=just))


E, I = "explicita", "inferida"
# ---- ALGA
R("vetores_rn", "prerequisite_of", "produto_interno", E, "alta", F["ALGA_R"] + "#2", "Produto interno definido para u, v ∈ Rⁿ.")
R("produto_interno", "prerequisite_of", "norma", E, "alta", F["ALGA_R"] + "#2", "‖u‖ = √(u·u).")
R("produto_interno", "prerequisite_of", "ortogonalidade", E, "alta", F["ALGA_R"] + "#2", "u ⊥ v se u·v = 0.")
R("vetores_rn", "prerequisite_of", "eq_vetorial", E, "alta", F["ALGA_S1"] + "#2", "Reta determinada por ponto e vetor diretor.")
R("ortogonalidade", "prerequisite_of", "eq_cartesiana", E, "alta", F["ALGA_R"] + "#2", "(a,b) é perpendicular à reta; (a,b,c) é o vetor normal do plano.")
R("eq_cartesiana", "related_to", "eq_vetorial", E, "alta", F["ALGA_R"] + "#2", "Conversão vetorial → cartesiana eliminando parâmetros.")
R("eq_linear", "prerequisite_of", "sist_homogeneo", E, "alta", F["ALGA_R"] + "#3", "Homogéneo associado obtém-se anulando os termos independentes.")
R("eq_linear", "prerequisite_of", "classif_sist", E, "alta", F["ALGA_R"] + "#3", "Classificação pelo nº de soluções.")
R("eq_cartesiana", "related_to", "eq_linear", E, "alta", F["ALGA_S1"] + "#2", "x + y = 1 é reta em R² e plano em R³: equações cartesianas são equações lineares; reta em R³ = sistema de 2 planos.")
R("eq_linear", "prerequisite_of", "matriz_ampliada", E, "alta", F["ALGA_R"] + "#4", "Um sistema corresponde à matriz ampliada (A|B).")
R("matriz", "prerequisite_of", "matriz_ampliada", E, "alta", F["ALGA_S1"] + "#6", "1.3 Matrizes e a resolução de sistemas lineares.")
R("op_elementares", "prerequisite_of", "gauss", E, "alta", F["ALGA_R"] + "#4", "Gauss usa operações elementares sobre linhas.")
R("matriz_ampliada", "prerequisite_of", "gauss", E, "alta", F["ALGA_R"] + "#4", "(A|B) → forma em escada.")
R("forma_escada", "prerequisite_of", "gauss", E, "alta", F["ALGA_R"] + "#4", "Gauss leva à forma em escada.")
R("forma_escada", "prerequisite_of", "forma_reduzida", E, "alta", F["ALGA_R"] + "#4", "Reduzida = em escada + pivôs 1 + zeros nas colunas-pivô.")
R("forma_reduzida", "prerequisite_of", "gauss_jordan", E, "alta", F["ALGA_R"] + "#4", "Gauss-Jordan: (A|B) → forma reduzida.")
R("gauss", "prerequisite_of", "gauss_jordan", I, "alta", F["ALGA_R"] + "#4", "Gauss-Jordan continua a eliminação até à forma reduzida.")
R("forma_escada", "prerequisite_of", "caracteristica", E, "alta", F["ALGA_R"] + "#4", "car(A) = nº de pivôs de uma forma em escada.")
R("caracteristica", "prerequisite_of", "discussao_sist", E, "alta", F["ALGA_R"] + "#4", "SI/SPI/SPD caracterizados por car(A) e car(A|B).")
R("classif_sist", "prerequisite_of", "discussao_sist", E, "alta", F["ALGA_R"] + "#4", "")
R("discussao_sist", "prerequisite_of", "sist_parametros", E, "alta", F["ALGA_R"] + "#10", "Método-tipo: olhar para a última linha (0…0 | f(a)).")
R("gauss", "prerequisite_of", "sist_parametros", E, "alta", F["ALGA_R"] + "#10", "Escalonar sem dividir por expressões que possam ser 0.")
R("gauss", "applied_in", "interpolacao", E, "alta", F["ALGA_R"] + "#4", "Substituir pontos dá um sistema 4×4.")
R("sist_homogeneo", "related_to", "classif_sist", E, "alta", F["ALGA_R"] + "#3", "Sistema possível tem solução única ⇔ homogéneo associado só tem a nula.")
R("op_elementares", "related_to", "classif_sist", E, "media", F["ALGA_R"] + "#3", "Operações elementares dão sistemas equivalentes (mesmo conjunto solução).")
R("matriz", "prerequisite_of", "op_matrizes", E, "alta", F["ALGA_S2"] + "#2", "")
R("op_matrizes", "prerequisite_of", "produto_matrizes", I, "media", F["ALGA_S2"] + "#3", "Ordem dos slides 2.2; propriedades combinam soma e produto.")
R("produto_interno", "prerequisite_of", "produto_matrizes", E, "alta", F["ALGA_R"] + "#5", "cᵢⱼ = (linha i de A)·(coluna j de B).")
R("produto_matrizes", "prerequisite_of", "forma_matricial", E, "alta", F["ALGA_S2"] + "#3", "Sistemas e multiplicação de matrizes.")
R("eq_linear", "prerequisite_of", "forma_matricial", E, "alta", F["ALGA_R"] + "#5", "Todo o sistema escreve-se AX = B.")
R("produto_matrizes", "prerequisite_of", "inversa", E, "alta", F["ALGA_R"] + "#6", "Definida por AB = I = BA.")
R("inversa", "applied_in", "forma_matricial", E, "alta", F["ALGA_R"] + "#6", "Se A invertível, AX = B tem solução X = A⁻¹B.")
R("inversa", "prerequisite_of", "inversa_2x2", E, "alta", F["ALGA_R"] + "#6", "")
R("gauss_jordan", "prerequisite_of", "inversa_gj", E, "alta", F["ALGA_R"] + "#6", "Método (Gauss-Jordan) com (A | I).")
R("inversa", "prerequisite_of", "inversa_gj", E, "alta", F["ALGA_R"] + "#6", "")
R("op_elementares", "prerequisite_of", "mat_elementares", E, "alta", F["ALGA_R"] + "#6", "E_α obtém-se aplicando α à identidade.")
R("inversa", "related_to", "mat_elementares", E, "alta", F["ALGA_R"] + "#6", "Matrizes elementares são invertíveis.")
R("op_elementares", "prerequisite_of", "det_def", E, "alta", F["ALGA_S3"] + "#1", "Definição formal usa A_α (operação elementar α).")
R("mat_elementares", "prerequisite_of", "det_prop", E, "alta", F["ALGA_S3"] + "#2", "det A = det E_α₁ ⋯ det E_αₙ · det A′.")
R("det_def", "prerequisite_of", "det_prop", E, "alta", F["ALGA_R"] + "#7", "")
R("det_prop", "prerequisite_of", "det_invertivel", E, "alta", F["ALGA_S3"] + "#2", "")
R("inversa", "prerequisite_of", "det_invertivel", E, "alta", F["ALGA_R"] + "#7", "")
R("det_def", "prerequisite_of", "laplace", E, "alta", F["ALGA_S3"] + "#3", "Laplace define uma função determinante (prova por indução na ordem).")
R("laplace", "prerequisite_of", "sarrus", I, "media", F["ALGA_S3"] + "#4", "Sarrus é um caso 3×3 apresentado após Laplace.")
R("laplace", "prerequisite_of", "det_estrategias", E, "alta", F["ALGA_R"] + "#8", "Estratégias 1 e 3.")
R("det_prop", "prerequisite_of", "det_estrategias", E, "alta", F["ALGA_R"] + "#8", "Estratégia 2 (Gauss + produto da diagonal).")
R("gauss", "applied_in", "det_estrategias", E, "alta", F["ALGA_R"] + "#8", "Levar à forma em escada (triangular) e multiplicar a diagonal.")
R("det_prop", "prerequisite_of", "areas_volumes", E, "alta", F["ALGA_R"] + "#9", "")
R("det_def", "prerequisite_of", "cramer", E, "alta", F["ALGA_R"] + "#9", "")
R("det_invertivel", "prerequisite_of", "cramer", E, "alta", F["ALGA_R"] + "#9", "Só se det A ≠ 0.")
R("forma_matricial", "prerequisite_of", "cramer", E, "alta", F["ALGA_R"] + "#9", "Solução de AX = B.")
R("det_def", "prerequisite_of", "produto_vetorial", E, "alta", F["ALGA_R"] + "#9", "u × v definido por determinante simbólico.")
R("ortogonalidade", "related_to", "produto_vetorial", E, "alta", F["ALGA_S3"] + "#7", "u × v é ortogonal a u e a v.")
R("produto_vetorial", "applied_in", "eq_cartesiana", E, "alta", F["ALGA_R"] + "#10", "Normal n = u × v para o plano por 3 pontos; direção de reta dada por 2 planos.")
R("produto_vetorial", "prerequisite_of", "produto_misto", E, "alta", F["ALGA_R"] + "#9", "u·(v × w) = det[u; v; w].")
R("produto_interno", "prerequisite_of", "produto_misto", E, "alta", F["ALGA_R"] + "#9", "")
R("produto_misto", "applied_in", "areas_volumes", E, "alta", F["ALGA_R"] + "#9", "Volume do paralelepípedo |det[u; v; w]|.")
# ---- CÁLCULO
R("sucessao", "prerequisite_of", "limite_eps_n", E, "alta", F["CAL_R"] + "#2", "")
R("limite_eps_n", "prerequisite_of", "prop_limites", E, "alta", F["CAL_R"] + "#2", "'Todas se provam pela definição ε–N.'")
R("desig_triangular", "prerequisite_of", "prop_limites", E, "alta", F["CAL_R"] + "#2", "Ideia da prova da soma.")
R("convergente_limitada", "prerequisite_of", "prop_limites", E, "alta", F["CAL_R"] + "#2", "Lema usado na prova do produto.")
R("limite_eps_n", "prerequisite_of", "convergente_limitada", E, "alta", cad("cal", 5) + "#2", "")
R("limite_eps_n", "prerequisite_of", "enquadramento", E, "alta", cad("cal", 5) + "#3", "Prova com ε comum e N = max.")
R("limite_eps_n", "prerequisite_of", "subsucessoes", E, "alta", F["CAL_R"] + "#3", "")
R("limite_eps_n", "prerequisite_of", "monotonas", I, "alta", F["CAL_R"] + "#4", "Teorema sobre convergência.")
R("lhopital", "related_to", "limite_eps_n", E, "media", F["CAL_R"] + "#3", "Ferramenta para calcular lim aₘ via lim f(x) com f(m) = aₘ (não para provar pela definição).")
R("continuidade", "prerequisite_of", "lim_continua", E, "alta", F["CAL_R"] + "#3", "Se f contínua em L, lim f(aₘ) = f(L).")
R("limite_eps_n", "prerequisite_of", "lim_continua", I, "alta", F["CAL_R"] + "#3", "")
R("sucessao", "prerequisite_of", "serie", E, "alta", F["CAL_R"] + "#4", "Série definida pela sucessão das somas parciais.")
R("limite_eps_n", "prerequisite_of", "serie", E, "alta", F["CAL_R"] + "#4", "Converge se lim Sₘ = s.")
R("serie", "prerequisite_of", "serie_geometrica", E, "alta", F["CAL_R"] + "#4", "Fórmula vem de Sₘ.")
R("serie", "prerequisite_of", "serie_telescopica", E, "alta", F["CAL_R"] + "#5", "Sₘ = a₁ − aₘ₊₁.")
R("subsucessoes", "applied_in", "serie", E, "alta", F["CAL_R"] + "#4", "Σ(−1)ᵐ diverge: subsucessões de Sₘ com limites diferentes.")
R("serie", "prerequisite_of", "termo_geral", E, "alta", F["CAL_R"] + "#5", "")
R("termo_geral", "related_to", "harmonica", E, "alta", F["CAL_R"] + "#5", "Recíproco falso: a harmónica diverge com 1/m → 0.")
R("serie", "prerequisite_of", "prop_series", E, "alta", F["CAL_R"] + "#5", "")
R("serie", "prerequisite_of", "p_series", E, "alta", F["CAL_R"] + "#5", "")
R("harmonica", "related_to", "p_series", I, "alta", F["CAL_R"] + "#5", "Harmónica é a p-série com p = 1.")
R("p_series", "prerequisite_of", "criterio_comparacao", E, "alta", F["CAL_R"] + "#6", "Exercícios comparam com p-séries.")
R("serie_geometrica", "prerequisite_of", "criterio_comparacao", E, "media", cad("cal", 4) + "#5", "Ex. 1a compara com (1/2)ᵐ.")
R("criterio_comparacao", "prerequisite_of", "comparacao_limite", I, "alta", F["CAL_R"] + "#6", "Versão no limite da comparação.")
R("limite_eps_n", "prerequisite_of", "comparacao_limite", I, "media", F["CAL_R"] + "#6", "Exige calcular lim aₘ/bₘ.")
R("monotonas", "prerequisite_of", "series_alternadas", E, "alta", cad("cal", 8) + "#2", "Condição (bₘ) decrescente.")
R("serie", "prerequisite_of", "series_alternadas", E, "alta", cad("cal", 8) + "#2", "")
R("criterio_comparacao", "applied_in", "conv_absoluta", E, "alta", cad("cal", 8) + "#3", "Σ|cos m|/2ᵐ comparada com a geométrica.")
R("series_alternadas", "related_to", "conv_absoluta", E, "alta", cad("cal", 8) + "#3", "Σ(−1)ᵐ/m converge (CSA) mas não absolutamente.")
R("conv_absoluta", "prerequisite_of", "criterio_razao", E, "alta", cad("cal", 8) + "#4", "Conclui convergência absoluta.")
R("conv_absoluta", "prerequisite_of", "criterio_raiz", E, "alta", cad("cal", 8) + "#5", "")
R("criterio_razao", "related_to", "criterio_raiz", I, "alta", cad("cal", 8) + "#5", "Mesma estrutura L < 1 / L > 1 / L = 1.")
R("serie_geometrica", "related_to", "criterio_razao", I, "media", cad("cal", 8) + "#4", "Razão constante x na geométrica.")
R("limite_eps_n", "prerequisite_of", "limite_funcao", I, "alta", F["CAL_R"] + "#6", "Mesma estrutura ∀ε ∃ (N ↔ δ).")
R("funcao", "prerequisite_of", "limite_funcao", I, "alta", cad("cal", 8) + "#6", "")
R("limite_funcao", "prerequisite_of", "continuidade", E, "alta", F["CAL_R"] + "#6", "Contínua se lim f(x) = f(x₀).")
R("limite_funcao", "prerequisite_of", "derivada", E, "alta", F["CAL_R"] + "#7", "Derivada = limite da taxa de variação.")
R("derivada", "prerequisite_of", "reta_tangente", E, "alta", cad("cal", 11) + "#2", "Declive da tangente = f'(a).")
R("derivada", "prerequisite_of", "regras_derivacao", E, "alta", F["CAL_R"] + "#7", "Provas a partir da definição.")
R("regras_derivacao", "prerequisite_of", "derivadas_elementares", I, "media", cad("cal", 11) + "#3", "tan = sen/cos usa a regra do quociente.")
R("derivada", "prerequisite_of", "dif_continua", E, "alta", cad("cal", 11) + "#3", "")
R("continuidade", "prerequisite_of", "dif_continua", E, "alta", cad("cal", 11) + "#3", "")
R("derivada", "prerequisite_of", "regra_cadeia", E, "alta", cad("cal", 9) + "#3", "Prova pela definição.")
R("regra_cadeia", "prerequisite_of", "derivada_inversa", E, "alta", cad("cal", 9) + "#3", "(g⁻¹∘g)' = 1 ⇒ fórmula.")
R("funcao", "prerequisite_of", "derivada_inversa", E, "media", cad("cal", 8) + "#6", "Funções inversas (arccos, ln).")
R("derivada", "prerequisite_of", "ordem_superior", I, "alta", cad("cal", 11) + "#3", "")
R("derivada", "prerequisite_of", "monotonia_derivada", E, "alta", cad("cal", 7) + "#2", "")
R("derivada", "prerequisite_of", "extremos", E, "alta", cad("cal", 11) + "#6", "Fermat: f'(c) = 0.")
R("ordem_superior", "prerequisite_of", "extremos", E, "media", cad("cal", 11) + "#6", "Teste da 2.ª derivada.")
R("continuidade", "prerequisite_of", "extremos", E, "alta", cad("cal", 11) + "#5", "Weierstrass exige continuidade em [a,b].")
R("derivada", "prerequisite_of", "taylor1", E, "alta", cad("cal", 9) + "#2", "")
R("limite_funcao", "prerequisite_of", "taylor1", E, "alta", cad("cal", 9) + "#2", "Prova a partir da definição ε–δ.")
R("reta_tangente", "related_to", "taylor1", E, "alta", cad("cal", 7) + "#3", "A aproximação de 1.ª ordem é a reta tangente.")
R("taylor1", "prerequisite_of", "newton", E, "alta", cad("cal", 9) + "#2", "0 = f(x) ≈ f(x₀) + f'(x₀)(x − x₀).")
R("reta_tangente", "prerequisite_of", "newton", E, "alta", cad("cal", 11) + "#6", "Interseção da tangente com o eixo das abcissas.")
R("newton", "related_to", "sucessao", E, "alta", cad("cal", 9) + "#3", "'xₘ₊₁ = xₘ − f(xₘ)/f'(xₘ) → Sucessão'.")
R("bolzano", "applied_in", "newton", E, "alta", cad("cal", 12) + "#3", "Garantir raiz em [−2, −1] antes de iterar.")
R("continuidade", "prerequisite_of", "bolzano", I, "alta", cad("cal", 12) + "#3", "Teorema sobre funções contínuas.")
R("extremos", "related_to", "newton", E, "media", cad("cal", 9) + "#2", "'f(x) máximo ou mínimo local ⇒ f'(x) = 0' → candidatos procurados como zeros.")
R("derivada", "prerequisite_of", "primitiva", E, "alta", cad("cal", 10) + "#2", "F' = f.")
R("derivadas_elementares", "prerequisite_of", "lhopital", I, "alta", F["CAL_R"] + "#3", "L'Hôpital deriva numerador e denominador.")
# ---- ED
R("proposicao", "prerequisite_of", "conectivas", E, "alta", F["ED_R"] + "#3", "")
R("conectivas", "prerequisite_of", "implicacao", E, "alta", F["ED_R"] + "#3", "")
R("conectivas", "prerequisite_of", "tabela_verdade", E, "alta", F["ED_L"] + "#9", "")
R("tabela_verdade", "prerequisite_of", "tautologia", E, "alta", F["ED_R"] + "#3", "Verdadeira para todas as atribuições.")
R("tautologia", "prerequisite_of", "equivalencia_logica", E, "alta", F["ED_R"] + "#4", "P₁ ⇔ P₂ sse P₁ ↔ P₂ é tautologia.")
R("equivalencia_logica", "prerequisite_of", "leis_equivalencia", E, "alta", F["ED_R"] + "#4", "")
R("leis_equivalencia", "contains", "de_morgan", E, "alta", F["ED_R"] + "#4", "De Morgan é uma das leis.")
R("implicacao", "related_to", "leis_equivalencia", E, "alta", F["ED_R"] + "#4", "Lei da implicação P → Q ⇔ ¬P ∨ Q.")
R("literal", "prerequisite_of", "fnn", E, "alta", F["ED_R"] + "#5", "")
R("de_morgan", "prerequisite_of", "fnn", E, "alta", F["ED_L"] + "#26", "FNN obtida com De Morgan e dupla negação.")
R("fnn", "prerequisite_of", "alg_fn", E, "alta", F["ED_R"] + "#5", "Passo 2 do algoritmo.")
R("leis_equivalencia", "prerequisite_of", "alg_fn", E, "alta", F["ED_R"] + "#5", "Eliminar →/↔ e distribuir.")
R("alg_fn", "prerequisite_of", "fnd", E, "alta", F["ED_R"] + "#5", "")
R("alg_fn", "prerequisite_of", "fnc", E, "alta", F["ED_R"] + "#5", "")
R("tabela_verdade", "prerequisite_of", "fnd", E, "alta", F["ED_R"] + "#5", "FND pelas linhas com φ = v.")
R("tabela_verdade", "prerequisite_of", "fnc", E, "alta", F["ED_R"] + "#5", "FNC pelas linhas com φ = f.")
R("fnd", "related_to", "fnc", E, "alta", F["ED_L"] + "#33", "'Por dualidade'.")
R("fnd", "prerequisite_of", "decisao_fn", E, "alta", F["ED_R"] + "#5", "FND satisfazível sse alguma conjunção o é.")
R("fnc", "prerequisite_of", "decisao_fn", E, "alta", F["ED_R"] + "#5", "FNC tautologia sse todas as disjunções o são.")
R("tautologia", "prerequisite_of", "decisao_fn", E, "alta", F["ED_R"] + "#5", "")
R("proposicao", "prerequisite_of", "predicados", E, "alta", F["ED_R"] + "#6", "LPO acrescenta variáveis, predicados e quantificadores ao CP.")
R("predicados", "prerequisite_of", "quantificadores", E, "alta", F["ED_R"] + "#6", "")
R("quantificadores", "prerequisite_of", "negacao_quant", E, "alta", F["ED_R"] + "#6", "")
R("de_morgan", "related_to", "negacao_quant", I, "media", F["ED_R"] + "#6", "A negação troca ∀/∃ tal como De Morgan troca ∧/∨.")
R("quantificadores", "prerequisite_of", "ordem_quant", E, "alta", F["ED_R"] + "#6", "")
R("quantificadores", "prerequisite_of", "formalizacao", E, "alta", F["ED_R"] + "#6", "")
R("implicacao", "prerequisite_of", "formalizacao", E, "alta", F["ED_R"] + "#6", "'Todo o A é B': ∀x(A(x) → B(x)).")
R("tautologia", "prerequisite_of", "regra_inferencia", E, "alta", F["ED_R"] + "#7", "Qualquer tautologia A → B dá uma regra A ⇒ B.")
R("implicacao", "prerequisite_of", "regra_inferencia", E, "alta", F["ED_R"] + "#7", "")
R("regra_inferencia", "prerequisite_of", "modus_ponens", E, "alta", F["ED_L"] + "#44", "")
R("regra_inferencia", "prerequisite_of", "modus_tollens", E, "alta", F["ED_L"] + "#47", "")
R("implicacao", "prerequisite_of", "modus_tollens", I, "alta", F["ED_R"] + "#3", "Contrapositiva P → Q ⇔ ¬Q → ¬P.")
R("regra_inferencia", "prerequisite_of", "outras_regras", E, "alta", F["ED_R"] + "#7", "")
R("regra_inferencia", "prerequisite_of", "falacias", E, "alta", F["ED_R"] + "#7", "")
R("modus_ponens", "prerequisite_of", "prova_formal", E, "alta", F["ED_R"] + "#13", "Ex. 15 usa transitividade e modus ponens.")
R("modus_tollens", "prerequisite_of", "prova_formal", E, "alta", F["ED_R"] + "#13", "Ex. 16.")
R("outras_regras", "prerequisite_of", "prova_formal", E, "alta", F["ED_R"] + "#13", "")
R("de_morgan", "applied_in", "prova_formal", E, "alta", F["ED_R"] + "#13", "Ex. 16 passos 2 e 4.")
R("conjunto", "prerequisite_of", "subconjunto", E, "alta", F["ED_R"] + "#8", "")
R("quantificadores", "prerequisite_of", "subconjunto", E, "alta", F["ED_R"] + "#8", "A ⊆ B ⇔ ∀x (x ∈ A → x ∈ B).")
R("implicacao", "prerequisite_of", "subconjunto", E, "alta", F["ED_R"] + "#8", "")
R("predicados", "prerequisite_of", "conjunto", E, "media", F["ED_C"] + "#4", "Definição por compreensão S = {X | P(X)}.")
R("subconjunto", "prerequisite_of", "partes", E, "alta", F["ED_R"] + "#8", "P(A) = {S | S ⊆ A}.")
R("conjunto", "prerequisite_of", "op_conjuntos", E, "alta", F["ED_R"] + "#8", "")
R("conectivas", "prerequisite_of", "op_conjuntos", E, "alta", F["ED_C"] + "#10", "∩ definida com 'e', ∪ com 'ou'.")
R("conjunto", "prerequisite_of", "produto_cartesiano", E, "alta", F["ED_R"] + "#8", "")
R("conjunto", "prerequisite_of", "cardinalidade", E, "alta", F["ED_R"] + "#9", "")
R("cardinalidade", "prerequisite_of", "inclusao_exclusao", E, "alta", F["ED_R"] + "#9", "")
R("op_conjuntos", "prerequisite_of", "inclusao_exclusao", E, "alta", F["ED_R"] + "#9", "")
R("partes", "related_to", "cardinalidade", E, "alta", F["ED_R"] + "#9", "|2ᴬ| = 2^|A|.")
R("leis_equivalencia", "prerequisite_of", "algebra_conjuntos", E, "alta", F["ED_R"] + "#9", "'São as mesmas leis da lógica com ∩ ↔ ∧, ∪ ↔ ∨'.")
R("op_conjuntos", "prerequisite_of", "algebra_conjuntos", E, "alta", F["ED_C"] + "#17", "")
R("de_morgan", "applied_in", "algebra_conjuntos", E, "alta", F["ED_C"] + "#18", "Leis de De Morgan para conjuntos.")
R("algebra_conjuntos", "prerequisite_of", "provas_conjuntos", E, "alta", F["ED_R"] + "#9", "")
R("equivalencia_logica", "prerequisite_of", "provas_conjuntos", E, "alta", F["ED_R"] + "#9", "Traduzir cada operação para lógica.")
R("subconjunto", "prerequisite_of", "provas_conjuntos", E, "alta", F["ED_R"] + "#9", "Igualdade = duas inclusões.")
R("prova_contradicao", "applied_in", "provas_conjuntos", E, "alta", F["ED_R"] + "#9", "Prova de A ∩ ∅ = ∅ por contradição.")
R("quantificadores", "prerequisite_of", "inducao", E, "alta", F["ED_R"] + "#11", "P(n₀) ∧ ∀n ≥ n₀ (P(n) → P(n+1)) → ∀n P(n).")
R("implicacao", "prerequisite_of", "inducao", E, "alta", F["ED_R"] + "#11", "")
R("inducao", "prerequisite_of", "inducao_forte", E, "alta", F["ED_I"] + "#10", "'A regra de inferência é ligeiramente modificada'.")
R("inducao", "prerequisite_of", "soma_geometrica", E, "alta", F["ED_R"] + "#11", "Provada por indução.")
R("inducao", "prerequisite_of", "recorrencia", E, "alta", F["ED_I"] + "#16", "Adivinhar fórmula para Tₙ e provar.")
R("prova_direta", "related_to", "prova_contradicao", E, "alta", F["ED_I"] + "#19", "'Outras técnicas de demonstração'.")
R("inducao", "related_to", "prova_direta", E, "media", F["ED_I"] + "#21", "Paridade provável por indução.")
R("regra_inferencia", "related_to", "inducao", E, "alta", F["ED_I"] + "#10", "Indução vista como regra de inferência.")
R("formalizacao", "prerequisite_of", "divisibilidade", E, "alta", F["ED_R"] + "#6", "a | b ⇔ ∃k ∈ Z (b = ka).")
R("divisibilidade", "prerequisite_of", "mdc_euclides", I, "alta", F["ED_E"] + "#22", "")
R("divisibilidade", "prerequisite_of", "primos", E, "alta", F["ED_R"] + "#6", "Primo(p) definido com d | p.")
R("inducao_forte", "applied_in", "primos", E, "alta", F["ED_I"] + "#11", "Todo o inteiro > 1 é produto de primos.")
R("produto_cartesiano", "prerequisite_of", "relacoes", I, "alta", F["ED_E"] + "#24", "Relações binárias como subconjuntos de A × B (ex. 132).")
R("relacoes", "prerequisite_of", "funcoes_discretas", I, "media", F["ED_E"] + "#29", "")
R("cardinalidade", "prerequisite_of", "contagem", I, "media", F["ED_E"] + "#30", "")
R("relacoes", "prerequisite_of", "grafos", I, "media", F["ED_E"] + "#36", "Ex. 236: relação de equivalência sobre vértices (componentes conexas).")
# ---- IP
R("py_io", "prerequisite_of", "py_tipos", I, "alta", IPF.format(3), "int(input()).")
R("py_tipos", "prerequisite_of", "py_operadores", I, "alta", IPF.format(4), "")
R("py_operadores", "prerequisite_of", "py_divint", I, "alta", IPF.format(7), "")
R("py_io", "prerequisite_of", "py_fstrings", I, "alta", IPF.format(2), "")
R("py_bool_ops", "prerequisite_of", "py_if", I, "alta", IPF.format(10), "")
R("py_if", "prerequisite_of", "py_while", I, "alta", IPF.format(12), "Condição do ciclo.")
R("py_while", "related_to", "py_for", I, "alta", IPF.format(13), "Duas formas de repetição.")
R("py_for", "prerequisite_of", "py_acumulador", I, "alta", IPF.format(14), "")
R("py_divint", "prerequisite_of", "py_digitos", I, "alta", IPF.format(17), "//10ⁱ e %10.")
R("py_acumulador", "prerequisite_of", "py_digitos", I, "alta", IPF.format(17), "")
R("py_def", "prerequisite_of", "py_fatorial", I, "alta", IPF.format(28), "")
R("py_acumulador", "prerequisite_of", "py_fatorial", I, "alta", IPF.format(28), "result *= i.")
R("py_divint", "prerequisite_of", "py_divisores", I, "alta", IPF.format(20), "num % i == 0.")
R("py_math", "applied_in", "py_divisores", I, "alta", IPF.format(32), "math.sqrt para o limite do ciclo.")
R("py_while", "prerequisite_of", "py_collatz", I, "alta", IPF.format(29), "")
R("py_def", "prerequisite_of", "py_strings", I, "media", IPF.format(33), "Exercícios de strings são funções.")
R("py_for", "prerequisite_of", "py_strings", I, "alta", IPF.format(37), "for i in word.")
R("py_strings", "related_to", "py_tuplos", I, "alta", IPF.format(35), "Ambos sequências indexáveis.")
R("py_strings", "prerequisite_of", "py_pesquisa", I, "alta", IPF.format(34), "")
R("py_tuplos", "prerequisite_of", "py_pesquisa", I, "alta", IPF.format(40), "")
R("py_tuplos", "prerequisite_of", "py_fibonacci", I, "alta", IPF.format(44), "FIB como tuplo.")
R("py_strings", "prerequisite_of", "py_fibonacci", I, "alta", IPF.format(43), "")
R("py_def", "prerequisite_of", "py_math", I, "baixa", IPF.format(18), "Ordem dos exercícios (ex18 usa import antes de ex23 def).")
# ---- IC
R("hardware_software", "prerequisite_of", "cpu", E, "alta", F["IC0"] + "#4", "Componentes de hardware.")
R("hardware_software", "prerequisite_of", "memoria", E, "alta", F["IC0"] + "#4", "")
R("hardware_software", "prerequisite_of", "armazenamento", E, "alta", F["IC0"] + "#4", "")
R("hardware_software", "prerequisite_of", "io_devices", E, "alta", F["IC0"] + "#4", "")
R("cpu", "prerequisite_of", "von_neumann", E, "alta", F["IC2"] + "#4", "Microprocessador que executa programas lidos da memória.")
R("memoria", "prerequisite_of", "von_neumann", E, "alta", F["IC2"] + "#4", "")
R("io_devices", "prerequisite_of", "von_neumann", E, "alta", F["IC2"] + "#4", "")
R("von_neumann", "prerequisite_of", "barramentos", E, "alta", F["IC2"] + "#8", "Barramentos implementados na placa principal.")
R("von_neumann", "prerequisite_of", "load_store", E, "alta", F["IC2"] + "#10", "")
R("von_neumann", "prerequisite_of", "harvard", E, "alta", F["IC2"] + "#10", "'Variante da arquitetura de von Neumann'.")
R("load_store", "prerequisite_of", "segmentos", E, "alta", F["IC3"] + "#10", "Dados acedidos via load/store.")
R("algoritmo", "prerequisite_of", "euclides_ic", E, "alta", F["IC1"] + "#5", "")
R("algoritmo", "prerequisite_of", "maquina_analitica", I, "media", F["IC1"] + "#9", "")
R("maquina_analitica", "followed_by", "turing", E, "media", F["IC1"] + "#19", "Ordem histórica nos slides.")
R("church_turing", "related_to", "turing", E, "alta", F["IC1"] + "#18", "Church e Turing desenvolveram um modelo geral do computável.")
R("turing", "prerequisite_of", "von_neumann", I, "media", F["IC1"] + "#37", "Ordem nos slides: Turing → ENIAC → von Neumann (stored-program).")
R("transistor", "prerequisite_of", "moore", E, "alta", F["IC1"] + "#59", "Lei de Moore conta transístores.")
R("moore", "prerequisite_of", "multicore", E, "media", F["IC1"] + "#63", "Aumento de performance via núcleos.")
R("cpu", "related_to", "multicore", I, "alta", F["IC1"] + "#63", "")
R("bit_byte", "prerequisite_of", "base_binaria", E, "alta", F["IC3"] + "#2", "'A base numérica ideal para representar um bit é a base 2'.")
R("base_binaria", "prerequisite_of", "octal_hex", E, "alta", F["IC3"] + "#18", "Compactam a informação binária.")
R("base_binaria", "prerequisite_of", "conversao_bases", E, "alta", F["IC3"] + "#23", "")
R("base_binaria", "prerequisite_of", "inteiros_sem_sinal", E, "alta", F["IC3"] + "#19", "")
R("inteiros_sem_sinal", "prerequisite_of", "inteiros_com_sinal", E, "alta", F["IC3"] + "#25", "")
R("inteiros_com_sinal", "prerequisite_of", "complemento2", E, "alta", F["IC3"] + "#26", "")
R("complemento2", "prerequisite_of", "extensao_sinal", E, "alta", F["IC3"] + "#31", "")
R("base_binaria", "prerequisite_of", "adicao_binaria", E, "alta", F["IC3"] + "#16", "")
R("complemento2", "prerequisite_of", "adicao_binaria", E, "alta", F["IC3"] + "#36", "Adição binária em complemento para 2.")
R("adicao_binaria", "prerequisite_of", "overflow", E, "alta", F["IC3"] + "#37", "")
R("complemento2", "related_to", "overflow", E, "alta", F["IC3"] + "#38", "Deteção pelo bit de sinal.")
R("inteiros_sem_sinal", "related_to", "overflow", E, "alta", F["IC3"] + "#40", "Overflow também sem sinal (2 + 3 com 2 bits).")
R("base_binaria", "prerequisite_of", "notacao_cientifica", E, "alta", F["IC3"] + "#44", "")
R("notacao_cientifica", "prerequisite_of", "virgula_flutuante", E, "alta", F["IC3"] + "#45", "")
R("virgula_flutuante", "prerequisite_of", "ieee754", E, "alta", F["IC3"] + "#46", "")
R("ieee754", "prerequisite_of", "adicao_vf", E, "alta", F["IC3"] + "#54", "")
R("bit_byte", "prerequisite_of", "texto_ascii", E, "alta", F["IC3"] + "#56", "Cada carácter tem uma sequência única de bits.")
R("inteiros_sem_sinal", "prerequisite_of", "texto_ascii", E, "media", F["IC3"] + "#13", "'As letras do alfabeto também são representadas por números inteiros'.")
R("bit_byte", "prerequisite_of", "interpretacao_contexto", E, "alta", F["IC3"] + "#5", "")
R("interpretacao_contexto", "related_to", "segmentos", E, "alta", F["IC3"] + "#9", "")
R("load_store", "related_to", "interpretacao_contexto", E, "alta", F["IC3"] + "#14", "Dados em registos interpretados pela instrução.")
R("sh_navegacao", "prerequisite_of", "sh_ficheiros", E, "media", F["F1"] + "#1", "Ordem dos exercícios da Folha 1.")
R("sh_ficheiros", "prerequisite_of", "sh_permissoes", E, "media", F["F1"] + "#2", "")
R("sh_ficheiros", "prerequisite_of", "sh_glob", E, "media", F["F2"] + "#1", "")
R("sh_ficheiros", "prerequisite_of", "sh_pipes", E, "media", F["F2"] + "#1", "")
R("sh_pipes", "prerequisite_of", "sh_filtros", E, "alta", F["F2"] + "#2", "Linhas de comando que combinam filtros.")
R("sh_filtros", "prerequisite_of", "regex", E, "alta", F["F2"] + "#3", "grep com expressão regular.")
R("sh_glob", "related_to", "regex", I, "media", F["F2"] + "#3", "Ambos são linguagens de padrões.")
R("sh_processos", "related_to", "segmentos", I, "baixa", F["IC3"] + "#10", "Processo = programa em execução com espaço de endereçamento.")
# ---- Horizonte (todas inferidas)
R("taylor1", "prerequisite_of", "hz_serie_taylor", I, "alta", F["STEW"], "Stewart 11.11 'Applications of Taylor Polynomials'; Taylor de 1.ª ordem é o primeiro termo.")
R("serie", "prerequisite_of", "hz_serie_taylor", I, "alta", F["STEW"], "Stewart 11.8 Power Series no mesmo capítulo das séries.")
R("criterio_razao", "prerequisite_of", "hz_serie_taylor", I, "media", F["STEW"], "Raio de convergência (Stewart 11.8) — inferido; apenas índice lido.")
R("primitiva", "prerequisite_of", "hz_integral", I, "alta", F["STEW"], "Stewart 4.9 Antiderivatives → cap. 5 Integrals.")
R("limite_funcao", "prerequisite_of", "hz_integral", I, "media", F["STEW"], "Stewart 5.1 Areas and Distances (limites de somas) — inferido.")
R("derivada", "prerequisite_of", "hz_derivadas_parciais", I, "alta", F["STEW"], "Stewart 14.3 Partial Derivatives generaliza a derivada.")
R("regra_cadeia", "prerequisite_of", "hz_derivadas_parciais", I, "media", F["STEW"], "Stewart 14.5 The Chain Rule (várias variáveis).")
R("taylor1", "related_to", "hz_derivadas_parciais", I, "media", F["STEW"], "Stewart 14.4 'Tangent Planes and Linear Approximations'.")
R("hz_derivadas_parciais", "prerequisite_of", "hz_gradiente", I, "alta", F["STEW"], "Ordem do capítulo 14.")
R("produto_interno", "prerequisite_of", "hz_gradiente", I, "media", F["STEW"], "Derivada direcional como produto interno com o gradiente (Stewart 14.6; conteúdo não lido, só o título).")
R("vetores_rn", "prerequisite_of", "hz_gradiente", I, "media", F["STEW"], "'Gradient Vector'.")
R("extremos", "prerequisite_of", "hz_otimizacao", I, "alta", F["STEW"], "Stewart 4.1 Maximum and Minimum Values → 4.7 Optimization → 14.7.")
R("hz_gradiente", "prerequisite_of", "hz_otimizacao", I, "media", F["STEW"], "14.6 precede 14.7–14.8.")
R("produto_interno", "related_to", "hz_vetores_stewart", I, "alta", F["STEW"], "12.3 The Dot Product.")
R("produto_vetorial", "related_to", "hz_vetores_stewart", I, "alta", F["STEW"], "12.4 The Cross Product.")
R("eq_cartesiana", "related_to", "hz_vetores_stewart", I, "alta", F["STEW"], "12.5 Equations of Lines and Planes.")
R("derivada", "prerequisite_of", "hz_edo", I, "media", F["STEW"], "Equações diferenciais envolvem derivadas.")
R("newton", "related_to", "hz_edo", I, "baixa", F["STEW"], "Ambos métodos numéricos iterativos (Euler) — semelhança estrutural.")
R("hz_bigdata", "related_to", "hz_ia", E, "alta", F["IC0"] + "#26", "Slides consecutivos: Big Data → IA extrai conhecimento de grandes volumes de dados.")
R("multicore", "related_to", "hz_redes_neuronais", E, "alta", F["IC1"] + "#64", "Unidades de processamento diferenciadas incluem IA.")
R("hz_redes_neuronais", "related_to", "hz_ia", I, "media", F["IC0"] + "#27", "Deep Learning ≈ redes neuronais (inferido).")
R("bit_byte", "related_to", "hz_bigdata", I, "baixa", F["IC0"] + "#26", "Unidades de medida (até YottaByte) e volumes de dados.")

# =============================================================================
# LIGAÇÕES ENTRE UCs (todas cuidadosamente justificadas)
# =============================================================================
R("quantificadores", "prerequisite_of", "limite_eps_n", I, "alta", F["CAL_R"] + "#2 + " + F["ED_R"] + "#6", "A definição ∀ε>0 ∃N … é uma fórmula de LPO com quantificadores encadeados.")
R("ordem_quant", "prerequisite_of", "limite_eps_n", I, "alta", F["ED_R"] + "#6", "N depende de ε (∀ε∃N ≠ ∃N∀ε) — exatamente o aviso 'A ordem importa!' de ED.")
R("negacao_quant", "applied_in", "subsucessoes", I, "media", F["CAL_R"] + "#3", "Provar divergência = negar ∀ε∃N…; feito via subsucessões com limites diferentes.")
R("implicacao", "prerequisite_of", "limite_eps_n", I, "alta", F["CAL_R"] + "#2", "m > N ⇒ |aₘ − L| < ε.")
R("quantificadores", "prerequisite_of", "limite_funcao", I, "alta", F["CAL_R"] + "#6", "∀ε ∃δ: …")
R("prova_direta", "applied_in", "prop_limites", I, "media", F["CAL_R"] + "#2", "As provas das propriedades são demonstrações diretas a partir da definição.")
R("soma_geometrica", "related_to", "serie_geometrica", I, "alta", F["ED_R"] + "#11 + " + F["CAL_R"] + "#4", "Mesma fórmula: ED prova Σrⁱ = (rⁿ⁺¹−1)/(r−1) por indução; Cálculo deriva Sₘ = a(1−xᵐ)/(1−x) e passa ao limite.")
R("inducao", "applied_in", "serie_geometrica", I, "media", F["ED_R"] + "#11", "A fórmula das somas parciais pode ser provada por indução (feito em ED).")
R("norma", "related_to", "desig_triangular", I, "media", F["ALGA_R"] + "#2 + " + F["CAL_R"] + "#2", "|aₘ − L| e d(u,v) = ‖u − v‖ são ambas distâncias; a desigualdade triangular vale para normas (não provado em ALGA).")
R("produto_cartesiano", "prerequisite_of", "vetores_rn", I, "media", F["ED_C"] + "#16 + " + F["ALGA_R"] + "#2", "Rⁿ = R × … × R; vetores são n-tuplos ordenados.")
R("conjunto", "related_to", "classif_sist", I, "media", F["ALGA_R"] + "#4", "Conjunto solução C.S. = {(4,3,0) + z(3,−2,1) : z ∈ R} escrito em compreensão.")
R("prova_contradicao", "related_to", "inversa", I, "baixa", F["ALGA_R"] + "#10", "V/F com matrizes: mostrar falsidade com contra-exemplo 2×2 (técnica comum a ED).")
R("provas_conjuntos", "related_to", "produto_matrizes", I, "media", F["ALGA_R"] + "#10 + " + F["ED_R"] + "#9", "Ambas as UCs ensinam a refutar com contra-exemplos pequenos (matrizes 2×2 / conjuntos ∅, {1}).")
R("inducao", "related_to", "det_def", I, "media", F["ALGA_S3"] + "#3", "Existência da função determinante mostrada por indução na ordem n (Laplace define det de ordem n a partir de n−1).")
R("bit_byte", "related_to", "proposicao", I, "alta", F["IC3"] + "#2 + " + F["ED_R"] + "#3", "Um bit pode ser um valor booleano (v/f); ED usa v/f, 1/0.")
R("cpu", "related_to", "conectivas", I, "media", F["IC0"] + "#8", "A UAL executa operações aritméticas e lógicas.")
R("algebra_conjuntos", "related_to", "bit_byte", I, "baixa", F["ED_C"] + "#17", "Álgebra booleana (ED) ↔ valores booleanos dos bits (IC).")
R("church_turing", "related_to", "formalizacao", I, "baixa", F["IC1"] + "#16", "Gödel: sistemas formais e expressões que não conseguem representar — ligação à lógica formal.")
R("algoritmo", "prerequisite_of", "gauss", I, "baixa", F["ALGA_S1"] + "#8", "Gauss é apresentado como algoritmo (pseudo-código nos slides 1.3).")
R("euclides_ic", "related_to", "mdc_euclides", E, "alta", F["IC1"] + "#5 + " + F["ED_E"] + "#22", "O mesmo algoritmo aparece na história (IC) e nos exercícios de teoria de números (ED, ex. 107).")
R("algoritmo", "prerequisite_of", "py_def", I, "media", F["IC1"] + "#2", "Programas implementam algoritmos ('software: instruções passo-a-passo').")
R("hardware_software", "related_to", "py_io", I, "baixa", F["IC0"] + "#5", "Dispositivos de entrada/saída ↔ input/print.")
R("py_divisores", "related_to", "primos", I, "alta", IPF.format(32) + " + " + F["ED_E"] + "#23", "factorize(n) calcula a factorização em primos (ED ex. 121; existência provada por indução forte).")
R("py_divisores", "related_to", "divisibilidade", I, "alta", IPF.format(20), "num % i == 0 testa i | num.")
R("py_divint", "related_to", "divisibilidade", I, "alta", IPF.format(12), "x % n == 0 ⇔ n | x.")
R("py_fatorial", "related_to", "inducao", I, "media", IPF.format(28) + " + " + F["ED_E"] + "#17", "Exercícios de indução com n! (ED 67–71).")
R("py_fibonacci", "related_to", "recorrencia", I, "alta", IPF.format(44) + " + " + F["ED_E"] + "#18", "Sequência de Fibonacci definida por recorrência em ED.")
R("py_collatz", "related_to", "sucessao", I, "media", IPF.format(29), "Collatz gera uma sucessão definida por recorrência.")
R("py_collatz", "related_to", "recorrencia", I, "media", IPF.format(29), "")
R("py_bool_ops", "related_to", "conectivas", I, "alta", IPF.format(10), "and / or / not ↔ ∧ / ∨ / ¬.")
R("py_if", "related_to", "implicacao", I, "baixa", IPF.format(8), "if P: Q tem a estrutura 'se P então Q' (semântica diferente).")
R("py_digitos", "related_to", "base_binaria", I, "media", IPF.format(17) + " + " + F["IC3"] + "#22", "Notação posicional: n = Σ dᵢ·10ⁱ, extraído com //10ⁱ — a mesma expansão usada em base 2 em IC.")
R("py_tipos", "related_to", "virgula_flutuante", I, "media", IPF.format(3) + " + " + F["IC3"] + "#45", "float em Python é vírgula flutuante (IEEE 754 de precisão dupla — não confirmado nos materiais de IP).")
R("py_tipos", "related_to", "inteiros_com_sinal", I, "baixa", F["IC3"] + "#25", "int representa inteiros com sinal.")
R("py_strings", "related_to", "texto_ascii", I, "media", F["IC3"] + "#56", "Strings são sequências de caracteres codificados (ASCII/Unicode).")
R("sh_filtros", "related_to", "py_pesquisa", I, "baixa", F["F2"] + "#2", "Pesquisa de padrões em texto (grep ↔ substring).")
R("newton", "related_to", "algoritmo", I, "media", cad("cal", 11) + "#6", "Método de Newton descrito em passos (1.º, 2.º, …).")
R("gauss", "related_to", "algoritmo", E, "alta", F["ALGA_S1"] + "#7", "Slides: 'Algoritmo para obter a forma reduzida'.")
R("alg_fn", "related_to", "algoritmo", E, "alta", F["ED_R"] + "#5", "'Prova (algoritmo)'.")
R("inducao", "related_to", "recorrencia", E, "alta", F["ED_I"] + "#15", "")
R("interpolacao", "related_to", "taylor1", I, "baixa", F["ALGA_R"] + "#4", "Ambos aproximam/descrevem funções por polinómios.")
R("produto_interno", "related_to", "produto_matrizes", E, "alta", F["ALGA_R"] + "#5", "(linha i de A)·(coluna j de B).")

# =============================================================================
# EXERCÍCIOS RESOLVIDOS NOS CADERNOS (Cálculo, ED, ALGA): (uc, rótulo, ficheiro, página, [conceitos testados], [secundários], dificuldade)
# =============================================================================
SOLVED = [
    ("cal", "Stewart 11.1 ex. 26", cad("cal", 1), 2, ["serie_geometrica", "limite_eps_n"], [], 2),
    ("cal", "Stewart 11.1 ex. 24", cad("cal", 1), 2, ["limite_eps_n"], ["prop_limites"], 2),
    ("cal", "Limite pela definição (3m−7,1)/(4m−10,3)", cad("cal", 2), 3, ["limite_eps_n"], [], 4),
    ("cal", "Stewart 11.2 ex. 26, 38", cad("cal", 4), 2, ["serie_geometrica"], [], 2),
    ("cal", "Stewart 11.2 ex. 59 (intervalo de convergência)", cad("cal", 4), 2, ["serie_geometrica"], [], 3),
    ("cal", "Stewart 11.2 ex. 62 (sen x / 3)", cad("cal", 4), 2, ["serie_geometrica"], ["funcao"], 3),
    ("cal", "Stewart 11.2 ex. 44, 46 (telescópicas)", cad("cal", 4), 3, ["serie_telescopica"], ["termo_geral"], 2),
    ("cal", "Stewart 11.4 ex. 1a, 3, 4, 9", cad("cal", 4), 5, ["criterio_comparacao"], ["p_series", "harmonica"], 3),
    ("cal", "Stewart 11.4 ex. 10, 25", cad("cal", 4), 6, ["comparacao_limite"], ["criterio_comparacao"], 3),
    ("cal", "Stewart 11.5 ex. 5, 7, 17, 35", cad("cal", 8), 2, ["series_alternadas"], ["termo_geral", "lim_continua"], 3),
    ("cal", "Σ sen(m)cos(m)/3ᵐ (convergência absoluta)", cad("cal", 8), 4, ["conv_absoluta"], ["criterio_comparacao", "serie_geometrica"], 3),
    ("cal", "Stewart 11.6 ex. 7, 10 (razão)", cad("cal", 8), 4, ["criterio_razao"], ["conv_absoluta"], 3),
    ("cal", "Stewart 11.6 ex. 25, 27 (raiz)", cad("cal", 8), 5, ["criterio_raiz"], ["conv_absoluta"], 3),
    ("cal", "Derivada de x² − 8x + 9 pela definição", cad("cal", 11), 2, ["derivada"], ["limite_funcao"], 2),
    ("cal", "Stewart 3.4 ex. 3, 11, 12, 30, 35, 61", cad("cal", 11), 5, ["regra_cadeia"], ["derivadas_elementares"], 3),
    ("cal", "Stewart 4.8 ex. 3, 4, 6, 7, 8", cad("cal", 12), 2, ["newton"], ["derivadas_elementares"], 3),
    ("cal", "Stewart 4.8 ex. 11, 15, 33", cad("cal", 12), 3, ["newton"], ["bolzano", "sucessao"], 4),
    ("ed", "ED ex. 1, 2, 3 (valores lógicos)", cad("ed", 1), 2, ["tabela_verdade", "conectivas"], ["tautologia"], 1),
    ("ed", "ED ex. 4, 6 (equivalências)", cad("ed", 1), 3, ["equivalencia_logica"], ["leis_equivalencia", "implicacao"], 2),
    ("ed", "ED ex. 7, 9, 14", cad("ed", 1), 4, ["equivalencia_logica"], ["leis_equivalencia"], 2),
    ("ed", "ED ex. 13 (tautologia/contradição)", cad("ed", 1), 5, ["tautologia"], ["tabela_verdade"], 2),
    ("ed", "ED ex. 11, 12 (FND/FNC)", cad("ed", 2), 2, ["fnd", "fnc"], ["alg_fn", "decisao_fn"], 3),
    ("ed", "ED ex. 15, 16 (inferência)", cad("ed", 2), 3, ["prova_formal"], ["modus_ponens", "modus_tollens", "de_morgan"], 3),
    ("ed", "ED ex. 23, 24 (quantificadores)", cad("ed", 2), 4, ["quantificadores"], ["predicados"], 2),
    ("ed", "ED ex. 25, 26, 27 (negação e formalização)", cad("ed", 2), 5, ["negacao_quant", "formalizacao"], ["quantificadores"], 3),
    ("ed", "Indução: Σi, 3ⁿ ímpar, Σrⁱ", cad("ed", 3), 2, ["inducao"], ["soma_geometrica"], 2),
    ("ed", "ED ex. 30, 31, 33, 34, 35 (conjuntos)", cad("ed", 5), 2, ["op_conjuntos", "partes"], ["subconjunto"], 2),
    ("ed", "ED ex. 36, 47, 53 (provas)", cad("ed", 5), 3, ["provas_conjuntos"], ["subconjunto", "partes"], 3),
    ("ed", "ED ex. 61, 63 (indução)", cad("ed", 6), 2, ["inducao"], [], 3),
    ("ed", "ED ex. 64, 65 (indução)", cad("ed", 6), 3, ["inducao"], ["cardinalidade"], 3),
    ("alga", "ALGA ex. 1.1 (retas)", cad("alga", 1), 2, ["eq_cartesiana", "eq_vetorial"], ["ortogonalidade"], 2),
    ("alga", "ALGA ex. 1.2 (planos)", cad("alga", 1), 3, ["eq_cartesiana"], ["produto_interno", "ortogonalidade"], 2),
    ("alga", "ALGA ex. 1.3 (equação vetorial)", cad("alga", 1), 4, ["eq_vetorial"], ["eq_cartesiana"], 2),
    ("alga", "ALGA ex. 1.5 (interseção de planos)", cad("alga", 1), 5, ["gauss"], ["eq_cartesiana", "classif_sist"], 2),
    ("alga", "ALGA ex. 1.7 (Gauss)", cad("alga", 2), 2, ["gauss"], ["matriz_ampliada", "classif_sist"], 3),
    ("alga", "ALGA ex. 1.8 (homogéneos)", cad("alga", 2), 3, ["discussao_sist"], ["caracteristica", "sist_homogeneo"], 3),
    ("alga", "ALGA ex. 1.9 (reta ∩ plano)", cad("alga", 2), 4, ["gauss"], ["eq_cartesiana"], 3),
    ("alga", "ALGA ex. 1.17 (interpolação)", cad("alga", 2), 5, ["interpolacao"], ["gauss"], 3),
    ("alga", "Sistema com parâmetros a, b", cad("alga", 3), 2, ["sist_parametros"], ["caracteristica", "discussao_sist"], 4),
    ("alga", "Propriedades do produto e da inversa", cad("alga", 3), 3, ["produto_matrizes", "inversa"], ["op_matrizes"], 3),
    ("alga", "Inversa 3×3 por Gauss-Jordan", cad("alga", 4), 2, ["inversa_gj"], ["gauss_jordan"], 3),
    ("alga", "ALGA ex. 2.7 (inversa 2×2 e AX = B)", cad("alga", 5), 2, ["inversa_2x2", "forma_matricial"], ["inversa"], 2),
    ("alga", "ALGA ex. 2.11, 2.12 (inversas)", cad("alga", 5), 2, ["inversa_gj"], ["gauss_jordan"], 3),
]

# Resolução de cada ex*.py de IP: (n, [conceitos principais], [secundários], descrição curta)
IP_EX = {
    1: (["py_io"], [], "Hello there"), 2: (["py_io", "py_fstrings"], [], "Nome com f-string"),
    3: (["py_tipos"], ["py_operadores"], "Média T/N com round"), 4: (["py_operadores"], ["py_tipos"], "Área do círculo"),
    5: (["py_operadores", "py_fstrings"], [], "Dias → horas/minutos/segundos"), 6: (["py_operadores"], ["py_tipos"], "Velocidade média"),
    7: (["py_divint"], ["py_fstrings"], "Somar tempos (// e %)"), 8: (["py_if"], [], "Valor absoluto"),
    9: (["py_if"], ["py_bool_ops"], "Máximo de três"), 10: (["py_if", "py_bool_ops"], [], "Escalões de nota"),
    11: (["py_if"], ["py_operadores"], "Preço com descontos"), 12: (["py_while", "py_divint"], ["py_if"], "FizzBuzz"),
    13: (["py_for", "py_divint"], ["py_strings"], "Múltiplos num intervalo"), 14: (["py_for", "py_acumulador"], ["py_divint"], "Contar pares/ímpares"),
    15: (["py_for"], ["py_strings"], "Desenhar quadrado"), 16: (["py_acumulador", "py_for"], [], "Maior sequência igual"),
    17: (["py_digitos"], ["py_divint"], "Soma de dígitos"), 18: (["py_if", "py_math"], [], "Diâmetro/perímetro/área"),
    19: (["py_if", "py_math"], ["py_operadores"], "Equação do 2.º grau (raízes complexas)"), 20: (["py_divisores"], ["py_for"], "Número perfeito"),
    21: (["py_for"], ["py_strings"], "Pirâmide de #"), 22: (["py_digitos"], ["py_while", "py_if"], "Increasing / decreasing / mountain / chaotic"),
    23: (["py_def"], [], "sum(a, b)"), 24: (["py_def"], ["py_operadores"], "Celsius → Fahrenheit"),
    25: (["py_def"], ["py_operadores"], "max/min/soma"), 26: (["py_def", "py_acumulador"], ["py_for"], "Soma dos ímpares"),
    27: (["py_def", "py_if"], ["py_divint"], "Ano bissexto"), 28: (["py_fatorial"], ["py_def"], "Fatorial"),
    29: (["py_collatz"], ["py_while"], "Collatz"), 30: (["py_digitos"], ["py_def", "py_strings"], "Maior sequência crescente de dígitos"),
    31: (["py_digitos"], ["py_math", "py_while"], "Média de dígitos"), 32: (["py_divisores"], ["py_math", "py_while"], "Factorização em primos"),
    33: (["py_strings", "py_tuplos"], [], "Primeira/última letra e meio"), 34: (["py_pesquisa"], ["py_strings"], "Palíndromo"),
    35: (["py_tuplos"], ["py_for"], "Posições ímpares/pares"), 36: (["py_tuplos"], ["py_for"], "Duplicar elementos"),
    37: (["py_strings"], ["py_for"], "Remover carácter"), 38: (["py_strings", "py_acumulador"], [], "Menor/maior comprimento"),
    39: (["py_strings"], ["py_acumulador"], "Contar letras"), 40: (["py_pesquisa"], ["py_tuplos"], "Primeira e última ocorrência"),
    41: (["py_pesquisa"], ["py_strings"], "Subsequência"), 42: (["py_strings"], ["py_for"], "Trocar pares de letras"),
    43: (["py_fibonacci"], ["py_strings"], "Evolução A→AB, B→A"), 44: (["py_fibonacci"], ["py_tuplos", "py_while"], "Letra na posição n"),
}

# Exercícios das fichas com texto extraído: mapeamento por palavras-chave (aplicado no build)
SHEET_RULES = {
    # ficheiro: [(regex no enunciado, conceito)]
    F["ALGA_E1"]: [(r"reta|plano", "eq_cartesiana"), (r"vetorial", "eq_vetorial"), (r"interse", "classif_sist"), (r"alargad|ampliad", "matriz_ampliada"),
                   (r"Gauss", "gauss"), (r"homog", "sist_homogeneo"), (r"par[âa]metr", "sist_parametros"), (r"polin[óo]mio|curva", "interpolacao"), (r"discut|classifiq|par\s*\(", "discussao_sist"), (r"afirma[çc]", "classif_sist"), (r"idade|custo|pre[çc]o", "eq_linear")],
    F["ALGA_E2"]: [(r"produto|AB|BA", "produto_matrizes"), (r"invers|invert", "inversa"), (r"transpost", "op_matrizes"), (r"sim[ée]tric|diagonal|triangular", "matriz"),
                   (r"elementar", "mat_elementares"), (r"AX\s*=\s*B|sistema", "forma_matricial"), (r"A\s*2|B\s*2|pot[êe]ncia|quadrad", "produto_matrizes")],
    F["F1"]: [(r"pwd|cd\b|mkdir|tree|history", "sh_navegacao"), (r"\bcp\b|\brm\b|cat\b|diff|tar\b|copi|apague|mova", "sh_ficheiros"), (r"chmod|permiss", "sh_permissoes"), (r"diret[óo]rio", "sh_navegacao"), (r"emacs|editor", "sh_ficheiros")],
    F["F2"]: [(r"\bps\b|jobs|kill", "sh_processos"), (r"glob", "sh_glob"), (r"redirecion|sa[ií]da\s+padr|entrada\s+padr", "sh_pipes"),
              (r"grep|sort|sed|find|campos|linha\s+de\s+comando", "sh_filtros"), (r"express[ãa]o\s+regular", "regex")],
    F["F3"]: [(r"CPU|GPU|mem[óo]ria|RAM|ROM", "memoria"), (r"motherboard|chipset|northbridge", "barramentos"), (r"transistor|circuito", "transistor"), (r"HDD|SSD", "armazenamento")],
    F["F4"]: [(r"bin[áa]rio|base\s+2", "base_binaria"), (r"octal|hexadecimal", "octal_hex"), (r"sem\s+sinal", "inteiros_sem_sinal"), (r"converta|converter|representa[çc][ãa]o\s+(decimal|em\s+bin)", "conversao_bases"),
              (r"overflow", "overflow"), (r"adi[çc][õo]es|soma|\+", "adicao_binaria"), (r"8\s+bits", "inteiros_sem_sinal")],
    F["ED_E"]: [(r"tabela|valor\s+l[óo]gico|valores\s+l[óo]gicos|frase\s+em\s+Portugu", "tabela_verdade"), (r"equivalent", "equivalencia_logica"), (r"tautologia|contradi|satisfaz", "tautologia"),
                (r"normal\s+(conjuntiva|disjuntiva)", "fnd"), (r"regras?\s+de\s+infer|argumento|conclus", "prova_formal"), (r"∀|∃|8x|9y|quantific|universo", "quantificadores"),
                (r"nega", "negacao_quant"), (r"[Ff]ormule|formaliz|f[óo]rmula\s+(matem|da\s+l[óo]gica)", "formalizacao"), (r"conjunto|A\s*\[|A\s*\\", "op_conjuntos"),
                (r"partes|2A|P\(A\)", "partes"), (r"[Pp]rove|[Mm]ostre", "provas_conjuntos"), (r"cardinal|\|A\|", "cardinalidade"), (r"indu", "inducao"), (r"Hanoi|Fibonacci|recorr", "recorrencia"),
                (r"mdc|Euclides", "mdc_euclides"), (r"primo", "primos"), (r"\||divis", "divisibilidade"), (r"rela[çc]", "relacoes"), (r"parti[çc]", "relacoes"), (r"injectiva|sobrejectiva|fun[çc][ãa]o", "funcoes_discretas"),
                (r"[Qq]uant[ao]s|maneiras", "contagem"), (r"grafo|v[ée]rtice", "grafos")],
}
