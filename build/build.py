# -*- coding: utf-8 -*-
"""
IACD Knowledge Graph — pipeline de construção.

Uso:
    python build/build.py                # usa a pasta-mãe do projeto como raiz dos materiais
    python build/build.py --root "<pasta 1º Semestre>"

Passos:
  1. inventário de todos os ficheiros da pasta de materiais;
  2. extração de texto dos PDFs (pdftotext ou pypdf), com cache em build/pdf_text.json;
  3. leitura da base curada (build/knowledge.py);
  4. localização automática das páginas de cada conceito (palavras-chave);
  5. extração e classificação dos exercícios das fichas;
  6. métricas (PageRank, dependentes, intermediação, pontes), bottlenecks e roadmap;
  7. layout (posições do mapa e do roadmap);
  8. exportação: data/kg.json, data/kg.js, data/csv/*.csv, data/kg.sqlite, data/rag_chunks.jsonl;
  9. relatório de qualidade: data/quality_report.md.
Só usa a biblioteca padrão do Python (+ pdftotext/pypdf opcionais para texto novo).
"""
import argparse, csv, json, math, os, re, shutil, sqlite3, subprocess, sys, unicodedata
from collections import defaultdict, deque, Counter
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import knowledge as K  # noqa: E402

PROJECT_DIRNAME = os.path.basename(PROJECT)


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


# ---------------------------------------------------------------------------- 1. inventário
def inventory(root):
    files = []
    for dp, dn, fn in os.walk(root):
        rel_dir = os.path.relpath(dp, root)
        parts = [] if rel_dir == "." else rel_dir.split(os.sep)
        if parts and (parts[0] == PROJECT_DIRNAME or parts[0].startswith(".")):
            dn[:] = []
            continue
        if any(p.startswith(".") for p in parts):
            continue
        dn[:] = [d for d in dn if not d.startswith(".") and d != PROJECT_DIRNAME]
        for f in fn:
            if f.startswith(".") or f.lower().endswith(".lnk"):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            st = os.stat(p)
            files.append(dict(path=rel, size=st.st_size, mtime=int(st.st_mtime), ext=os.path.splitext(f)[1].lower().lstrip(".")))
    files.sort(key=lambda x: x["path"])
    return files


# ---------------------------------------------------------------------------- 2. texto
def extract_pdf(path, max_pages=None):
    try:
        info = subprocess.run(["pdfinfo", path], capture_output=True, text=True, timeout=60).stdout
        n = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        last = min(n, max_pages) if max_pages else n
        txt = subprocess.run(["pdftotext", "-f", "1", "-l", str(last), path, "-"], capture_output=True, text=True, timeout=300).stdout
        return n, txt.split("\f")[:last]
    except Exception:
        pass
    try:
        from pypdf import PdfReader
        r = PdfReader(path)
        n = len(r.pages)
        last = min(n, max_pages) if max_pages else n
        return n, [(r.pages[i].extract_text() or "") for i in range(last)]
    except Exception as e:
        print("  ! não foi possível extrair", path, e)
        return 0, []


def load_texts(root, files):
    cache_path = os.path.join(HERE, "pdf_text.json")
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
    changed = False
    out = {}
    for f in files:
        if f["ext"] != "pdf":
            continue
        c = cache.get(f["path"])
        full = os.path.join(root, f["path"])
        if c and (c.get("size") in (None, f["size"])) and c.get("text") is not None:
            out[f["path"]] = c
            continue
        if not os.path.exists(full) or f["size"] == 0:
            continue
        big = f["size"] > 20_000_000 and "Stewart" in f["path"]
        n, pages = extract_pdf(full, 25 if big else None)
        out[f["path"]] = dict(pages=n, extracted_pages=len(pages), text=pages, size=f["size"])
        cache[f["path"]] = out[f["path"]]
        changed = True
        print("  texto extraído:", f["path"], n, "páginas")
    if changed:
        json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
    return out


# ---------------------------------------------------------------------------- utilidades
def file_kind(path):
    base = os.path.basename(path)
    low = base.lower()
    if re.match(r"^(CAL|ED|ALGA) \d+\.pdf$", base):
        return "caderno"
    if low.startswith("resumo"):
        return "resumo"
    if "stewart" in low:
        return "livro"
    if low.endswith(".py"):
        return "codigo"
    if re.match(r"^f\d+\.pdf$", low) or "exerc" in low:
        return "ficha"
    if low.endswith(".json"):
        return "config"
    return "slides"


KIND_LABEL = dict(caderno="Caderno (apontamentos manuscritos)", resumo="Resumo (apontamentos organizados)", livro="Livro de referência",
                  codigo="Código (resolução)", ficha="Ficha de exercícios", slides="Slides do professor", config="Configuração")


def uc_of_path(path):
    top = path.split("/")[0]
    for u in K.UCS:
        if u["folder"] and u["folder"] == top:
            return u["id"]
    return None


