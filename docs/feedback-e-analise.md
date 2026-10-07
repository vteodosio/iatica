# Quiz Feedback & Per-Question Analytics (D + E)

> **Scope:** **E — quiz feedback** (show *why* an answer is correct + link back to the lesson) and
> **D — per-question analytics** (show the class's success rate per question in the report).

---

## Summary

| Area | What changed | Why it matters |
|---|---|---|
| **E. Quiz feedback** | Each question now carries an **explanation** and a **link to its lesson**; the result page shows "💡 Por quê" and a "📚 Revisar lição" button. | Turns the quiz from a right/wrong scoreboard into a learning moment — the student understands *why*, and can jump straight to the material. |
| **D. Analytics** | The group report now has a **"Dificuldade por Questão"** table: per-question success rate, mapped to the lesson, sorted hardest-first. | Tells the teacher exactly *what the class struggled with*, so they know where to reteach. |

**Verification:** 16 tests pass (3 new) · `manage.py check` clean · `seed_data` re-run cleanly · data verified.

---

## E. Quiz feedback & remediation

### What changed
1. **`Pergunta` gained two fields:**
   - `explicacao` (Text) — why the correct answer is right.
   - `licao` (FK → `content.Licao`, `SET_NULL`) — which lesson the question relates to.
2. **`seed_data.py`** now seeds an explanation and lesson link for all 8 questions (Q1→L1, Q2→L2, Q3→L3, Q4→L4, Q5→L5, Q6→L3, Q7→L5, Q8→L4).
3. **`resultado.html`** shows, under each answer:
   - `💡 Por quê:` the explanation.
   - `📚 Revisar lição: <título>` — a link back to `licao_detalhe` (works because the student is already a group member).

### Files
| File | Change |
|---|---|
| `apps/quiz/models.py` | `Pergunta.explicacao` + `Pergunta.licao` |
| `apps/quiz/migrations/0002_pergunta_explicacao_licao.py` | **new** migration |
| `apps/content/management/commands/seed_data.py` | explanations + lesson links; UTF-8 stdout fix |
| `apps/quiz/views.py` | `select_related('pergunta__licao')` |
| `templates/quiz/resultado.html` | explanation + "revisar lição" link |

---

## D. Per-question analytics

### What changed
`relatorio_grupo` now aggregates `RespostaAluno` for the group's **completed** attempts and computes, per question: total answers, correct answers, and success percentage. It's rendered as a new **"🎯 Dificuldade por Questão"** table (color-coded bar: red < 60%, amber < 80%, green ≥ 80%), sorted **hardest-first**.

### Files
| File | Change |
|---|---|
| `apps/reports/views.py` | aggregation into `dados_perguntas` context |
| `templates/reports/relatorio_grupo.html` | new "Dificuldade por Questão" section |
| `apps/reports/tests.py` | **new** — aggregation correctness + empty-group case |

---

## Migration & seed

```bash
python manage.py migrate        # applies quiz.0002_pergunta_explicacao_licao
python manage.py seed_data      # (re)populates explanations + lesson links
```

> `seed_data` is idempotent (`update_or_create`). On Windows it now forces UTF-8 stdout so the
> ✅/🔄 emoji output doesn't crash on a cp1252 console.

## Tests

```bash
python manage.py test apps.groups apps.quiz apps.content apps.reports
# 16 tests, all passing
```

New tests:
- `apps.quiz.tests.ResultadoQuizFeedbackTests` — result page renders the explanation + lesson link.
- `apps.reports.tests.RelatorioPerQuestaoTests` — per-question totals/percentages are correct, and an empty group doesn't crash.

## Notes / behavior

- Questions with no linked lesson (or deleted lesson) show `—` and omit the "revisar lição" link gracefully (`SET_NULL`).
- The analytics table only counts **completed** attempts (`finalizado_em` set), consistent with the rest of the report.
- The PDF report is unchanged by this PR (per-question analytics is web-only for now; adding it to the PDF is a possible follow-up).