# ---------------------------------------------------------------------------- 3–5 construção
def build(root):
    t0 = datetime.now()
    files = inventory(root)
    print(f"Inventário: {len(files)} ficheiros")
    texts = load_texts(root, files)
    fset = {f["path"]: f for f in files}

    nodes, edges = {}, []
    issues = defaultdict(list)

    def add_node(n):
        if n["id"] in nodes:
            issues["ids_duplicados"].append(n["id"])
        nodes[n["id"]] = n
        return n

    def add_edge(s, t, typ, nature="explicita", conf="alta", evidence="", just="", **kw):
        e = dict(id=f"e{len(edges)}", source=s, target=t, type=typ, nature=nature, confidence=conf, evidence=evidence, justification=just)
        e.update(kw)
        edges.append(e)
        return e

    ucmap = {u["id"]: u for u in K.UCS}
    add_node(dict(id="iacd", type="root", label=K.ROOT["name"], desc=K.ROOT["full"], uc=None))
    for i, u in enumerate(K.UCS):
        add_node(dict(id=u["id"], type="uc", label=u["name"], short=u["short"], code=u["code"], desc=u["desc"], uc=u["id"], hue=u["hue"],
                      folder=u["folder"], horizon=bool(u.get("horizon")), order=i, status="horizonte" if u.get("horizon") else "lecionado"))
        add_edge("iacd", u["id"], "contains", "explicita", "alta", u["folder"] or "—", "Estrutura de pastas do semestre." if u["folder"] else "Agrupamento de material de referência.")
    tema_order = defaultdict(int)
    for tid, uc, name, desc, status in K.TEMAS:
        tema_order[uc] += 1
        add_node(dict(id=tid, type="tema", label=name, desc=desc, uc=uc, status=status, order=tema_order[uc]))
        add_edge(uc, tid, "contains", "explicita" if status != "horizonte" else "inferida", "alta", "", "Tema identificado nos índices dos resumos/slides." if uc != "ip" else "Tema inferido a partir do código (sem enunciados na pasta).")
    # temas: followed_by na ordem dos índices
    by_uc = defaultdict(list)
    for tid, uc, *_ in K.TEMAS:
        by_uc[uc].append(tid)
    order_src = dict(alga=K.F["ALGA_R"] + "#1", cal=K.F["CAL_R"] + "#1", ed=K.F["ED_R"] + "#1", ic="Introdução aos Computadores (00→03, f01→f04)", ip="Introdução à Programação (ex1→ex44)")
    for uc, ts in by_uc.items():
        if uc == "hz":
            continue
        for a, b in zip(ts, ts[1:]):
            if nodes[b]["status"] == "programado" and nodes[a]["status"] == "programado":
                ev, nat = K.F["ED_L"] + "#4", "explicita"
            else:
                ev, nat = order_src.get(uc, ""), "explicita" if uc in ("alga", "cal", "ed") else "inferida"
            add_edge(a, b, "followed_by", nat, "alta" if nat == "explicita" else "media", ev, "Ordem do índice/programa (não implica dependência conceptual).")

    # conceitos
    concept_ids = set()
    for c in K.CONCEPTS:
        st = c["status"] or ("horizonte" if c["uc"] == "hz" else "lecionado")
        if c["tema"] and nodes.get(c["tema"], {}).get("status") == "programado":
            st = "programado"
        n = dict(id=c["id"], type=c["type"], label=c["name"], uc=c["uc"], tema=c["tema"], desc=c["desc"], formula=c["formula"],
                 aliases=c["aliases"], status=st, kw=c["kw"],
                 difficulty=(c["diff"] or (None, ""))[0], difficulty_why=(c["diff"] or (None, ""))[1],
                 sources=[])
        for s in c["src"]:
            n["sources"].append(dict(file=s["file"], page=s["page"], note=s["note"], verified=True, kind=file_kind(s["file"])))
        add_node(n)
        concept_ids.add(c["id"])
        add_edge(c["tema"], c["id"], "contains", "explicita" if c["uc"] not in ("ip", "hz") else "inferida", "alta", "", "")

    # ---------------------------------------------------- localização automática de páginas (palavras-chave)
    page_hits = defaultdict(lambda: defaultdict(int))  # concept -> (file,page) -> hits
    for v in texts.values():
        v["text"] = [unicodedata.normalize("NFC", t) for t in v["text"]]
    file_pages_text = {p: v["text"] for p, v in texts.items()}
    for c in K.CONCEPTS:
        if not c["kw"]:
            continue
        rx = [re.compile(k, re.I if not re.search(r"[A-Z]{2,}", k) else 0) for k in c["kw"]]
        scope = []
        for p in file_pages_text:
            uc = uc_of_path(p)
            if c["uc"] == "hz":
                if "Stewart" in p or p.startswith("Introdução aos Computadores/0"):
                    scope.append(p)
            elif uc == c["uc"] and "Stewart" not in p:
                scope.append(p)
        for p in scope:
            for i, t in enumerate(file_pages_text[p]):
                h = sum(len(r.findall(t)) for r in rx)
                if h:
                    page_hits[c["id"]][(p, i + 1)] += h
    for cid, hits in page_hits.items():
        n = nodes[cid]
        have = {(s["file"], s["page"]) for s in n["sources"]}
        per_file = defaultdict(list)
        for (p, pg), h in hits.items():
            per_file[p].append((h, pg))
        auto = []
        for p, lst in per_file.items():
            lst.sort(reverse=True)
            for h, pg in lst[:3]:
                if (p, pg) not in have:
                    auto.append((h, p, pg))
        auto.sort(reverse=True)
        for h, p, pg in auto[:6]:
            n["sources"].append(dict(file=p, page=pg, note=f"{h} ocorrência(s) de palavras-chave", verified=False, kind=file_kind(p)))
        n["page_count"] = len(hits)
    for cid in concept_ids:
        nodes[cid].setdefault("page_count", 0)
        nodes[cid]["page_count"] += sum(1 for s in nodes[cid]["sources"] if s["verified"])

    # horizonte: localizar a página do índice do Stewart
    stew = file_pages_text.get(K.F["STEW"], [])
    for c in K.CONCEPTS:
        if c["uc"] != "hz":
            continue
        for s in nodes[c["id"]]["sources"]:
            if s["file"] == K.F["STEW"] and s["page"] is None and stew:
                m = re.search(r"(\d+\.\d+)", s["note"])
                if m:
                    for i, t in enumerate(stew):
                        if re.search(r"^\s*" + re.escape(m.group(1)) + r"\b", t, re.M):
                            s["page"] = i + 1
                            s["note"] += f" — índice na pág. {i + 1} do PDF"
                            break

    # ---------------------------------------------------- relações curadas
    for r in K.REL:
        if r["source"] not in nodes or r["target"] not in nodes:
            issues["relacoes_com_no_inexistente"].append(f"{r['source']} --{r['type']}--> {r['target']}")
            continue
        if not r["evidence"]:
            issues["relacoes_sem_justificacao_removidas"].append(f"{r['source']} --{r['type']}--> {r['target']}")
            continue
        if not r["justification"]:
            r = dict(r, justification="Relação indicada diretamente na fonte citada." if r["nature"] == "explicita" else "Inferida a partir do conteúdo da fonte citada.")
            issues["relacoes_com_justificacao_generica"].append(f"{r['source']} --{r['type']}--> {r['target']}")
        cross = nodes[r["source"]]["uc"] != nodes[r["target"]]["uc"]
        add_edge(r["source"], r["target"], r["type"], r["nature"], r["confidence"], r["evidence"], r["justification"], cross_uc=cross)

    # ---------------------------------------------------- ficheiros e aulas (cadernos)
    file_node = {}
    for f in files:
        kind = file_kind(f["path"])
        uc = uc_of_path(f["path"])
        if kind in ("codigo", "config"):
            continue
        t = texts.get(f["path"])
        pages = t["pages"] if t else None
        chars = sum(len(x.strip()) for x in t["text"]) if t else 0
        if kind == "caderno":
            m = re.match(r"^(CAL|ED|ALGA) (\d+)\.pdf$", os.path.basename(f["path"]))
            nid = f"aula_{m.group(1).lower()}_{int(m.group(2)):02d}"
            n = add_node(dict(id=nid, type="aula", label=f"{m.group(1)} {m.group(2)}", desc="Caderno de apontamentos manuscritos (digitalizado; lido visualmente).",
                              uc=uc, file=f["path"], pages=pages, kind=kind, seq=int(m.group(2)), status="lecionado"))
        else:
            nid = "f_" + re.sub(r"[^a-z0-9]+", "_", norm(f["path"])).strip("_")
            label = os.path.splitext(os.path.basename(f["path"]))[0]
            n = add_node(dict(id=nid, type="ficheiro", label=label, desc=KIND_LABEL[kind], uc=uc, file=f["path"], pages=pages, kind=kind,
                              text_chars=chars, partial=(t and t.get("extracted_pages", pages) != pages), status="lecionado"))
        file_node[f["path"]] = nid
    # aulas: followed_by (ordem pela numeração dos ficheiros)
    aulas = defaultdict(list)
    for n in nodes.values():
        if n["type"] == "aula":
            aulas[n["uc"]].append(n)
    for uc, lst in aulas.items():
        lst.sort(key=lambda x: x["seq"])
        for a, b in zip(lst, lst[1:]):
            add_edge(a["id"], b["id"], "followed_by", "inferida", "media", "numeração dos ficheiros", "Ordem assumida pela numeração dos cadernos (as datas de modificação são iguais).")
    # slides / fichas numeradas pelo professor
    seqs = [[K.F["IC0"], K.F["IC1"], K.F["IC2"], K.F["IC3"]], [K.F["F1"], K.F["F2"], K.F["F3"], K.F["F4"]],
            [K.F["ALGA_S1"], K.F["ALGA_S2"], K.F["ALGA_S3"]], [K.F["ALGA_E1"], K.F["ALGA_E2"]]]
    for seq in seqs:
        for a, b in zip(seq, seq[1:]):
            if a in file_node and b in file_node:
                add_edge(file_node[a], file_node[b], "followed_by", "explicita", "alta", "numeração do professor", "Ficheiros numerados (capítulos/folhas).")
    # UC contém ficheiros/aulas
    for p, nid in file_node.items():
        uc = nodes[nid]["uc"]
        if uc:
            add_edge(uc, nid, "contains", "explicita", "alta", p, "Ficheiro na pasta da UC.")

    # conceito -> fonte (explained_in / appears_in)
    for cid in concept_ids:
        n = nodes[cid]
        seen = set()
        for s in n["sources"]:
            tgt = file_node.get(s["file"])
            if not tgt or (tgt, s["page"]) in seen:
                continue
            seen.add((tgt, s["page"]))
            typ = "explained_in" if s["kind"] in ("slides", "resumo", "caderno", "livro") else "appears_in"
            add_edge(cid, tgt, typ, "explicita" if s["verified"] else "inferida", "alta" if s["verified"] else "media",
                     f"{s['file']}#{s['page']}" if s["page"] else s["file"], s["note"] or ("Localizado por palavras-chave." if not s["verified"] else ""),
                     page=s["page"])

    # ---------------------------------------------------- exercícios
    ex_count = 0

    def add_ex(eid, label, uc, file, page, primary, secondary, diff, desc="", solved_in=None, status="lecionado", extra=None):
        nonlocal ex_count
        n = dict(id=eid, type="exercicio", label=label, uc=uc, file=file, page=page, desc=desc, difficulty=diff,
                 difficulty_why="Estimativa (INFERIDA) pelo nº de conceitos e passos envolvidos." if diff else "",
                 primary=primary, secondary=secondary, solved_in=solved_in or [], status=status)
        if extra:
            n.update(extra)
        add_node(n)
        ex_count += 1
        for c in primary:
            if c in nodes:
                add_edge(c, eid, "tested_by", "explicita" if solved_in or uc == "ip" else "inferida", "alta" if solved_in else "media", f"{file}#{page}" if page else file,
                         "Conceito principal do exercício (resolução lida)." if solved_in else "Classificado por palavras-chave do enunciado.")
        for c in secondary:
            if c in nodes:
                add_edge(eid, c, "requires", "inferida", "media", f"{file}#{page}" if page else file, "Conceito secundário usado na resolução.")
        if file in file_node:
            add_edge(eid, file_node[file], "appears_in", "explicita", "alta", f"{file}#{page}" if page else file, "", page=page)
        for s in solved_in or []:
            if s["file"] in file_node and s["file"] != file:
                add_edge(eid, file_node[s["file"]], "appears_in", "explicita", "alta", f"{s['file']}#{s['page']}", "Resolução no caderno.", page=s["page"])
        return n

    # IP: cada exN.py é um exercício
    for nnum, (prim, sec, d) in K.IP_EX.items():
        path = f"Introdução à Programação/ex{nnum}.py"
        if path not in fset:
            issues["ficheiros_esperados_em_falta"].append(path)
            continue
        code = ""
        try:
            code = open(os.path.join(root, path), encoding="utf-8", errors="replace").read()
        except Exception:
            pass
        diff = 1 + min(4, (len(code) > 150) + (len(code) > 280) + (len(code) > 450) + ("while" in code and "for" in code))
        add_ex(f"ex_ip_{nnum:02d}", f"IP ex{nnum} · {d}", "ip", path, None, prim, sec, diff, desc=d,
               solved_in=[dict(file=path, page=None)], extra=dict(code_lines=code.count("\n") + 1 if code else None))
    # aulas IP: sem cadernos — a ordem ex1→ex44 já está no tema

    # fichas com texto
    solved_map = defaultdict(list)  # (file, numero) -> [(caderno, page)]
    loose_solved = []
    for uc, label, file, page, prim, sec, d in K.SOLVED:
        nums = []
        if uc == "ed" and label.startswith("ED ex."):
            nums = [int(x) for x in re.findall(r"\b(\d+)\b", label.split("(")[0])]
            tgt = K.F["ED_E"]
        elif uc == "alga" and label.startswith("ALGA ex."):
            nums = re.findall(r"(\d+\.\d+)", label)
            tgt = K.F["ALGA_E1"] if all(x.startswith("1.") for x in nums) else K.F["ALGA_E2"]
        if nums:
            for x in nums:
                solved_map[(tgt, str(x))].append(dict(file=file, page=page, prim=prim, sec=sec))
        else:
            loose_solved.append((uc, label, file, page, prim, sec, d))
    for i, (uc, label, file, page, prim, sec, d) in enumerate(loose_solved):
        add_ex(f"ex_{uc}_cad_{i:02d}", label, uc, file, page, prim, sec, d, desc="Exercício resolvido no caderno.", solved_in=[dict(file=file, page=page)])

    def parse_sheet(path, pattern, seq_int):
        pages = texts.get(path, {}).get("text", [])
        items, cur, expected = [], None, 1
        for pi, t in enumerate(pages):
            for line in t.splitlines():
                m = re.match(pattern, line)
                ok = False
                if m:
                    num = m.group(1)
                    if seq_int:
                        ok = int(num) == expected
                    else:
                        ok = True
                if ok:
                    if cur:
                        items.append(cur)
                    cur = dict(num=num, page=pi + 1, text=line)
                    if seq_int:
                        expected = int(num) + 1
                elif cur:
                    cur["text"] += "\n" + line
        if cur:
            items.append(cur)
        return items

    ed_sections = [(1, 28, ["tabela_verdade", "equivalencia_logica", "tautologia", "fnd", "fnc", "prova_formal", "quantificadores", "negacao_quant", "formalizacao", "conectivas"], "lecionado"),
                   (29, 60, ["op_conjuntos", "partes", "provas_conjuntos", "cardinalidade", "subconjunto", "produto_cartesiano", "inclusao_exclusao"], "lecionado"),
                   (61, 97, ["inducao", "recorrencia", "inducao_forte", "prova_contradicao", "prova_direta"], "lecionado"),
                   (98, 131, ["divisibilidade", "mdc_euclides", "primos"], "programado"),
                   (132, 173, ["relacoes", "funcoes_discretas", "produto_cartesiano"], "programado"),
                   (174, 214, ["contagem"], "programado"),
                   (215, 999, ["grafos"], "programado")]
    sheet_specs = [(K.F["ALGA_E1"], r"^\s*(\d\.\d+)\s", False, "alga"), (K.F["ALGA_E2"], r"^\s*(\d\.\d+)\s", False, "alga"),
                   (K.F["F1"], r"^\s*(\d+)\.\s", True, "ic"), (K.F["F2"], r"^\s*(\d+)\.\s", True, "ic"), (K.F["F3"], r"^\s*(\d+)\.\s", True, "ic"),
                   (K.F["F4"], r"^\s*(\d+)\.\s", True, "ic"), (K.F["ED_E"], r"^\s*(\d+)\.\s", True, "ed")]
    blocks = {}
    for path, pat, seq_int, uc in sheet_specs:
        if path not in texts:
            issues["fichas_sem_texto"].append(path)
            continue
        items = parse_sheet(path, pat, seq_int)
        rules = [(re.compile(rx, re.I), c) for rx, c in K.SHEET_RULES.get(path, [])]
        for it in items:
            num = it["num"]
            pool, status = None, "lecionado"
            if path == K.F["ED_E"]:
                k = int(num)
                for a, b, pl, stt in ed_sections:
                    if a <= k <= b:
                        pool, status = pl, stt
                        break
            found = []
            for rx, c in rules:
                if rx.search(it["text"]) and c not in found and (pool is None or c in pool):
                    found.append(c)
            if not found and pool:
                found = [pool[0]]
            if not found:
                issues["exercicios_sem_conceito"].append(f"{path} ex. {num}")
                continue
            short = re.sub(r"\s+", " ", it["text"]).strip()
            short = re.sub(r"^\d+(\.\d+)?\.?\s*", "", short)[:180]
            solved = solved_map.get((path, num), [])
            label_prefix = {"alga": "ALGA", "ic": "IC " + os.path.basename(path)[:-4], "ed": "ED"}[uc]
            if status == "programado":
                key = (path, found[0])
                if key not in blocks:
                    blocks[key] = dict(nums=[], page=it["page"], concept=found[0], uc=uc)
                blocks[key]["nums"].append(num)
                continue
            prim = found[:1] + [c for s in solved for c in s["prim"] if c not in found[:1]]
            sec = [c for c in found[1:4] if c not in prim] + [c for s in solved for c in s["sec"] if c not in prim]
            nconc = len(set(prim + sec))
            d = min(5, 1 + nconc // 2 + (len(it["text"]) > 400) + (len(it["text"]) > 900))
            add_ex(f"ex_{uc}_{norm(os.path.basename(path)).replace(' ', '_')}_{num.replace('.', '_')}", f"{label_prefix} ex. {num}", uc, path, it["page"],
                   prim, list(dict.fromkeys(sec)), d, desc=short, solved_in=[dict(file=s["file"], page=s["page"]) for s in solved])
    for (path, cid), b in blocks.items():
        nums = b["nums"]
        add_ex(f"exb_{cid}", f"ED ex. {nums[0]}–{nums[-1]} ({len(nums)} exercícios)", b["uc"], path, b["page"], [cid], [], 3,
               desc=f"Bloco de {len(nums)} exercícios de um tema ainda não lecionado (agrupados para não sobrecarregar a graph).", status="programado",
               extra=dict(block=True, count=len(nums)))
    print(f"Exercícios: {ex_count}")

    # ---------------------------------------------------- validação de relações
    conc = [n for n in nodes.values() if n["type"] in ("conceito", "formula", "algoritmo", "ferramenta")]
    cids = {n["id"] for n in conc}
    DEP = ("prerequisite_of", "applied_in", "used_in")
    pairs = defaultdict(set)
    for e in edges:
        pairs[(e["source"], e["target"])].add(e["type"])
    for e in edges:
        if e["type"] == "prerequisite_of" and "prerequisite_of" in pairs.get((e["target"], e["source"]), set()):
            issues["relacoes_contraditorias"].append(f"{e['source']} ⇄ {e['target']}")
    # ciclos no grafo de dependências -> remover a aresta de menor confiança
    rank = dict(alta=3, media=2, baixa=1)
    while True:
        adj = defaultdict(list)
        for e in edges:
            if e["type"] in DEP and e["source"] in cids and e["target"] in cids and not e.get("dropped"):
                adj[e["source"]].append(e)
        color, stack_edges, cycle = {}, [], None

        def dfs(u):
            nonlocal cycle
            color[u] = 1
            for e in adj[u]:
                v = e["target"]
                if cycle:
                    return
                if color.get(v) == 1:
                    idx = next(i for i, x in enumerate(stack_edges) if x["source"] == v) if any(x["source"] == v for x in stack_edges) else 0
                    cycle = stack_edges[idx:] + [e]
                    return
                if color.get(v) is None:
                    stack_edges.append(e)
                    dfs(v)
                    if cycle:
                        return
                    stack_edges.pop()
            color[u] = 2

        sys.setrecursionlimit(10000)
        for u in list(adj):
            if color.get(u) is None and not cycle:
                dfs(u)
        if not cycle:
            break
        weakest = min(cycle, key=lambda e: (rank[e["confidence"]], e["nature"] == "explicita"))
        weakest["type"] = "related_to"
        weakest["justification"] += " [convertida de dependência em related_to para eliminar um ciclo]"
        issues["ciclos_resolvidos"].append(" → ".join([x["source"] for x in cycle] + [cycle[-1]["target"]]))

    # ---------------------------------------------------- métricas
    dep_out, dep_in = defaultdict(set), defaultdict(set)
    for e in edges:
        if e["type"] in DEP and e["source"] in cids and e["target"] in cids:
            dep_out[e["source"]].add(e["target"])
            dep_in[e["target"]].add(e["source"])

    def reach(start, g):
        seen, dq = set(), deque([start])
        while dq:
            u = dq.popleft()
            for v in g[u]:
                if v not in seen:
                    seen.add(v)
                    dq.append(v)
        return seen

    desc = {c: reach(c, dep_out) for c in cids}
    anc = {c: reach(c, dep_in) for c in cids}
    # PageRank no grafo invertido (dependente -> pré-requisito)
    N = len(cids)
    pr = {c: 1 / N for c in cids}
    for _ in range(60):
        newp = {c: (1 - 0.85) / N for c in cids}
        for c in cids:
            outs = dep_in[c]  # dependente c aponta para os seus pré-requisitos
            if outs:
                share = 0.85 * pr[c] / len(outs)
                for p in outs:
                    newp[p] += share
            else:
                for p in cids:
                    newp[p] += 0.85 * pr[c] / N
        pr = newp
    # intermediação (Brandes) no grafo não dirigido de conceitos
    und = defaultdict(set)
    for e in edges:
        if e["source"] in cids and e["target"] in cids and e["type"] not in ("contains", "followed_by"):
            und[e["source"]].add(e["target"])
            und[e["target"]].add(e["source"])
    bc = dict.fromkeys(cids, 0.0)
    for s in cids:
        S, P, sigma, dist = [], defaultdict(list), dict.fromkeys(cids, 0), dict.fromkeys(cids, -1)
        sigma[s], dist[s] = 1, 0
        Q = deque([s])
        while Q:
            v = Q.popleft()
            S.append(v)
            for w in und[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    Q.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    P[w].append(v)
        delta = dict.fromkeys(cids, 0.0)
        while S:
            w = S.pop()
            for v in P[w]:
                delta[v] += sigma[v] / sigma[w] * (1 + delta[w])
            if w != s:
                bc[w] += delta[w]
    # exercícios por conceito
    ex_primary, ex_secondary = Counter(), Counter()
    for e in edges:
        if e["type"] == "tested_by" and e["source"] in cids:
            tn = nodes[e["target"]]
            w = tn.get("count", 1) * (0.2 if tn.get("status") == "programado" else 1)
            ex_primary[e["source"]] += w
        if e["type"] == "requires" and e["target"] in cids and nodes[e["source"]]["type"] == "exercicio":
            ex_secondary[e["target"]] += 1
    # vizinhos de outras UCs
    cross_ucs = defaultdict(set)
    for e in edges:
        if e["source"] in cids and e["target"] in cids and e["type"] not in ("contains", "followed_by"):
            a, b = nodes[e["source"]], nodes[e["target"]]
            if a["uc"] != b["uc"]:
                cross_ucs[a["id"]].add(b["uc"])
                cross_ucs[b["id"]].add(a["uc"])

    def nz(d):
        m = max(d.values()) or 1
        return {k: v / m for k, v in d.items()}

    f_pr, f_desc, f_ex = nz(pr), nz({c: len(desc[c]) for c in cids}), nz({c: math.sqrt(ex_primary[c] + 0.5 * ex_secondary[c]) for c in cids})
    f_freq, f_bc = nz({c: nodes[c]["page_count"] for c in cids}), nz({c: math.sqrt(bc[c]) for c in cids})
    score = {c: 0.30 * f_pr[c] + 0.30 * f_desc[c] + 0.15 * f_ex[c] + 0.12 * f_freq[c] + 0.13 * f_bc[c] for c in cids}
    ranked = sorted(cids, key=lambda c: -score[c])
    for i, c in enumerate(ranked):
        q = i / max(1, len(ranked) - 1)
        imp = 5 if q < 0.08 else 4 if q < 0.25 else 3 if q < 0.55 else 2 if q < 0.82 else 1
        n = nodes[c]
        parts = []
        if desc[c]:
            parts.append(f"pré-requisito (direto ou indireto) de {len(desc[c])} conceito(s)")
        if ex_primary[c] or ex_secondary[c]:
            parts.append(f"testado em {ex_primary[c]} exercício(s) como conceito principal e {ex_secondary[c]} como secundário")
        if n["page_count"]:
            parts.append(f"aparece em {n['page_count']} página(s) dos materiais")
        if cross_ucs[c]:
            parts.append("liga a " + ", ".join(sorted(ucmap[u]["short"] for u in cross_ucs[c])))
        if bc[c] > 0 and f_bc[c] > 0.35:
            parts.append("ponte entre áreas (intermediação alta)")
        n.update(importance=imp, importance_score=round(score[c], 4), importance_why="; ".join(parts).capitalize() + "." if parts else "Pouco ligado a outros conceitos.",
                 metrics=dict(pagerank=round(pr[c], 5), dependents=len(desc[c]), prerequisites_total=len(anc[c]), direct_dependents=len(dep_out[c]),
                              direct_prerequisites=len(dep_in[c]), exercises=ex_primary[c], exercises_secondary=ex_secondary[c],
                              betweenness=round(bc[c], 2), cross_uc=sorted(cross_ucs[c]), pages=n["page_count"]))
    # profundidade / camadas
    layer = {}

    def L(c, stack=()):
        if c in layer:
            return layer[c]
        ps = [p for p in dep_in[c] if p not in stack]
        layer[c] = 0 if not ps else 1 + max(L(p, stack + (c,)) for p in ps)
        return layer[c]

    for c in cids:
        L(c)
        nodes[c]["layer"] = layer[c]
        nodes[c]["depth"] = layer[c]

    # bottlenecks
    def bscore(c):
        return sum(1 + nodes[d]["importance"] / 5 for d in desc[c])

    bott = sorted([c for c in cids if desc[c]], key=lambda c: -bscore(c))[:20]
    bottlenecks = []
    for c in bott:
        ds = sorted(desc[c], key=lambda d: (-nodes[d]["importance"], nodes[d]["label"]))
        ucs_aff = sorted({nodes[d]["uc"] for d in ds})
        # caminho mais longo a partir de c (exemplo de cadeia)
        best = []

        def longest(u, path):
            nonlocal best
            if len(path) > len(best):
                best = list(path)
            for v in dep_out[u]:
                if v not in path and len(path) < 12:
                    longest(v, path + [v])

        longest(c, [c])
        bottlenecks.append(dict(id=c, score=round(bscore(c), 2), dependents=len(ds), dependents_list=ds, ucs=ucs_aff, chain=best,
                                horizon=[d for d in ds if nodes[d]["status"] == "horizonte"]))
        nodes[c]["bottleneck_rank"] = len(bottlenecks)

    # ---------------------------------------------------- layout: mapa radial
    uc_list = [u["id"] for u in K.UCS]
    tema_list = defaultdict(list)
    for tid, uc, *_ in K.TEMAS:
        tema_list[uc].append(tid)
    conc_by_tema = defaultdict(list)
    for c in K.CONCEPTS:
        conc_by_tema[c["tema"]].append(c["id"])
    # profundidade local (só dependências dentro da UC)
    local = {}

    def LL(c, stack=()):
        if c in local:
            return local[c]
        ps = [p for p in dep_in[c] if nodes[p]["uc"] == nodes[c]["uc"] and p not in stack]
        local[c] = 0 if not ps else 1 + max(LL(p, stack + (c,)) for p in ps)
        return local[c]

    for c in cids:
        LL(c)
    # sub-layout de cada tema: coluna por profundidade relativa ao mínimo do tema
    SPX, SPY = 96, 60
    tema_box = {}
    for t, lst in conc_by_tema.items():
        mind = min(local[c] for c in lst)
        rank = {dpt: i for i, dpt in enumerate(sorted({local[c] for c in lst}))}  # comprime saltos de profundidade
        cols = defaultdict(list)
        for c in lst:
            cols[rank[local[c]]].append(c)
        for k in cols:
            cols[k].sort(key=lambda c: (-nodes[c]["importance"], nodes[c]["label"]))
        width = max(len(v) for v in cols.values())
        tema_box[t] = dict(cols=cols, width=width, depth=max(cols) + 1, mind=mind)
    tema_label = {tid: name for tid, _uc, name, *_ in K.TEMAS}

    def tema_w(t):  # largura reservada no anel: o maior entre a "pílula" do tema e o leque de conceitos
        return max(len(tema_label[t]) * 9.6 + 40 + 36, max(1.6, tema_box.get(t, {"width": 1})["width"]) * SPY + 70)

    cluster_w = {}
    for uc in uc_list:
        cluster_w[uc] = sum(tema_w(t) for t in tema_list[uc])
    total = sum(cluster_w.values())
    R = max(1300, total / (2 * math.pi) * 1.05)
    ang = -math.pi / 2
    pos = {"iacd": (0.0, 0.0)}
    for uc in uc_list:
        span = cluster_w[uc] / total * 2 * math.pi
        a = ang + span / 2
        ang += span
        ux, uy = math.cos(a), math.sin(a)
        vx, vy = -uy, ux
        cx, cy = R * 0.55 * ux, R * 0.55 * uy
        pos[uc] = (cx, cy)
        # temas ao longo do arco exterior
        ts = tema_list[uc]
        arc_w = cluster_w[uc]
        offs = -arc_w / 2
        for t in ts:
            w = tema_w(t)
            mid = offs + w / 2
            offs += w
            ta = a + mid / R  # ângulo do tema no anel
            tr = R * 0.86
            tx, ty = tr * math.cos(ta), tr * math.sin(ta)
            pos[t] = (tx, ty)
            box = tema_box.get(t)
            if not box:
                continue
            tux, tuy = math.cos(ta), math.sin(ta)
            tvx, tvy = -tuy, tux
            for k, lst in box["cols"].items():
                for j, c in enumerate(lst):
                    off = (j - (len(lst) - 1) / 2) * SPY
                    d = 115 + k * SPX
                    pos[c] = (tx + tux * d + tvx * off, ty + tuy * d + tvy * off)
        # ficheiros e aulas: anel interior perto da UC
        fl = [n for n in nodes.values() if n["type"] in ("ficheiro", "aula") and n["uc"] == uc]
        fl.sort(key=lambda n: (n["type"], n.get("seq", 0), n["label"]))
        for j, n in enumerate(fl):
            off = (j - (len(fl) - 1) / 2) * 44
            pos[n["id"]] = (cx - ux * 210 + vx * off, cy - uy * 210 + vy * off)
    # exercícios orbitam o conceito principal
    orbit = defaultdict(int)
    for n in nodes.values():
        if n["type"] == "exercicio":
            anchor = (n.get("primary") or [None])[0]
            base = pos.get(anchor) or pos.get(n["uc"]) or (0, 0)
            k = orbit[anchor]
            orbit[anchor] += 1
            rr = 46 + 14 * (k // 8)
            th = k * (2 * math.pi / 8) + 0.4 * (k // 8)
            pos[n["id"]] = (base[0] + rr * math.cos(th), base[1] + rr * math.sin(th))
    for nid, n in nodes.items():
        x, y = pos.get(nid, (0, 0))
        n["pos"] = dict(map=dict(x=round(x, 1), y=round(y, 1)))

    # ---------------------------------------------------- layout: roadmap (camadas × faixas por UC)
    lanes = [u for u in uc_list]
    max_layer = max(layer.values()) if layer else 0
    lane_y, y = {}, 0
    LX, LY = 240, 46
    lane_info = []
    for uc in lanes:
        cs = [c for c in cids if nodes[c]["uc"] == uc]
        per = Counter(layer[c] for c in cs)
        h = max(per.values()) if per else 1
        lane_y[uc] = y
        lane_info.append(dict(uc=uc, y=y, h=h * LY + 40))
        bylayer = defaultdict(list)
        for c in cs:
            bylayer[layer[c]].append(c)
        for l, lst in bylayer.items():
            lst.sort(key=lambda c: (nodes[c]["tema"], -nodes[c]["importance"]))
            for j, c in enumerate(lst):
                nodes[c]["pos"]["roadmap"] = dict(x=l * LX, y=y + 20 + j * LY)
        y += h * LY + 70
    stage_names = ["Fundamentos", "Linguagem e ferramentas", "Técnicas", "Construções", "Métodos", "Aplicações", "Síntese", "Avançado", "Avançado", "Avançado", "Avançado", "Avançado", "Avançado"]
    roadmap = dict(layers=max_layer + 1, lanes=lane_info, LX=LX,
                   stages=[dict(layer=i, name=stage_names[min(i, len(stage_names) - 1)], count=sum(1 for c in cids if layer[c] == i)) for i in range(max_layer + 1)])

    # ---------------------------------------------------- qualidade
    names = defaultdict(list)
    for c in conc:
        names[norm(c["label"])].append(c["id"])
    for k, v in names.items():
        if len(v) > 1:
            issues["conceitos_duplicados"].append(f"{k}: {v}")
    alias_owner = defaultdict(set)
    for c in conc:
        for a in c.get("aliases", []):
            alias_owner[norm(a)].add(c["id"])
    for a, owners in alias_owner.items():
        if len(owners) > 1 and a:
            issues["nomes_ambiguos_partilhados"].append(f"'{a}': {sorted(owners)}")
    for c in conc:
        if not c["sources"]:
            issues["conceitos_sem_fonte"].append(c["id"])
        if not any(s["verified"] for s in c["sources"]):
            issues["conceitos_sem_fonte_verificada"].append(c["id"])
    # ligações a ficheiros
    for n in nodes.values():
        for s in n.get("sources", []):
            if s["file"] not in fset:
                issues["links_partidos"].append(f"{n['id']} → {s['file']}")
            elif s["page"] and texts.get(s["file"]) and s["page"] > texts[s["file"]]["pages"]:
                issues["paginas_invalidas"].append(f"{n['id']} → {s['file']}#{s['page']}")
        if n.get("file") and n["file"] not in fset:
            issues["links_partidos"].append(f"{n['id']} → {n['file']}")
    analysed = []
    for f in files:
        k = file_kind(f["path"])
        t = texts.get(f["path"])
        if k == "codigo":
            st = "lido (código)"
        elif k == "config":
            st = "ignorado (configuração do editor)"
        elif k == "caderno":
            chars = sum(len(x.strip()) for x in t["text"]) if t else 0
            st = "lido visualmente (digitalização sem texto)" if chars < 200 else "texto extraído"
            if f["path"].endswith("ED 4.pdf"):
                st = "vazio (2 páginas em branco)"
        elif t and t.get("extracted_pages", 0) < t.get("pages", 0):
            st = f"parcial (índice: {t['extracted_pages']} de {t['pages']} páginas)"
        elif t:
            st = "texto extraído e analisado"
        else:
            st = "NÃO analisado"
            issues["ficheiros_nao_analisados"].append(f["path"])
        analysed.append(dict(path=f["path"], kind=KIND_LABEL.get(k, k), status=st, size=f["size"]))
    nat = Counter((e["nature"], e["confidence"]) for e in edges if e["type"] not in ("contains",))

    # ---------------------------------------------------- estatísticas
    stats = dict(ucs=sum(1 for n in nodes.values() if n["type"] == "uc" and not n.get("horizon")),
                 temas=sum(1 for n in nodes.values() if n["type"] == "tema"),
                 conceitos=len(conc), exercicios=sum(1 for n in nodes.values() if n["type"] == "exercicio"),
                 ficheiros_analisados=sum(1 for a in analysed if "NÃO" not in a["status"] and "ignorado" not in a["status"]),
                 ficheiros_total=len(files),
                 relacoes=len(edges), relacoes_conceptuais=sum(1 for e in edges if e["source"] in cids and e["target"] in cids),
                 relacoes_entre_ucs=sum(1 for e in edges if e["source"] in cids and e["target"] in cids and nodes[e["source"]]["uc"] != nodes[e["target"]]["uc"]),
                 explicitas=sum(1 for e in edges if e["nature"] == "explicita"), inferidas=sum(1 for e in edges if e["nature"] == "inferida"),
                 by_type=Counter(n["type"] for n in nodes.values()), by_edge=Counter(e["type"] for e in edges),
                 by_uc={u: sum(1 for c in conc if c["uc"] == u) for u in uc_list})
    for c in conc:
        c.pop("kw", None)
    meta = dict(title="IACD Knowledge Graph", generated=datetime.now().isoformat(timespec="seconds"), root=os.path.basename(os.path.abspath(root)),
                version=2, build_seconds=None,
                relation_types=dict(contains="A contém B (hierarquia UC → tema → conceito)", part_of="inverso de contains (derivado)",
                                    prerequisite_of="A é pré-requisito de B", requires="exercício requer conceito (secundário)",
                                    related_to="relação simétrica/associativa", used_in="A é usado em B", applied_in="A é aplicado em B",
                                    appears_in="A aparece no ficheiro B", explained_in="A é explicado no ficheiro/aula B",
                                    tested_by="conceito A é testado pelo exercício B", followed_by="ordem temporal (não implica dependência)"),
                confidence=dict(explicita="indicada diretamente nos materiais", inferida="deduzida a partir do conteúdo — nunca apresentada como ensinada"))
    meta["build_seconds"] = round((datetime.now() - t0).total_seconds(), 2)
    data = dict(meta=meta, stats=stats, nodes=list(nodes.values()), edges=edges, bottlenecks=bottlenecks, roadmap=roadmap,
                files=analysed, quality={k: v for k, v in issues.items()}, confidence_breakdown={f"{a}/{b}": v for (a, b), v in nat.items()})
    return data


# ---------------------------------------------------------------------------- exportação
def export(data, outdir):
    os.makedirs(outdir, exist_ok=True)
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(outdir, "kg.json"), "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=1))
    open(os.path.join(outdir, "kg.js"), "w", encoding="utf-8").write("/* gerado por build/build.py — não editar */\nwindow.KG_DATA = " + js + ";\n")
    csvdir = os.path.join(outdir, "csv")
    os.makedirs(csvdir, exist_ok=True)
    ncols = ["id", "type", "label", "uc", "tema", "status", "difficulty", "importance", "layer", "desc", "formula", "file", "page"]
    with open(os.path.join(csvdir, "nodes.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(ncols + ["aliases", "dependents", "pagerank", "betweenness"])
        for n in data["nodes"]:
            m = n.get("metrics", {})
            w.writerow([n.get(k) if n.get(k) is not None else "" for k in ncols] + ["|".join(n.get("aliases", []) or []), m.get("dependents", ""), m.get("pagerank", ""), m.get("betweenness", "")])
    ecols = ["id", "source", "target", "type", "nature", "confidence", "evidence", "justification"]
    with open(os.path.join(csvdir, "edges.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(ecols)
        for e in data["edges"]:
            w.writerow([e.get(k, "") for k in ecols])
    with open(os.path.join(csvdir, "sources.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["node_id", "file", "page", "verified", "kind", "note"])
        for n in data["nodes"]:
            for s in n.get("sources", []):
                w.writerow([n["id"], s["file"], s["page"] or "", int(bool(s["verified"])), s["kind"], s["note"]])
    dbp = os.path.join(outdir, "kg.sqlite")
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="iacd_kg_")
    tmp = os.path.join(tmpdir, "kg.sqlite")  # construída fora da pasta (OneDrive/ligações remotas não gostam de journals)
    db = sqlite3.connect(tmp)
    db.executescript("""
    CREATE TABLE nodes(id TEXT PRIMARY KEY, type TEXT, label TEXT, uc TEXT, tema TEXT, status TEXT, difficulty INT, difficulty_why TEXT,
        importance INT, importance_why TEXT, layer INT, description TEXT, formula TEXT, file TEXT, page INT, aliases TEXT, metrics_json TEXT);
    CREATE TABLE edges(id TEXT PRIMARY KEY, source TEXT REFERENCES nodes(id), target TEXT REFERENCES nodes(id), type TEXT, nature TEXT,
        confidence TEXT, evidence TEXT, justification TEXT);
    CREATE TABLE sources(node_id TEXT REFERENCES nodes(id), file TEXT, page INT, verified INT, kind TEXT, note TEXT);
    CREATE TABLE files(path TEXT PRIMARY KEY, kind TEXT, status TEXT, size INT);
    CREATE TABLE bottlenecks(rank INT, concept_id TEXT, score REAL, dependents INT, chain TEXT);
    CREATE INDEX ix_edges_s ON edges(source); CREATE INDEX ix_edges_t ON edges(target); CREATE INDEX ix_nodes_type ON nodes(type);
    """)
    for n in data["nodes"]:
        db.execute("INSERT INTO nodes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (n["id"], n["type"], n["label"], n.get("uc"), n.get("tema"), n.get("status"),
                   n.get("difficulty"), n.get("difficulty_why"), n.get("importance"), n.get("importance_why"), n.get("layer"), n.get("desc"), n.get("formula"),
                   n.get("file"), n.get("page"), "|".join(n.get("aliases", []) or []), json.dumps(n.get("metrics", {}), ensure_ascii=False)))
        for s in n.get("sources", []):
            db.execute("INSERT INTO sources VALUES (?,?,?,?,?,?)", (n["id"], s["file"], s["page"], int(bool(s["verified"])), s["kind"], s["note"]))
    for e in data["edges"]:
        db.execute("INSERT INTO edges VALUES (?,?,?,?,?,?,?,?)", tuple(e.get(k) for k in ecols))
    for f in data["files"]:
        db.execute("INSERT INTO files VALUES (?,?,?,?)", (f["path"], f["kind"], f["status"], f["size"]))
    for i, b in enumerate(data["bottlenecks"]):
        db.execute("INSERT INTO bottlenecks VALUES (?,?,?,?,?)", (i + 1, b["id"], b["score"], b["dependents"], " → ".join(b["chain"])))
    db.commit()
    db.close()
    shutil.copyfile(tmp, dbp)
    shutil.rmtree(tmpdir, ignore_errors=True)
    # RAG
    idx = {n["id"]: n for n in data["nodes"]}
    pre, post = defaultdict(list), defaultdict(list)
    for e in data["edges"]:
        if e["type"] == "prerequisite_of":
            pre[e["target"]].append((e["source"], e["nature"], e["confidence"]))
            post[e["source"]].append(e["target"])
    with open(os.path.join(outdir, "rag_chunks.jsonl"), "w", encoding="utf-8") as f:
        for n in data["nodes"]:
            if n["type"] not in ("conceito", "formula", "algoritmo", "ferramenta"):
                continue
            uc = idx.get(n["uc"], {}).get("label", "")
            tema = idx.get(n["tema"], {}).get("label", "")
            txt = [f"# {n['label']}", f"UC: {uc} · Tema: {tema} · Estado: {n['status']}", n["desc"] or ""]
            if n.get("formula"):
                txt.append(f"Fórmula: {n['formula']}")
            if pre[n["id"]]:
                txt.append("Pré-requisitos: " + "; ".join(f"{idx[a]['label']} ({nat}/{conf})" for a, nat, conf in pre[n["id"]]))
            if post[n["id"]]:
                txt.append("Depende dele: " + "; ".join(idx[b]["label"] for b in post[n["id"]]))
            txt.append("Fontes: " + "; ".join(f"{s['file']}" + (f" p.{s['page']}" if s["page"] else "") for s in n["sources"] if s["verified"]))
            f.write(json.dumps(dict(id=n["id"], title=n["label"], uc=uc, tema=tema, difficulty=n.get("difficulty"), importance=n.get("importance"),
                                    text="\n".join(txt), sources=[s for s in n["sources"]]), ensure_ascii=False) + "\n")
    # relatório de qualidade
    q = data["quality"]
    st = data["stats"]
    L = [f"# Relatório de qualidade — IACD Knowledge Graph", f"Gerado em {data['meta']['generated']}", "",
         "## Números", f"- UCs: {st['ucs']} (+ grupo Horizonte)", f"- Temas: {st['temas']}", f"- Conceitos: {st['conceitos']}", f"- Exercícios: {st['exercicios']}",
         f"- Ficheiros analisados: {st['ficheiros_analisados']} de {st['ficheiros_total']}", f"- Relações: {st['relacoes']} (conceptuais: {st['relacoes_conceptuais']}, entre UCs: {st['relacoes_entre_ucs']})",
         f"- Explícitas: {st['explicitas']} · Inferidas: {st['inferidas']}", "", "## Confiança (sem `contains`)"]
    for k, v in sorted(data["confidence_breakdown"].items()):
        L.append(f"- {k}: {v}")
    L += ["", "## Verificações"]
    checks = [("conceitos_duplicados", "Conceitos duplicados"), ("nomes_ambiguos_partilhados", "Sinónimos partilhados por vários conceitos (nomes inconsistentes)"),
              ("relacoes_contraditorias", "Relações contraditórias (A pré-req. de B e B de A)"), ("ciclos_resolvidos", "Ciclos de dependência resolvidos"),
              ("conceitos_sem_fonte", "Conceitos sem fonte"), ("conceitos_sem_fonte_verificada", "Conceitos sem fonte verificada manualmente"),
              ("relacoes_sem_justificacao_removidas", "Relações sem fonte (removidas)"), ("relacoes_com_justificacao_generica", "Relações com fonte mas sem justificação escrita (texto genérico)"), ("relacoes_com_no_inexistente", "Relações com nós inexistentes (removidas)"),
              ("ficheiros_nao_analisados", "Ficheiros não analisados"), ("links_partidos", "Links para materiais partidos"), ("paginas_invalidas", "Páginas fora do intervalo"),
              ("exercicios_sem_conceito", "Exercícios sem conceito associado"), ("fichas_sem_texto", "Fichas sem texto"), ("ids_duplicados", "IDs duplicados")]
    for key, title in checks:
        v = q.get(key, [])
        L.append(f"### {title}: {len(v)}")
        for x in v[:40]:
            L.append(f"- {x}")
        if len(v) > 40:
            L.append(f"- … (+{len(v) - 40})")
    L += ["", "## Ficheiros", "| Ficheiro | Tipo | Estado |", "|---|---|---|"]
    for f in data["files"]:
        L.append(f"| {f['path']} | {f['kind']} | {f['status']} |")
    open(os.path.join(outdir, "quality_report.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(PROJECT), help="pasta com os materiais (por omissão, a pasta-mãe do projeto)")
    ap.add_argument("--out", default=os.path.join(PROJECT, "data"))
    a = ap.parse_args()
    data = build(a.root)
    export(data, a.out)
    s = data["stats"]
    print(f"OK: {s['conceitos']} conceitos, {s['exercicios']} exercícios, {s['relacoes']} relações ({s['relacoes_entre_ucs']} entre UCs) → {a.out}")
    for k, v in data["quality"].items():
        print(f"  qualidade · {k}: {len(v)}")


if __name__ == "__main__":
    main()
